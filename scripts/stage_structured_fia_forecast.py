#!/usr/bin/env python3
"""Three-census stage-specific forecasts on previously hash-pinned FIA archives."""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, zipfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import niche_demographic_divergence_fia_pilot as p

ROOT=pathlib.Path(__file__).resolve().parents[1]
REGIONS={"northeast":("ME","NH","VT"),"appalachia":("PA","WV","VA"),"great_lakes":("MI","WI","MN")}
TABLES={**p.TABLES}
TABLES["COND"]=p.TABLES["COND"]+["MICRPROP_UNADJ","SUBPPROP_UNADJ"]
TABLES["TREE"]=p.TABLES["TREE"]+["PREV_TRE_CN"]
IDCOLS=set(p.IDS)|{"PREV_TRE_CN"}
BASE_FEATURES=["adult_log","adult_past","diameter_log","small_adult_fraction","density_x_adult","density_x_past"]
STOCK=["early_stock","late_stock"]
HISTORY=["early_history","late_history"]
MODELS={
    "A":BASE_FEATURES,
    "S":BASE_FEATURES+STOCK,
    "H":BASE_FEATURES+STOCK+HISTORY,
    "E":BASE_FEATURES+["early_stock","early_history"],
    "L":BASE_FEATURES+["late_stock","late_history"],
}

def read(root, state, table):
    with zipfile.ZipFile(root/f"{state}_{table}.zip") as z:
        n=[n for n in z.namelist() if pathlib.Path(n).name.upper()==f"{state}_{table}.CSV"]
        if len(n)!=1:raise ValueError(("archive schema",state,table))
        cols=TABLES[table]
        with z.open(n[0]) as f:
            d=pd.read_csv(f,usecols=cols,dtype={k:"string" for k in cols if k in IDCOLS},low_memory=False)
    return d

def stage_of(t):
    live=t.STATUSCD.eq(1)
    adult=live&t.DIA.ge(5)&np.isclose(t.TPA_UNADJ,6.018046,atol=.02)
    early=live&t.DIA.ge(1)&t.DIA.lt(3)&np.isclose(t.TPA_UNADJ,74.965282,atol=.02)
    late=live&t.DIA.ge(3)&t.DIA.lt(5)&np.isclose(t.TPA_UNADJ,74.965282,atol=.02)
    return np.select([adult,early,late],["adult","early","late"],default="other")

def triples_from(v):
    base=v[(v.arm==1)&v.year.between(2004,2012)][["CN","key","year"]].rename(columns={"CN":"t0","year":"year0"})
    middle=v[v.arm==1][["CN","key","year","PREV_PLT_CN","LAT","LON"]].rename(columns={"CN":"t1","year":"year1","PREV_PLT_CN":"prev0"})
    end=v[v.arm==1][["CN","key","year","PREV_PLT_CN"]].rename(columns={"CN":"t2","year":"year2","PREV_PLT_CN":"prev1"})
    t=base.merge(middle,left_on=["key","t0"],right_on=["key","prev0"]).merge(end,left_on=["key","t1"],right_on=["key","prev1"])
    t["dt01"]=t.year1-t.year0;t["dt12"]=t.year2-t.year1
    t=t[t.dt01.between(4,8)&t.dt12.between(4,8)].sort_values(["year0","year1","year2","t0","t1","t2"]).drop_duplicates("key").copy()
    assert not t.key.duplicated().any()
    assert t.year2.le(2024).all()
    return t

def count_maps(live):
    # one entry per sampled stem, within a fixed expansion-factor class
    live=live.copy()
    live["small_adult"]=(live.stage.eq("adult")&live.DIA.lt(10)).astype(int)
    x=live.groupby(["PLT_CN","sp","stage"],as_index=False).agg(n=("CN","size"),dia_sum=("DIA","sum"),small=("small_adult","sum"))
    by={}
    for r in x.itertuples(index=False):
        by.setdefault(r.PLT_CN,{}).setdefault(r.sp,{})[r.stage]=(int(r.n),float(r.dia_sum),int(r.small))
    return by

