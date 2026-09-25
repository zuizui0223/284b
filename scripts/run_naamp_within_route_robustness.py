#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parent
PRIMARY=ROOT/"run_naamp_primary.py"
spec=importlib.util.spec_from_file_location("naamp_primary",PRIMARY)
mod=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)

def weighted_demean(df, cols, group, weight):
    out=df.copy()
    w=out[weight].astype(float)
    for col in cols:
        num=(out[col].astype(float)*w).groupby(out[group]).transform("sum")
        den=w.groupby(out[group]).transform("sum")
        out[col+"_w"]=out[col].astype(float)-num/den
    return out

def main():
    df=mod.build_frame(mod.load()).copy()
    df["runnum"]=pd.to_numeric(df["RunNumber"],errors="coerce")
    df=df[np.isfinite(df.runnum)].copy()
    dummies=pd.get_dummies(df["runnum"].astype(int),prefix="run",drop_first=True,dtype=float)
    for c in dummies.columns:
        df[c]=dummies[c]
    cols=["prop","rain_z","year_z",*dummies.columns]
    d=weighted_demean(df,cols,"route_cluster","trials")
    informative=d.groupby("route_cluster")["rain_z"].agg(lambda x: float(np.nanmax(x)-np.nanmin(x))>1e-12)
    keep=set(informative[informative].index)
    d=d[d.route_cluster.isin(keep)].copy()

    y=d["prop_w"].astype(float)
    xcols=["rain_z_w","year_z_w",*[c+"_w" for c in dummies.columns]]
    X=d[xcols].astype(float)
    model=sm.WLS(y,X,weights=d["trials"].astype(float))
    fit=model.fit(cov_type="cluster",cov_kwds={"groups":d["route_cluster"]})
    b=float(fit.params["rain_z_w"]); se=float(fit.bse["rain_z_w"]); p=float(fit.pvalues["rain_z_w"])
    q=1.959963984540054; lo=b-q*se; hi=b+q*se
    result={
      "analysis":"naamp_within_route_spatial_confounding_v0_1",
      "contract":"SPATIAL_CONFOUNDING_ROBUSTNESS_CONTRACT_V0_1.json",
      "n_runs":int(len(d)),
      "n_routes":int(d.route_cluster.nunique()),
      "sampled_stops":int(d.trials.sum()),
      "estimator":"weighted within-route fixed-effects linear probability diagnostic",
      "beta_rain_within_probability_scale":b,
      "se_route_cluster":se,
      "ci95_beta":[lo,hi],
      "p_value":p,
      "direction_negative":bool(b<0),
      "ci_excludes_zero_negative":bool(hi<0),
      "primary_replaced":False
    }
    Path("frog_naamp_within_route_robustness_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
