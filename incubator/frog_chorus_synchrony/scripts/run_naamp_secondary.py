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
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-secondary/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-secondary/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f): return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            return file_url(f)
    raise RuntimeError(name)

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

def base_frame(raw):
    runs={}
    for r in raw["Runs.csv"]:
        y=year(r.get("SurveyYear")) or year(r.get("SurveyDate"))
        if y is None or not 2001<=y<=2015: continue
        if (r.get("UnifiedProtocol") or "").strip()!="1": continue
        rid=(r.get("RunID") or "").strip()
        if not rid: continue
        try: dsr=float((r.get("DaysSinceRain") or "").strip())
        except Exception: continue
        if dsr<0: continue
        rn=(r.get("RunNumber") or "").strip()
        if rn not in {"1","2","3","4"}: continue
        runs[rid]={
          "RunID":rid,"State":(r.get("State") or "").strip(),
          "RouteNumber":(r.get("RouteNumber") or "").strip(),
          "RouteType":(r.get("RouteType") or "").strip(),
          "RunNumber":rn,"SurveyYear":y,"DaysSinceRain":dsr,
          "TempScale":(r.get("TempScale") or "").strip(),
        }

    sampled=set(); trials=defaultdict(int); temps=defaultdict(list)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in runs: continue
        if (s.get("SkippedStop") or "").strip()!="0": continue
        stop=(s.get("StopNumber") or "").strip()
        if not stop: continue
        key=(rid,stop)
        if key in sampled: continue
        sampled.add(key); trials[rid]+=1
        rawtemp=(s.get("AirTemp") or "").strip()
        if rawtemp:
            try:
                t=float(rawtemp)
                scale=runs[rid]["TempScale"]
                if scale=="F": t=(t-32.0)*5.0/9.0
                elif scale!="C": continue
                if np.isfinite(t): temps[rid].append(t)
            except Exception:
                pass

    spp=defaultdict(set)
    for c in raw["Counts.csv"]:
        key=((c.get("RunID") or "").strip(),(c.get("StopNumber") or "").strip())
        if key not in sampled: continue
        if (c.get("CallingIndex") or "").strip() not in POS: continue
        sp=(c.get("Species") or "").strip()
        if sp: spp[key].add(sp)

    succ=defaultdict(int)
    for key in sampled:
        if len(spp.get(key,set()))>=2: succ[key[0]]+=1

    rows=[]
    for rid,r in runs.items():
        n=trials.get(rid,0)
        if n<1 or not r["State"] or not r["RouteNumber"] or not r["RouteType"]: continue
        rows.append({
          **r,"successes":succ.get(rid,0),"trials":n,
          "n_temp_stops":len(temps.get(rid,[])),
          "mean_temp_c":float(np.mean(temps[rid])) if temps.get(rid) else np.nan,
        })
    df=pd.DataFrame(rows)
    df["prop"]=df.successes/df.trials
    df["rain_z"]=z(np.log1p(df.DaysSinceRain.astype(float)))
    df["year_z"]=z(df.SurveyYear.astype(float))
    df["route_cluster"]=df.State.astype(str)+":"+df.RouteNumber.astype(str)

    state_last=(df.groupby("State")["RunNumber"]
                  .apply(lambda s:max(int(x) for x in s if str(x) in {"1","2","3","4"}))
                  .to_dict())
    df["state_last_window"]=df.State.map(state_last)
    df["shoulder"]=((df.RunNumber.astype(int)==1) |
                    (df.RunNumber.astype(int)==df.state_last_window)).astype(int)
    return df,state_last

def fit(df,formula,term):
    m=smf.glm(formula,data=df,family=sm.families.Binomial(),freq_weights=df.trials.astype(float))
    f=m.fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster})
    b=float(f.params[term]); se=float(f.bse[term]); p=float(f.pvalues[term])
    q=1.959963984540054; lo=b-q*se; hi=b+q*se
    return {
      "n_runs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
      "sampled_stops":int(df.trials.sum()),"multi_species_stops":int(df.successes.sum()),
      "term":term,"beta":b,"se_cluster":se,"ci95_beta":[lo,hi],
      "odds_ratio":math.exp(b),"ci95_or":[math.exp(lo),math.exp(hi)],
      "p_value":p
    }

def main():
    df,state_last=base_frame(load())

    tdf=df[(df.n_temp_stops>=8) & np.isfinite(df.mean_temp_c)].copy()
    tdf["temp_z"]=z(tdf.mean_temp_c)
    tf="prop ~ rain_z + temp_z + C(State) + C(RunNumber) + C(RouteType) + year_z"
    temp=fit(tdf,tf,"temp_z")
    temp["support_rule_pass"]=bool(temp["beta"]>0 and temp["p_value"]<0.05 and temp["ci95_beta"][0]>0)
    t10=tdf[tdf.trials==10].copy()
    temp10=fit(t10,tf,"temp_z")
    temp10["support_rule_pass"]=bool(temp10["beta"]>0 and temp10["p_value"]<0.05 and temp10["ci95_beta"][0]>0)

    hdf=df[df.state_last_window.isin([3,4])].copy()
    hf="prop ~ rain_z + rain_z:shoulder + C(State) + C(RunNumber) + C(RouteType) + year_z"
    h3=fit(hdf,hf,"rain_z:shoulder")
    h3["support_rule_pass"]=bool(h3["beta"]<0 and h3["p_value"]<0.05 and h3["ci95_beta"][1]<0)
    h4state=hdf[hdf.state_last_window==4].copy()
    h3_four=fit(h4state,hf,"rain_z:shoulder")
    h3_four["support_rule_pass"]=bool(h3_four["beta"]<0 and h3_four["p_value"]<0.05 and h3_four["ci95_beta"][1]<0)

    result={
      "analysis":"naamp_chorus_synchrony_secondary_v0_1",
      "contract":"NAAMP_SECONDARY_CONTRACT_V0_1.json",
      "temperature":{
        "formula":tf,
        "mean_temp_c_summary":{
          "mean":float(tdf.mean_temp_c.mean()),"sd":float(tdf.mean_temp_c.std(ddof=0)),
          "min":float(tdf.mean_temp_c.min()),"max":float(tdf.mean_temp_c.max()),
        },
        "primary":temp,
        "complete_10_stop_sensitivity":temp10,
      },
      "seasonal_shoulder":{
        "formula":hf,
        "state_last_window_counts":{str(k):int(v) for k,v in pd.Series(state_last).value_counts().sort_index().items()},
        "shoulder_run_counts":{str(k):int(v) for k,v in hdf.RunNumber.value_counts().sort_index().items()},
        "primary":h3,
        "four_window_states_sensitivity":h3_four,
      },
      "primary_rain_result_replaced":False,
      "network_effect_opened":False,
      "causal_claim_authorized":False,
    }
    Path("frog_naamp_chorus_synchrony_secondary_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