def linked_tallies(trees,tr):
    # Unlinked and ambiguous old adults must not be coded as dead.
    old=trees[trees.PLT_CN.isin(tr.t1)][["CN","PLT_CN","sp","SUBP","stage","STATUSCD"]].merge(tr[["t1","t2"]],left_on="PLT_CN",right_on="t1",validate="many_to_one")
    nxt=trees[trees.PLT_CN.isin(tr.t2)&trees.PREV_TRE_CN.notna()][["CN","PLT_CN","PREV_TRE_CN","sp","SUBP","stage","STATUSCD"]].merge(tr[["t1","t2"]],left_on="PLT_CN",right_on="t2",validate="many_to_one")
    ambiguous=nxt.duplicated(["t1","PREV_TRE_CN"],keep=False)
    namb=int(ambiguous.sum());nxt=nxt[~ambiguous]
    j=nxt.merge(old,left_on=["t1","t2","PREV_TRE_CN"],right_on=["t1","t2","CN"],suffixes=("_2","_1"),validate="one_to_one")
    same=j.sp_2.notna()&j.sp_1.notna()&j.sp_2.eq(j.sp_1)&j.SUBP_2.eq(j.SUBP_1)
    j=j[same]
    promoted=j[j.stage_1.isin(["early","late"])&j.stage_2.eq("adult")]
    pp=promoted.groupby(["t1","sp_1"]).size().to_dict()
    oldadult=j[j.stage_1.eq("adult")&j.STATUSCD_2.isin([1,2,3])].copy()
    oldadult["loss"]=oldadult.STATUSCD_2.isin([2,3]).astype(int)
    l=oldadult.groupby(["t1","sp_1"]).agg(linked=("loss","size"),loss=("loss","sum"))
    loss={k:(int(row.linked),int(row.loss)) for k,row in l.iterrows()}
    return pp,loss,{"ambiguous_later_links":namb,"identified_promoted_stems":len(promoted),"identified_baseline_adult_statuses":len(oldadult)}

def tv(a,b):
    sa=sum(a.values());sb=sum(b.values())
    if sa==0 or sb==0:return np.nan
    return .5*sum(abs(a.get(k,0)/sa-b.get(k,0)/sb) for k in set(a)|set(b))

def make_rows(tr, by, pp, loss, climate, state):
    rows=[];used=0
    def stagecount(visit,sp,stage):return by.get(visit,{}).get(sp,{}).get(stage,(0,0,0))[0]
    def adults(visit):
        return {sp:v["adult"][0] for sp,v in by.get(visit,{}).items() if "adult" in v}
    for r in tr.itertuples(index=False):
        aa=adults(r.t0);bb=adults(r.t1);cc=adults(r.t2)
        eligible=sorted(sp for sp,n in bb.items() if n>=2)
        if len(eligible)<2:continue
        used+=1
        stable=tv(aa,bb)
        den=math.log1p(sum(bb.values()))
        block=f"{math.floor(r.LAT)}|{math.floor(r.LON)}"
        fold=int(hashlib.sha256(block.encode()).hexdigest()[:8],16)%5
        for sp in eligible:
            n0,n1,n2=aa.get(sp,0),bb[sp],cc.get(sp,0)
            e0,e1=[stagecount(v,sp,"early") for v in (r.t0,r.t1)]
            l0,l1=[stagecount(v,sp,"late") for v in (r.t0,r.t1)]
            prom=pp.get((r.t1,sp),0)
            assert 0<=prom<=n2
            known,dead=loss.get((r.t1,sp),(0,0))
            assert 0<=dead<=known<=n1
            alog=math.log(n1+.5);past=(alog-math.log(n0+.5))*5/r.dt01
            n,dia,small=by[r.t1][sp]["adult"]
            assert n==n1
            rows.append({
                "plot":r.key,"sp":sp,"state":state,"block":block,"fold":fold,
                "year0":int(r.year0),"year1":int(r.year1),"year2":int(r.year2),
                "stable":bool(np.isfinite(stable) and stable<=.10),"prior_turnover":float(stable),
                "adult_log":alog,"adult_past":past,"diameter_log":math.log(dia/n),
                "small_adult_fraction":small/n,"density_x_adult":den*alog,"density_x_past":den*past,
                "early_stock":math.log1p(e1),"late_stock":math.log1p(l1),
                "early_history":(math.log1p(e1)-math.log1p(e0))*5/r.dt01,
                "late_history":(math.log1p(l1)-math.log1p(l0))*5/r.dt01,
                "future":(math.log(n2+.5)-alog)*5/r.dt12,
                "future_without_identified_promotions":(math.log(n2-prom+.5)-alog)*5/r.dt12,
                "linked_loss":dead/n1 if known==n1 else np.nan,
                "n0":n0,"n1":n1,"n2":n2,"promotions":prom,
                "known_old_status":known,"linked_dead_removed":dead,
                "bin":climate.get(r.t1,None)
            })
    return pd.DataFrame(rows),used

