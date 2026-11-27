#!/usr/bin/env python3
"""Complementary three-census cohort; excludes all qualified four-visit keys."""
import argparse,hashlib,json,math,pathlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import stage_forecast_four_census as f
import stage_structured_fia_forecast as s
import niche_demographic_divergence_fia_pilot as p
ROOT=pathlib.Path(__file__).resolve().parents[1]
REGIONS=f.REGIONS
MODELS=f.MODELS

def state_data(root,state):
    v=s.read(root,state,"PLOT")
    if v.CN.duplicated().any() or v.CN.isna().any():raise ValueError("duplicate/missing plot CN")
    v=v.dropna(subset=["STATECD","UNITCD","COUNTYCD","PLOT","LAT","LON","MEASYEAR"]).copy()
    v["key"]=p.physical(v);v["year"]=v.MEASYEAR;v["arm"]=v.key.map(p.arm)
    v=v[v.year.between(2004,2024)&v.PLOT_STATUS_CD.eq(1)&v.DESIGNCD.eq(1)].copy()
    audit={"state":state,"design_visits":len(v)}
    c=s.read(root,state,"COND");c=c[c.PLT_CN.isin(v.CN)].copy()
    c["ok"]=c.COND_STATUS_CD.eq(1)&np.isclose(c.CONDPROP_UNADJ,1,atol=1e-6)&np.isclose(c.MICRPROP_UNADJ,1,atol=1e-6)&np.isclose(c.SUBPPROP_UNADJ,1,atol=1e-6)&c[["TRTCD1","TRTCD2","TRTCD3"]].fillna(0).eq(0).all(axis=1)
    good=c.groupby("PLT_CN").agg(n=("ok","size"),ok=("ok","all"))
    v=v[v.CN.isin(good[(good.n==1)&good.ok].index)]
    sub=s.read(root,state,"SUBPLOT");sub=sub[sub.PLT_CN.isin(v.CN)&sub.SUBP.isin([1,2,3,4])].copy()
    sub["ok"]=sub.SUBP_STATUS_CD.eq(1)
    ss=sub.groupby("PLT_CN").agg(n=("SUBP","size"),unique=("SUBP","nunique"),ok=("ok","all"))
    v=v[v.CN.isin(ss[(ss.n==4)&(ss.unique==4)&ss.ok].index)].copy()
    audit["complete_area_visits"]=len(v)
    trees=s.read(root,state,"TREE");trees=trees[trees.PLT_CN.isin(v.CN)].copy()
    if trees.CN.isna().any() or trees.CN.duplicated().any():raise ValueError("bad tree CN")
    sp=pd.to_numeric(trees.SPCD,errors="coerce")
    trees["sp"]=sp.where(sp.notna()&sp.gt(0)&sp.eq(np.floor(sp))).astype("Int64").astype("string")
    trees["stage"]=s.stage_of(trees)
    live=trees.STATUSCD.eq(1)
    bad=(live&(trees.sp.isna()|~trees.SUBP.isin([1,2,3,4])|trees.stage.eq("other")))|trees.STATUSCD.isna()
    badvis=set(trees.loc[bad,"PLT_CN"]);v=v[~v.CN.isin(badvis)].copy()
    audit["excluded_invalid_tree_visits"]=len(badvis)
    four=f.quads(v)
    q=s.triples_from(v)
    excluded=set(four.key)
    q=q[~q.key.isin(excluded)].copy()
    assert not set(q.key)&excluded
    audit['four_chain_keys_excluded']=len(excluded)
    needed=set().union(*(set(q[f"t{k}"]) for k in range(3)))
    trees=trees[trees.PLT_CN.isin(needed)&trees.stage.isin(["adult","early","late"])].copy()
    by=s.count_maps(trees)
    def adults(visit):return {a:x["adult"][0] for a,x in by.get(visit,{}).items() if "adult" in x}
    def nstage(v,sp,stage):return by.get(v,{}).get(sp,{}).get(stage,(0,0,0))[0]
    rows=[];undefined=0;few=0
    for r in q.itertuples(index=False):
        adult=[adults(getattr(r,f"t{k}")) for k in range(3)]
        tv=s.tv(adult[0],adult[1])
        if not np.isfinite(tv):undefined+=1;continue
        eligible=sorted(sp for sp,n in adult[1].items() if n>=2)
        if len(eligible)<2:few+=1;continue
        total=sum(adult[1].values());den=math.log1p(total)
        dia=sum(x["adult"][1] for x in by[r.t1].values() if "adult" in x)/total
        block=f"{math.floor(r.LAT)}|{math.floor(r.LON)}"
        fold=int(hashlib.sha256(block.encode()).hexdigest()[:8],16)%5
        for sp in eligible:
            n0,n1,n2=[x.get(sp,0) for x in adult]
            x0,x1,x2=[math.log(n+.5) for n in (n0,n1,n2)]
            past=(x1-x0)*5/r.dt01
            n,ds,small=by[r.t1][sp]["adult"]
            assert n==n1
            e0,e1=[nstage(getattr(r,f"t{k}"),sp,"early") for k in (0,1)]
            l0,l1=[nstage(getattr(r,f"t{k}"),sp,"late") for k in (0,1)]
            rows.append({"plot":r.key,"state":state,"block":block,"fold":fold,"sp":sp,
                "stable":bool(tv<=.10),"prior_turnover":float(tv),
                "total_adult":total,"richness":len(adult[1]),"mean_adult_dia":dia,
                "adult_log":x1,"adult_past":past,"diameter_log":math.log(ds/n),
                "small_adult_fraction":small/n,"density_x_adult":den*x1,"density_x_past":den*past,
                "early_stock":math.log1p(e1),"late_stock":math.log1p(l1),
                "early_history":(math.log1p(e1)-math.log1p(e0))*5/r.dt01,
                "late_history":(math.log1p(l1)-math.log1p(l0))*5/r.dt01,
                "short":(x2-x1)*5/r.dt12,
                "year0":int(r.year0),"year1":int(r.year1),"year2":int(r.year2),
                "dt01":int(r.dt01),"dt12":int(r.dt12)})
    d=pd.DataFrame(rows)
    audit.update({"qualified_complementary_triples":len(q),"undefined_stability_excluded":undefined,"few_adult_species_excluded":few,
                  "forecast_plots":int(d["plot"].nunique()) if len(d) else 0,"rows":len(d)})
    print("STATE",json.dumps(audit),flush=True)
    return d,audit


