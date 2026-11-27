#!/usr/bin/env python3
"""Reproduce the post-outcome stable vs changing contrast from the 3 signed ZIPs."""
import argparse,hashlib,json,pathlib,zipfile
import numpy as np
import pandas as pd
REGIONS={
"northeast":"559810b15ffaa5c2b20365c7aaf8819abbd80f41da327b3add78b804ba88f556",
"appalachia":"a934913145d8d7579bede13f59eb8665585b42597b52802f9f88750d768a6c6d",
"great_lakes":"9150af6d4d354a9b7946b90a4cd023a58f6818e1c4003a739d00bf1d285de022"}
def main():
    p=argparse.ArgumentParser();p.add_argument("--directory",type=pathlib.Path,required=True);p.add_argument("--out",type=pathlib.Path,required=True);a=p.parse_args()
    out={}
    for region,sha in REGIONS.items():
        f=a.directory/f"284b_stage_forecast_{region}_20261127.zip"
        if hashlib.sha256(f.read_bytes()).hexdigest()!=sha:raise ValueError("artifact digest mismatch "+region)
        with zipfile.ZipFile(f) as z:
            if z.testzip() is not None:raise ValueError("archive CRC failure")
            s=json.loads(z.read("summary.json"));d=pd.read_csv(z.open("heldout_block_loss_sums.csv"))
        assert int(d.plots.sum())==s["forecast_plots"]
        for m,v in s["results"]["primary"]["mean_squared_errors"].items():
            assert np.isclose(d["err_"+m].sum()/d.plots.sum(),v,rtol=0,atol=1e-12)
        for m,v in s["results"]["stable_adult_subset"]["mean_squared_errors"].items():
            x=d[d.stable]
            assert np.isclose(x["err_"+m].sum()/x.plots.sum(),v,rtol=0,atol=1e-12)
        by=d.groupby(["block","stable"])[["err_A","err_S","err_H","plots"]].sum().unstack(fill_value=0)
        ix=np.random.default_rng(284218).integers(0,len(by),(2000,len(by)))
        def sums(k,stable):return by[(k,stable)].to_numpy()[ix].sum(axis=1)
        out[region]={}
        for model in ("S","H"):
            stats=[];gb=[];db=[]
            for stable in (True,False):
                x=d[d.stable==stable];n=int(x.plots.sum());aa=x.err_A.sum();bb=x["err_"+model].sum()
                aa_b=sums("err_A",stable);bb_b=sums("err_"+model,stable);n_b=sums("plots",stable)
                g=np.divide(100*(aa_b-bb_b),aa_b,out=np.full(len(ix),np.nan),where=aa_b>0)
                e=np.divide(aa_b-bb_b,n_b,out=np.full(len(ix),np.nan),where=n_b>0)
                stats.append({"plots":n,"percent_reduction":float(100*(aa-bb)/aa),"percent_ci":np.nanquantile(g,[.025,.975]).tolist(),"absolute_mse_reduction":float((aa-bb)/n)})
                gb.append(g);db.append(e)
            out[region][model]={"stable":stats[0],"changing":stats[1],
               "changing_minus_stable_percent_points":stats[1]["percent_reduction"]-stats[0]["percent_reduction"],
               "joint_block_bootstrap_95_percent_points":np.nanquantile(gb[1]-gb[0],[.025,.975]).tolist(),
               "changing_minus_stable_absolute_mse":stats[1]["absolute_mse_reduction"]-stats[0]["absolute_mse_reduction"],
               "joint_block_bootstrap_95_absolute_mse":np.nanquantile(db[1]-db[0],[.025,.975]).tolist()}
    a.out.write_text(json.dumps({"status":"retrospective_conditional_loss_audit","new_confirmatory_endpoints":0,"regions":out},indent=2,allow_nan=False)+"\n")
if __name__=="__main__":main()
