#!/usr/bin/env python3
"""Outcome-blind structural audit of the USGS NAAMP ScienceBase release.

The audit inventories files, table schemas, candidate event/species/weather fields,
and standardized event counts. It does not estimate or print weather-effect directions.
"""
from __future__ import annotations

import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import Counter, defaultdict
from pathlib import Path

ITEM_ID="583dc314e4b0d1899f9dea8d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
YEAR_MIN=2001
YEAR_MAX=2015

SPECIES_PAT=re.compile(r"(species|taxon|scientific|common.?name)",re.I)
EVENT_PAT=re.compile(r"(survey|event|visit|route|stop|station|sample|site)",re.I)
DATE_PAT=re.compile(r"(date|year|month|period|round)",re.I)
WEATHER_PAT=re.compile(r"(temp|temperature|rain|precip|weather|wind|sky|cloud|humidity)",re.I)
CALL_PAT=re.compile(r"(call|calling|index|detect|heard|presence)",re.I)
NUMERIC_EFFECT_PAT=re.compile(r"(estimate|coef|beta|odds|probab|fit|resid)",re.I)

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-chorus-synchrony-structural-audit/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-chorus-synchrony-structural-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")

def read_tables(name,data):
    low=name.lower()
    if low.endswith(".zip"):
        out=[]
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for member in z.namelist():
                if member.lower().endswith((".csv",".tsv",".txt")):
                    out.extend(read_tables(member,z.read(member)))
        return out
    if not low.endswith((".csv",".tsv",".txt")):
        return []
    text=data.decode("utf-8-sig",errors="replace")
    sample=text[:20000]
    try:
        dialect=csv.Sniffer().sniff(sample,delimiters=",\t;|")
    except Exception:
        dialect=csv.excel_tab if "\t" in sample else csv.excel
    reader=csv.DictReader(io.StringIO(text),dialect=dialect)
    return [(name,reader.fieldnames or [],list(reader))]

def parse_year(value):
    s=str(value or "")
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",s)
    return int(m.group(1)) if m else None

def first_nonempty(row,cols):
    for c in cols:
        v=(row.get(c) or "").strip()
        if v:
            return v
    return ""

def main():
    item=get_json(ITEM_URL)
    files=item.get("files") or []
    inventory=[]
    tables=[]
    for f in files:
        name=f.get("name") or ""
        url=file_url(f)
        rec={
            "name":name,
            "size":f.get("size"),
            "contentType":f.get("contentType"),
            "has_download_uri":bool(url),
        }
        if url and name.lower().endswith((".zip",".csv",".tsv",".txt")):
            data=get_bytes(url)
            rec["sha256"]=hashlib.sha256(data).hexdigest()
            rec["downloaded_bytes"]=len(data)
            tables.extend(read_tables(name,data))
        inventory.append(rec)

    receipts=[]
    candidate_event_counts=[]
    candidate_multispecies_counts=[]
    possible_state_values=set()

    for name,headers,rows in tables:
        species_cols=[h for h in headers if SPECIES_PAT.search(h or "") and not NUMERIC_EFFECT_PAT.search(h or "")]
        event_cols=[h for h in headers if EVENT_PAT.search(h or "") and not SPECIES_PAT.search(h or "")]
        date_cols=[h for h in headers if DATE_PAT.search(h or "")]
        weather_cols=[h for h in headers if WEATHER_PAT.search(h or "")]
        call_cols=[h for h in headers if CALL_PAT.search(h or "") and not NUMERIC_EFFECT_PAT.search(h or "")]

        # Heuristic event key candidates are structural only.
        route_cols=[h for h in headers if re.search(r"route",h or "",re.I)]
        stop_cols=[h for h in headers if re.search(r"stop|station",h or "",re.I)]
        survey_cols=[h for h in headers if re.search(r"survey|visit|event|sample",h or "",re.I)]
        state_cols=[h for h in headers if re.search(r"state|province|region",h or "",re.I)]

        event_species=defaultdict(set)
        standardized_rows=0
        for i,row in enumerate(rows):
            year=None
            for c in date_cols:
                y=parse_year(row.get(c))
                if y is not None:
                    year=y
                    break
            if year is None or not (YEAR_MIN<=year<=YEAR_MAX):
                continue
            standardized_rows+=1
            species=first_nonempty(row,species_cols)
            route=first_nonempty(row,route_cols)
            stop=first_nonempty(row,stop_cols)
            survey=first_nonempty(row,survey_cols)
            # Use row date string as part of structural event identity if present.
            date_token=first_nonempty(row,date_cols)
            if route and stop and date_token:
                key=(route,stop,date_token,survey)
            elif stop and date_token:
                key=(stop,date_token,survey)
            elif survey:
                key=(survey,)
            else:
                key=None
            if key and species:
                event_species[key].add(species)
            for c in state_cols:
                v=(row.get(c) or "").strip()
                if v:
                    possible_state_values.add(v)

        events=len(event_species)
        multi=sum(len(s)>=2 for s in event_species.values())
        if events:
            candidate_event_counts.append(events)
            candidate_multispecies_counts.append(multi)

        receipts.append({
            "name":name,
            "row_count":len(rows),
            "headers":headers,
            "species_candidate_columns":species_cols,
            "event_candidate_columns":event_cols,
            "date_candidate_columns":date_cols,
            "weather_candidate_columns":weather_cols,
            "call_candidate_columns":call_cols,
            "route_candidate_columns":route_cols,
            "stop_candidate_columns":stop_cols,
            "survey_candidate_columns":survey_cols,
            "standardized_2001_2015_rows":standardized_rows,
            "candidate_event_count":events,
            "candidate_multispecies_event_count":multi,
        })

    max_events=max(candidate_event_counts or [0])
    max_multi=max(candidate_multispecies_counts or [0])
    has_species=any(r["species_candidate_columns"] for r in receipts)
    has_event=any(r["candidate_event_count"]>0 for r in receipts)
    has_weather=any(r["weather_candidate_columns"] for r in receipts)

    result={
        "audit":"naamp_chorus_synchrony_structural_v0_1",
        "sciencebase_item_id":ITEM_ID,
        "title":item.get("title"),
        "file_inventory":inventory,
        "table_receipts":receipts,
        "max_candidate_standardized_event_count":max_events,
        "max_candidate_multispecies_event_count":max_multi,
        "distinct_state_region_labels_seen":len(possible_state_values),
        "structural_gate_pass":(
            max_events>=10000
            and max_multi>=3000
            and len(possible_state_values)>=10
            and has_species
            and has_event
            and has_weather
        ),
        "weather_effect_direction_opened":False,
        "species_pair_effect_opened":False,
        "network_effect_opened":False,
    }
    Path("frog_naamp_chorus_synchrony_structural_v0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