def summarize(a):
    mods=["A","S","H","E","L"]
    cols=["weight"]+mods
    d=a.copy()
    for k in mods:d[k]=d[k]*d.weight
    b=d.groupby(["block","stable"],as_index=False)[cols].sum()
    wide=b.set_index(["block","stable"]).unstack(fill_value=0)
    if not all((c,st) in wide for c in cols for st in (True,False)):
        return {"status":"unresolved_missing_stability_class"},b
    arr=np.array([[wide[(c,st)].to_numpy() for c in cols] for st in (True,False)])
    ix=np.random.default_rng(284227).integers(0,arr.shape[2],(1000,arr.shape[2]))
    sample=arr[:,:,ix].sum(axis=-1)
    point=arr.sum(axis=-1)
    point=np.concatenate([point,point.sum(axis=0,keepdims=True)],axis=0)
    sample=np.concatenate([sample,sample.sum(axis=0,keepdims=True)],axis=0)
    def value(v,g,kind):
        n,a,b,h,e,l=v[g]
        if kind=="percent":den=a;num=100*(a-b)
        elif kind=="absolute":den=n;num=a-b
        elif kind=="history":den=b;num=100*(b-h)
        elif kind=="early_preference":den=a;num=100*(l-e)
        else:raise ValueError(kind)
        with np.errstate(divide="ignore",invalid="ignore"):
            return np.where(den>0,num/den,np.nan)
    def stat(v,w):
        w=np.asarray(w);ok=w[np.isfinite(w)]
        return {"estimate":float(v),"conditional_ci95":np.quantile(ok,[.025,.975]).tolist() if len(ok)>=800 and len(wide)>=8 else None,"valid_bootstraps":len(ok)}
    res={"status":"evaluated","plots":len(a),"blocks":len(wide),"groups":{},"contrasts":{}}
    for i,name in enumerate(("stable","changing","all")):
        res["groups"][name]={k:stat(value(point,i,k),value(sample,i,k)) for k in ("percent","absolute","history","early_preference")}
    for k in ("percent","absolute"):
        res["contrasts"]["changing_minus_stable_"+k]=stat(value(point,1,k)-value(point,0,k),value(sample,1,k)-value(sample,0,k))
    return res,b

