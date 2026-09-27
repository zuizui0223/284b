#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, math, re, urllib.request
from collections import defaultdict
from itertools import combinations
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
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-network/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.loads(r.read().decode())

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-network/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:return r.read()

def file_url(f):return f.get("downloadUri") or f.get("url") or f.get("uri")
def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:return file_url(f)
    raise RuntimeError(name)

def year(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def z(x):
    x=np.asarray(x,float); sd=np.nanstd(x)
    if not np.isfinite(sd) or sd==0:raise ValueError("bad sd")
    return (x-np.nanmean(x))/sd

def load():
    item=get_json(ITEM_URL); out={}
    for name,sha in PINS.items():
        b=get_bytes(find_file(item,name))
        if hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError("hash drift "+name)
        out[name]=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    return out

def make_frame(raw,repeat_threshold=1):
    runs={}
    for r in raw["Runs.csv"]:
        y=year(r.get("SurveyYear")) or year(r.get("SurveyDate"))
        if y is None or not 2001<=y<=2015:continue
        if (r.get("UnifiedProtocol") or "").strip()!="1":continue
        rid=(r.get("RunID") or "").strip()
        try:dsr=float((r.get("DaysSinceRain") or "").strip())
        except:continue
        rn=(r.get("RunNumber") or "").strip()
        if not rid or dsr<0 or rn not in {"1","2","3","4"}:continue
        runs[rid]={
          "RunID":rid,"State":(r.get("State") or "").strip(),
          "RouteNumber":(r.get("RouteNumber") or "").strip(),
          "RouteType":(r.get("RouteType") or "").strip(),
          "RunNumber":rn,"SurveyYear":y,"DaysSinceRain":dsr
        }

    sampled=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in runs or (s.get("SkippedStop") or "").strip()!="0":continue
        stop=(s.get("StopNumber") or "").strip()
        if stop:sampled[rid].add(stop)

    stop_species=defaultdict(set)
    for c in raw["Counts.csv"]:
        rid=(c.get("RunID") or "").strip(); stop=(c.get("StopNumber") or "").strip()
        if rid not in sampled or stop not in sampled[rid]:continue
        if (c.get("CallingIndex") or "").strip() not in POS:continue
        sp=(c.get("Species") or "").strip()
        if sp:stop_species[(rid,stop)].add(sp)

    rows=[]
    for rid,r in runs.items():
        if len(sampled.get(rid,set()))!=10:continue
        if not r["State"] or not r["RouteNumber"] or not r["RouteType"]:continue
        pool=set()
        pair_stop_counts=defaultdict(int)
        for stop in sampled[rid]:
            ss=stop_species.get((rid,stop),set())
            pool.update(ss)
            for pair in combinations(sorted(ss),2):
                pair_stop_counts[pair]+=1
        S=len(pool)
        if S<2:continue
        trials=S*(S-1)//2
        successes=sum(n>=repeat_threshold for n in pair_stop_counts.values())
        rows.append({**r,"pool_richness":S,"pair_trials":trials,"pair_successes":successes})

    df=pd.DataFrame(rows)
    df["prop"]=df.pair_successes/df.pair_trials
    df["rain_z"]=z(np.log1p(df.DaysSinceRain))
    df["year_z"]=z(df.SurveyYear)
    df["route_cluster"]=df.State.astype(str)+":"+df.RouteNumber.astype(str)
    return df

FORM="prop ~ rain_z + C(State) + C(RunNumber) + C(RouteType) + year_z + C(pool_richness)"

def fit(d):
    m=smf.glm(FORM,data=d,family=sm.families.Binomial(),freq_weights=d.pair_trials.astype(float))
    f=m.fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    b=float(f.params["rain_z"]); se=float(f.bse["rain_z"]); p=float(f.pvalues["rain_z"])
    q=1.959963984540054; lo=b-q*se; hi=b+q*se
    return {
      "n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
      "pair_trials":int(d.pair_trials.sum()),"pair_successes":int(d.pair_successes.sum()),
      "beta_rain_z":b,"se_cluster":se,"ci95_beta":[lo,hi],
      "odds_ratio":math.exp(b),"ci95_or":[math.exp(lo),math.exp(hi)],
      "p_value":p,"support_rule_pass":bool(b<0 and p<0.05 and hi<0)
    }

def main():
    raw=load()
    d1=make_frame(raw,1)
    d2=make_frame(raw,2)
    result={
      "analysis":"naamp_chorus_network_H4_v0_1",
      "contract":"NAAMP_NETWORK_CONTRACT_V0_1.json",
      "primary":fit(d1),
      "repeat_edge_sensitivity":fit(d2),
      "formula":FORM,
      "rainfall_causal_claim_authorized":False,
      "individual_edge_effects_opened":False
    }
    Path("frog_naamp_chorus_network_H4_v0_1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
