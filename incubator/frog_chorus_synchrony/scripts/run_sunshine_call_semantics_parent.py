#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import Counter, defaultdict
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr24697.zip"
EXPECTED_SHA="ef55f7fc903583ade788d2ed0c32668bc6a9a48fca8706c07a706e365fa6d97b"
CALL_CODES={"HEA","SHD"}

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frog-sunshine-call-semantics-v0.1.2"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def parse_table(z,name):
    text=z.read(name).decode("utf-8-sig",errors="replace")
    reader=csv.DictReader(io.StringIO(text),delimiter="\t")
    return reader.fieldnames or [], list(reader)

def first(row,*names):
    for n in names:
        v=(row.get(n) or "").strip()
        if v: return v
    return ""

def year_of(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def main():
    data=fetch()
    sha=hashlib.sha256(data).hexdigest()
    if sha!=EXPECTED_SHA: raise SystemExit(f"source hash drift {sha}")
    z=zipfile.ZipFile(io.BytesIO(data))
    eh,events=parse_table(z,"event.txt")
    oh,occ=parse_table(z,"occurrence.txt")
    vh,verb=parse_table(z,"verbatim_occurrence.txt")

    species_by_oid={}
    event_by_oid={}
    status_by_oid={}
    for r in occ:
        oid=first(r,"occurrenceID","id")
        if not oid: continue
        species_by_oid[oid]=first(r,"scientificName","species","vernacularName")
        event_by_oid[oid]=first(r,"eventID")
        status_by_oid[oid]=first(r,"occurrenceStatus").upper()

    remark_by_oid={}
    remark_counts=Counter()
    for r in verb:
        oid=first(r,"occurrenceID","id")
        if not oid: continue
        code=first(r,"occurrenceRemarks").upper()
        if code:
            remark_by_oid[oid]=code
            remark_counts[code]+=1

    parent_by_event={}
    date_by_event={}
    location_by_event={}
    coords_by_event={}
    for r in events:
        eid=first(r,"eventID")
        if not eid: continue
        parent_by_event[eid]=first(r,"parentEventID")
        date_by_event[eid]=first(r,"eventDate")
        location_by_event[eid]=first(r,"locationID","locality")
        try:
            lat=float(first(r,"decimalLatitude"))
            lon=float(first(r,"decimalLongitude"))
            if -90<=lat<=90 and -180<=lon<=180:
                coords_by_event[eid]=(lat,lon)
        except Exception:
            pass

    calling_species=defaultdict(set)
    call_occurrences=0
    for oid,code in remark_by_oid.items():
        if code not in CALL_CODES: continue
        if status_by_oid.get(oid)=="ABSENT": continue
        eid=event_by_oid.get(oid,"")
        sp=species_by_oid.get(oid,"")
        if eid and sp:
            calling_species[eid].add(sp)
            call_occurrences+=1

    event_ids={e for e in event_by_oid.values() if e}
    multi_events={e for e,s in calling_species.items() if len(s)>=2}

    children_by_parent=defaultdict(set)
    for e in event_ids:
        p=parent_by_event.get(e,"")
        if p: children_by_parent[p].add(e)

    parent_multi=Counter()
    for e in multi_events:
        p=parent_by_event.get(e,"")
        if p: parent_multi[p]+=1

    parent_geometry={}
    for p,children in children_by_parent.items():
        coords={coords_by_event[e] for e in children if e in coords_by_event}
        if len(coords)==1:
            parent_geometry[p]=next(iter(coords))

    years=set()
    parent_dates={}
    parent_locations={}
    for p,children in children_by_parent.items():
        ds={date_by_event.get(e,"") for e in children if date_by_event.get(e,"")}
        locs={location_by_event.get(e,"") for e in children if location_by_event.get(e,"")}
        if len(ds)==1: parent_dates[p]=next(iter(ds))
        if len(locs)==1: parent_locations[p]=next(iter(locs))
        for d in ds:
            y=year_of(d)
            if y: years.add(y)

    n_parent=len(children_by_parent)
    ge8=sum(len(v)>=8 for v in children_by_parent.values())
    parents_multi=sum(v>=1 for v in parent_multi.values())
    geom_fraction=len(parent_geometry)/n_parent if n_parent else 0

    quadrat_hist=Counter(len(v) for v in children_by_parent.values())
    multi_hist=Counter(parent_multi.get(p,0) for p in children_by_parent)

    result={
      "audit":"sunshine_call_semantics_parent_geometry_v0_1_2",
      "source_sha256":sha,
      "frozen_call_codes":{"HEA":"Heard","SHD":"Seen and Heard"},
      "marginal_occurrence_remark_counts":dict(sorted(remark_counts.items())),
      "call_positive_occurrence_rows":call_occurrences,
      "quadrat_events":len(event_ids),
      "quadrat_events_with_any_calling_species":len(calling_species),
      "multispecies_call_quadrats":len(multi_events),
      "parent_surveys":n_parent,
      "parent_surveys_ge8_quadrats":ge8,
      "parent_surveys_with_any_multispecies_call_quadrat":parents_multi,
      "parent_quadrat_count_histogram":{str(k):v for k,v in sorted(quadrat_hist.items())},
      "parent_multispecies_quadrat_count_histogram":{str(k):v for k,v in sorted(multi_hist.items())},
      "parent_surveys_with_exact_consistent_child_coordinates":len(parent_geometry),
      "parent_coordinate_coverage_fraction":geom_fraction,
      "parent_surveys_with_single_exact_date":len(parent_dates),
      "parent_surveys_with_single_locationID":len(parent_locations),
      "years":sorted(years),
      "n_years":len(years),
      "structural_gate_pass":(
        n_parent>=50 and ge8>=40 and len(multi_events)>=30
        and parents_multi>=20 and len(years)>=3 and geom_fraction>=0.90
      ),
      "rainfall_values_read":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_sunshine_call_semantics_parent_geometry_v0_1_2.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
