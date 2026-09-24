#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import Counter, defaultdict
from pathlib import Path

URL="https://dwca-exports.ala.org.au/dr24697.zip"
EXPECTED_SHA="ef55f7fc903583ade788d2ed0c32668bc6a9a48fca8706c07a706e365fa6d97b"

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frog-sunshine-dwca-repair/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def parse_table(z,name):
    raw=z.read(name)
    text=raw.decode("utf-8-sig",errors="replace")
    sample=text[:20000]
    try:
        dialect=csv.Sniffer().sniff(sample,delimiters=",\t;|")
    except Exception:
        dialect=csv.excel_tab if "\t" in sample else csv.excel
    reader=csv.DictReader(io.StringIO(text),dialect=dialect)
    return reader.fieldnames or [], list(reader)

def first(row,names):
    for n in names:
        if n in row:
            v=(row.get(n) or "").strip()
            if v: return v
    return ""

def year_of(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def explicit_call(x):
    s=str(x or "").strip().lower()
    if not s: return False
    return any(k in s for k in ("heard","hearing","call","calling","audio","acoustic"))

def main():
    data=fetch()
    sha=hashlib.sha256(data).hexdigest()
    if sha!=EXPECTED_SHA:
        raise SystemExit(f"source hash drift: {sha}")
    z=zipfile.ZipFile(io.BytesIO(data))
    required=["event.txt","occurrence.txt","verbatim_occurrence.txt"]
    for n in required:
        if n not in z.namelist(): raise SystemExit(f"missing {n}")

    eh,events=parse_table(z,"event.txt")
    oh,occ=parse_table(z,"occurrence.txt")
    vh,verb=parse_table(z,"verbatim_occurrence.txt")

    species_by_occ={}
    event_by_occ={}
    status_by_occ={}
    for r in occ:
        oid=first(r,["occurrenceID","id"])
        if not oid: continue
        species_by_occ[oid]=first(r,["scientificName","species","vernacularName"])
        event_by_occ[oid]=first(r,["eventID"])
        status_by_occ[oid]=first(r,["occurrenceStatus"]).lower()

    call_by_occ={}
    raw_labels=Counter()
    relevant_fields=[h for h in vh if re.search(r"(remark|behav|protocol|method|evidence|record)",h or "",re.I)]
    for r in verb:
        oid=first(r,["occurrenceID","id"])
        if not oid: continue
        labels=[]
        for h in relevant_fields:
            v=(r.get(h) or "").strip()
            if v:
                raw_labels[f"{h}={v}"]+=1
                labels.append(v)
        call_by_occ[oid]=any(explicit_call(v) for v in labels)

    parent_by_event={}
    coords_by_event={}
    date_by_event={}
    event_location={}
    for r in events:
        eid=first(r,["eventID"])
        if not eid: continue
        parent_by_event[eid]=first(r,["parentEventID"])
        date_by_event[eid]=first(r,["eventDate"])
        event_location[eid]=first(r,["locationID","locality"])
        try:
            lat=float(first(r,["decimalLatitude"]))
            lon=float(first(r,["decimalLongitude"]))
            if -90<=lat<=90 and -180<=lon<=180:
                coords_by_event[eid]=(lat,lon)
        except Exception:
            pass

    calling_species_by_event=defaultdict(set)
    for oid,is_call in call_by_occ.items():
        if not is_call: continue
        if status_by_occ.get(oid) in {"absent","absence"}: continue
        sp=species_by_occ.get(oid,"")
        eid=event_by_occ.get(oid,"")
        if sp and eid:
            calling_species_by_event[eid].add(sp)

    event_ids=set(event_by_occ.values())-{""}
    parents={parent_by_event.get(e,"") for e in event_ids if parent_by_event.get(e,"")}
    years={y for e in event_ids if (y:=year_of(date_by_event.get(e))) is not None}
    multi={e:s for e,s in calling_species_by_event.items() if len(s)>=2}
    parents_with_multi={parent_by_event[e] for e in multi if parent_by_event.get(e)}
    coord_fraction=sum(e in coords_by_event for e in event_ids)/len(event_ids) if event_ids else 0

    result={
      "audit":"sunshine_coast_dwca_mapping_repair_v0_1_1",
      "source_sha256":sha,
      "headers":{"event":eh,"occurrence":oh,"verbatim_occurrence":vh},
      "verbatim_fields_scanned_for_call_semantics":relevant_fields,
      "marginal_raw_call_evidence_labels":dict(sorted(raw_labels.items())),
      "occurrence_ids_with_explicit_call_evidence":sum(call_by_occ.values()),
      "quadrat_events":len(event_ids),
      "parent_surveys":len(parents),
      "years":sorted(years),
      "n_years":len(years),
      "events_with_any_calling_species":len(calling_species_by_event),
      "multispecies_call_quadrats":len(multi),
      "parent_surveys_with_multispecies_call_quadrat":len(parents_with_multi),
      "coordinate_coverage_fraction":coord_fraction,
      "structural_gate_pass":(
         len(parents)>=50 and len(event_ids)>=300 and len(multi)>=30
         and len(years)>=3 and coord_fraction>=0.90
      ),
      "rainfall_values_read":False,
      "weather_synchrony_association_opened":False
    }
    Path("frog_sunshine_dwca_mapping_repair_v0_1_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
