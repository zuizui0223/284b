#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, math, re, urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ITEM_ID="583dc314e4b0d1899f9dea8d"; ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
PINS={"Runs.csv":"ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730","Stops.csv":"28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f","Counts.csv":"60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086"}
POS={"1","2","3"}; LO,HI=-10.0,45.0

def gj(u):
    q=urllib.request.Request(u,headers={"User-Agent":"frog-naamp-robustness/0.1","Accept":"application/json"})
    with urllib.request.urlopen(q,timeout=60) as r:return json.loads(r.read().decode())
def gb(u):
    q=urllib.request.Request(u,headers={"User-Agent":"frog-naamp-robustness/0.1"})
    with urllib.request.urlopen(q,timeout=120) as r:return r.read()
def fu(f):return f.get("downloadUri") or f.get("url") or f.get("uri")
def ff(item,n):
    for f in item.get("files") or []:
        if (f.get("name") or "")==n:return fu(f)
    raise RuntimeError(n)
def yr(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or "")); return int(m.group(1)) if m else None
def doy(x):
    s=str(x or "").strip()
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%Y/%m/%d"):
        try:return datetime.strptime(s,fmt).timetuple().tm_yday
        except:pass
    return None
def z(x):
    a=np.asarray(x,float); sd=np.nanstd(a)
    if not np.isfinite(sd) or sd==0:raise ValueError("bad sd")
    return (a-np.nanmean(a))/sd
def load():
    item=gj(ITEM_URL); o={}
    for n,h in PINS.items():
        b=gb(ff(item,n))
        if hashlib.sha256(b).hexdigest()!=h:raise RuntimeError("hash drift "+n)
        o[n]=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    return o

def frame(raw):
    runs={}
    for r in raw["Runs.csv"]:
        y=yr(r.get("SurveyYear")) or yr(r.get("SurveyDate")); d=doy(r.get("SurveyDate"))
        if y is None or d is None or not 2001<=y<=2015 or (r.get("UnifiedProtocol") or "").strip()!="1":continue
        rid=(r.get("RunID") or "").strip(); rn=(r.get("RunNumber") or "").strip()
        try:rain=float((r.get("DaysSinceRain") or "").strip())
        except:continue
        if not rid or rain<0 or rn not in {"1","2","3","4"}:continue
        runs[rid]={"RunID":rid,"State":(r.get("State") or "").strip(),"RouteNumber":(r.get("RouteNumber") or "").strip(),"RouteType":(r.get("RouteType") or "").strip(),"RunNumber":rn,"SurveyYear":y,"DaysSinceRain":rain,"TempScale":(r.get("TempScale") or "").strip(),"doy":d}
    sampled=set(); trials=defaultdict(int); temps=defaultdict(list)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in runs or (s.get("SkippedStop") or "").strip()!="0":continue
        st=(s.get("StopNumber") or "").strip()
        if not st:continue
        key=(rid,st)
        if key in sampled:continue
        sampled.add(key);trials[rid]+=1
        try:t=float((s.get("AirTemp") or "").strip())
        except:continue
        sc=runs[rid]["TempScale"]
        if sc=="F":t=(t-32)*5/9
        elif sc!="C":continue
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
        ts=temps.get(rid,[])
        if trials.get(rid,0)<1 or len(ts)<8 or not r["State"] or not r["RouteNumber"] or not r["RouteType"]:continue
        mt=float(np.mean(ts))
        if mt<LO or mt>HI:continue
        rows.append({**r,"trials":trials[rid],"successes":succ.get(rid,0),"mean_temp_c":mt})
    d=pd.DataFrame(rows)
    d["prop"]=d.successes/d.trials; d["rain_z"]=z(np.log1p(d.DaysSinceRain));d["temp_z"]=z(d.mean_temp_c);d["year_z"]=z(d.SurveyYear);d["route_cluster"]=d.State.astype(str)+":"+d.RouteNumber.astype(str)
    return d

def fit(d,formula):
    f=smf.glm(formula,data=d,family=sm.families.Binomial(),freq_weights=d.trials.astype(float)).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    out={}
    for term in ("rain_z","temp_z"):
        b=float(f.params[term]);se=float(f.bse[term]);p=float(f.pvalues[term]);q=1.959963984540054
        lo=b-q*se;hi=b+q*se
        out[term]={"beta":b,"se":se,"ci95_beta":[lo,hi],"odds_ratio":math.exp(b),"ci95_or":[math.exp(lo),math.exp(hi)],"p_value":p}
    return {"n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),"terms":out}

def main():
    d=frame(load())
    joint="prop ~ rain_z + temp_z + C(State) + C(RunNumber) + C(RouteType) + year_z"
    date="prop ~ rain_z + temp_z + bs(doy, df=5, degree=3) + C(State) + C(RunNumber) + C(RouteType) + year_z"
    result={"analysis":"naamp_joint_weather_robustness_v0_1","contract":"NAAMP_JOINT_WEATHER_ROBUSTNESS_CONTRACT_V0_1.json","joint_readback":fit(d,joint),"doy_spline_robustness":fit(d,date),"causal_claim_authorized":False}
    Path("frog_naamp_joint_weather_robustness_v0_1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
