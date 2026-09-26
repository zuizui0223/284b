#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ITEM_ID="657ca143d34e23d35331ce9d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
CSV_NAME="ROMO_data_release.csv"
CSV_SHA="aa42c97dcc506b96f832c2ea4180f057527b1efeec302586d06801751c1cda3a"
SPECIES={
    "psma_stage":("Pseudacris maculata",{"A","E","J","L","M","NA","U"}),
    "lisy_stage":("Lithobates sylvaticus",{"A","E","J","L","M","NA","U"}),
    "amma_stage":("Ambystoma mavortium",{"A","E","J","L","NA","P","U"}),
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-token-audit/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-token-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            u=file_url(f)
            if not u: raise RuntimeError(f"{name}: no download URI")
            return u
    raise RuntimeError(f"missing file {name}")

def year_from_string(s):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(s or ""))
    return int(m.group(1)) if m else None

def tokens(raw):
    if raw is None: return []
    return sorted(set(p.strip() for p in str(raw).split(",") if p.strip()))

def main():
    item=get_json(ITEM_URL)
    data=get_bytes(find_file(item,CSV_NAME))
    if hashlib.sha256(data).hexdigest()!=CSV_SHA:
        raise SystemExit("CSV hash drift")
    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig",errors="strict")))
    visits=defaultdict(set)
    token_rows={c:Counter() for c in SPECIES}
    token_siteyears={c:defaultdict(set) for c in SPECIES}
    adult_siteyears={c:set() for c in SPECIES}
    downstream_siteyears={c:set() for c in SPECIES}
    unknown=Counter()

    for row in reader:
        site=(row.get("site_name") or "").strip()
        raw_date=(row.get("date") or "").strip()
        year=year_from_string(raw_date)
        key=(site,year) if site and year and year>=2003 else None
        if key:
            visits[key].add(raw_date)
        for col,(species,allowed) in SPECIES.items():
            ts=tokens(row.get(col))
            for t in ts:
                if t not in allowed:
                    unknown[(col,t)]+=1
                    continue
                token_rows[col][t]+=1
                if key:
                    token_siteyears[col][t].add(key)
            if key and "A" in ts:
                adult_siteyears[col].add(key)
            if key and any(t in ts for t in ("E","L")):
                downstream_siteyears[col].add(key)

    receipts={}
    for col,(species,allowed) in SPECIES.items():
        receipts[col]={
            "species":species,
            "token_row_counts":dict(sorted(token_rows[col].items())),
            "token_site_year_counts":{
                t:len(token_siteyears[col][t]) for t in sorted(token_siteyears[col])
            },
            "adult_site_years":len(adult_siteyears[col]),
            "downstream_E_or_L_site_years":len(downstream_siteyears[col]),
        }

    primary=receipts["psma_stage"]
    validation=receipts["lisy_stage"]
    repeat=sum(len(v)>=2 for v in visits.values())
    result={
        "audit":"rmnp_stage_token_normalization_v0_1",
        "post2002_site_years":len(visits),
        "post2002_site_years_ge2_visits":repeat,
        "stage_columns":receipts,
        "unknown_tokens":{
            f"{col}|{tok}":n for (col,tok),n in sorted(unknown.items())
        },
        "structural_gate_pass":(
            primary["adult_site_years"]>=50
            and primary["downstream_E_or_L_site_years"]>=30
            and repeat>=50
            and validation["adult_site_years"]>=5
            and validation["downstream_E_or_L_site_years"]>=10
            and not unknown
        ),
        "species_detection_columns_read":False,
        "adult_downstream_joint_state_opened":False,
        "environment_values_read":False,
    }
    out=Path("frog_rmnp_stage_token_normalization_v0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