def climate_bins(pframe,root):
    q=p.climate_frame(pframe.copy(),root/"climate.zip")
    return dict(zip(q.CN,np.floor(q.mat/2).astype(int).astype(str)+"|"+np.floor(q["map"]/200).astype(int).astype(str)))

def state_data(root,state):
    v=read(root,state,"PLOT")
    if v.CN.duplicated().any():raise ValueError("duplicate plot visit CN")
    v=v.dropna(subset=["CN","STATECD","UNITCD","COUNTYCD","PLOT","LAT","LON","MEASYEAR"]).copy()
    v["key"]=p.physical(v);v["year"]=v.MEASYEAR;v["arm"]=v.key.map(p.arm)
    v=v[v.year.between(2004,2024)&v.PLOT_STATUS_CD.eq(1)&v.DESIGNCD.eq(1)].copy()
    audit={"state":state,"design_eligible_visits":len(v)}
    cond=read(root,state,"COND")
    cond=cond[cond.PLT_CN.isin(v.CN)].copy()
    cond["valid"]=cond.COND_STATUS_CD.eq(1)&np.isclose(cond.CONDPROP_UNADJ,1,atol=1e-6)&np.isclose(cond.MICRPROP_UNADJ,1,atol=1e-6)&np.isclose(cond.SUBPPROP_UNADJ,1,atol=1e-6)&cond[["TRTCD1","TRTCD2","TRTCD3"]].fillna(0).eq(0).all(axis=1)
    good=cond.groupby("PLT_CN").agg(n=("valid","size"),ok=("valid","all"))
    v=v[v.CN.isin(good[(good.n==1)&good.ok].index)]
    sub=read(root,state,"SUBPLOT")
    sub=sub[sub.PLT_CN.isin(v.CN)&sub.SUBP.isin([1,2,3,4])].copy()
    sub["valid"]=sub.SUBP_STATUS_CD.eq(1)
    s=sub.groupby("PLT_CN").agg(n=("SUBP","size"),unique=("SUBP","nunique"),ok=("valid","all"))
    v=v[v.CN.isin(s[(s.n==4)&(s.unique==4)&s.ok].index)].copy()
    audit["complete_area_visits"]=len(v)
    trees=read(root,state,"TREE")
    trees=trees[trees.PLT_CN.isin(v.CN)].copy()
    if trees.CN.duplicated().any() or trees.CN.isna().any():raise ValueError("duplicate or missing tree CN")
    sp=pd.to_numeric(trees.SPCD,errors="coerce")
    trees["sp"]=sp.where(sp.notna()&sp.gt(0)&sp.eq(np.floor(sp))).astype("Int64").astype("string")
    trees["stage"]=stage_of(trees)
    live=trees.STATUSCD.eq(1)
    bad=live&(trees.sp.isna()|~trees.SUBP.isin([1,2,3,4])|trees.stage.eq("other"))
    bad=bad|trees.STATUSCD.isna()
    badvis=set(trees.loc[bad,"PLT_CN"])
    v=v[~v.CN.isin(badvis)].copy()
    audit["invalid_live_or_missing_status_visits_excluded"]=len(badvis)
    audit["valid_visits"]=len(v)
    ref=v[(v.arm==0)&v.year.between(2004,2012)].sort_values(["year","CN"]).drop_duplicates("key").copy()
    tr=triples_from(v);tr["state"]=state
    assert not set(ref.key)&set(tr.key)
    needed=set(ref.CN)|set(tr.t0)|set(tr.t1)|set(tr.t2)
    trees=trees[trees.PLT_CN.isin(needed)].copy()
    live=trees[trees.stage.isin(["early","late","adult"])].copy()
    by=count_maps(live)
    pp,loss,linkaudit=linked_tallies(trees,tr)
    clim=climate_bins(v[v.CN.isin(set(ref.CN)|set(tr.t1))][["CN","LAT","LON"]],root)
    rows,used=make_rows(tr,by,pp,loss,clim,state)
    ref=ref[["CN","key"]].copy()
    ref["bin"]=ref.CN.map(clim)
    ref=ref[ref.bin.notna()]
    rdata=[]
    for r in ref.itertuples(index=False):
        for sp,x in by.get(r.CN,{}).items():
            rdata.append((r.CN,sp,r.bin,int("adult" in x),int("early" in x or "late" in x)))
    rdf=pd.DataFrame(rdata,columns=["CN","sp","bin","adult","juvenile"])
    audit.update({"reference_plots_with_climate":len(ref),"forecast_triples":len(tr),"eligible_forecast_plots":used,"species_plot_rows":len(rows),"adult_stems_t1":int(rows.n1.sum()) if len(rows) else 0,**linkaudit})
    print("STATE",json.dumps(audit),flush=True)
    return rows,ref,rdf,audit

