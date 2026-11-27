#!/usr/bin/env python3
"""Geographic extension: balanced four-census FIA stage forecasts."""
import argparse, hashlib, json, math, pathlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import niche_demographic_divergence_fia_pilot as p
import stage_structured_fia_forecast as s

REGIONS={"central_hardwoods":("OH","IN","IL"),"southern_uplands":("KY","TN","NC")}
MODELS={"A":s.BASE_FEATURES,"S":s.BASE_FEATURES+s.STOCK,
        "H":s.BASE_FEATURES+s.STOCK+s.HISTORY,
        "E":s.BASE_FEATURES+["early_stock"],"L":s.BASE_FEATURES+["late_stock"]}
HORIZONS=("short","delayed","cumulative")

def quads(v):
    # Exact previous-visit identifiers plus immutable physical plot key.
    q=v[(v.arm==1)&v.year.between(2004,2012)][["CN","key","year"]].rename(columns={"CN":"t0","year":"year0"})
    for k in (1,2,3):
        x=v[v.arm==1][["CN","key","year","PREV_PLT_CN"]].rename(columns={"CN":f"t{k}","year":f"year{k}","PREV_PLT_CN":f"prev{k}"})
        if k==1:
            x=x.merge(v[["CN","LAT","LON"]],left_on="t1",right_on="CN",validate="one_to_one").drop(columns="CN")
        q=q.merge(x,left_on=["key",f"t{k-1}"],right_on=["key",f"prev{k}"],how="inner")
        q[f"dt{k-1}{k}"]=q[f"year{k}"]-q[f"year{k-1}"]
        q=q[q[f"dt{k-1}{k}"].between(4,8)].copy()
    q=q.sort_values(["year0","year1","year2","year3","t0","t1","t2","t3"]).drop_duplicates("key")
    assert q.year3.le(2024).all() and not q.key.duplicated().any()
    for k in (1,2,3):assert q[f"t{k-1}"].eq(q[f"prev{k}"]).all()
    return q

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
    q=quads(v)
    needed=set().union(*(set(q[f"t{k}"]) for k in range(4)))
    trees=trees[trees.PLT_CN.isin(needed)&trees.stage.isin(["adult","early","late"])].copy()
    by=s.count_maps(trees)
    def adults(visit):return {a:x["adult"][0] for a,x in by.get(visit,{}).items() if "adult" in x}
    def nstage(v,sp,stage):return by.get(v,{}).get(sp,{}).get(stage,(0,0,0))[0]
    rows=[];undefined=0;few=0
    for r in q.itertuples(index=False):
        adult=[adults(getattr(r,f"t{k}")) for k in range(4)]
        tv=s.tv(adult[0],adult[1])
        if not np.isfinite(tv):undefined+=1;continue
        eligible=sorted(sp for sp,n in adult[1].items() if n>=2)
        if len(eligible)<2:few+=1;continue
        total=sum(adult[1].values());den=math.log1p(total)
        dia=sum(x["adult"][1] for x in by[r.t1].values() if "adult" in x)/total
        block=f"{math.floor(r.LAT)}|{math.floor(r.LON)}"
        fold=int(hashlib.sha256(block.encode()).hexdigest()[:8],16)%5
        for sp in eligible:
            n0,n1,n2,n3=[x.get(sp,0) for x in adult]
            x0,x1,x2,x3=[math.log(n+.5) for n in (n0,n1,n2,n3)]
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
                "short":(x2-x1)*5/r.dt12,"delayed":(x3-x2)*5/r.dt23,
                "cumulative":(x3-x1)*5/(r.dt12+r.dt23),
                "year0":int(r.year0),"year1":int(r.year1),"year2":int(r.year2),"year3":int(r.year3),
                "dt01":int(r.dt01),"dt12":int(r.dt12),"dt23":int(r.dt23)})
    d=pd.DataFrame(rows)
    audit.update({"qualified_quads":len(q),"undefined_stability_excluded":undefined,"few_adult_species_excluded":few,
                  "forecast_plots":int(d["plot"].nunique()) if len(d) else 0,"rows":len(d)})
    print("STATE",json.dumps(audit),flush=True)
    return d,audit

