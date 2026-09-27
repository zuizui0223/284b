#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import Counter, defaultdict
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr24697.zip"
EXPECTED_SHA="ef55f7fc903583ade788d2ed0c32668bc6a9a48fca8706c07a706e365fa6d97b"
CALL={"HEA","SHD"}

def fetch():
    q=urllib.request.Request(URL,headers={"User-Agent":"frog-sunshine-registry-subset/0.1.4"})
    with urllib.request.urlopen(q,timeout=120) as r:return r.read()
def table(z,n):
    rd=csv.DictReader(io.StringIO(z.read(n).decode("utf-8-sig",errors="replace")),delimiter="\t")
    return list(rd)
def v(r,k):return (r.get(k) or "").strip()
def year(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""));return int(m.group(1)) if m else None

def main():
    data=fetch()
    if hashlib.sha256(data).hexdigest()!=EXPECTED_SHA:raise SystemExit("source hash drift")
    z=zipfile.ZipFile(io.BytesIO(data))
    events=table(z,"event.txt");verb=table(z,"verbatim_occurrence.txt")

    parent_by_event={};date_by_event={};coord_by_event={};children=defaultdict(set)
    for r in events:
        eid=v(r,"eventID")
        if not eid:continue
        p=v(r,"parentEventID");parent_by_event[eid]=p;date_by_event[eid]=v(r,"eventDate")
        if p:children[p].add(eid)
        try:
            lat=float(v(r,"decimalLatitude"));lon=float(v(r,"decimalLongitude"))
            if -90<=lat<=90 and -180<=lon<=180:coord_by_event[eid]=(lat,lon)
        except:pass

    sites_by_event=defaultdict(set);calls=defaultdict(set)
    for r in verb:
        eid=v(r,"eventID");site=v(r,"locationID");sp=v(r,"scientificName");code=v(r,"occurrenceRemarks").upper()
        if eid and site:sites_by_event[eid].add(site)
        if eid and sp and code in CALL:calls[eid].add(sp)
    event_site={e:next(iter(s)) for e,s in sites_by_event.items() if len(s)==1}

    coords_by_site=defaultdict(set)
    for e,site in event_site.items():
        if e in coord_by_event:coords_by_site[site].add(coord_by_event[e])
    registry={site:next(iter(cs)) for site,cs in coords_by_site.items() if len(cs)==1}

    parent_info={}
    for p,ch in children.items():
        child_sites={event_site[e] for e in ch if e in event_site}
        dates={date_by_event[e] for e in ch if date_by_event.get(e)}
        if len(child_sites)!=1 or len(dates)!=1:continue
        site=next(iter(child_sites))
        if site not in registry:continue
        parent_info[p]={"site":site,"coord":registry[site],"date":next(iter(dates)),"children":set(ch)}

    multi={e for e,s in calls.items() if len(s)>=2}
    total_quads=sum(len(x["children"]) for x in parent_info.values())
    ge8=sum(len(x["children"])>=8 for x in parent_info.values())
    eligible_multi={e for p,x in parent_info.items() for e in x["children"] if e in multi}
    parents_multi=sum(any(e in multi for e in x["children"]) for x in parent_info.values())
    years={y for x in parent_info.values() if (y:=year(x["date"])) is not None}
    site_counts=Counter(x["site"] for x in parent_info.values())
    result={
      "audit":"sunshine_registry_complete_parent_subset_v0_1_4",
      "source_sha256":EXPECTED_SHA,
      "eligible_parent_surveys":len(parent_info),
      "eligible_parent_surveys_ge8_quadrats":ge8,
      "eligible_quadrat_events":total_quads,
      "eligible_multispecies_call_quadrats":len(eligible_multi),
      "eligible_parents_with_any_multispecies_call":parents_multi,
      "eligible_site_labels":dict(sorted(site_counts.items())),
      "n_years":len(years),"years":sorted(years),
      "coordinate_coverage_fraction":1.0 if parent_info else 0.0,
      "gate_pass":(
        len(parent_info)>=50 and ge8>=35 and total_quads>=300
        and len(eligible_multi)>=30 and parents_multi>=20 and len(years)>=3
      ),
      "rainfall_values_read":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_sunshine_registry_subset_v0_1_4.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
