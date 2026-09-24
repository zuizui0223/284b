#!/usr/bin/env python3
"""Outcome-blind semantic audit for NAAMP TempScale and RunNumber.

Reads publisher metadata and marginal category counts only. Does not join these
categories to chorus synchrony or compute weather effects.
"""
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ITEM_ID="583dc314e4b0d1899f9dea8d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
RUNS_SHA="ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730"
STOPS_SHA="28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f"
XML_SHA="a713631a7d55392b23d876fad7488ccfcb6a570a37b8d1af131a359a1ebf39e8"
YEAR_MIN,YEAR_MAX=2001,2015

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-semantic-audit/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-semantic-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f): return f.get("downloadUri") or f.get("url") or f.get("uri")
def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            return file_url(f)
    raise RuntimeError(name)

def parse_year(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def norm(x): return " ".join((x or "").split())

def attrs(xml):
    root=ET.fromstring(xml)
    wanted={"TempScale","AirTemp","RunNumber","RouteType","SurveyDate"}
    out={}
    for attr in root.findall(".//attr"):
        label=norm(attr.findtext("attrlabl"))
        if label not in wanted: continue
        enums={}
        for edom in attr.findall(".//edom"):
            k=norm(edom.findtext("edomv")); v=norm(edom.findtext("edomvd"))
            if k: enums[k]=v
        ranges=[]
        for rdom in attr.findall(".//rdom"):
            ranges.append({
                "min":norm(rdom.findtext("rdommin")),
                "max":norm(rdom.findtext("rdommax")),
                "unit":norm(rdom.findtext("attrunit")),
            })
        out[label]={"definition":norm(attr.findtext("attrdef")),"enumerated":enums,"ranges":ranges}
    return out

def main():
    item=get_json(ITEM_URL)
    rb=get_bytes(find_file(item,"Runs.csv"))
    sb=get_bytes(find_file(item,"Stops.csv"))
    xb=get_bytes(find_file(item,"NAAMP_Eastern_and_Central_United_States_1994_2015.xml"))
    assert hashlib.sha256(rb).hexdigest()==RUNS_SHA
    assert hashlib.sha256(sb).hexdigest()==STOPS_SHA
    assert hashlib.sha256(xb).hexdigest()==XML_SHA

    runs=list(csv.DictReader(io.StringIO(rb.decode("utf-8-sig"))))
    stops=list(csv.DictReader(io.StringIO(sb.decode("utf-8-sig"))))
    eligible={}
    temp_scale=Counter(); run_number=Counter(); route_type=Counter()
    for r in runs:
        y=parse_year(r.get("SurveyYear")) or parse_year(r.get("SurveyDate"))
        if y is None or not YEAR_MIN<=y<=YEAR_MAX: continue
        if (r.get("UnifiedProtocol") or "").strip()!="1": continue
        rid=(r.get("RunID") or "").strip()
        if not rid: continue
        eligible[rid]=r
        temp_scale[(r.get("TempScale") or "").strip()]+=1
        run_number[(r.get("RunNumber") or "").strip()]+=1
        route_type[(r.get("RouteType") or "").strip()]+=1

    airtemp_parse=Counter()
    for s in stops:
        rid=(s.get("RunID") or "").strip()
        if rid not in eligible: continue
        if (s.get("SkippedStop") or "").strip()!="0": continue
        raw=(s.get("AirTemp") or "").strip()
        if not raw:
            airtemp_parse["missing"]+=1; continue
        try:
            float(raw); airtemp_parse["numeric"]+=1
        except Exception:
            airtemp_parse["nonnumeric"]+=1

    result={
      "audit":"naamp_temperature_run_semantics_v0_1",
      "metadata":attrs(xb),
      "eligible_runs":len(eligible),
      "temp_scale_marginal_counts":dict(sorted(temp_scale.items())),
      "run_number_marginal_counts":dict(sorted(run_number.items())),
      "route_type_marginal_counts":dict(sorted(route_type.items())),
      "sampled_stop_airtemp_parseability":dict(sorted(airtemp_parse.items())),
      "synchrony_values_read":False,
      "temperature_synchrony_association_opened":False,
      "rain_shoulder_interaction_opened":False,
    }
    Path("frog_naamp_temperature_run_semantics_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
