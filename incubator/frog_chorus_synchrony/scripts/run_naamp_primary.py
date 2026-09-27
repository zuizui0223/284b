#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, math, re, urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ITEM_ID="583dc314e4b0d1899f9dea8d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
PINS={
 "Runs.csv":"ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
 "Stops.csv":"28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
 "Counts.csv":"60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086",
}
POS={"1","2","3"}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-primary-analysis/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-primary-analysis/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f): return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            return file_url(f)
    raise RuntimeError(f"missing {name}")

def year(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def z(x):
    x=np.asarray(x,dtype=float)
    sd=np.nanstd(x,ddof=0)
    if not np.isfinite(sd) or sd==0: raise ValueError("zero/invalid SD")
    return (x-np.nanmean(x))/sd

def load():
    item=get_json(ITEM_URL)
    out={}
    for name,sha in PINS.items():
        b=get_bytes(find_file(item,name))
        if hashlib.sha256(b).hexdigest()!=sha:
            raise RuntimeError(f"hash drift {name}")
        out[name]=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    return out

def build_frame(raw):
    runs={}
    for r in raw["Runs.csv"]:
        y=year(r.get("SurveyYear")) or year(r.get("SurveyDate"))
        if y is None or not 2001<=y<=2015: continue
        if (r.get("UnifiedProtocol") or "").strip()!="1": continue
        rid=(r.get("RunID") or "").strip()
        if not rid: continue
        try:
            dsr=float((r.get("DaysSinceRain") or "").strip())
        except Exception:
            continue
        if dsr<0: continue
        runs[rid]={
            "RunID":rid,"State":(r.get("State") or "").strip(),
            "RouteNumber":(r.get("RouteNumber") or "").strip(),
            "RouteType":(r.get("RouteType") or "").strip(),
            "RunNumber":(r.get("RunNumber") or "").strip(),
            "SurveyYear":y,"DaysSinceRain":dsr,
        }

    sampled=set()
    trials=defaultdict(int)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in runs: continue
        if (s.get("SkippedStop") or "").strip()!="0": continue
        stop=(s.get("StopNumber") or "").strip()
        if not stop: continue
        key=(rid,stop)
        if key in sampled: continue
        sampled.add(key); trials[rid]+=1

    spp=defaultdict(set)
    for c in raw["Counts.csv"]:
        rid=(c.get("RunID") or "").strip()
        stop=(c.get("StopNumber") or "").strip()
        key=(rid,stop)
        if key not in sampled: continue
        if (c.get("CallingIndex") or "").strip() not in POS: continue
        sp=(c.get("Species") or "").strip()
        if sp: spp[key].add(sp)

    succ=defaultdict(int)
    for key in sampled:
        if len(spp.get(key,set()))>=2:
            succ[key[0]]+=1

    rows=[]
    for rid,r in runs.items():
        n=trials.get(rid,0)
        if n<1: continue
        if not r["State"] or not r["RouteNumber"] or not r["RunNumber"]:
            continue
        rows.append({**r,"successes":succ.get(rid,0),"trials":n})
    df=pd.DataFrame(rows)
    df["prop"]=df["successes"]/df["trials"]
    df["rain_log"]=np.log1p(df["DaysSinceRain"].astype(float))
    df["rain_z"]=z(df["rain_log"])
    df["year_z"]=z(df["SurveyYear"].astype(float))
    df["route_cluster"]=df["State"].astype(str)+":"+df["RouteNumber"].astype(str)
    return df

FORMULA="prop ~ rain_z + C(State) + C(RunNumber) + C(RouteType) + year_z"

def fit_one(df):
    model=smf.glm(
        FORMULA,data=df,
        family=sm.families.Binomial(),
        freq_weights=df["trials"].astype(float),
    )
    fit=model.fit(
        cov_type="cluster",
        cov_kwds={"groups":df["route_cluster"]},
    )
    b=float(fit.params["rain_z"])
    se=float(fit.bse["rain_z"])
    lo=b-1.959963984540054*se
    hi=b+1.959963984540054*se
    p=float(fit.pvalues["rain_z"])
    return {
      "n_runs":int(len(df)),
      "n_routes":int(df["route_cluster"].nunique()),
      "sampled_stops":int(df["trials"].sum()),
      "multi_species_stops":int(df["successes"].sum()),
      "beta_rain_z":b,
      "se_cluster":se,
      "ci95_beta":[lo,hi],
      "odds_ratio_per_sd_log1p_days_since_rain":math.exp(b),
      "ci95_odds_ratio":[math.exp(lo),math.exp(hi)],
      "p_value_two_sided":p,
      "support_rule_pass":bool(b<0 and p<0.05 and hi<0),
    }

def main():
    df=build_frame(load())
    result={
      "analysis":"naamp_chorus_synchrony_primary_v0_1",
      "contract":"NAAMP_MODEL_CONTRACT_V0_1.json",
      "formula":FORMULA,
      "primary":fit_one(df),
      "sensitivity_complete_10_stops":fit_one(df[df["trials"]==10].copy()),
      "sensitivity_ge8_stops":fit_one(df[df["trials"]>=8].copy()),
      "primary_predictor":"z(log1p(DaysSinceRain))",
      "directional_hypothesis":"negative",
      "temperature_effect_opened":False,
      "species_pair_weather_effect_opened":False,
      "causal_claim_authorized":False,
    }
    Path("frog_naamp_chorus_synchrony_primary_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
