#!/usr/bin/env python3
"""Exploratory held-out FIA regional census test; no old 284b endpoints read."""
import argparse, hashlib, itertools, json, math, pathlib, zipfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import requests
import rasterio

STATES = ("ME", "NH", "VT")
BASE = "https://apps.fs.usda.gov/fia/datamart/CSV/"
CLIMATE = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip"
TABLES = {
    "PLOT": ["CN","PREV_PLT_CN","STATECD","UNITCD","COUNTYCD","PLOT","MEASYEAR","LAT","LON","PLOT_STATUS_CD","DESIGNCD"],
    "COND": ["PLT_CN","COND_STATUS_CD","CONDPROP_UNADJ","TRTCD1","TRTCD2","TRTCD3"],
    "SUBPLOT": ["PLT_CN","SUBP","SUBP_STATUS_CD"],
    "TREE": ["CN","PLT_CN","SUBP","STATUSCD","SPCD","DIA","TPA_UNADJ"],
}
IDS = {"CN","PREV_PLT_CN","PLT_CN","STATECD","UNITCD","COUNTYCD","PLOT","SPCD"}

def acquire(url, path):
    if not path.exists():
        tmp=path.with_suffix(".part")
        with requests.get(url,stream=True,timeout=(30,180),headers={"User-Agent":"284b research data provenance/1.0"}) as r:
            r.raise_for_status()
            with tmp.open("wb") as f:
                for chunk in r.iter_content(2**20):
                    f.write(chunk)
        tmp.replace(path)
    with zipfile.ZipFile(path) as z:
        if not z.namelist(): raise ValueError("empty archive")
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(2**20),b""): h.update(b)
    return {"url":url,"bytes":path.stat().st_size,"sha256":h.hexdigest()}

def read_table(path, table, state):
    with zipfile.ZipFile(path) as z:
        cand=[n for n in z.namelist() if pathlib.Path(n).name.upper()==f"{state}_{table}.CSV"]
        if len(cand)!=1: raise ValueError((path.name,"unexpected archive entries",z.namelist()[:5]))
        cols=TABLES[table]
        with z.open(cand[0]) as f:
            d=pd.read_csv(f,usecols=cols,dtype={c:"string" for c in cols if c in IDS},low_memory=False)
    return d

def physical(p):
    return p[["STATECD","UNITCD","COUNTYCD","PLOT"]].astype("string").agg("|".join,axis=1)

def arm(key):
    return int(hashlib.sha256(str(key).encode()).hexdigest()[:8],16)%2

def climate_frame(p, path):
    coords=list(zip(p.LON,p.LAT))
    for k,n in [(1,"mat"),(12,"map")]:
        with rasterio.open(f"zip://{path.resolve()}!wc2.1_10m_bio_{k}.tif") as src:
            assert src.crs.to_epsg()==4326
            ar=np.asarray([float(v[0]) if not np.ma.is_masked(v[0]) else np.nan for v in src.sample(coords,masked=True)])
            if src.nodata is not None: ar[np.isclose(ar,src.nodata)]=np.nan
        p[n]=ar
    valid=p.mat.between(-20,35)&p["map"].between(50,4000)
    return p.loc[valid].copy()

