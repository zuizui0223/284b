"""Post-outcome, checksum-locked common-pair/common-reference audit."""
import argparse, json, pathlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import niche_demographic_divergence_fia_pilot as p

ROOT=pathlib.Path(__file__).resolve().parents[1]
REGIONS={"appalachia":("PA","WV","VA"),"great_lakes":("MI","WI","MN")}
EXPECTED={"appalachia":(10728,.006524307844870464),"great_lakes":(10556,-.015913724320846843)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--data",type=pathlib.Path,required=True);ap.add_argument("--out",type=pathlib.Path,required=True);args=ap.parse_args()
    args.data.mkdir(parents=True,exist_ok=True);args.out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/"config/niche_demography_replication_source_sha256_v1.json").read_text())
    allstates=sum(REGIONS.values(),())
    urls=[(p.CLIMATE,args.data/"climate.zip")]+[(f"{p.BASE}{s}_{t}.zip",args.data/f"{s}_{t}.zip") for s in allstates for t in p.TABLES]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for (_,f),r in zip(urls,ex.map(lambda u:p.acquire(*u),urls)):
            if r["sha256"]!=manifest[f.name]:raise ValueError("SOURCE_VERSION_CHANGED "+f.name)
    data={s:p.state_data(s,args.data) for s in allstates}
    inputs={};d={}
    for region,states in REGIONS.items():
        ref,interval,agg=[pd.concat([data[s][i] for s in states],ignore_index=True) for i in (0,1,2)]
        assert not (set(ref.key)&set(interval.key))
        inputs[region]=(ref,interval,agg)
        niche,_,_,_=p.reference_niches(ref,agg)
        df=p.evaluations(interval,agg,niche)
        expected_n,expected_beta=EXPECTED[region]
        beta=p.fit(df,"opposite_count")["slope_per_0_1_D"]
        if len(df)!=expected_n or not np.isclose(beta,expected_beta,atol=1e-10):
            raise ValueError(f"ORIGINAL_NOT_REPRODUCED {region} {len(df)} {beta}")
        d[region]=df
    def abundant_pairs(df):
        counts=df.groupby(["a","b"]).size()
        return set(counts[counts>=20].index)
    common=abundant_pairs(d["appalachia"])&abundant_pairs(d["great_lakes"])
    assert len(common)==27
    shared_species=set(sum((list(k) for k in common),[]))
    assert len(shared_species)==12
    pooled_ref=pd.concat([inputs[k][0] for k in REGIONS],ignore_index=True)
    pooled_agg=pd.concat([inputs[k][2] for k in REGIONS],ignore_index=True)
    common_niche,mat,av,ref=p.reference_niches(pooled_ref,pooled_agg)
    assert all(k in common_niche for k in common)
    result={"status":"postoutcome_descriptive_audit","source_hashes_verified":len(manifest),"original_full_region_slopes_reproduced":True,"common_pairs":len(common),"common_species":len(shared_species),"pooled_reference_plots":len(ref),"pooled_climate_bins":len(av),"regions":{},"new_confirmatory_endpoints":0}
    details=[]
    for region,df in d.items():
        take=np.array([(a,b) in common for a,b in zip(df.a,df.b)])
        s=df[take].copy()
        s["D_common"]=[common_niche[(a,b)][0] for a,b in zip(s.a,s.b)]
        s["J_common"]=[common_niche[(a,b)][1] for a,b in zip(s.a,s.b)]
        t=s.copy();t["J"]=t.J_common
        result["regions"][region]={"common_pair_rows":len(s),"common_pair_plots":int(s["plot"].nunique()),"regional_D_regional_J":p.fit(s,"opposite_count",bootstrap=True),"common_D_regional_J":p.fit(s,"opposite_count","D_common",bootstrap=True),"common_D_common_J":p.fit(t,"opposite_count","D_common",bootstrap=True),"basal_area_common_D_regional_J":p.fit(s,"opposite_ba","D_common",bootstrap=True)}
        summary=s.groupby(["a","b"],as_index=False).agg(n=("plot","size"),D_regional=("D","first"),D_common=("D_common","first"),J_regional=("J","first"),J_common=("J_common","first"),opposition=("opposite_count","mean"),opposition_ba=("opposite_ba","mean"));summary["region"]=region;details.append(summary)
    tab=pd.concat(details,ignore_index=True);tab.to_csv(args.out/"shared_pair_audit.csv",index=False)
    pivot=tab.pivot(index=["a","b"],columns="region",values="D_regional")
    result["regional_D_rank_correlation_shared_pairs"]=float(pivot.corr(method="spearman").iloc[0,1])
    result["interpretation"]="Retrospective matched-pair and common climatic-reference sensitivity. Same species pairs and common D remove two sources of heterogeneity, not all site or sampling confounding. Spatial bootstrap conditional on estimated niches."
    (args.out/"summary.json").write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