def eligible_rows(df,outcome):
    x=df[np.isfinite(pd.to_numeric(df[outcome],errors="coerce"))].copy()
    n=x.groupby("plot")[outcome].transform("size")
    return x[n>=2].reset_index(drop=True)

def center_frame(df,features):
    f=df[features].astype(float)
    return (f-f.groupby(df["plot"]).transform("mean")).to_numpy()

def fit_cv(d,outcome,models):
    # Model comparisons on the exact same rows; no fold or hyperparameter tuning.
    d=eligible_rows(d,outcome)
    if len(d)<100 or d["plot"].nunique()<50 or d.block.nunique()<8 or d.fold.nunique()<3:
        return None,{"status":"unresolved_support","rows":len(d),"plots":int(d["plot"].nunique()),"blocks":int(d.block.nunique())}
    sp=pd.get_dummies(d.sp,dtype=float)
    sp=(sp-sp.groupby(d["plot"]).transform("mean")).to_numpy()
    y=center_frame(d,[outcome]).ravel()
    w=1/d.groupby("plot")[outcome].transform("size").to_numpy()
    assert np.allclose(pd.Series(w).groupby(d["plot"]).sum(),1)
    pred={"zero":np.zeros(len(d))}
    coef={k:[] for k in models}
    for name,features in models.items():
        X=np.column_stack([center_frame(d,features),sp])
        if not np.isfinite(X).all():raise ValueError("nonfinite model features")
        result=np.full(len(d),np.nan)
        for fold in sorted(d.fold.unique()):
            test=d.fold.eq(fold).to_numpy();train=~test
            assert not set(d.loc[train,"block"])&set(d.loc[test,"block"])
            wtr=w[train];total=wtr.sum()
            if total<30:return None,{"status":"unresolved_fold_training_support"}
            x=X[train]
            scale=np.sqrt((x*x*wtr[:,None]).sum(axis=0)/total)
            scale=np.where(scale>1e-9,scale,1)
            x=x/scale
            gram=(x*wtr[:,None]).T@x+np.eye(x.shape[1])*.01*total
            beta=np.linalg.solve(gram,(x*wtr[:,None]).T@y[train])
            result[test]=(X[test]/scale)@beta
            coef[name].append({f:float(b) for f,b in zip(features,beta[:len(features)]/scale[:len(features)])})
        assert np.isfinite(result).all()
        pred[name]=result
    z=d[["plot","state","block","fold","stable","sp"]].copy()
    z["y"]=y
    for name,x in pred.items():
        z["pred_"+name]=x
        z["err_"+name]=(y-x)**2
    co={k:{f:{"mean":float(np.mean([v[f] for v in arr])),"minimum":float(min(v[f] for v in arr)),"maximum":float(max(v[f] for v in arr))} for f in arr[0]} for k,arr in coef.items()}
    return z,{"status":"cross_validated_descriptive","species":int(d.sp.nunique()),"folds":int(d.fold.nunique()),"fold_coefficients_unscaled":co}