def state_data(state, root):
    paths={t:root/f"{state}_{t}.zip" for t in TABLES}
    p=read_table(paths["PLOT"],"PLOT",state)
    assert not p.CN.duplicated().any()
    p=p.dropna(subset=["CN","STATECD","UNITCD","COUNTYCD","PLOT","LAT","LON","MEASYEAR"]).copy()
    p["key"]=physical(p); p["state"]=state
    p["year"]=p.MEASYEAR
    p=p[p.year.between(2004,2024)&p.PLOT_STATUS_CD.eq(1)&p.DESIGNCD.eq(1)].copy()
    c=read_table(paths["COND"],"COND",state)
    c=c[c.PLT_CN.isin(p.CN)].copy()
    c["ok"]=c.COND_STATUS_CD.eq(1)&np.isclose(c.CONDPROP_UNADJ,1,atol=1e-6)&c[["TRTCD1","TRTCD2","TRTCD3"]].fillna(0).eq(0).all(axis=1)
    c=c.groupby("PLT_CN").agg(n=("ok","size"),ok=("ok","all"))
    cgood=set(c[(c.n==1)&c.ok].index)
    sub=read_table(paths["SUBPLOT"],"SUBPLOT",state)
    sub=sub[sub.PLT_CN.isin(p.CN)&sub.SUBP.isin([1,2,3,4])].copy()
    sub["ok"]=sub.SUBP_STATUS_CD.eq(1)
    s=sub.groupby("PLT_CN").agg(n=("SUBP","size"),unique=("SUBP","nunique"),ok=("ok","all"))
    sgood=set(s[(s.n==4)&(s.unique==4)&s.ok].index)
    p=p[p.CN.isin(cgood&sgood)].copy()
    p["arm"]=p.key.map(arm)
    before=len(p)
    p=climate_frame(p,root/"climate.zip")
    ref=p[(p.arm==0)&p.year.between(2004,2012)].sort_values(["year","CN"]).drop_duplicates("key")
    older=p[(p.arm==1)&p.year.between(2013,2018)][["CN","key","year","LAT","LON","state"]]
    newer=p[p.arm==1][["CN","key","year","PREV_PLT_CN"]].rename(columns={"CN":"end","year":"year1"})
    pairs=older.merge(newer,left_on=["CN","key"],right_on=["PREV_PLT_CN","key"],how="inner")
    pairs["dt"]=pairs.year1-pairs.year
    pairs=pairs[pairs.dt.between(4,8)].sort_values(["year","year1","CN","end"]).drop_duplicates("key").copy()
    needed=set(ref.CN)|set(pairs.CN)|set(pairs.end)
    t=read_table(paths["TREE"],"TREE",state)
    t=t[t.PLT_CN.isin(needed)&t.STATUSCD.eq(1)&t.SUBP.isin([1,2,3,4])&t.DIA.ge(5)&np.isclose(t.TPA_UNADJ,6.018046,atol=0.02)].copy()
    if t.CN.duplicated().any(): raise ValueError("duplicate sampled tree ID")
    if t.SPCD.isna().any() or t.DIA.isna().any(): raise ValueError("missing admitted tree species/diameter")
    t["ba"]=np.pi*(t.DIA/2)**2
    agg=t.groupby(["PLT_CN","SPCD"],as_index=False).agg(n=("CN","size"),ba=("ba","sum"))
    audit={"state":state,"qualified_visits_preclimate":before,"qualified_visits":len(p),"reference_plots":len(ref),"validation_intervals":len(pairs),"admitted_live_adult_stems":len(t),"unique_ref_response_keys":len(set(ref.key)&set(pairs.key))}
    print("STATE",json.dumps(audit),flush=True)
    assert not audit["unique_ref_response_keys"]
    return ref,pairs,agg,audit

def reference_niches(ref,agg):
    ref=ref.copy()
    ref["bin"]=(np.floor(ref.mat/2).astype(int).astype(str)+"|"+np.floor(ref["map"]/200).astype(int).astype(str))
    av=ref.bin.value_counts()
    ref=ref[ref.bin.isin(av[av>=10].index)]
    av=ref.bin.value_counts().sort_index()
    if len(av)<3: raise RuntimeError("fewer than three adequately sampled reference climate bins")
    occ=agg.merge(ref[["CN","bin"]],left_on="PLT_CN",right_on="CN",how="inner")
    mat=pd.crosstab(occ.SPCD,occ.bin).reindex(columns=av.index,fill_value=0)
    mat=mat[mat.sum(axis=1)>=40].sort_index()
    if len(mat)<8: raise RuntimeError("fewer than eight reference-qualified taxa")
    rates=mat.div(av,axis=1); probs=rates.div(rates.sum(axis=1),axis=0)
    raw=mat.div(mat.sum(axis=1),axis=0)
    presence={s:set(g.PLT_CN) for s,g in occ[occ.SPCD.isin(mat.index)].groupby("SPCD")}
    d={}
    for a,b in itertools.combinations(mat.index,2):
        d[(a,b)]=(float(np.minimum(probs.loc[a],probs.loc[b]).sum()),float(len(presence[a]&presence[b])/len(presence[a]|presence[b])),float(np.minimum(raw.loc[a],raw.loc[b]).sum()))
    return d,mat,av,ref

