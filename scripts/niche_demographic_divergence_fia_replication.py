"""Fixed geographic replication of the initial NE pilot; secondary marginal null."""
import argparse, json, pathlib, sys
import numpy as np
import pandas as pd
import niche_demographic_divergence_fia_pilot as p

REGIONS={"great_lakes":("MI","WI","MN"),"appalachia":("PA","WV","VA")}

def marginal_null(df):
    # Unique plot/species observations; repeated pair appearances must be identical.
    a=df[["plot","state","a","n0a","n1a"]].rename(columns={"a":"sp","n0a":"n0","n1a":"n1"})
    b=df[["plot","state","b","n0b","n1b"]].rename(columns={"b":"sp","n0b":"n0","n1b":"n1"})
    u=pd.concat([a,b],ignore_index=True).drop_duplicates().reset_index(drop=True)
    if u.duplicated(["plot","sp"]).any():raise ValueError("species-plot disagreement")
    u["stratum"]=pd.cut(u.n0,[1,3,7,np.inf],labels=["2-3","4-7","8+"])
    groups=list(u.groupby(["sp","state","stratum"],observed=True).indices.values())
    moving=sum(len(ix) for ix in groups if len(ix)>1)
    sign=np.sign((u.n1-u.n0).to_numpy())
    ids={(r.plot,r.sp):i for i,r in enumerate(u.itertuples(index=False))}
    n=df.groupby("plot").opposite_count.transform("size")
    d=df[n>=2].copy()
    if len(d)<30:return {"status":"insufficient_within_plot_support"}
    cols=["D","J","logn","imbalance"]
    sizes=d.groupby("plot").opposite_count.transform("size").to_numpy()
    X=(d[cols]-d.groupby("plot")[cols].transform("mean")).to_numpy()
    xx=(X/sizes[:,None]).T@X
    if np.linalg.matrix_rank(xx)<4:return {"status":"rank_failure"}
    # Because X is centered within plot, the raw outcome gives the same beta.
    w=np.linalg.solve(xx,(X/sizes[:,None]).T)[0]*.1
    aa=np.array([ids[(r.plot,r.a)] for r in d.itertuples(index=False)])
    bb=np.array([ids[(r.plot,r.b)] for r in d.itertuples(index=False)])
    y=(sign[aa]*sign[bb]<0).astype(float)
    observed=float(w@y)
    original=p.fit(df,"opposite_count")["slope_per_0_1_D"]
    if not np.isclose(observed,original,atol=1e-10):raise ValueError("FWL inconsistency")
    rng=np.random.default_rng(284128); null=[]; rates=[]
    for _ in range(499):
        s=sign.copy()
        for ix in groups:
            if len(ix)>1:s[ix]=rng.permutation(sign[ix])
        ny=(s[aa]*s[bb]<0)
        null.append(float(w@ny));rates.append(float(ny.mean()))
    med=float(np.median(null))
    return {"status":"descriptive_marginal_null_not_p_value","unique_species_plot_observations":len(u),"strata":len(groups),"fraction_movable":moving/len(u),"observed_slope_per_0_1_D":observed,"null_slope_median":med,"null_slope_95_range":list(map(float,np.quantile(null,[.025,.975]))),"observed_minus_null_median":observed-med,"observed_opposition_rate_within_plot_rows":float(y.mean()),"null_opposition_rate_median":float(np.median(rates)),"replicates":499,"interpretation":"Preserves per-species state/baseline-count class marginal changes and pair membership; no claim of spatial exchangeability or causality."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--region",choices=list(REGIONS),required=True)
    ap.add_argument("--data",type=pathlib.Path,required=True)
    ap.add_argument("--out",type=pathlib.Path,required=True)
    args=ap.parse_args()
    p.STATES=REGIONS[args.region]
    original=p.evaluations
    def capture(*a,**kw):
        df=original(*a,**kw)
        res=marginal_null(df)
        (args.out/"marginal_sign_null.json").write_text(json.dumps(res,indent=2,allow_nan=False))
        print("MARGINAL_NULL",json.dumps(res),flush=True)
        return df
    p.evaluations=capture
    sys.argv=[sys.argv[0],"--data",str(args.data),"--out",str(args.out)]
    p.main()
if __name__=="__main__":main()