def ridge(X,y,w,train,test):
    total=w[train].sum()
    if total<30:raise ValueError("insufficient nested training support")
    x=X[train];ww=w[train]
    scale=np.sqrt((x*x*ww[:,None]).sum(axis=0)/total);scale=np.where(scale>1e-9,scale,1.)
    x=x/scale
    beta=np.linalg.solve((x*ww[:,None]).T@x+np.eye(x.shape[1])*.01*total,(x*ww[:,None]).T@y[train])
    return (X[test]/scale)@beta

def honest_difficulty(d,short):
    # Outer test outcomes cannot enter model or difficulty estimate. Inner training errors are OOF.
    sp=pd.get_dummies(d.sp,dtype=float)
    X=np.column_stack([s.center_frame(d,s.BASE_FEATURES),(sp-sp.groupby(d["plot"]).transform("mean")).to_numpy()])
    y=s.center_frame(d,["short"]).ravel()
    w=1/d.groupby("plot").short.transform("size").to_numpy()
    assert d[["plot","sp"]].equals(short[["plot","sp"]])
    if d.fold.nunique()!=5:raise ValueError("difficulty requires all five folds")
    results=[]
    for fold in sorted(d.fold.unique()):
        test=d.fold.eq(fold).to_numpy();train=~test
        a=ridge(X,y,w,train,test)
        assert np.allclose(a,short.loc[test,"pred_A"],atol=1e-10,rtol=0)
        inner=np.full(len(d),np.nan)
        for j in sorted(d.loc[train,"fold"].unique()):
            val=train&d.fold.eq(j).to_numpy();fit=train&~val
            inner[val]=ridge(X,y,w,fit,val)
        assert np.isfinite(inner[train]).all()
        def aggregate(mask,forecast,training):
            z=d.loc[mask,["plot","total_adult","richness","mean_adult_dia","prior_turnover"]].copy()
            z["amp2"]=forecast**2
            if training:z["err2"]=(y[mask]-forecast)**2
            ag={k:"first" for k in ("total_adult","richness","mean_adult_dia","prior_turnover")}
            ag["amp2"]="mean"
            if training:ag["err2"]="mean"
            return z.groupby("plot").agg(ag)
        tr=aggregate(train,inner[train],True);te=aggregate(test,a,False)
        def features(x):
            return np.column_stack([np.log1p(x.total_adult),np.log1p(x.richness),np.log(x.mean_adult_dia),
                                    x.prior_turnover,np.sqrt(x.amp2)])
        f=features(tr);g=features(te);mu=f.mean(axis=0);sd=f.std(axis=0);sd=np.where(sd>1e-9,sd,1.)
        f=(f-mu)/sd;g=(g-mu)/sd
        target=np.log(tr.err2.to_numpy()+1e-4);intercept=target.mean()
        beta=np.linalg.solve(f.T@f+np.eye(f.shape[1])*.01*len(f),f.T@(target-intercept))
        te["pred_log_difficulty"]=intercept+g@beta
        results.append(te[["pred_log_difficulty"]].reset_index())
    r=pd.concat(results,ignore_index=True)
    assert r["plot"].is_unique and len(r)==d["plot"].nunique()
    return r

def match_weights(a):
    # a contains one row per plot. No realized future losses used for binning.
    a=a.copy()
    for k,n in (("pred_log_difficulty",3),("total_adult",3),("mean_adult_dia",2)):
        edges=np.unique(np.quantile(a[k],np.linspace(0,1,n+1)))
        if len(edges)!=n+1:return None,{"status":"unresolved_tied_quantile_edges","variable":k}
        edges[0]=-np.inf;edges[-1]=np.inf
        a[k+"_bin"]=pd.cut(a[k],edges,labels=False,include_lowest=True)
    bins=["pred_log_difficulty_bin","total_adult_bin","mean_adult_dia_bin"]
    cnt=a.groupby(bins+["stable"],observed=True).size().unstack(fill_value=0).reindex(columns=[False,True],fill_value=0)
    good=cnt[(cnt[False]>=10)&(cnt[True]>=10)]
    if good.empty:return None,{"status":"unresolved_no_common_strata"}
    weights=good.stack().rename("class_n").reset_index()
    mn=good.min(axis=1).rename("common_n").reset_index()
    weights=weights.merge(mn,on=bins,validate="many_to_one")
    a=a.merge(weights,on=bins+["stable"],how="inner",validate="many_to_one")
    a["weight"]=a.common_n/a.class_n
    info={"status":"matched","strata":len(good),"plots":len(a),"discarded_plots":int(cnt.to_numpy().sum()-len(a)),"groups":{},"weighted_mean_covariates":{}}
    for st,g in a.groupby("stable"):
        name="stable" if st else "changing";w=g.weight.to_numpy()
        info["groups"][name]={"plots":len(g),"sum_weights":float(w.sum()),"effective_n":float(w.sum()**2/(w@w))}
        info["weighted_mean_covariates"][name]={k:float(np.average(g[k],weights=w)) for k in ("pred_log_difficulty","total_adult","mean_adult_dia","richness","prior_turnover")}
    return a,info