def evaluations(pairs,agg,niches):
    counts={k:{str(a):(int(n),float(ba)) for a,n,ba in g[["SPCD","n","ba"]].itertuples(index=False,name=None)} for k,g in agg.groupby("PLT_CN")}
    out=[]
    for r in pairs.itertuples(index=False):
        start=counts.get(r.CN,{})
        end=counts.get(r.end,{})
        species=sorted(a for a in start if start[a][0]>=2)
        for a,b in itertools.combinations(species,2):
            if (a,b) not in niches: continue
            d,j,raw=niches[(a,b)]
            n0a,ba0a=start[a];n0b,ba0b=start[b]
            n1a,ba1a=end.get(a,(0,0));n1b,ba1b=end.get(b,(0,0))
            da=n1a-n0a;db=n1b-n0b
            xa=np.log(n0a);xb=np.log(n0b)
            out.append((r.key,r.state,f"{math.floor(r.LAT)}|{math.floor(r.LON)}",a,b,d,j,raw,int(da*db<0),int((ba1a-ba0a)*(ba1b-ba0b)<0),(xa+xb)/2,abs(xa-xb),n0a,n0b,n1a,n1b,r.dt))
    return pd.DataFrame(out,columns=["plot","state","block","a","b","D","J","D_raw","opposite_count","opposite_ba","logn","imbalance","n0a","n0b","n1a","n1b","dt"])

def centered_stats(df, outcome, predictor="D"):
    cols=[predictor,"J","logn","imbalance",outcome]
    n=df.groupby("plot")[outcome].transform("size")
    d=df.loc[n>=2].copy()
    if len(d)<30: return None
    ns=d.groupby("plot")[outcome].transform("size").to_numpy()
    m=d[cols]-d.groupby("plot")[cols].transform("mean")
    A=m[cols[:-1]].to_numpy()/np.sqrt(ns[:,None])
    b=m[outcome].to_numpy()/np.sqrt(ns)
    cross=[]
    for block,idx in d.groupby("block").indices.items():
        X=A[idx];y=b[idx]
        cross.append((block,X.T@X,X.T@y))
    xx=A.T@A;xy=A.T@b
    if np.linalg.matrix_rank(xx)<4:return None
    coef=np.linalg.solve(xx,xy)
    return {"slope_per_0_1_D":float(coef[0]*0.1),"plots":int(d["plot"].nunique()),"pair_plot_rows":len(d),"blocks":len(cross),"cross":cross}

