#!/usr/bin/env python3
"""Outcome-blind eligibility audit for the frozen RMNP Pseudacris model."""
from __future__ import annotations

import csv, hashlib, io, json, math, re, urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ITEM_ID="657ca143d34e23d35331ce9d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
CSV_NAME="ROMO_data_release.csv"
EXPECTED_SHA="aa42c97dcc506b96f832c2ea4180f057527b1efeec302586d06801751c1cda3a"
YEAR_MIN,YEAR_MAX=2003,2022
SURVEY_MAP={"0-25":0.125,"26-50":0.38,"51-75":0.63,"76-99":0.875,"100":1.0}
SHALLOW={"< or = 1","<=1","≤1","< or = 1 m"}
DEEPER={">1 - <2",">2",">1-<2",">1 - <2 m",">2 m"}


def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-eligibility/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-eligibility/0.1"})
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
    raise RuntimeError(f"missing {name}")


def parse_date(value):
    s=(value or "").strip()
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%Y/%m/%d"):
        try:
            return datetime.strptime(s,fmt).date()
        except ValueError:
            pass
    return None


def stage_tokens(value):
    s=(value or "").strip().upper()
    if not s:
        return set()
    # Codes are publisher-defined single letters; compound values may be comma/semicolon/slash separated.
    return {x for x in re.split(r"[^A-Z]+",s) if x}


def parse_detection(value):
    s=(value or "").strip().upper()
    if s in {"0","1"}: return int(s)
    return None


def survey_fraction(value):
    s=(value or "").strip()
    return SURVEY_MAP.get(s)


def classify_visit(row):
    det=parse_detection(row.get("psma"))
    sf=survey_fraction(row.get("perc_surveyed"))
    if det is None or sf is None:
        return None
    stages=stage_tokens(row.get("psma_stage"))
    if det==0:
        return 0
    if {"E","L"} & stages:
        return 1
    if "A" in stages:
        return 0
    return None


def adult_detected(row):
    return parse_detection(row.get("psma"))==1 and "A" in stage_tokens(row.get("psma_stage"))


def depth_class(value):
    s=(value or "").strip()
    if s in SHALLOW: return "shallow"
    if s in DEEPER: return "deeper"
    return None


def parse_positive_float(v):
    try:
        x=float((v or "").strip())
    except Exception:
        return None
    return x if math.isfinite(x) and x>0 else None


def annual_covariates(rows):
    ordered=sorted(rows,key=lambda r:r["_date"])
    depth=None
    for r in ordered:
        depth=depth_class(r.get("max_depth"))
        if depth: break

    fish_values=[(r.get("fish") or "").strip().upper() for r in ordered]
    if "Y" in fish_values:
        fish="Y"
    elif "N" in fish_values:
        fish="N"
    else:
        fish=None

    log_area=None
    for r in ordered:
        length=parse_positive_float(r.get("site_length_m"))
        width=parse_positive_float(r.get("site_width_m"))
        if length is not None and width is not None:
            log_area=math.log1p(length*width)
            break
    return depth,fish,log_area


def audit_rows(rows):
    filtered=[]
    duplicate=Counter()
    for row in rows:
        d=parse_date(row.get("date"))
        site=(row.get("site_name") or "").strip()
        if not d or not site or not (YEAR_MIN<=d.year<=YEAR_MAX):
            continue
        row=dict(row)
        row["_date"]=d
        row["_site"]=site
        row["_year"]=d.year
        filtered.append(row)
        duplicate[(site,d.isoformat())]+=1

    dup_count=sum(n-1 for n in duplicate.values() if n>1)
    if dup_count:
        return {"duplicate_site_date_excess_rows":dup_count,"fail_closed_duplicate":True}

    by_sy=defaultdict(list)
    for r in filtered:
        by_sy[(r["_site"],r["_year"])].append(r)

    adult_confirmed=[]
    endpoint_ge2=0
    reproductive_positive=0
    valid_visit_hist=Counter()
    process_rows=[]
    depth_counts=Counter()
    fish_counts=Counter()
    area_complete=0

    for key,rs in by_sy.items():
        if not any(adult_detected(r) for r in rs):
            continue
        adult_confirmed.append(key)
        ys=[classify_visit(r) for r in rs]
        ys=[y for y in ys if y is not None]
        valid_visit_hist[len(ys)]+=1
        if len(ys)>=2:
            endpoint_ge2+=1
        if any(y==1 for y in ys):
            reproductive_positive+=1

        depth,fish,log_area=annual_covariates(rs)
        if depth: depth_counts[depth]+=1
        else: depth_counts["missing"]+=1
        if fish: fish_counts[fish]+=1
        else: fish_counts["missing"]+=1
        if log_area is not None: area_complete+=1
        if depth is not None and log_area is not None:
            process_rows.append((key,depth,fish,log_area))

    complete_primary=len(process_rows)
    primary_depth=Counter(x[1] for x in process_rows)
    complete_secondary=[x for x in process_rows if x[2] in {"Y","N"}]
    secondary_fish=Counter(x[2] for x in complete_secondary)

    endpoint_pass=(
        len(adult_confirmed)>=50
        and endpoint_ge2>=30
        and reproductive_positive>=15
    )
    depth_pass=(
        complete_primary>=40
        and primary_depth["shallow"]>=10
        and primary_depth["deeper"]>=10
    )
    fish_pass=(
        secondary_fish["Y"]>=10
        and secondary_fish["N"]>=10
    )

    return {
        "duplicate_site_date_excess_rows":0,
        "fail_closed_duplicate":False,
        "post2002_rows":len(filtered),
        "site_years_total":len(by_sy),
        "adult_confirmed_site_years":len(adult_confirmed),
        "adult_confirmed_site_years_ge2_valid_endpoint_visits":endpoint_ge2,
        "reproductive_positive_adult_confirmed_site_years":reproductive_positive,
        "valid_endpoint_visit_count_histogram":dict(sorted(valid_visit_hist.items())),
        "adult_confirmed_depth_coverage":dict(sorted(depth_counts.items())),
        "adult_confirmed_fish_coverage":dict(sorted(fish_counts.items())),
        "adult_confirmed_area_complete":area_complete,
        "primary_process_complete_site_years":complete_primary,
        "primary_process_depth_counts":dict(sorted(primary_depth.items())),
        "secondary_fish_complete_site_years":len(complete_secondary),
        "secondary_fish_counts":dict(sorted(secondary_fish.items())),
        "endpoint_gate_pass":endpoint_pass,
        "primary_depth_gate_pass":depth_pass,
        "secondary_fish_gate_pass":fish_pass,
        "confirmatory_primary_model_authorized":endpoint_pass and depth_pass,
        "effect_model_fitted":False,
        "effect_direction_opened":False
    }


def main():
    item=get_json(ITEM_URL)
    data=get_bytes(find_file(item,CSV_NAME))
    sha=hashlib.sha256(data).hexdigest()
    if sha!=EXPECTED_SHA:
        raise SystemExit(f"source hash drift: {sha}")
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig",errors="strict"))))
    result=audit_rows(rows)
    result.update({
        "audit":"rmnp_psma_eligibility_v0_1",
        "sciencebase_item_id":ITEM_ID,
        "source_sha256":sha,
        "epoch":[YEAR_MIN,YEAR_MAX],
        "focal_species":"Pseudacris maculata",
        "contract":"RMNP_MODEL_CONTRACT_V0_2 + RMNP_ELIGIBILITY_GATE_V0_1",
    })
    out=Path("frog_rmnp_psma_eligibility_v0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
