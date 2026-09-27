#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, re, sys, urllib.request
from collections import defaultdict
from pathlib import Path

ITEM_ID="657ca143d34e23d35331ce9d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
CSV_NAME="ROMO_data_release.csv"
CSV_SHA="aa42c97dcc506b96f832c2ea4180f057527b1efeec302586d06801751c1cda3a"
EFFORT={"0-25":0.125,"26-50":0.38,"51-75":0.63,"76-99":0.875,"100":1.0}
DEPTH={"< or = 1":0,">1 - <2":1,">2":2}
YEAR_CENTER=2012.5

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-primary-analysis/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 frog-rmnp-primary-analysis/0.1"})
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

def aggregate(rows):
    groups=defaultdict(list)
    for row in rows:
        y=year_from_string(row.get("date"))
        site=(row.get("site_name") or "").strip()
        if site and y and 2003<=y<=2022:
            groups[(site,y)].append(row)
    out=[]
    for (site,year),rs in groups.items():
        valid=[r for r in rs if (r.get("psma") or "").strip() in {"0","1"}]
        dates={str(r.get("date") or "").strip() for r in valid if str(r.get("date") or "").strip()}
        if len(dates)<2: continue
        if not any((r.get("psma") or "").strip()=="1" for r in valid): continue
        eff=[EFFORT[(r.get("perc_surveyed") or "").strip()] for r in rs if (r.get("perc_surveyed") or "").strip() in EFFORT]
        if not eff: continue
        fishvals={(r.get("fish") or "").strip() for r in rs if (r.get("fish") or "").strip() in {"Y","N"}}
        fish=1 if "Y" in fishvals else (0 if "N" in fishvals else None)
        if fish is None: continue
        depthvals=[DEPTH[(r.get("max_depth") or "").strip()] for r in rs if (r.get("max_depth") or "").strip() in DEPTH]
        adult=int(any("A" in tokens(r.get("psma_stage")) for r in rs))
        repro=int(any(tokens(r.get("psma_stage")) & {"E","L"} for r in rs))
        out.append({
            "site_name":site,
            "year":year,
            "year_centered":year-YEAR_CENTER,
            "adult":adult,
            "repro":repro,
            "fish_present":fish,
            "max_effort":max(eff),
            "n_visits":len(dates),
            "depth_class":max(depthvals) if depthvals else None,
        })
    return out

def fit_gee(df,formula,label):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    if df.empty:
        return {"label":label,"status":"not_estimable_empty"}
    try:
        model=smf.gee(
            formula=formula,
            groups="site_name",
            data=df,
            family=sm.families.Binomial(),
            cov_struct=sm.cov_struct.Exchangeable(),
        )
        res=model.fit()
        rows={}
        for name in res.params.index:
            ci=res.conf_int().loc[name]
            rows[name]={
                "coef":float(res.params[name]),
                "robust_se":float(res.bse[name]),
                "p_value":float(res.pvalues[name]),
                "ci95_low":float(ci.iloc[0]),
                "ci95_high":float(ci.iloc[1]),
                "odds_ratio":float(__import__("math").exp(res.params[name])),
            }
        return {
            "label":label,
            "status":"fit",
            "n_rows":int(df.shape[0]),
            "n_site_year_stage_pairs":int(df.shape[0]//2),
            "n_sites":int(df["site_name"].nunique()),
            "formula":formula,
            "terms":rows,
            "converged":bool(getattr(res,"converged",True)),
        }
    except Exception as exc:
        return {"label":label,"status":"fit_failed","error":repr(exc),"formula":formula}

def long_df(siteyears):
    import pandas as pd
    rows=[]
    for x in siteyears:
        base={k:v for k,v in x.items() if k not in {"adult","repro"}}
        rows.append({**base,"reproductive_stage":0,"stage_evidence":x["adult"]})
        rows.append({**base,"reproductive_stage":1,"stage_evidence":x["repro"]})
    return pd.DataFrame(rows)

def main():
    import numpy as np, pandas as pd, statsmodels
    item=get_json(ITEM_URL)
    data=get_bytes(find_file(item,CSV_NAME))
    if hashlib.sha256(data).hexdigest()!=CSV_SHA:
        raise SystemExit("CSV hash drift")
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig",errors="strict"))))
    sy=aggregate(rows)
    pdf=long_df(sy)

    primary_formula="stage_evidence ~ reproductive_stage * fish_present + year_centered + max_effort + n_visits"
    temporal_formula="stage_evidence ~ reproductive_stage * year_centered + fish_present + max_effort + n_visits"
    depth_formula="stage_evidence ~ reproductive_stage * fish_present + year_centered + max_effort + n_visits + depth_class"

    primary=fit_gee(pdf,primary_formula,"primary_stage_x_fish")
    temporal=fit_gee(pdf,temporal_formula,"secondary_stage_x_year")

    high_sy=[x for x in sy if x["max_effort"]>=0.875]
    high=fit_gee(long_df(high_sy),primary_formula,"high_effort_sensitivity")

    depth_sy=[x for x in sy if x["depth_class"] is not None]
    depth=fit_gee(long_df(depth_sy),depth_formula,"depth_complete_case_sensitivity")

    result={
        "analysis":"rmnp_stage_filtering_confirmatory_v0_1",
        "source_sha256":CSV_SHA,
        "software":{
            "python":sys.version.split()[0],
            "numpy":np.__version__,
            "pandas":pd.__version__,
            "statsmodels":statsmodels.__version__,
        },
        "site_years":len(sy),
        "adult_positive_site_years":sum(x["adult"] for x in sy),
        "reproductive_positive_site_years":sum(x["repro"] for x in sy),
        "fish_present_site_years":sum(x["fish_present"]==1 for x in sy),
        "fish_not_observed_site_years":sum(x["fish_present"]==0 for x in sy),
        "primary":primary,
        "secondary_temporal":temporal,
        "high_effort_sensitivity":high,
        "depth_complete_case_sensitivity":depth,
        "claim_boundary":{
            "stage_evidence_not_true_absence":True,
            "causal_fish_claim_authorized":False,
            "adult_recruitment_claim_authorized":False,
        }
    }
    Path("frog_rmnp_stage_filtering_confirmatory_v0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