def block_summary(a):
    # Fixed weights; jointly resample blocks across all horizons and both groups.
    cols=[f"{h}_{m}" for h in HORIZONS for m in ("A","S","H","E","L")]
    d=a.copy()
    for c in cols:d[c]=d[c]*d.weight
    b=d.groupby(["block","stable"],as_index=False)[["weight"]+cols].sum()
    wide=b.set_index(["block","stable"]).unstack(fill_value=0)
    if not all((c,st) in wide for c in ["weight"]+cols for st in (True,False)):
        return {"status":"unresolved_missing_stability_class"},b
    arr=np.array([[wide[(c,st)].to_numpy() for c in ["weight"]+cols] for st in (True,False)])
    # shape [stratum, loss, spatial block], one set of resamples for every contrast
    idx=np.random.default_rng(284227).integers(0,arr.shape[2],(1000,arr.shape[2]))
    sampled=arr[:,:,idx].sum(axis=-1)
    point=arr.sum(axis=-1)
    allpoint=point.sum(axis=0,keepdims=True);allsamp=sampled.sum(axis=0,keepdims=True)
    point=np.concatenate([point,allpoint],axis=0);sampled=np.concatenate([sampled,allsamp],axis=0)
    def vals(mat,g,h,kind):
        a=mat[g,1+cols.index(h+"_A")];ss=mat[g,1+cols.index(h+"_S")]
        n=mat[g,0]
        if kind=="percent":den=a;num=100*(a-ss)
        elif kind=="absolute":den=n;num=a-ss
        elif kind=="early_preference":den=a;num=100*(mat[g,1+cols.index(h+"_L")]-mat[g,1+cols.index(h+"_E")])
        elif kind=="history":den=ss;num=100*(ss-mat[g,1+cols.index(h+"_H")])
        else:raise ValueError(kind)
        with np.errstate(divide="ignore",invalid="ignore"):return np.where(den>0,num/den,np.nan)
    def stat(v,w):
        finite=np.asarray(w)[np.isfinite(w)]
        return {"estimate":float(v),"conditional_ci95":np.quantile(finite,[.025,.975]).tolist() if len(finite)>=800 and len(wide)>=8 else None,
                "valid_bootstraps":len(finite)}
    out={"status":"evaluated","plots":len(a),"blocks":len(wide),"groups":{},"contrasts":{}}
    for g,name in enumerate(("stable","changing","all")):
        out["groups"][name]={}
        for h in HORIZONS:
            out["groups"][name][h]={kind:stat(vals(point,g,h,kind),vals(sampled,g,h,kind)) for kind in ("percent","absolute","early_preference","history")}
        for kind in ("percent","early_preference"):
            out["contrasts"][name+"_delayed_minus_short_"+kind]=stat(vals(point,g,"delayed",kind)-vals(point,g,"short",kind),vals(sampled,g,"delayed",kind)-vals(sampled,g,"short",kind))
            out["contrasts"][name+"_cumulative_minus_short_"+kind]=stat(vals(point,g,"cumulative",kind)-vals(point,g,"short",kind),vals(sampled,g,"cumulative",kind)-vals(sampled,g,"short",kind))
    for h in HORIZONS:
        for kind in ("percent","absolute"):
            out["contrasts"][h+"_changing_minus_stable_"+kind]=stat(vals(point,1,h,kind)-vals(point,0,h,kind),vals(sampled,1,h,kind)-vals(sampled,0,h,kind))
    return out,b

