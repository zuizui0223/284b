#!/usr/bin/env python3
"""Outcome-blind NAAMP call-index and weather-coverage audit.

Reads publisher metadata, marginal CallingIndex categories, and missingness/identity
coverage. It never computes synchrony-weather associations.
"""
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

ITEM_ID="583dc314e4b0d1899f9dea8d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
PINS={
 "Runs.csv":"ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
 "Stops.csv":"28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
 "Counts.csv":"60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086",
 "Species.csv":"ac97118a3a1ccd72a94136009e9696173dabd29b042ac63e474a74c5a9fcd1cb",
}
XML_NAME="NAAMP_Eastern_and_Central_United_States_1994_2015.xml"
YEAR_MIN,YEAR_MAX=2001,2015

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-coverage-audit/0.2","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-coverage-audit/0.2"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f): return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            u=file_url(f)
            if not u: raise RuntimeError(f"{name}: missing download URI")
            return u
    raise RuntimeError(f"missing file {name}")

def parse_year(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def nonempty(x): return str(x or "").strip()!=""

def attr_metadata(xml_bytes):
    root=ET.fromstring(xml_bytes)
    wanted={"CallingIndex","AirTemp","DaysSinceRain","UnifiedProtocol","SkippedStop","State","RunID","StopNumber"}
    out={}
    for attr in root.findall(".//attr"):
        label=" ".join((attr.findtext("attrlabl") or "").split())
        if label not in wanted: continue
        enums={}
        for edom in attr.findall(".//edom"):
            code=" ".join((edom.findtext("edomv") or "").split())
            desc=" ".join((edom.findtext("edomvd") or "").split())
            if code: enums[code]=desc
        ranges=[]
        for rdom in attr.findall(".//rdom"):
            ranges.append({
              "min":" ".join((rdom.findtext("rdommin") or "").split()),
              "max":" ".join((rdom.findtext("rdommax") or "").split()),
              "unit":" ".join((rdom.findtext("attrunit") or "").split()),
            })
        out[label]={
          "definition":" ".join((attr.findtext("attrdef") or "").split()),
          "enumerated":enums,
          "ranges":ranges,
        }
    return out

def main():
    item=get_json(ITEM_URL)
    blobs={}
    for name in [*PINS,XML_NAME]:
        blobs[name]=get_bytes(find_file(item,name))
        if name in PINS and hashlib.sha256(blobs[name]).hexdigest()!=PINS[name]:
            raise SystemExit(f"hash drift {name}")

    meta=attr_metadata(blobs[XML_NAME])
    runs=list(csv.DictReader(io.StringIO(blobs["Runs.csv"].decode("utf-8-sig"))))
    stops=list(csv.DictReader(io.StringIO(blobs["Stops.csv"].decode("utf-8-sig"))))
    counts=list(csv.DictReader(io.StringIO(blobs["Counts.csv"].decode("utf-8-sig"))))

    eligible_runs={}
    state_labels=set()
    for r in runs:
        y=parse_year(r.get("SurveyYear")) or parse_year(r.get("SurveyDate"))
        unified=(r.get("UnifiedProtocol") or "").strip()
        if y is None or not (YEAR_MIN<=y<=YEAR_MAX):
            continue
        # Preserve all years in core epoch; report UnifiedProtocol categories separately.
        runid=(r.get("RunID") or "").strip()
        if not runid: continue
        eligible_runs[runid]=r
        st=(r.get("State") or "").strip()
        if st: state_labels.add(st)

    event_rows={}
    airtemp_nonempty=0
    skipped_labels=Counter()
    for s in stops:
        runid=(s.get("RunID") or "").strip()
        if runid not in eligible_runs: continue
        stop=(s.get("StopNumber") or "").strip()
        if not stop: continue
        key=(runid,stop)
        event_rows[key]=s
        if nonempty(s.get("AirTemp")): airtemp_nonempty+=1
        skipped_labels[(s.get("SkippedStop") or "").strip()]+=1

    daysrain_nonempty=sum(nonempty(r.get("DaysSinceRain")) for r in eligible_runs.values())
    unified_labels=Counter((r.get("UnifiedProtocol") or "").strip() for r in eligible_runs.values())

    calling_counts=Counter()
    species_per_event=defaultdict(set)
    records_per_event=Counter()
    for c in counts:
        runid=(c.get("RunID") or "").strip()
        stop=(c.get("StopNumber") or "").strip()
        key=(runid,stop)
        if key not in event_rows: continue
        idx=(c.get("CallingIndex") or "").strip()
        sp=(c.get("Species") or "").strip()
        if idx!="": calling_counts[idx]+=1
        records_per_event[key]+=1
        # Do not define positive until metadata semantics below; just retain marginal categories.
        if sp: species_per_event[key].add(sp)

    call_meta=meta.get("CallingIndex",{})
    positive_codes=[]
    for code,desc in (call_meta.get("enumerated") or {}).items():
        text=(code+" "+desc).lower()
        # Mechanical semantic rule frozen here: any documented code explicitly meaning
        # "not heard"/"no calling"/absence is nonpositive; other valid call-index levels are positive.
        if any(t in text for t in ("not heard","no calling","not calling","none heard","absent")):
            continue
        if code.strip()!="":
            positive_codes.append(code)

    positive_species_by_event=defaultdict(set)
    for c in counts:
        key=((c.get("RunID") or "").strip(),(c.get("StopNumber") or "").strip())
        if key not in event_rows: continue
        idx=(c.get("CallingIndex") or "").strip()
        sp=(c.get("Species") or "").strip()
        if idx in positive_codes and sp:
            positive_species_by_event[key].add(sp)

    rich_hist=Counter(len(v) for v in positive_species_by_event.values())
    # Events with no positive rows must remain represented as 0-richness if the stop itself is valid.
    all_event_richness=Counter()
    for key in event_rows:
        all_event_richness[len(positive_species_by_event.get(key,set()))]+=1

    n_events=len(event_rows)
    result={
      "audit":"naamp_callindex_weather_coverage_v0_2",
      "source_sha256":{k:hashlib.sha256(v).hexdigest() for k,v in blobs.items()},
      "metadata":meta,
      "eligible_runs_2001_2015":len(eligible_runs),
      "eligible_stop_events_2001_2015":n_events,
      "distinct_state_labels":len(state_labels),
      "unified_protocol_labels":dict(sorted(unified_labels.items())),
      "skipped_stop_labels":dict(sorted(skipped_labels.items())),
      "airtemp_nonempty_events":airtemp_nonempty,
      "airtemp_coverage_fraction":airtemp_nonempty/n_events if n_events else 0,
      "days_since_rain_nonempty_runs":daysrain_nonempty,
      "days_since_rain_coverage_fraction":daysrain_nonempty/len(eligible_runs) if eligible_runs else 0,
      "calling_index_marginal_counts":dict(sorted(calling_counts.items())),
      "publisher_defined_positive_call_codes":sorted(positive_codes),
      "event_positive_calling_species_richness_histogram":{str(k):v for k,v in sorted(all_event_richness.items())},
      "events_with_ge2_positive_calling_species":sum(v for k,v in all_event_richness.items() if k>=2),
      "primary_predictor_structurally_selected":(
          "DaysSinceRain" if (daysrain_nonempty/len(eligible_runs) if eligible_runs else 0)>=0.70
          else ("AirTemp" if (airtemp_nonempty/n_events if n_events else 0)>=0.80 else None)
      ),
      "weather_richness_association_opened":False,
      "species_pair_weather_effect_opened":False,
    }
    Path("frog_naamp_callindex_weather_coverage_v0_2.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
