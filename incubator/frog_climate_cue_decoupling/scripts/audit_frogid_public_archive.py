#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, math, urllib.request, zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr14760.zip"
EXPECTED_FIELDS={"eventID","eventDate","scientificName","decimalLatitude","decimalLongitude"}
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}

def download():
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 frog-cue-decoupling-structural-audit/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def local(term):
    return term.rsplit("/",1)[-1].rsplit("#",1)[-1] if term else ""

def dec(v,default):
    if v is None: return default
    return bytes(v,"utf-8").decode("unicode_escape")

def core_rows(zf,meta):
    core=meta.find("dwc:core",NS)
    files=core.find("dwc:files",NS)
    loc=files.find("dwc:location",NS)
    fn=loc.text.strip()
    delim=dec(core.attrib.get("fieldsTerminatedBy"),"\t")
    quote=dec(core.attrib.get("fieldsEnclosedBy"),'"')
    ignore=int(core.attrib.get("ignoreHeaderLines","0"))
    enc=core.attrib.get("encoding","UTF-8").replace("-","")
    idel=core.find("dwc:id",NS)
    ididx=int(idel.attrib["index"]) if idel is not None else None
    fields={local(f.attrib.get("term","")):int(f.attrib["index"]) for f in core.findall("dwc:field",NS)}
    reader=csv.reader(io.StringIO(zf.read(fn).decode(enc,errors="strict")),delimiter=delim,quotechar=quote or '"')
    for _ in range(ignore): next(reader,None)
    for row in reader:
        yield row,fields,ididx

def get(row,fields,name):
    i=fields.get(name)
    return row[i].strip() if i is not None and i<len(row) else ""

def parse_date(s):
    if not s: return None
    for candidate in (s[:10],s):
        try: return date.fromisoformat(candidate)
        except Exception: pass
    return None

def project_year(d):
    # project-year ending 9 Nov of label year
    return d.year+1 if (d.month,d.day)>=(11,10) else d.year

def cell025(lat,lon):
    return (math.floor(lat*4)/4.0,math.floor(lon*4)/4.0)

def main():
    data=download()
    sha=hashlib.sha256(data).hexdigest()
    zf=zipfile.ZipFile(io.BytesIO(data))
    meta=ET.fromstring(zf.read("meta.xml"))
    core=meta.find("dwc:core",NS)
    schema=sorted(local(f.attrib.get("term","")) for f in core.findall("dwc:field",NS))
    missing=sorted(EXPECTED_FIELDS-set(schema))
    if missing: raise SystemExit(f"missing required fields: {missing}")

    n=0
    dates=[]
    species=Counter()
    species_py=defaultdict(Counter)
    species_cells=defaultdict(set)
    event_species=defaultdict(set)
    uncertainty=Counter()
    generalization=Counter()

    for row,fields,ididx in core_rows(zf,meta):
        n+=1
        sp=get(row,fields,"scientificName")
        rawd=get(row,fields,"eventDate")
        d=parse_date(rawd)
        eid=get(row,fields,"eventID")
        if sp: species[sp]+=1
        if d:
            dates.append(d)
            py=project_year(d)
            if sp: species_py[sp][py]+=1
        if eid and sp: event_species[eid].add(sp)
        try:
            lat=float(get(row,fields,"decimalLatitude"))
            lon=float(get(row,fields,"decimalLongitude"))
            if sp and math.isfinite(lat) and math.isfinite(lon):
                species_cells[sp].add(cell025(lat,lon))
        except Exception:
            pass
        u=get(row,fields,"coordinateUncertaintyInMeters")
        if u: uncertainty[u]+=1
        g=get(row,fields,"dataGeneralizations")
        if g: generalization[g]+=1

    ref={2018,2019,2020}
    conf={2021,2022,2023,2024}
    eligible=[]
    for sp,total in species.items():
        py=species_py[sp]
        ge50=sum(py[y]>=50 for y in py)
        has_ref=sum(py[y] for y in ref)>0
        has_conf=sum(py[y] for y in conf)>0
        cells=len(species_cells[sp])
        if total>=1000 and ge50>=6 and cells>=20 and has_ref and has_conf:
            eligible.append({
                "scientificName":sp,
                "records":total,
                "project_years_ge50":ge50,
                "quarter_degree_cells":cells,
                "reference_records":sum(py[y] for y in ref),
                "confirmatory_records":sum(py[y] for y in conf)
            })

    multi_events=sum(len(v)>1 for v in event_species.values())
    result={
        "audit":"frogid_public_archive_structural_v0_1",
        "source_url":URL,
        "archive_sha256":sha,
        "archive_bytes":len(data),
        "schema_fields":schema,
        "row_count":n,
        "date_min":min(dates).isoformat() if dates else None,
        "date_max":max(dates).isoformat() if dates else None,
        "distinct_species":len(species),
        "distinct_event_ids":len(event_species),
        "events_with_multiple_species":multi_events,
        "eligible_species_count":len(eligible),
        "eligible_species":sorted(eligible,key=lambda x:x["scientificName"]),
        "top_species_structural_counts":[
            {"scientificName":sp,"records":cnt,"quarter_degree_cells":len(species_cells[sp])}
            for sp,cnt in species.most_common(20)
        ],
        "coordinate_uncertainty_nonempty_rows":sum(uncertainty.values()),
        "data_generalizations_nonempty_rows":sum(generalization.values()),
        "release_gate":{
            "row_count_ge_1m":n>=1000000,
            "species_ge_200":len(species)>=200,
            "date_starts_by_2017_11_15":bool(dates and min(dates)<=date(2017,11,15)),
            "date_reaches_2024_11_01":bool(dates and max(dates)>=date(2024,11,1)),
            "pass":(
                n>=1000000 and len(species)>=200
                and bool(dates and min(dates)<=date(2017,11,15))
                and bool(dates and max(dates)>=date(2024,11,1))
                and len(eligible)>=20
            )
        },
        "within_year_phenology_opened":False,
        "climate_values_opened":False,
        "cue_conflict_effect_opened":False
    }
    Path("frogid_structural_audit_v0_1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