def fit(df,outcome,predictor="D",bootstrap=False):
    r=centered_stats(df,outcome,predictor)
    if r is None:return {"status":"unresolved_rank_or_support"}
    cross=r.pop("cross")
    if bootstrap and len(cross)>=8:
        rng=np.random.default_rng(284127)
        mats=np.array([x[1] for x in cross]);vec=np.array([x[2] for x in cross]);b=[]
        for _ in range(500):
            i=rng.integers(0,len(cross),len(cross));xx=mats[i].sum(axis=0);xy=vec[i].sum(axis=0)
            if np.linalg.matrix_rank(xx)==4:b.append(float(np.linalg.solve(xx,xy)[0]*.1))
        if len(b)>=400:r["conditional_spatial_block_bootstrap_95"]=list(map(float,np.quantile(b,[.025,.975])))
        r["bootstrap_fits"]=len(b)
    r["status"]="exploratory_descriptive"
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--data",type=pathlib.Path,required=True);ap.add_argument("--out",type=pathlib.Path,required=True);args=ap.parse_args()
    args.data.mkdir(parents=True,exist_ok=True);args.out.mkdir(parents=True,exist_ok=True)
    requests_= [(CLIMATE,args.data/"climate.zip")]+[(f"{BASE}{s}_{t}.zip",args.data/f"{s}_{t}.zip") for s in STATES for t in TABLES]
    prov={}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for (_,path),rec in zip(requests_,ex.map(lambda u:acquire(*u),requests_)):
            prov[path.name]=rec;print("ACQUIRED",path.name,rec["bytes"],flush=True)
    (args.out/"provenance.json").write_text(json.dumps(prov,indent=2))
    datas=[state_data(s,args.data) for s in STATES]
    ref=pd.concat([x[0] for x in datas],ignore_index=True)
    pairs=pd.concat([x[1] for x in datas],ignore_index=True)
    agg=pd.concat([x[2] for x in datas],ignore_index=True)
    assert not (set(ref.key)&set(pairs.key))
    niches,mat,av,ref=reference_niches(ref,agg)
    df=evaluations(pairs,agg,niches)
    if df.empty:raise RuntimeError("no evaluation pairs")
    print("EVALUATION",len(df),"rows",df["plot"].nunique(),"plots",flush=True)
    fitmain=fit(df,"opposite_count",bootstrap=True)
    states={s:fit(df[df.state==s],"opposite_count") for s in STATES}
    taxa=sorted(set(df.a)|set(df.b))
    loo={s:fit(df[(df.a!=s)&(df.b!=s)],"opposite_count").get("slope_per_0_1_D") for s in taxa}
    table=df.groupby(["a","b"],as_index=False).agg(n_shared=("plot","size"),D=("D","first"),J=("J","first"),opposition=("opposite_count","mean"),opposition_ba=("opposite_ba","mean"))
    table=table[table.n_shared>=20].sort_values(["D","a","b"],ascending=[False,True,True])
    table.to_csv(args.out/"pair_summary.csv",index=False)
    mat.to_csv(args.out/"reference_occupancy_counts.csv");av.to_csv(args.out/"reference_climate_availability.csv")
    bins=pd.cut(df.D,[-.00001,.4,.7,1.00001],labels=["D<=0.4","0.4<D<=0.7","D>0.7"])
    desc=df.groupby(bins,observed=False).agg(rows=("D","size"),plots=("plot","nunique"),opposition=("opposite_count","mean"),opposition_ba=("opposite_ba","mean")).reset_index()
    desc.to_csv(args.out/"descriptive_overlap_bins.csv",index=False)
    result={"status":"exploratory_pilot_not_confirmatory","independent_new_confirmatory_endpoints":0,"source_state_audits":[x[3] for x in datas],"reference_eligible_plots":len(ref),"reference_climate_bins":len(av),"reference_species":len(mat),"validation_intervals":len(pairs),"evaluation_plots":int(df["plot"].nunique()),"evaluation_species":len(taxa),"pair_plot_rows":len(df),"pair_summary_n_shared_ge20":len(table),"opposite_count_fraction_unadjusted":float(df.opposite_count.mean()),"primary_within_plot":fitmain,"basal_area_sensitivity":fit(df,"opposite_ba",bootstrap=True),"raw_occurrence_D_sensitivity":fit(df,"opposite_count","D_raw",bootstrap=True),"state_specific":states,"leave_one_species_out":loo,"note":"No actual climate exposure measured; adult sample counts, not whole-state abundance. Exploratory, plot-conditioned slope; bootstrap conditional on reference estimates; pairs share plots and species."}
    (args.out/"summary.json").write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
