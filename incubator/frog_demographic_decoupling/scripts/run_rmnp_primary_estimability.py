#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request
from collections import defaultdict
from pathlib import Path

ITEM_ID="657ca143d34e23d35331ce9d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
CSV_NAME="ROMO_data_release.csv"
CSV_SHA="aa42c97dcc506b96f832c2ea4180f057527b1efeec302586d06801751c1cda3a"
EFFORT={"0-25":0.125,"26-50":0.38,"51-75":0.63,"76-99":0.875,"100":1.0}
DEPTH={"< or = 1":0,">1 - <2":1,">2":2}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-estimability/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-estimability/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f): return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            u=file_url(f)
            if not u: raise RuntimeError("no download uri")
            return u
    raise RuntimeError("missing file")

def year_from_string(s):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(s or ""))
    return int(m.group(1)) if m else None

def tokens(raw):
    return set(p.strip() for p in str(raw or "").split(",") if p.strip())

def main():
    item=get_json(ITEM_URL)
    data=get_bytes(find_file(item,CSV_NAME))
    if hashlib.sha256(data).hexdigest()!=CSV_SHA:
        raise SystemExit("CSV hash drift")
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig",errors="strict")))
    groups=defaultdict(list)
    for row in reader:
        y=year_from_string(row.get("date"))
        site=(row.get("site_name") or "").strip()
        if site and y and 2003<=y<=2022:
            groups[(site,y)].append(row)

    eligible=[]
    for (site,year),rows in groups.items():
        valid=[r for r in rows if (r.get("psma") or "").strip() in {"0","1"}]
        dates={str(r.get("date") or "").strip() for r in valid if str(r.get("date") or "").strip()}
        if len(dates)<2:
            continue
        if not any((r.get("psma") or "").strip()=="1" for r in valid):
            continue
        eff=[EFFORT[(r.get("perc_surveyed") or "").strip()] for r in rows if (r.get("perc_surveyed") or "").strip() in EFFORT]
        if not eff:
            continue
        adult=any("A" in tokens(r.get("psma_stage")) for r in rows)
        repro=any(tokens(r.get("psma_stage")) & {"E","L"} for r in rows)
        fish_vals={(r.get("fish") or "").strip() for r in rows if (r.get("fish") or "").strip() in {"Y","N"}}
        fish=1 if "Y" in fish_vals else (0 if "N" in fish_vals else None)
        depth_vals=[DEPTH[(r.get("max_depth") or "").strip()] for r in rows if (r.get("max_depth") or "").strip() in DEPTH]
        depth=max(depth_vals) if depth_vals else None
        eligible.append({
            "site":site,"year":year,"adult":adult,"repro":repro,"fish":fish,
            "depth":depth,"max_effort":max(eff),"n_visits":len(dates)
        })

    known_fish=[x for x in eligible if x["fish"] is not None]
    complete=[x for x in known_fish if x["depth"] is not None]
    out={
        "audit":"rmnp_primary_estimability_v0_1",
        "eligible_site_years":len(eligible),
        "adult_positive_site_years":sum(x["adult"] for x in eligible),
        "reproductive_positive_site_years":sum(x["repro"] for x in eligible),
        "fish_known_site_years":len(known_fish),
        "fish_present_site_years":sum(x["fish"]==1 for x in known_fish),
        "fish_not_observed_site_years":sum(x["fish"]==0 for x in known_fish),
        "depth_known_site_years":sum(x["depth"] is not None for x in eligible),
        "complete_primary_model_site_years":len(complete),
        "effort_known_by_definition":len(eligible),
        "primary_gate_pass":(
            len(eligible)>=100
            and sum(x["fish"]==1 for x in known_fish)>=20
            and sum(x["fish"]==0 for x in known_fish)>=20
            and sum(x["repro"] for x in eligible)>=20
        ),
        "primary_complete_case_gate_pass":(
            len(complete)>=100
            and sum(x["fish"]==1 for x in complete)>=20
            and sum(x["fish"]==0 for x in complete)>=20
            and sum(x["repro"] for x in complete)>=20
        ),
        "effect_directions_opened":False,
        "adult_reproductive_association_opened":False
    }
    Path("frog_rmnp_primary_estimability_v0_1.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
