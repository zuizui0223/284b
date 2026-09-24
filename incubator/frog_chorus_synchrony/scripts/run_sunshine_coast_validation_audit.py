#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import Counter, defaultdict
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr24697.zip"

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frog-chorus-synchrony-validation-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def parse_archive(data):
    z=zipfile.ZipFile(io.BytesIO(data))
    tables=[]
    for n in z.namelist():
        if not n.lower().endswith((".csv",".txt",".tsv")):
            continue
        text=z.read(n).decode("utf-8-sig",errors="replace")
        sample=text[:20000]
        try:
            dialect=csv.Sniffer().sniff(sample,delimiters=",\t;|")
        except Exception:
            dialect=csv.excel_tab if "\t" in sample else csv.excel
        reader=csv.DictReader(io.StringIO(text),dialect=dialect)
        tables.append((n,reader.fieldnames or [],list(reader)))
    return z.namelist(),tables

def year_of(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def is_call_label(x):
    s=str(x or "").strip().lower()
    if not s: return False
    return any(k in s for k in ("heard","hearing","call","calling","audio","acoustic"))

def main():
    data=fetch()
    names,tables=parse_archive(data)
    chosen=None
    for name,headers,rows in tables:
        h=set(headers)
        score=sum(k in h for k in ["eventID","parentEventID","scientificName","eventDate"])
        if chosen is None or score>chosen[0]:
            chosen=(score,name,headers,rows)
    if not chosen or chosen[0]<3:
        raise SystemExit("no suitable occurrence/event table found")

    _,name,headers,rows=chosen
    parent_events=set(); quadrat_events=set(); years=set()
    species_by_quadrat=defaultdict(set)
    call_label_counts=Counter()
    parent_by_event={}
    coords_total=0; coords_valid=0

    for r in rows:
        event=(r.get("eventID") or "").strip()
        parent=(r.get("parentEventID") or "").strip()
        sp=(r.get("scientificName") or "").strip()
        status=(r.get("occurrenceStatus") or "").strip().lower()
        yr=year_of(r.get("eventDate"))
        if yr: years.add(yr)
        if event: quadrat_events.add(event)
        if parent: parent_events.add(parent)
        if event and parent: parent_by_event[event]=parent

        if event:
            coords_total+=1
            try:
                la=float((r.get("decimalLatitude") or "").strip())
                lo=float((r.get("decimalLongitude") or "").strip())
                if -90<=la<=90 and -180<=lo<=180:
                    coords_valid+=1
            except Exception:
                pass

        labels=[
            (r.get("occurrenceRemarks") or "").strip(),
            (r.get("behavior") or "").strip(),
            (r.get("samplingProtocol") or "").strip(),
        ]
        for v in labels:
            if v: call_label_counts[v]+=1

        if status in {"absent","absence"}:
            continue
        if event and sp and any(is_call_label(v) for v in labels):
            species_by_quadrat[event].add(sp)

    multi={e:s for e,s in species_by_quadrat.items() if len(s)>=2}
    parents_with_multi={parent_by_event[e] for e in multi if e in parent_by_event}
    coord_fraction=coords_valid/coords_total if coords_total else 0

    result={
      "audit":"sunshine_coast_chorus_validation_structural_v0_1",
      "source_url":URL,
      "source_sha256":hashlib.sha256(data).hexdigest(),
      "archive_files":names,
      "selected_table":name,
      "selected_headers":headers,
      "parent_surveys":len(parent_events),
      "quadrat_events":len(quadrat_events),
      "years":sorted(years),
      "n_years":len(years),
      "marginal_call_evidence_labels":dict(sorted(call_label_counts.items())),
      "quadrat_events_with_positive_call_evidence":len(species_by_quadrat),
      "multispecies_call_quadrats":len(multi),
      "parent_surveys_with_multispecies_call_quadrat":len(parents_with_multi),
      "coordinate_coverage_fraction":coord_fraction,
      "structural_gate_pass":(
        len(parent_events)>=50 and len(quadrat_events)>=300 and len(multi)>=30
        and len(years)>=3 and coord_fraction>=0.90
      ),
      "rainfall_values_read":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_sunshine_coast_validation_structural_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
