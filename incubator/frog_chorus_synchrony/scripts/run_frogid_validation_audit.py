#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import Counter, defaultdict
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr14760.zip"

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frogid-chorus-synchrony-structural-audit/0.2"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def pick_occurrence(z):
    names=z.namelist()
    for preferred in ("occurrence.txt","occurrence.csv"):
        for n in names:
            if n.lower().endswith(preferred):
                return n
    candidates=[n for n in names if n.lower().endswith((".txt",".csv",".tsv")) and "occurrence" in n.lower()]
    if candidates: return candidates[0]
    raise RuntimeError("no occurrence table")

def dialect_for(text):
    sample=text[:20000]
    try: return csv.Sniffer().sniff(sample,delimiters=",\t;|")
    except Exception: return csv.excel_tab if "\t" in sample else csv.excel

def year_date(raw):
    s=str(raw or "").strip()
    m=re.search(r"(?<!\d)((?:19|20)\d{2})[-/]?(\d{2})?[-/]?(\d{2})?(?!\d)",s)
    if not m: return None
    y=int(m.group(1)); mo=int(m.group(2) or 1); d=int(m.group(3) or 1)
    return (y,mo,d)

def main():
    data=fetch()
    sha=hashlib.sha256(data).hexdigest()
    z=zipfile.ZipFile(io.BytesIO(data))
    table=pick_occurrence(z)
    text=z.read(table).decode("utf-8-sig",errors="replace")
    reader=csv.DictReader(io.StringIO(text),dialect=dialect_for(text))
    headers=reader.fieldnames or []
    required={"eventID","scientificName","eventDate"}
    missing=sorted(required-set(headers))
    if missing: raise SystemExit(f"missing required columns: {missing}")

    event_species=defaultdict(set)
    dates=[]
    state=Counter()
    behavior=Counter()
    protocol=Counter()
    n=0
    n_date=0
    n_coord=0
    n_time=0
    event_rows=Counter()
    coord_events=set()
    date_events=set()
    time_events=set()

    for row in reader:
        n+=1
        event=(row.get("eventID") or "").strip()
        sp=(row.get("scientificName") or "").strip()
        rawdate=(row.get("eventDate") or "").strip()
        if event:
            event_rows[event]+=1
            if sp: event_species[event].add(sp)
        dt=year_date(rawdate)
        if dt:
            n_date+=1; dates.append(dt)
            if event: date_events.add(event)
        if (row.get("eventTime") or "").strip():
            n_time+=1
            if event: time_events.add(event)
        lat=(row.get("decimalLatitude") or "").strip()
        lon=(row.get("decimalLongitude") or "").strip()
        try:
            la=float(lat); lo=float(lon)
            if -90<=la<=90 and -180<=lo<=180:
                n_coord+=1
                if event: coord_events.add(event)
        except Exception: pass
        st=(row.get("stateProvince") or "").strip()
        if st: state[st]+=1
        b=(row.get("behavior") or "").strip()
        if b: behavior[b]+=1
        p=(row.get("samplingProtocol") or "").strip()
        if p: protocol[p]+=1

    richness=Counter(len(s) for s in event_species.values())
    events=len(event_species)
    maxdate=max(dates) if dates else None
    mindate=min(dates) if dates else None
    v7=(n>=1000000 and maxdate is not None and maxdate>=(2024,11,1))
    result={
      "audit":"frogid_external_validation_structural_v0_2",
      "source_url":URL,
      "source_sha256":sha,
      "archive_files":z.namelist(),
      "occurrence_table":table,
      "headers":headers,
      "occurrence_rows":n,
      "distinct_eventIDs":events,
      "min_event_date":mindate,
      "max_event_date":maxdate,
      "v7_compatible_by_frozen_rule":v7,
      "event_date_coverage_fraction":len(date_events)/events if events else 0,
      "event_time_coverage_fraction":len(time_events)/events if events else 0,
      "coordinate_coverage_fraction":len(coord_events)/events if events else 0,
      "distinct_state_territory_labels":len(state),
      "state_territory_row_counts":dict(sorted(state.items())),
      "behavior_marginal_counts":dict(sorted(behavior.items())),
      "samplingProtocol_marginal_counts":dict(sorted(protocol.items())),
      "event_species_richness_histogram":{str(k):v for k,v in sorted(richness.items())},
      "multispecies_recordings_ge2":sum(v for k,v in richness.items() if k>=2),
      "multispecies_recordings_ge3":sum(v for k,v in richness.items() if k>=3),
      "max_species_per_recording":max(richness) if richness else 0,
      "structural_gate_pass":(
        events>=100000
        and sum(v for k,v in richness.items() if k>=2)>=30000
        and sum(v for k,v in richness.items() if k>=3)>=5000
        and len(state)>=6
        and (len(date_events)/events if events else 0)>=0.99
        and (len(coord_events)/events if events else 0)>=0.90
      ),
      "weather_values_read":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_frogid_validation_structural_v0_2.json").write_text(
      json.dumps(result,indent=2,sort_keys=True,default=list)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True,default=list))

if __name__=="__main__":
    main()
