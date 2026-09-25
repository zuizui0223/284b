#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import xarray as xr
from timezonefinder import TimezoneFinder

FROGID_URL="https://dwca-exports.ala.org.au/dr14760.zip"
FROGID_SHA="f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d"
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}

TIME_CHUNK=8736
LAT_CHUNK=12
LON_CHUNK=12
WET_MM=1.0
DRY_CAP=30
NEG_TOL_M=-1e-8
EXPECTED_N=40754
EXPECTED_MULTI=18174
EXPECTED_CELLS=1623
EXPECTED_CHUNKS=470


def fetch_bytes(url: str, timeout: int=180) -> bytes:
    req=urllib.request.Request(
        url,
        headers={
            "User-Agent":"frogid-chorus-synchrony-earthmover-validation/0.1",
            "Accept":"application/json,*/*",
        },
    )
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()


def local_term(term: str) -> str:
    return term.rsplit("/",1)[-1].rsplit("#",1)[-1] if term else ""


def decode_sep(value: str|None, default: str) -> str:
    if value is None:
        return default
    return bytes(value,"utf-8").decode("unicode_escape")


def core_rows(zf: zipfile.ZipFile):
    meta=ET.fromstring(zf.read("meta.xml"))
    core=meta.find("dwc:core",NS)
    if core is None:
        raise RuntimeError("DwC-A missing core")
    files=core.find("dwc:files",NS)
    loc=files.find("dwc:location",NS) if files is not None else None
    if loc is None or not loc.text:
        raise RuntimeError("DwC-A core missing location")
    fields={
        local_term(f.attrib.get("term","")):int(f.attrib["index"])
        for f in core.findall("dwc:field",NS)
    }
    delim=decode_sep(core.attrib.get("fieldsTerminatedBy"),"\t")
    quote=decode_sep(core.attrib.get("fieldsEnclosedBy"),'"')
    ignore=int(core.attrib.get("ignoreHeaderLines","0"))
    enc=core.attrib.get("encoding","UTF-8").replace("-","")
    reader=csv.reader(
        io.StringIO(zf.read(loc.text.strip()).decode(enc,errors="replace")),
        delimiter=delim,
        quotechar=quote or '"',
    )
    for _ in range(ignore):
        next(reader,None)
    return fields,reader


def get(row,fields,name):
    i=fields.get(name)
    return row[i].strip() if i is not None and i<len(row) else ""


def selected(event_id: str) -> bool:
    return hashlib.sha256(event_id.encode("utf-8")).digest()[0] < 16


def grid_cell(v: float) -> float:
    return round(v*4.0)/4.0


def parse_date(raw: str) -> date:
    return date.fromisoformat(str(raw or "").strip()[:10])


def parse_hour(raw: str) -> float:
    m=re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}(?:\.\d+)?))?",str(raw or "").strip())
    if not m:
        raise ValueError(raw)
    h=int(m.group(1))+int(m.group(2))/60.0
    if m.group(3):
        h+=float(m.group(3))/3600.0
    if not 0<=h<24:
        raise ValueError(raw)
    return h


