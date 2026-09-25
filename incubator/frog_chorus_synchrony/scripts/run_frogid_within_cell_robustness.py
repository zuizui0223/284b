#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, math
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.discrete.conditional_models import ConditionalLogit

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"run_frogid_rain_validation_earthmover.py"
spec=importlib.util.spec_from_file_location("frogid_base",SRC)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

original_fit=base.fit_model
cache={}

def conditional_cell_fit(df, cluster_col):
    if cluster_col!="cell_id":
        return original_fit(df,cluster_col)
    key=(len(df),int(df.multi.sum()),int(df.cell_id.nunique()))
    if key in cache:
        return cache[key]

    d=df.copy()
    month=pd.get_dummies(d["month"].astype(int),prefix="month",drop_first=True,dtype=float)
    X=pd.DataFrame({
      "dry_z":d["dry_z"].astype(float),
      "year_z":d["year_z"].astype(float),
      "sin_hour":d["sin_hour"].astype(float),
      "cos_hour":d["cos_hour"].astype(float),
    },index=d.index)
    X=pd.concat([X,month.set_axis(d.index)],axis=1)

    stats=d.groupby("cell_id").agg(
      y_min=("multi","min"),y_max=("multi","max"),dry_min=("dry_z","min"),dry_max=("dry_z","max")
    )
    good=stats[(stats.y_min<stats.y_max) & ((stats.dry_max-stats.dry_min)>1e-12)].index
    d=d[d.cell_id.isin(good)].copy()
    X=X.loc[d.index].astype(float)
    y=d["multi"].astype(int).to_numpy()
    groups=d["cell_id"].astype(str).to_numpy()

    model=ConditionalLogit(y,X.to_numpy(),groups=groups)
    fit=model.fit(method="bfgs",maxiter=250,disp=False)
    names=list(X.columns)
    i=names.index("dry_z")
    b=float(fit.params[i]); se=float(fit.bse[i]); p=float(fit.pvalues[i])
    q=1.959963984540054; lo=b-q*se; hi=b+q*se
    out={
      "n_recordings":int(len(d)),
      "multi_species_recordings":int(d.multi.sum()),
      "informative_weather_cells":int(d.cell_id.nunique()),
      "estimator":"conditional logistic regression with ERA5-cell strata",
      "adjustments":["month indicators","year_z","sin_hour","cos_hour"],
      "beta_dry_z":b,
      "se_conditional":se,
      "ci95_beta":[lo,hi],
      "odds_ratio_within_cell":math.exp(b),
      "ci95_or":[math.exp(lo),math.exp(hi)],
      "p_value":p,
      "direction_negative":bool(b<0),
      "ci_excludes_zero_negative":bool(hi<0)
    }
    cache[key]=out
    return out

def main():
    base.fit_model=conditional_cell_fit
    base.main()
    src=Path("frog_frogid_rain_validation_earthmover_v0_2.json")
    payload=json.loads(src.read_text(encoding="utf-8"))
    result={
      "analysis":"frogid_within_weather_cell_spatial_confounding_v0_1",
      "contract":"SPATIAL_CONFOUNDING_ROBUSTNESS_CONTRACT_V0_1.json",
      "source_validation_contract":payload.get("contract"),
      "primary_within_cell":payload["primary"],
      "high_precision_within_cell":payload["sensitivities"]["coordinate_uncertainty_le10km"],
      "primary_replaced":False,
      "weather_source":payload["era5_source"]["provider"],
      "required_daily_weather_sha256":payload["era5_source"]["required_daily_weather_sha256"]
    }
    Path("frog_frogid_within_cell_robustness_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
