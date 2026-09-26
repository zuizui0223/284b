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

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-woodfrog-estimability/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-woodfrog-estimability/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f): return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            u=file_url(f)
            if not u: raise RuntimeError("no download URI")
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
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig",errors="strict"))))
    groups=defaultdict(list)
    for row in rows:
        y=year_from_string(row.get("date"))
        site=(row.get("site_name") or "").strip()
        if site and y and 2003<=y<=2022:
            groups[(site,y)].append(row)

    eligible=[]
    for (site,year),rs in groups.items():
        valid=[r for r in rs if (r.get("lisy") or "").strip() in {"0","1"}]
        dates={str(r.get("date") or "").strip() for r in valid if str(r.get("date") or "").strip()}
        if len(dates)<2:
            continue
        if not any((r.get("lisy") or "").strip()=="1" for r in valid):
            continue
        eff=[EFFORT[(r.get("perc_surveyed") or "").strip()] for r in rs if (r.get("perc_surveyed") or "").strip() in EFFORT]
        if not eff:
            continue
        adult=any("A" in tokens(r.get("lisy_stage")) for r in rs)
        repro=any(tokens(r.get("lisy_stage")) & {"E","L"} for r in rs)
        fishvals={(r.get("fish") or "").strip() for r in rs if (r.get("fish") or "").strip() in {"Y","N"}}
        fish=1 if "Y" in fishvals else (0 if "N" in fishvals else None)
        eligible.append({
            "site":site,"year":year,"adult":adult,"repro":repro,
            "fish_known":fish is not None,"fish":fish,
            "max_effort":max(eff),"n_visits":len(dates)
        })

    out={
        "audit":"rmnp_woodfrog_validation_estimability_v0_1",
        "eligible_site_years":len(eligible),
        "adult_positive_site_years":sum(x["adult"] for x in eligible),
        "reproductive_positive_site_years":sum(x["repro"] for x in eligible),
        "fish_known_site_years":sum(x["fish_known"] for x in eligible),
        "fish_present_site_years":sum(x["fish"]==1 for x in eligible),
        "fish_not_observed_site_years":sum(x["fish"]==0 for x in eligible),
        "validation_gate":{
            "eligible_min":30,
            "adult_positive_min":5,
            "reproductive_positive_min":10,
            "pass":(
                len(eligible)>=30
                and sum(x["adult"] for x in eligible)>=5
                and sum(x["repro"] for x in eligible)>=10
            )
        },
        "effect_directions_opened":False,
        "adult_reproductive_association_opened":False
    }
    Path("frog_rmnp_woodfrog_validation_estimability_v0_1.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