def metrics(z,comparisons):
    if z is None or len(z)==0:return {"status":"unresolved_no_rows"}
    cols=[x for x in z if x.startswith("err_")]
    a=z.groupby(["plot","block","state"],as_index=False)[cols].mean()
    out={"plots":len(a),"rows":len(z),"blocks":int(a.block.nunique()),"mean_squared_errors":{c[4:]:float(a[c].mean()) for c in cols},"comparisons":{}}
    blocks=a.groupby("block")
    sums=blocks[cols].sum()
    sizes=blocks.size().reindex(sums.index).to_numpy()
    rng=np.random.default_rng(284217)
    for base,model in comparisons:
        if "err_"+base not in cols or "err_"+model not in cols:continue
        x=out["mean_squared_errors"][base];y=out["mean_squared_errors"][model]
        r={"baseline_mse":x,"augmented_mse":y,"mse_reduction":x-y,"percent_reduction":100*(x-y)/x if x>0 else None}
        if len(sums)>=8:
            bx=sums["err_"+base].to_numpy();by=sums["err_"+model].to_numpy()
            i=rng.integers(0,len(sums),(500,len(sums)))
            sx=bx[i].sum(axis=1);sy=by[i].sum(axis=1);nn=sizes[i].sum(axis=1)
            r["conditional_block_bootstrap_95_mse_reduction"]=list(map(float,np.quantile((sx-sy)/nn,[.025,.975])))
            good=sx>0
            if good.sum()>=400:r["conditional_block_bootstrap_95_percent_reduction"]=list(map(float,np.quantile(100*(sx[good]-sy[good])/sx[good],[.025,.975])))
        out["comparisons"][base+"_to_"+model]=r
    return out

def stage_reference(ref,occ):
    valid=ref.bin.value_counts();bins=set(valid[valid>=10].index)
    ref=ref[ref.bin.isin(bins)]
    occ=occ[occ.CN.isin(ref.CN)]
    tot=occ.groupby("sp")[["adult","juvenile"]].sum()
    good=tot[(tot.adult>=40)&(tot.juvenile>=40)]
    occ=occ[occ.sp.isin(good.index)]
    by=occ.groupby(["sp","bin"])[["adult","juvenile"]].sum()
    scores={}
    for sp,row in good.iterrows():
        global_ratio=math.log((row.juvenile+.5)/(row.adult+.5))
        for b in bins:
            a,j=by.loc[(sp,b),["adult","juvenile"]] if (sp,b) in by.index else (0,0)
            scores[(sp,b)]=math.log((j+.5)/(a+.5))-global_ratio
    return scores,{"reference_plots":len(ref),"bins":len(bins),"species":len(good)}