def analyze(d,out):
    d=d.sort_values(["plot","sp"]).reset_index(drop=True)
    assert not d.duplicated(["plot","sp"]).any()
    assert d.groupby("plot").sp.transform("size").ge(2).all()
    plotcols=["plot","block","state","stable","total_adult","richness","mean_adult_dia","prior_turnover","dt01","dt12","dt23","year1","year3"]
    a=d[plotcols].drop_duplicates("plot").copy()
    res={"plots":len(a),"rows":len(d),"species_codes":sorted(map(str,d.sp.unique())),"state_plot_counts":a.state.value_counts().to_dict(),
         "stable_plots":int(a.stable.sum()),"changing_plots":int((~a.stable).sum()),
         "median_years":{"short":float(a.dt12.median()),"delayed":float(a.dt23.median()),"cumulative":float((a.dt12+a.dt23).median())},
         "range_years":{"short":[int(a.dt12.min()),int(a.dt12.max())],"delayed":[int(a.dt23.min()),int(a.dt23.max())],"cumulative":[int((a.dt12+a.dt23).min()),int((a.dt12+a.dt23).max())]},"fits":{}}
    short=None
    for h in HORIZONS:
        z,t=s.fit_cv(d,h,MODELS)
        if z is None:
            res["status"]="unresolved_forecast_support";res["failed_fit"]=t;return res
        assert len(z)==len(d) and z[["plot","sp"]].equals(d[["plot","sp"]])
        if h=="short":short=z
        loss=[f"err_{m}" for m in ("A","S","H","E","L")]
        l=z.groupby("plot",as_index=False)[loss].mean().rename(columns={f"err_{m}":f"{h}_{m}" for m in ("A","S","H","E","L")})
        a=a.merge(l,on="plot",validate="one_to_one")
        res["fits"][h]={"status":t["status"],"folds":t["folds"],"stock_coefficients":{k:v for k,v in t["fold_coefficients_unscaled"]["S"].items() if k in s.STOCK},
                        "metrics":s.metrics(z,[("zero","A"),("A","S"),("S","H"),("A","E"),("A","L")])}
    a["weight"]=1.
    res["unmatched"],b=block_summary(a)
    b.to_csv(out/"unmatched_block_loss_sums.csv",index=False)
    try:
        dif=honest_difficulty(d,short);a=a.merge(dif,on="plot",validate="one_to_one")
        m,info=match_weights(a);res["matching"]=info
        if m is not None:
            res["matched"],b=block_summary(m)
            b.to_csv(out/"matched_block_loss_sums.csv",index=False)
    except ValueError as e:
        res["matching"]={"status":"unresolved_difficulty_support","reason":str(e)}
    res["status"]="four_census_evaluated"
    return res

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--region",choices=REGIONS,required=True);ap.add_argument("--data",type=pathlib.Path,required=True);ap.add_argument("--out",type=pathlib.Path,required=True);args=ap.parse_args()
    args.data.mkdir(parents=True,exist_ok=True);args.out.mkdir(parents=True,exist_ok=True)
    states=REGIONS[args.region]
    urls=[(f"{p.BASE}{st}_{t}.zip",args.data/f"{st}_{t}.zip") for st in states for t in s.TABLES]
    prov={}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for (_,f),rec in zip(urls,ex.map(lambda u:p.acquire(*u),urls)):
            prov[f.name]=rec;print("ACQUIRED",f.name,rec["sha256"],rec["bytes"],flush=True)
    (args.out/"provenance.json").write_text(json.dumps(prov,indent=2)+"\n")
    items=[state_data(args.data,st) for st in states]
    d=pd.concat([x[0] for x in items],ignore_index=True)
    r={"schema":"284b.fia_four_census_forecast.v1","region":args.region,"states":list(states),"source_files":len(prov),"state_audits":[x[1] for x in items],"new_confirmatory_endpoints":0}
    if len(d):r.update(analyze(d,args.out))
    else:r["status"]="unresolved_no_eligible_quads"
    r["boundary"]="Spatially held-out regional forecast, fixed size classes and future complete census support. No climate causation, full recruitment decomposition, or independent field network."
    (args.out/"summary.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n")
    print("RESULT_JSON",json.dumps(r,allow_nan=False),flush=True)
if __name__=="__main__":main()
