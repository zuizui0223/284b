#!/usr/bin/env python3
"""Structural-only audit of the current Mohonk Preserve GBIF DwC-A.

Never reads individualCount/organismQuantity and never computes ecological associations.
It inventories whether adult/call, egg, larval states and repeated pool-year structure
survive the GBIF transformation.
"""
from __future__ import annotations
import csv, hashlib, io, json, urllib.request, zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

URL="https://ipt.gbif.us/archive.do?r=mohonk-amphibian-spring-sampling"
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}
LABEL_FIELDS=[
    "lifeStage","behavior","occurrenceStatus","occurrenceRemarks",
    "reproductiveCondition","sex","basisOfRecord"
]


def download():
    req=urllib.request.Request(URL,headers={"User-Agent":"frog-mohonk-structural-audit/0.1"})
    with urllib.request.urlopen(req,timeout=90) as r:
        return r.read()


def local(term):
    return term.rsplit("/",1)[-1].rsplit("#",1)[-1] if term else ""


def dec(v,default):
    if v is None: return default
    return bytes(v,"utf-8").decode("unicode_escape")


def rows(zf,section):
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
    return row[idx].strip() if idx is not None and idx<len(row) else ""


def main():
    data=download()
    sha=hashlib.sha256(data).hexdigest()
    zf=zipfile.ZipFile(io.BytesIO(data))
    meta=ET.fromstring(zf.read("meta.xml"))
    core=meta.find("dwc:core",NS)
    exts=meta.findall("dwc:extension",NS)

    core_fields=sorted(local(f.attrib.get("term","")) for f in core.findall("dwc:field",NS))
    extension_inventory=[
        {
            "rowType":e.attrib.get("rowType",""),
            "fields":sorted(local(f.attrib.get("term","")) for f in e.findall("dwc:field",NS))
        }
        for e in exts
    ]

    labels={k:Counter() for k in LABEL_FIELDS}
    species=Counter()
    year_rows=Counter()
    pool_rows=Counter()
    pool_year_rows=Counter()
    month_rows=Counter()
    field_nonempty=Counter()

    forbidden={"individualCount","organismQuantity","organismQuantityType"}
    forbidden_read=False

    for row,fields,ididx,_ in rows(zf,core):
        # Guard: abundance-bearing fields may exist in schema, but values are never accessed.
        if forbidden & set(fields):
            pass
        sp=get(row,fields,"scientificName")
        if sp: species[sp]+=1
        rawdate=get(row,fields,"eventDate")
        locality=get(row,fields,"locality") or get(row,fields,"locationID") or get(row,fields,"verbatimLocality")
        if rawdate:
            try:
                d=date.fromisoformat(rawdate[:10])
                year_rows[d.year]+=1
                month_rows[d.month]+=1
                if locality: pool_year_rows[(locality,d.year)]+=1
            except ValueError:
                pass
        if locality: pool_rows[locality]+=1
        for name in LABEL_FIELDS:
            value=get(row,fields,name)
            if value:
                labels[name][value]+=1
        for name in [
            "eventID","eventDate","locality","locationID","scientificName",
            "lifeStage","behavior","reproductiveCondition","occurrenceStatus"
        ]:
            if get(row,fields,name)!="": field_nonempty[name]+=1

    years_since_1991={y for y in year_rows if y>=1991}
    pool_years_since_1991={(p,y) for (p,y) in pool_year_rows if y>=1991}

    result={
        "audit":"mohonk_structural_schema_v0_1",
        "source_url":URL,
        "source_sha256":sha,
        "archive_bytes":len(data),
        "core_rowType":core.attrib.get("rowType",""),
        "core_fields":core_fields,
        "extension_inventory":extension_inventory,
        "row_count":sum(species.values()),
        "species_row_counts":dict(sorted(species.items())),
        "label_counts":{
            k:dict(sorted(v.items())) for k,v in labels.items()
        },
        "year_range":[min(year_rows) if year_rows else None,max(year_rows) if year_rows else None],
        "month_row_counts":dict(sorted(month_rows.items())),
        "distinct_pool_labels":len(pool_rows),
        "pool_years_since_1991":len(pool_years_since_1991),
        "years_since_1991":len(years_since_1991),
        "field_nonempty_counts":dict(sorted(field_nonempty.items())),
        "abundance_values_read":False,
        "transition_association_opened":False,
        "hydroclimate_effect_direction_opened":False
    }
    out=Path("frog_mohonk_structural_schema_v0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
