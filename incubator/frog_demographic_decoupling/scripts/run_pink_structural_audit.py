#!/usr/bin/env python3
"""Structural-only schema and repeat-visit audit of current PINK Amphibia DwC-A.

Allowed: source hash, row types/fields, event/location/date structure, distinct
lifeStage/behavior/sex/status labels and counts by those labels.
Forbidden: individualCount values and any biological stage association.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

URL="https://ipt.inbo.be/archive.do?r=pink-amphibia-events"
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}
FOCAL="Hyla arborea"


def download():
    req=urllib.request.Request(URL,headers={"User-Agent":"frog-pink-structural-audit/0.1"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return r.read()


def local(term):
    return term.rsplit("/",1)[-1].rsplit("#",1)[-1] if term else ""


def dec(v,default):
    if v is None: return default
    return bytes(v,"utf-8").decode("unicode_escape")


def section_rows(zf,section):
    files=section.find("dwc:files",NS)
    loc=files.find("dwc:location",NS)
    fn=loc.text.strip()
    delim=dec(section.attrib.get("fieldsTerminatedBy"),"\t")
    quote=dec(section.attrib.get("fieldsEnclosedBy"),'"')
    ignore=int(section.attrib.get("ignoreHeaderLines","0"))
    enc=section.attrib.get("encoding","UTF-8").replace("-","")
    idel=section.find("dwc:id",NS)
    coreidel=section.find("dwc:coreid",NS)
    ididx=int(idel.attrib["index"]) if idel is not None else None
    coreidx=int(coreidel.attrib["index"]) if coreidel is not None else None
    fields={local(f.attrib.get("term","")):int(f.attrib["index"]) for f in section.findall("dwc:field",NS)}
    reader=csv.reader(io.StringIO(zf.read(fn).decode(enc)),delimiter=delim,quotechar=quote or '"')
    for _ in range(ignore): next(reader,None)
    for row in reader:
        yield row,fields,ididx,coreidx


def get(row,fields,name):
    idx=fields.get(name)
    return row[idx].strip() if idx is not None and idx < len(row) else ""


def main():
    data=download()
    sha=hashlib.sha256(data).hexdigest()
    zf=zipfile.ZipFile(io.BytesIO(data))
    meta=ET.fromstring(zf.read("meta.xml"))
    core=meta.find("dwc:core",NS)
    exts=meta.findall("dwc:extension",NS)

    extension_inventory=[]
    for ext in exts:
        extension_inventory.append({
            "rowType":ext.attrib.get("rowType",""),
            "fields":sorted(local(f.attrib.get("term","")) for f in ext.findall("dwc:field",NS))
        })

    events={}
    site_year_events=defaultdict(set)
    event_months=Counter()
    location_field_candidates=["locationID","locality","parentEventID"]

    for row,fields,ididx,_ in section_rows(zf,core):
        coreid=row[ididx].strip() if ididx is not None else get(row,fields,"eventID")
        eventid=get(row,fields,"eventID") or coreid
        rawdate=get(row,fields,"eventDate")
        if not rawdate:
            continue
        d=date.fromisoformat(rawdate[:10])
        locationid=get(row,fields,"locationID")
        locality=get(row,fields,"locality")
        parent=get(row,fields,"parentEventID")
        stable_site=locationid or locality or parent
        events[coreid]={"eventID":eventid,"date":d,"site":stable_site}
        if stable_site:
            site_year_events[(stable_site,d.year)].add(coreid)
        event_months[d.month]+=1

    occ=None
    for ext in exts:
        if "Occurrence" in ext.attrib.get("rowType",""):
            occ=ext
            break
    if occ is None:
        raise SystemExit("PINK archive has no Occurrence extension")

    label_fields=["lifeStage","behavior","sex","occurrenceStatus","occurrenceRemarks"]
    labels={name:Counter() for name in label_fields}
    focal_labels={name:Counter() for name in label_fields}
    focal_event_rows=Counter()
    species_rows=Counter()

    for row,fields,_,coreidx in section_rows(zf,occ):
        if "individualCount" in fields:
            pass  # field may exist but is deliberately never read
        coreid=row[coreidx].strip()
        species=get(row,fields,"scientificName")
        species_rows[species]+=1
        for name in label_fields:
            value=get(row,fields,name)
            if value!="":
                labels[name][value]+=1
                if species==FOCAL:
                    focal_labels[name][value]+=1
        if species==FOCAL and coreid in events:
            focal_event_rows[coreid]+=1

    repeated_ge2=sum(len(v)>=2 for v in site_year_events.values())
    repeated_ge3=sum(len(v)>=3 for v in site_year_events.values())

    result={
        "audit":"pink_structural_schema_v0_1",
        "source_url":URL,
        "source_sha256":sha,
        "archive_bytes":len(data),
        "core_event_count":len(events),
        "site_year_count":len(site_year_events),
        "site_years_ge2_events":repeated_ge2,
        "site_years_ge3_events":repeated_ge3,
        "event_month_counts":dict(sorted(event_months.items())),
        "extension_inventory":extension_inventory,
        "distinct_label_counts":{
            name:dict(sorted(counter.items()))
            for name,counter in labels.items()
        },
        "focal_species":FOCAL,
        "focal_label_counts":{
            name:dict(sorted(counter.items()))
            for name,counter in focal_labels.items()
        },
        "focal_event_count_with_occurrence_row":len(focal_event_rows),
        "species_row_counts":dict(sorted(species_rows.items())),
        "individual_count_read":False,
        "stage_association_opened":False,
        "ecological_effect_direction_opened":False
    }
    out=Path("frog_pink_structural_schema_v0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