def analyze(d,out):
    d=d.sort_values(["plot","sp"]).reset_index(drop=True)
    assert not d.duplicated(["plot","sp"]).any()
    a=d[["plot","block","state","stable","total_adult","richness","mean_adult_dia","prior_turnover","dt01","dt12"]].drop_duplicates("plot").copy()
    r={"plots":len(a),"rows":len(d),"species_codes":sorted(map(str,d.sp.unique())),"stable_plots":int(a.stable.sum()),"changing_plots":int((~a.stable).sum()),"median_interval":float(a.dt12.median()),"state_plot_counts":a.state.value_counts().to_dict()}
    z,t=s.fit_cv(d,"short",MODELS)
    if z is None:
        r.update({"status":"unresolved_forecast_support","failed_fit":t});return r
    assert len(z)==len(d) and z[["plot","sp"]].equals(d[["plot","sp"]])
    cols=[f"err_{m}" for m in MODELS]
    losses=z.groupby("plot",as_index=False)[cols].mean().rename(columns={f"err_{m}":m for m in MODELS})
    a=a.merge(losses,on="plot",validate="one_to_one");a["weight"]=1.
    r["fit"]={"folds":t["folds"],"metrics":s.metrics(z,[("zero","A"),("A","S"),("S","H"),("A","E"),("A","L")]),"stock_coefficients":{k:v for k,v in t["fold_coefficients_unscaled"]["S"].items() if k in s.STOCK}}
    r["unmatched"],b=summarize(a);b.to_csv(out/"unmatched_block_loss_sums.csv",index=False)
    try:
        diff=f.honest_difficulty(d,z);a=a.merge(diff,on="plot",validate="one_to_one")
        m,info=f.match_weights(a);r["matching"]=info
        if m is not None:
            r["matched"],b=summarize(m);b.to_csv(out/"matched_block_loss_sums.csv",index=False)
    except ValueError as e:
        r["matching"]={"status":"unresolved_difficulty_support","reason":str(e)}
    r["status"]="complementary_three_census_evaluated";return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--region",choices=REGIONS,required=True);ap.add_argument("--data",type=pathlib.Path,required=True);ap.add_argument("--out",type=pathlib.Path,required=True);a=ap.parse_args()
    a.data.mkdir(parents=True,exist_ok=True);a.out.mkdir(parents=True,exist_ok=True)
    pins=json.loads((ROOT/"config/stage_forecast_four_census_sources_sha256_v1.json").read_text())
    urls=[(f"{p.BASE}{st}_{t}.zip",a.data/f"{st}_{t}.zip") for st in REGIONS[a.region] for t in s.TABLES]
    prov={}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for (_,path),rec in zip(urls,ex.map(lambda u:p.acquire(*u),urls)):
            if rec["sha256"]!=pins[path.name]["sha256"] or rec["bytes"]!=pins[path.name]["bytes"]:
                raise ValueError("SOURCE_VERSION_CHANGED "+path.name)
            prov[path.name]=rec
            print("VERIFIED",path.name,rec["sha256"],rec["bytes"],flush=True)
    (a.out/"provenance.json").write_text(json.dumps(prov,indent=2)+"\n")
    items=[state_data(a.data,st) for st in REGIONS[a.region]]
    d=pd.concat([i[0] for i in items],ignore_index=True)
    r={"schema":"284b.stage_complementary_three_census.v1","region":a.region,"states":list(REGIONS[a.region]),"source_files_verified":len(prov),"state_audits":[x[1] for x in items],"new_confirmatory_endpoints":0}
    if len(d):r.update(analyze(d,a.out))
    else:r["status"]="unresolved_no_complementary_triples"
    r["boundary"]="Post-four-census protocol, disjoint plot keys, exact source pins. Short-horizon only. Conditional predictive comparison, not mechanism or long-horizon rescue."
    (a.out/"summary.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n")
    print("RESULT_JSON",json.dumps(r,allow_nan=False),flush=True)
if __name__=="__main__":main()
