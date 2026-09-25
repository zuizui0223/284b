#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"run_frogid_rain_validation_earthmover.py"
spec=importlib.util.spec_from_file_location("frogid_base",SRC)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

original_fit=base.fit_model
cache={}

def within_cell_fit(df, cluster_col):
    if cluster_col!="cell_id":
        return original_fit(df,cluster_col)

    key=(len(df),int(df.multi.sum()),int(df.cell_id.nunique()))
    if key in cache:
        return cache[key]

    d=df.copy()
    month=pd.get_dummies(
        d["month"].astype(int),prefix="month",drop_first=True,dtype=float
    )
    X=pd.DataFrame({
      "dry_z":d["dry_z"].astype(float),
      "year_z":d["year_z"].astype(float),
      "sin_hour":d["sin_hour"].astype(float),
      "cos_hour":d["cos_hour"].astype(float),
    },index=d.index)
    X=pd.concat([X,month.set_axis(d.index)],axis=1)
    d["_y"]=d["multi"].astype(float)

    # Exact within-cell fixed-effect transform. Retain only cells with repeated
    # observations and actual within-cell exposure variation.
    stats=d.groupby("cell_id").agg(
      n=("_y","size"),dry_min=("dry_z","min"),dry_max=("dry_z","max")
    )
    good=stats[(stats.n>=2) & ((stats.dry_max-stats.dry_min)>1e-12)].index
    d=d[d.cell_id.isin(good)].copy()
    X=X.loc[d.index].copy()

    groups=d["cell_id"].astype(str)
    y=d["_y"]-d.groupby("cell_id")["_y"].transform("mean")
    Xw=pd.DataFrame(index=d.index)
    for col in X.columns:
        vals=X[col].astype(float)
        Xw[col]=vals-vals.groupby(groups).transform("mean")

    model=sm.OLS(y.astype(float),Xw.astype(float))
    fit=model.fit(cov_type="cluster",cov_kwds={"groups":groups})
    b=float(fit.params["dry_z"])
    se=float(fit.bse["dry_z"])
    p=float(fit.pvalues["dry_z"])
    q=1.959963984540054
    lo=b-q*se; hi=b+q*se
    out={
      "n_recordings":int(len(d)),
      "multi_species_recordings":int(d.multi.sum()),
      "informative_weather_cells":int(d.cell_id.nunique()),
      "estimator":"within-ERA5-cell fixed-effects linear probability diagnostic",
      "adjustments":["within-cell month indicators","within-cell year_z","within-cell sin_hour","within-cell cos_hour"],
      "beta_dry_within_probability_scale":b,
      "se_cell_cluster":se,
      "ci95_beta":[lo,hi],
      "p_value":p,
      "direction_negative":bool(b<0),
      "ci_excludes_zero_negative":bool(hi<0)
    }
    cache[key]=out
    return out

def main():
    base.fit_model=within_cell_fit
    base.main()
    src=Path("frog_frogid_rain_validation_earthmover_v0_2.json")
    payload=json.loads(src.read_text(encoding="utf-8"))
    result={
      "analysis":"frogid_within_weather_cell_spatial_confounding_v0_1_1",
      "contract":"SPATIAL_CONFOUNDING_ROBUSTNESS_CONTRACT_V0_1_1.json",
      "repair":"SPATIAL_CONFOUNDING_REPAIR_V0_1.md",
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