def analyze(df,ref,occ,out):
    comparisons=[("zero","A"),("A","S"),("A","H"),("S","H"),("A","E"),("A","L"),("E","L")]
    z,s=fit_cv(df,"future",MODELS)
    result={"primary_fit":{k:v for k,v in s.items() if k!="fold_coefficients_unscaled"}}
    if z is None:return result
    result["primary"]=metrics(z,comparisons)
    result["stable_adult_subset"]=metrics(z[z.stable],comparisons)
    result["state_specific"]={state:metrics(g,[("A","H"),("S","H")]) for state,g in z.groupby("state")}
    result["mean_coef_H"]={k:v for k,v in s["fold_coefficients_unscaled"]["H"].items() if k in STOCK+HISTORY}
    result["cohort_accounting"]={
      "t1_eligible_adult_stems":int(df.n1.sum()),"t2_eligible_species_adult_stems":int(df.n2.sum()),
      "identified_sapling_promotions":int(df.promotions.sum()),"baseline_adults_with_explicit_later_status":int(df.known_old_status.sum()),
      "baseline_adults_dead_or_removed_explicitly":int(df.linked_dead_removed.sum()),
      "complete_link_species_plot_rows":int(df.linked_loss.notna().sum()),
      "stable_adult_plots":int(df.loc[df.stable,"plot"].nunique())}
    smaller={k:MODELS[k] for k in ("A","S","H")}
    for outcome in ("future_without_identified_promotions","linked_loss"):
        x,t=fit_cv(df,outcome,smaller)
        result[outcome]={"fit_status":t["status"],"metrics":metrics(x,[("A","S"),("A","H"),("S","H")])}
    scores,r=stage_reference(ref,occ)
    df=df.copy();df["climate_stage_mismatch"]=[scores.get((sp,b),np.nan) for sp,b in zip(df.sp,df.bin)]
    cx=df[df.climate_stage_mismatch.notna()].copy()
    x,t=fit_cv(cx,"future",{"H":MODELS["H"],"HC":MODELS["H"]+["climate_stage_mismatch"]})
    result["climate_stage_reference"]={"reference":r,"fit_status":t["status"],"metrics":metrics(x,[("H","HC")])}
    # Reusable audit: no identifiable plot keys, only region-level spatial blocks and state aggregation.
    cols=[c for c in z if c.startswith("err_")]
    perplot=z.groupby(["plot","block","state","stable"],as_index=False)[cols].mean()
    perplot.groupby(["block","state","stable"],as_index=False).agg(plots=("plot","size"),**{k:(k,"sum") for k in cols}).to_csv(out/"heldout_block_loss_sums.csv",index=False)
    z.groupby(["sp"],as_index=False).agg(rows=("y","size"),actual_mean=("y","mean"),adult_only_mse=("err_A","mean"),juvenile_history_mse=("err_H","mean")).to_csv(out/"taxon_descriptive_scores.csv",index=False)
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--region",choices=list(REGIONS),required=True);ap.add_argument("--data",type=pathlib.Path,required=True);ap.add_argument("--out",type=pathlib.Path,required=True);args=ap.parse_args()
    args.data.mkdir(parents=True,exist_ok=True);args.out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/"config/stage_structured_fia_sources_sha256_v1.json").read_text())
    states=REGIONS[args.region]
    sources=[(p.CLIMATE,args.data/"climate.zip")]+[(f"{p.BASE}{s}_{t}.zip",args.data/f"{s}_{t}.zip") for s in states for t in TABLES]
    prov={}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for (_,f),r in zip(sources,ex.map(lambda u:p.acquire(*u),sources)):
            if r["sha256"]!=manifest[f.name]:raise ValueError("SOURCE_VERSION_CHANGED "+f.name)
            prov[f.name]=r;print("VERIFIED_SOURCE",f.name,flush=True)
    (args.out/"provenance.json").write_text(json.dumps(prov,indent=2))
    items=[state_data(args.data,s) for s in states]
    df,ref,occ=[pd.concat([x[i] for x in items],ignore_index=True) for i in range(3)]
    if len(df)==0:raise RuntimeError("no eligible three-census data")
    assert not df.duplicated(["plot","sp"]).any()
    assert not set(ref.key)&set(df["plot"])
    result={"status":"exploratory_three_census_forecast","new_confirmatory_endpoints":0,"region":args.region,"hashes_verified":len(prov),"state_audits":[x[3] for x in items],"forecast_rows":len(df),"forecast_plots":int(df["plot"].nunique()),"forecast_species":int(df.sp.nunique()),"results":analyze(df,ref,occ,args.out),"limitations":"Size-class composition, not reproductive maturity or climate causation; count losses limited to explicit links; block bootstrap conditional on fitted predictors and regional species set."}
    (args.out/"summary.json").write_text(json.dumps(result,indent=2,allow_nan=False))
    print("RESULT_JSON",json.dumps(result,allow_nan=False),flush=True)
if __name__=="__main__":main()
