#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import Counter, defaultdict
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr24697.zip"
EXPECTED_SHA="ef55f7fc903583ade788d2ed0c32668bc6a9a48fca8706c07a706e365fa6d97b"
CALL_CODES={"HEA","SHD"}

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frog-sunshine-verbatim-call-v0.1.3"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def table(z,name):
    txt=z.read(name).decode("utf-8-sig",errors="replace")
    rd=csv.DictReader(io.StringIO(txt),delimiter="\t")
    return rd.fieldnames or [],list(rd)

def val(r,k):
    return (r.get(k) or "").strip()

def year_of(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def main():
    data=fetch()
    sha=hashlib.sha256(data).hexdigest()
    if sha!=EXPECTED_SHA: raise SystemExit(f"source hash drift {sha}")
    z=zipfile.ZipFile(io.BytesIO(data))
    eh,events=table(z,"event.txt")
    vh,verb=table(z,"verbatim_occurrence.txt")

    parent_by_event={}
    date_by_event={}
    coords_by_event={}
    children_by_parent=defaultdict(set)
    for r in events:
        eid=val(r,"eventID")
        if not eid: continue
        p=val(r,"parentEventID")
        parent_by_event[eid]=p
        date_by_event[eid]=val(r,"eventDate")
        if p: children_by_parent[p].add(eid)
        try:
            lat=float(val(r,"decimalLatitude")); lon=float(val(r,"decimalLongitude"))
            if -90<=lat<=90 and -180<=lon<=180:
                coords_by_event[eid]=(lat,lon)
        except Exception:
            pass

    locations_by_event=defaultdict(set)
    calling_species=defaultdict(set)
    remarks=Counter()
    for r in verb:
        eid=val(r,"eventID")
        sp=val(r,"scientificName")
        loc=val(r,"locationID")
        code=val(r,"occurrenceRemarks").upper()
        if loc and eid: locations_by_event[eid].add(loc)
        if code: remarks[code]+=1
        if eid and sp and code in CALL_CODES:
            calling_species[eid].add(sp)

    event_site={}
    ambiguous_event_sites=0
    for eid,locs in locations_by_event.items():
        if len(locs)==1:
            event_site[eid]=next(iter(locs))
        elif len(locs)>1:
            ambiguous_event_sites+=1

    coords_by_site=defaultdict(set)
    for eid,site in event_site.items():
        if eid in coords_by_event:
            coords_by_site[site].add(coords_by_event[eid])
    site_registry={site:next(iter(cs)) for site,cs in coords_by_site.items() if len(cs)==1}
    ambiguous_site_geometry={site:len(cs) for site,cs in coords_by_site.items() if len(cs)>1}

    parent_site={}
    parent_geom={}
    parent_date={}
    for p,children in children_by_parent.items():
        sites={event_site[e] for e in children if e in event_site}
        if len(sites)==1:
            s=next(iter(sites)); parent_site[p]=s
            if s in site_registry: parent_geom[p]=site_registry[s]
        dates={date_by_event[e] for e in children if date_by_event.get(e)}
        if len(dates)==1: parent_date[p]=next(iter(dates))

    multi_events={e for e,s in calling_species.items() if len(s)>=2}
    parent_multi=Counter()
    for e in multi_events:
        p=parent_by_event.get(e,"")
        if p: parent_multi[p]+=1

    years={y for d in parent_date.values() if (y:=year_of(d)) is not None}
    nparent=len(children_by_parent)
    ge8=sum(len(ch)>=8 for ch in children_by_parent.values())
    pmulti=sum(parent_multi.get(p,0)>=1 for p in children_by_parent)
    coverage=len(parent_geom)/nparent if nparent else 0
    qhist=Counter(len(ch) for ch in children_by_parent.values())
    mhist=Counter(parent_multi.get(p,0) for p in children_by_parent)

    result={
      "audit":"sunshine_verbatim_call_parent_registry_v0_1_3",
      "source_sha256":sha,
      "frozen_call_codes":{"HEA":"Heard","SHD":"Seen and Heard"},
      "marginal_occurrence_remark_counts":dict(sorted(remarks.items())),
      "events_with_unique_verbatim_locationID":len(event_site),
      "events_with_ambiguous_locationID":ambiguous_event_sites,
      "site_coordinate_registry_entries":len(site_registry),
      "site_coordinate_registry_ambiguous_sites":ambiguous_site_geometry,
      "quadrat_events":sum(len(v) for v in children_by_parent.values()),
      "quadrat_events_with_any_calling_species":len(calling_species),
      "multispecies_call_quadrats":len(multi_events),
      "parent_surveys":nparent,
      "parent_surveys_ge8_quadrats":ge8,
      "parent_surveys_with_any_multispecies_call_quadrat":pmulti,
      "parent_surveys_with_unique_siteID":len(parent_site),
      "parent_surveys_with_registry_coordinate":len(parent_geom),
      "parent_coordinate_coverage_fraction":coverage,
      "parent_surveys_with_exact_date":len(parent_date),
      "parent_quadrat_count_histogram":{str(k):v for k,v in sorted(qhist.items())},
      "parent_multispecies_quadrat_count_histogram":{str(k):v for k,v in sorted(mhist.items())},
      "years":sorted(years),
      "n_years":len(years),
      "structural_gate_pass":(
        nparent>=50 and ge8>=40 and len(multi_events)>=30 and pmulti>=20
        and len(years)>=3 and coverage>=0.90
      ),
      "rainfall_values_read":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_sunshine_verbatim_call_parent_registry_v0_1_3.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
