#!/usr/bin/env python3
"""Outcome-blind FrogID verbatim-field recovery audit.

Uses exact eventID only. It asks whether eventTime and stateProvince omitted from the
DwC core are retained in verbatim_occurrence.txt. No rainfall or synchrony association
is opened.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr14760.zip"
EXPECTED_SHA="e0f87176607db7a065016f9b2b3ec85e81145907c4238633b48a31af92c8afe2"

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frogid-verbatim-field-recovery/0.2.1"})
    with urllib.request.urlopen(req,timeout=240) as r:
        return r.read()

def clean(row,key):
    return (row.get(key) or "").strip()

def main():
    data=fetch()
    sha=hashlib.sha256(data).hexdigest()
    if sha!=EXPECTED_SHA:
        raise SystemExit(f"source hash drift {sha}")
    z=zipfile.ZipFile(io.BytesIO(data))
    if "verbatim_occurrence.txt" not in z.namelist():
        raise SystemExit("verbatim_occurrence.txt absent")

    raw=z.open("verbatim_occurrence.txt")
    text=io.TextIOWrapper(raw,encoding="utf-8-sig",errors="replace",newline="")
    reader=csv.DictReader(text,delimiter="\t")
    headers=reader.fieldnames or []

    wanted=["eventID","eventTime","stateProvince","eventDate","decimalLatitude","decimalLongitude","recordedBy"]
    present=[x for x in wanted if x in headers]

    # Per-event exact-value sets for structural fields only.
    values={field:defaultdict(set) for field in wanted if field!="eventID" and field in headers}
    event_ids=set()
    row_count=0

    for row in reader:
        row_count+=1
        eid=clean(row,"eventID")
        if not eid:
            continue
        event_ids.add(eid)
        for field,mapping in values.items():
            v=clean(row,field)
            if v:
                mapping[eid].add(v)

    def coverage(field):
        m=values.get(field,{})
        n=sum(bool(v) for v in m.values())
        return n/len(event_ids) if event_ids else 0.0

    def consistent(field):
        m=values.get(field,{})
        n=sum(len(v)==1 for v in m.values() if v)
        return n/len(event_ids) if event_ids else 0.0

    states=set()
    for vals in values.get("stateProvince",{}).values():
        states.update(vals)

    result={
      "audit":"frogid_verbatim_field_recovery_v0_2_1",
      "source_sha256":sha,
      "verbatim_headers":headers,
      "requested_fields_present":present,
      "verbatim_rows":row_count,
      "verbatim_eventIDs":len(event_ids),
      "eventTime_coverage_fraction":coverage("eventTime"),
      "eventTime_consistency_fraction_all_events":consistent("eventTime"),
      "stateProvince_coverage_fraction":coverage("stateProvince"),
      "distinct_stateProvince_values":len(states),
      "stateProvince_values":sorted(states),
      "eventDate_coverage_fraction":coverage("eventDate"),
      "eventDate_consistency_fraction_all_events":consistent("eventDate"),
      "coordinate_pair_coverage_fraction":min(coverage("decimalLatitude"),coverage("decimalLongitude")),
      "recordedBy_coverage_fraction":coverage("recordedBy"),
      "recovery_gate_pass":(
        coverage("eventTime")>=0.90
        and len(states)>=5
      ),
      "rainfall_values_read":False,
      "synchrony_response_stratified_by_recovered_fields":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_frogid_verbatim_field_recovery_v0_2_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