def load_frogid_sample():
    data=fetch_bytes(FROGID_URL)
    if hashlib.sha256(data).hexdigest()!=FROGID_SHA:
        raise RuntimeError("FrogID hash drift")
    zf=zipfile.ZipFile(io.BytesIO(data))
    fields,reader=core_rows(zf)
    required={
        "eventID","scientificName","eventDate","eventTime",
        "decimalLatitude","decimalLongitude","coordinateUncertaintyInMeters",
        "stateProvince","recordedBy",
    }
    missing=required-set(fields)
    if missing:
        raise RuntimeError(f"missing fields {sorted(missing)}")

    events={}
    event_species=defaultdict(set)
    for row in reader:
        eid=get(row,fields,"eventID")
        if not eid or not selected(eid):
            continue
        sp=get(row,fields,"scientificName")
        if sp:
            event_species[eid].add(sp)
        if eid in events:
            continue
        try:
            lat=float(get(row,fields,"decimalLatitude"))
            lon=float(get(row,fields,"decimalLongitude"))
            unc=float(get(row,fields,"coordinateUncertaintyInMeters"))
        except Exception:
            continue
        if not(-90<=lat<=90 and -180<=lon<=180):
            continue
        if not math.isfinite(unc) or unc>25000:
            continue

        raw_date=get(row,fields,"eventDate")
        raw_time=get(row,fields,"eventTime")
        state=get(row,fields,"stateProvince")
        recorder=get(row,fields,"recordedBy")
        if not raw_date or not raw_time or not state or not recorder:
            continue
        try:
            d=parse_date(raw_date)
            hour=parse_hour(raw_time)
        except Exception:
            continue

        events[eid]={
            "eventID":eid,
            "event_date":d,
            "event_hour":hour,
            "state":state,
            "recorder":recorder,
            "uncertainty_m":unc,
            "lat":lat,
            "lon":lon,
            "cell_lat":grid_cell(lat),
            "cell_lon":grid_cell(lon),
        }

    rows=[]
    for eid,meta in events.items():
        richness=len(event_species.get(eid,set()))
        if richness<1:
            continue
        rows.append({
            **meta,
            "richness":richness,
            "multi":int(richness>=2),
            "year":meta["event_date"].year,
            "month":meta["event_date"].month,
            "cell_id":f"{meta['cell_lat']:.2f},{meta['cell_lon']:.2f}",
        })
    df=pd.DataFrame(rows)
    if len(df)!=EXPECTED_N:
        raise RuntimeError(f"frozen sample drift {len(df)} != {EXPECTED_N}")
    if int(df.multi.sum())!=EXPECTED_MULTI:
        raise RuntimeError("multi-species count drift")
    if int(df.cell_id.nunique())!=EXPECTED_CELLS:
        raise RuntimeError("weather cell count drift")
    return df


def zscore(values):
    x=np.asarray(values,dtype=float)
    mean=float(np.mean(x)); sd=float(np.std(x,ddof=0))
    if not math.isfinite(sd) or sd==0:
        raise RuntimeError("invalid z-score SD")
    return (x-mean)/sd,mean,sd


def fit_model(df: pd.DataFrame, cluster_col: str):
    formula="multi ~ dry_z + C(state) * C(month) + year_z + sin_hour + cos_hour"
    model=smf.glm(formula,data=df,family=sm.families.Binomial())
    fitted=model.fit(
        cov_type="cluster",
        cov_kwds={"groups":df[cluster_col]},
        maxiter=100,
    )
    b=float(fitted.params["dry_z"])
    se=float(fitted.bse["dry_z"])
    p=float(fitted.pvalues["dry_z"])
    q=1.959963984540054
    lo=b-q*se; hi=b+q*se
    return {
        "n_recordings":int(len(df)),
        "multi_species_recordings":int(df.multi.sum()),
        "n_clusters":int(df[cluster_col].nunique()),
        "formula":formula,
        "cluster":cluster_col,
        "beta":b,
        "se_cluster":se,
        "ci95_beta":[lo,hi],
        "odds_ratio_per_sd_log1p_dry_days":math.exp(b),
        "ci95_or":[math.exp(lo),math.exp(hi)],
        "p_value":p,
        "support_rule_pass":bool(b<0 and p<0.05 and hi<0),
    }


