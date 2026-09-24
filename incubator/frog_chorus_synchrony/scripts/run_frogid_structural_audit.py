#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, urllib.request, zipfile
from collections import Counter, defaultdict
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr14760.zip"

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frogid-synchrony-structural-audit/0.2"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def parse_best(z):
    candidates=[]
    for name in z.namelist():
        if not name.lower().endswith((".txt",".csv",".tsv")): continue
        text=z.read(name).decode("utf-8-sig",errors="replace")
        sample=text[:20000]
        try:
            dialect=csv.Sniffer().sniff(sample,delimiters=",\t;|")
        except Exception:
            dialect=csv.excel_tab if "\t" in sample else csv.excel
        reader=csv.DictReader(io.StringIO(text),dialect=dialect)
        headers=reader.fieldnames or []
        score=sum(k in headers for k in ["eventID","scientificName","eventDate","decimalLatitude","decimalLongitude"])
        candidates.append((score,name,headers,list(reader)))
    if not candidates: raise SystemExit("no tabular file")
    return max(candidates,key=lambda x:x[0])

def main():
    data=fetch()
    sha=hashlib.sha256(data).hexdigest()
    z=zipfile.ZipFile(io.BytesIO(data))
    score,name,headers,rows=parse_best(z)
    if score<4: raise SystemExit(f"no suitable occurrence table; best {name} score={score}")

    species_by_event=defaultdict(set)
    coords_by_event=defaultdict(set)
    dates_by_event=defaultdict(set)
    times_by_event=defaultdict(set)
    users_by_event=defaultdict(set)
    states=set()
    n_coord_rows=n_date_rows=n_time_rows=n_user_rows=0

    for r in rows:
        eid=(r.get("eventID") or "").strip()
        if not eid: continue
        sp=(r.get("scientificName") or "").strip()
        if sp: species_by_event[eid].add(sp)
        d=(r.get("eventDate") or "").strip()
        if d:
            dates_by_event[eid].add(d); n_date_rows+=1
        t=(r.get("eventTime") or "").strip()
        if t:
            times_by_event[eid].add(t); n_time_rows+=1
        u=(r.get("recordedBy") or "").strip()
        if u:
            users_by_event[eid].add(u); n_user_rows+=1
        st=(r.get("stateProvince") or "").strip()
        if st: states.add(st)
        try:
            lat=float((r.get("decimalLatitude") or "").strip())
            lon=float((r.get("decimalLongitude") or "").strip())
            if -90<=lat<=90 and -180<=lon<=180:
                coords_by_event[eid].add((lat,lon)); n_coord_rows+=1
        except Exception:
            pass

    events=set(species_by_event)|set(dates_by_event)|set(coords_by_event)
    n=len(events)
    multi=sum(len(species_by_event[e])>=2 for e in events)
    coord_events=sum(bool(coords_by_event[e]) for e in events)
    date_events=sum(bool(dates_by_event[e]) for e in events)
    time_events=sum(bool(times_by_event[e]) for e in events)
    user_events=sum(bool(users_by_event[e]) for e in events)
    coord_consistent=sum(len(coords_by_event[e])<=1 and bool(coords_by_event[e]) for e in events)
    date_consistent=sum(len(dates_by_event[e])<=1 and bool(dates_by_event[e]) for e in events)
    time_consistent=sum(len(times_by_event[e])<=1 and bool(times_by_event[e]) for e in events)

    richness=Counter(len(species_by_event[e]) for e in events)
    result={
      "audit":"frogid_v6_synchrony_structural_v0_2",
      "source_url":URL,
      "source_sha256":sha,
      "archive_files":z.namelist(),
      "selected_table":name,
      "selected_headers":headers,
      "occurrence_rows":len(rows),
      "events":n,
      "distinct_species":len({s for v in species_by_event.values() for s in v}),
      "distinct_states":len(states),
      "multispecies_events":multi,
      "event_species_richness_histogram":{str(k):v for k,v in sorted(richness.items())},
      "coordinate_event_coverage_fraction":coord_events/n if n else 0,
      "date_event_coverage_fraction":date_events/n if n else 0,
      "time_event_coverage_fraction":time_events/n if n else 0,
      "recordedBy_event_coverage_fraction":user_events/n if n else 0,
      "coordinate_consistency_fraction_all_events":coord_consistent/n if n else 0,
      "date_consistency_fraction_all_events":date_consistent/n if n else 0,
      "time_consistency_fraction_all_events":time_consistent/n if n else 0,
      "structural_gate_pass":(
        n>=100000 and multi>=10000 and len(states)>=5
        and (coord_events/n if n else 0)>=0.95
        and (date_events/n if n else 0)>=0.99
        and (time_events/n if n else 0)>=0.90
        and (coord_consistent/n if n else 0)>=0.99
      ),
      "rainfall_values_read":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_frogid_v6_synchrony_structural_v0_2.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
