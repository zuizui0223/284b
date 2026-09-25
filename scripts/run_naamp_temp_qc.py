#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, math, re, urllib.request
from collections import defaultdict, Counter
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
LO,HI=-10.0,45.0

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-temp-qc/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.loads(r.read().decode())

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-temp-qc/0.1"})
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

def frame(raw):
    runs={}
    for r in raw["Runs.csv"]:
        y=year(r.get("SurveyYear")) or year(r.get("SurveyDate"))
        if y is None or not 2001<=y<=2015:continue
        if (r.get("UnifiedProtocol") or "").strip()!="1":continue
        rid=(r.get("RunID") or "").strip()
        try:dsr=float((r.get("DaysSinceRain") or "").strip())
        except:continue
        if not rid or dsr<0:continue
        rn=(r.get("RunNumber") or "").strip()
        if rn not in {"1","2","3","4"}:continue
        runs[rid]={
          "RunID":rid,"State":(r.get("State") or "").strip(),
          "RouteNumber":(r.get("RouteNumber") or "").strip(),
          "RouteType":(r.get("RouteType") or "").strip(),
          "RunNumber":rn,"SurveyYear":y,"DaysSinceRain":dsr,
          "TempScale":(r.get("TempScale") or "").strip()
        }

    sampled=set(); trials=defaultdict(int); temps=defaultdict(list)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in runs or (s.get("SkippedStop") or "").strip()!="0":continue
        stop=(s.get("StopNumber") or "").strip()
        if not stop:continue
        key=(rid,stop)
        if key in sampled:continue
        sampled.add(key); trials[rid]+=1
        rawt=(s.get("AirTemp") or "").strip()
        try:t=float(rawt)
        except:continue
        scale=runs[rid]["TempScale"]
        if scale=="F":t=(t-32)*5/9
        elif scale!="C":continue
        if np.isfinite(t):temps[rid].append(t)

    spp=defaultdict(set)
    for c in raw["Counts.csv"]:
        key=((c.get("RunID") or "").strip(),(c.get("StopNumber") or "").strip())
        if key not in sampled or (c.get("CallingIndex") or "").strip() not in POS:continue
        sp=(c.get("Species") or "").strip()
        if sp:spp[key].add(sp)
    succ=defaultdict(int)
    for key in sampled:
        if len(spp.get(key,set()))>=2:succ[key[0]]+=1

    rows=[]
    for rid,r in runs.items():
        if trials.get(rid,0)<1 or not r["State"] or not r["RouteNumber"] or not r["RouteType"]:continue
        ts=temps.get(rid,[])
        rows.append({**r,"trials":trials[rid],"successes":succ.get(rid,0),
          "n_temp_stops":len(ts),"mean_temp_c":float(np.mean(ts)) if ts else np.nan})
    df=pd.DataFrame(rows)
    df["prop"]=df.successes/df.trials
    df["rain_z"]=z(np.log1p(df.DaysSinceRain))
    df["year_z"]=z(df.SurveyYear)
    df["route_cluster"]=df.State.astype(str)+":"+df.RouteNumber.astype(str)
    return df

FORM="prop ~ rain_z + temp_z + C(State) + C(RunNumber) + C(RouteType) + year_z"

def fit(d):
    d=d.copy(); d["temp_z"]=z(d.mean_temp_c)
    m=smf.glm(FORM,data=d,family=sm.families.Binomial(),freq_weights=d.trials.astype(float))
    f=m.fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    b=float(f.params["temp_z"]); se=float(f.bse["temp_z"]); p=float(f.pvalues["temp_z"])
    q=1.959963984540054; lo=b-q*se; hi=b+q*se
    return {"n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
      "beta":b,"se_cluster":se,"ci95_beta":[lo,hi],"odds_ratio":math.exp(b),
      "ci95_or":[math.exp(lo),math.exp(hi)],"p_value":p,
      "support_rule_pass":bool(b>0 and p<0.05 and lo>0)}

def main():
    df=frame(load())
    base=df[(df.n_temp_stops>=8)&np.isfinite(df.mean_temp_c)].copy()
    quantiles={str(q):float(base.mean_temp_c.quantile(q)) for q in [0,0.001,0.01,0.05,0.5,0.95,0.99,0.999,1]}
    extremes={
      "below_-10":int((base.mean_temp_c<LO).sum()),
      "above_45":int((base.mean_temp_c>HI).sum()),
      "above_50":int((base.mean_temp_c>50).sum())
    }
    byscale={}
    for scale in ["F","C"]:
        d=base[base.TempScale==scale].copy()
        byscale[scale]={
          "n_runs":int(len(d)),
          "n_routes":int(d.route_cluster.nunique()),
          "min":float(d.mean_temp_c.min()) if len(d) else None,
          "max":float(d.mean_temp_c.max()) if len(d) else None,
          "eligible_for_effect_sensitivity":bool(len(d)>=500 and d.route_cluster.nunique()>=50)
        }

    qc=base[(base.mean_temp_c>=LO)&(base.mean_temp_c<=HI)].copy()
    result={
      "analysis":"naamp_temperature_qc_v0_1",
      "contract":"NAAMP_TEMP_QC_CONTRACT_V0_1.json",
      "raw_temperature_distribution":{"n_runs":int(len(base)),"quantiles_c":quantiles,"extreme_counts":extremes,"by_scale":byscale},
      "plausibility_filtered":{"bounds_c":[LO,HI],"excluded_runs":int(len(base)-len(qc)),"effect":fit(qc)},
      "scale_stratified":{},
      "original_temperature_result_replaced":False
    }
    for scale in ["F","C"]:
        d=base[(base.TempScale==scale)&(base.mean_temp_c>=LO)&(base.mean_temp_c<=HI)].copy()
        if len(d)>=500 and d.route_cluster.nunique()>=50:
            result["scale_stratified"][scale]=fit(d)
        else:
            result["scale_stratified"][scale]={"not_estimable_under_frozen_floor":True,"n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique())}
    Path("frog_naamp_temperature_qc_v0_1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