def main():
    df=load_frogid_sample()

    tf=TimezoneFinder(in_memory=True)
    tz_cache={}
    event_tz=[]
    for r in df.itertuples(index=False):
        key=(float(r.lat),float(r.lon))
        if key not in tz_cache:
            tz=tf.timezone_at(lng=key[1],lat=key[0])
            if not tz:
                raise RuntimeError(f"timezone unresolved {key}")
            tz_cache[key]=tz
        event_tz.append(tz_cache[key])
    df=df.copy()
    df["timezone"]=event_tz

    storage=icechunk.s3_storage(
        bucket="earthmover-icechunk-era5",
        prefix="icechunkV2",
        region="us-east-1",
        anonymous=True,
    )
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    tp=ds["tp"]
    attrs=tp.attrs
    if attrs.get("GRIB_paramId") not in (228,"228"):
        raise RuntimeError("tp parameter identity drift")
    if str(attrs.get("units"))!="m":
        raise RuntimeError("tp units drift")
    if "1 hour" not in str(attrs.get("accumulation_comment","")):
        raise RuntimeError("tp accumulation semantics drift")

    lats=np.asarray(ds.latitude.values,dtype=float)
    lons=np.asarray(ds.longitude.values,dtype=float)
    times=np.asarray(ds.valid_time.values)

    cell_indices={}
    for r in df.itertuples(index=False):
        key=(float(r.cell_lat),float(r.cell_lon))
        if key in cell_indices:
            continue
        yi=int(np.abs(lats-key[0]).argmin())
        lon360=key[1]%360.0
        xi=int(np.abs(lons-lon360).argmin())
        if abs(lats[yi]-key[0])>0.126 or abs(lons[xi]-lon360)>0.126:
            raise RuntimeError(f"ERA5 nearest-cell mismatch {key}")
        cell_indices[key]=(yi,xi)

    needed_dates=defaultdict(set)
    chunk_requirements=defaultdict(set)

    for r in df.itertuples(index=False):
        cell=(float(r.cell_lat),float(r.cell_lon))
        combo=(cell[0],cell[1],str(r.timezone))
        for off in range(1,DRY_CAP+1):
            needed_dates[combo].add(r.event_date-timedelta(days=off))

        yi,xi=cell_indices[cell]
        start=np.datetime64(r.event_date-timedelta(days=32),"h")
        end=np.datetime64(r.event_date+timedelta(days=1),"h")
        i0=int(np.searchsorted(times,start,side="left"))
        i1=max(i0,int(np.searchsorted(times,end,side="right")-1))
        i0=max(0,i0); i1=min(len(times)-1,i1)
        for tc in range(i0//TIME_CHUNK,i1//TIME_CHUNK+1):
            chunk_requirements[(tc,yi//LAT_CHUNK,xi//LON_CHUNK)].add(combo)

    if len(chunk_requirements)!=EXPECTED_CHUNKS:
        raise RuntimeError(f"chunk footprint drift {len(chunk_requirements)} != {EXPECTED_CHUNKS}")

    # Only the daily values actually needed by retained events are kept.
    daily=defaultdict(float)
    normalized_hash=hashlib.sha256()
    local_date_cache={}
    chunk_min=math.inf
    chunk_max=-math.inf
    hourly_values_read=0

    for chunk_no,cid in enumerate(sorted(chunk_requirements),start=1):
        tc,yc,xc=cid
        t0=tc*TIME_CHUNK; t1=min((tc+1)*TIME_CHUNK,len(times))
        y0=yc*LAT_CHUNK; y1=min((yc+1)*LAT_CHUNK,len(lats))
        x0=xc*LON_CHUNK; x1=min((xc+1)*LON_CHUNK,len(lons))

        arr=np.asarray(
            tp.isel(
                valid_time=slice(t0,t1),
                latitude=slice(y0,y1),
                longitude=slice(x0,x1),
            ).values,
            dtype=np.float64,
        )
        if arr.shape!=(t1-t0,y1-y0,x1-x0):
            raise RuntimeError(f"chunk shape mismatch {cid}: {arr.shape}")
        if not np.isfinite(arr).all():
            raise RuntimeError(f"nonfinite tp in required chunk {cid}")
        amin=float(arr.min()); amax=float(arr.max())
        chunk_min=min(chunk_min,amin); chunk_max=max(chunk_max,amax)
        if amin<NEG_TOL_M:
            raise RuntimeError(f"tp below frozen negative tolerance {cid}: {amin}")
        if amin<0:
            arr[arr<0]=0.0
        hourly_values_read+=int(arr.size)

        utc_mid=pd.DatetimeIndex(times[t0:t1]).tz_localize("UTC")-pd.Timedelta(minutes=30)

        for lat,lon,tzname in sorted(chunk_requirements[cid]):
            yi,xi=cell_indices[(lat,lon)]
            vals=arr[:,yi-y0,xi-x0]*1000.0
            cache_key=(tc,tzname)
            if cache_key not in local_date_cache:
                local_dates=np.asarray(
                    utc_mid.tz_convert(ZoneInfo(tzname)).date,
                    dtype="datetime64[D]",
                )
                local_date_cache[cache_key]=local_dates
            else:
                local_dates=local_date_cache[cache_key]

            unique_days,inverse=np.unique(local_dates,return_inverse=True)
            sums=np.bincount(inverse,weights=vals,minlength=len(unique_days))
            wanted=needed_dates[(lat,lon,tzname)]
            for d64,total in zip(unique_days,sums):
                d=date.fromisoformat(str(d64))
                if d in wanted:
                    daily[(lat,lon,tzname,d)]+=float(total)

    dry=[]
    for r in df.itertuples(index=False):
        combo=(float(r.cell_lat),float(r.cell_lon),str(r.timezone))
        n=0
        for off in range(1,DRY_CAP+1):
            d=r.event_date-timedelta(days=off)
            key=(*combo,d)
            if key not in daily:
                raise RuntimeError(f"missing required local daily precipitation {key}")
            p=float(daily[key])
            if not math.isfinite(p) or p<0:
                raise RuntimeError(f"invalid daily precipitation {key}: {p}")
            if p>=WET_MM:
                break
            n+=1
        dry.append(n)

    # Hash only required daily exposure values in canonical order.
    for key in sorted(daily,key=lambda x:(x[0],x[1],x[2],x[3].isoformat())):
        p=daily[key]
        normalized_hash.update(
            f"{key[0]:.2f},{key[1]:.2f},{key[2]},{key[3].isoformat()},{p:.8f}\\n".encode()
        )

    df["dry_days"]=dry
    df["log1p_dry"]=np.log1p(df.dry_days.astype(float))
    df["dry_z"],dry_mean,dry_sd=zscore(df.log1p_dry)
    df["year_z"],year_mean,year_sd=zscore(df.year.astype(float))
    rad=2.0*math.pi*df.event_hour.astype(float)/24.0
    df["sin_hour"]=np.sin(rad)
    df["cos_hour"]=np.cos(rad)

    required=[
        "multi","dry_z","state","month","year_z","sin_hour","cos_hour",
        "cell_id","recorder","uncertainty_m",
    ]
    if df[required].isna().any().any():
        raise RuntimeError("missing modeled value after frozen construction")

    primary=fit_model(df,"cell_id")
    hp=df[df.uncertainty_m<=10000].copy()
    if len(hp)<10000:
        raise RuntimeError("high-precision sensitivity structurally underpowered")
    precision=fit_model(hp,"cell_id")
    recorder=fit_model(df,"recorder")

    dry_hist=Counter(int(x) for x in df.dry_days)
    timezone_counts=Counter(df.timezone.astype(str))

    result={
        "analysis":"frogid_rain_synchrony_external_validation_v0_2",
        "contract":"FROGID_VALIDATION_MODEL_CONTRACT_V0_4.json",
        "frogid_source_sha256":FROGID_SHA,
        "era5_source":{
            "provider":"Earthmover public Icechunk ERA5",
            "bucket":"earthmover-icechunk-era5",
            "prefix":"icechunkV2",
            "branch":"main",
            "group":"single/temporal",
            "variable":"tp",
            "units":"m",
            "accumulation":"1 hour ending at valid_time",
            "chunks_read":len(chunk_requirements),
            "hourly_grid_values_read":hourly_values_read,
            "required_daily_weather_sha256":normalized_hash.hexdigest(),
            "required_tp_min_m_before_small_negative_clamp":chunk_min,
            "required_tp_max_m":chunk_max,
        },
        "frozen_sample":{
            "recordings":int(len(df)),
            "multi_species_recordings":int(df.multi.sum()),
            "weather_cells":int(df.cell_id.nunique()),
            "recorders":int(df.recorder.nunique()),
            "high_precision_recordings_le10km":int(len(hp)),
            "timezones":dict(sorted(timezone_counts.items())),
        },
        "exposure":{
            "dry_days_histogram":{str(k):int(v) for k,v in sorted(dry_hist.items())},
            "log1p_dry_mean":dry_mean,
            "log1p_dry_sd":dry_sd,
            "calendar_year_mean":year_mean,
            "calendar_year_sd":year_sd,
        },
        "primary":primary,
        "sensitivities":{
            "coordinate_uncertainty_le10km":precision,
            "recorder_cluster":recorder,
        },
        "naamp_primary_replaced":False,
        "causal_claim_authorized":False,
        "post_opening_retuning_performed":False,
    }

    ds.close()
    out=Path("frog_frogid_rain_validation_earthmover_v0_2.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
