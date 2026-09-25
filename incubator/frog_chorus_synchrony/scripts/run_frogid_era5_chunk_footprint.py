#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, math, re, urllib.request, zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import icechunk
import numpy as np
import xarray as xr

FROGID_URL="https://dwca-exports.ala.org.au/dr14760.zip"
FROGID_SHA="f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d"
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}
TIME_CHUNK=8736
LAT_CHUNK=12
LON_CHUNK=12

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogid-era5-chunk-footprint/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def local_term(term):
    return term.rsplit("/",1)[-1].rsplit("#",1)[-1] if term else ""

def decode_sep(v,default):
    if v is None: return default
    return bytes(v,"utf-8").decode("unicode_escape")

def core_rows(zf):
    meta=ET.fromstring(zf.read("meta.xml"))
    core=meta.find("dwc:core",NS)
    files=core.find("dwc:files",NS)
    loc=files.find("dwc:location",NS)
    fields={local_term(f.attrib.get("term","")):int(f.attrib["index"]) for f in core.findall("dwc:field",NS)}
    delim=decode_sep(core.attrib.get("fieldsTerminatedBy"),"\t")
    quote=decode_sep(core.attrib.get("fieldsEnclosedBy"),'"')
    ignore=int(core.attrib.get("ignoreHeaderLines","0"))
    enc=core.attrib.get("encoding","UTF-8").replace("-","")
    reader=csv.reader(io.StringIO(zf.read(loc.text.strip()).decode(enc,errors="replace")),delimiter=delim,quotechar=quote or '"')
    for _ in range(ignore): next(reader,None)
    return fields,reader

def get(row,fields,name):
    i=fields.get(name)
    return row[i].strip() if i is not None and i<len(row) else ""

def selected(event_id):
    return hashlib.sha256(event_id.encode("utf-8")).digest()[0] < 16

def grid_cell(v):
    return round(v*4.0)/4.0

def main():
    data=fetch_bytes(FROGID_URL)
    if hashlib.sha256(data).hexdigest()!=FROGID_SHA:
        raise SystemExit("FrogID hash drift")
    zf=zipfile.ZipFile(io.BytesIO(data))
    fields,reader=core_rows(zf)

    events={}
    species=defaultdict(set)
    for row in reader:
        eid=get(row,fields,"eventID")
        if not eid or not selected(eid): continue
        sp=get(row,fields,"scientificName")
        if sp: species[eid].add(sp)
        if eid in events: continue
        try:
            lat=float(get(row,fields,"decimalLatitude"))
            lon=float(get(row,fields,"decimalLongitude"))
            unc=float(get(row,fields,"coordinateUncertaintyInMeters"))
        except Exception:
            continue
        if unc>25000 or not(-90<=lat<=90 and -180<=lon<=180): continue
        raw=get(row,fields,"eventDate")
        state=get(row,fields,"stateProvince")
        t=get(row,fields,"eventTime")
        rec=get(row,fields,"recordedBy")
        if not raw or not state or not t or not rec: continue
        try: d=date.fromisoformat(raw[:10])
        except Exception: continue
        events[eid]=(grid_cell(lat),grid_cell(lon),d)

    retained=[(eid,*meta) for eid,meta in events.items() if len(species.get(eid,set()))>=1]
    if len(retained)!=40754:
        raise SystemExit(f"sample drift {len(retained)}")

    storage=icechunk.s3_storage(bucket="earthmover-icechunk-era5",prefix="icechunkV2",region="us-east-1",anonymous=True)
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    lats=np.asarray(ds["latitude"].values,dtype=float)
    lons=np.asarray(ds["longitude"].values,dtype=float)
    times=np.asarray(ds["valid_time"].values)

    # Coordinate arrays only. No tp values are accessed.
    cell_indices={}
    for _,lat,lon,_ in retained:
        key=(lat,lon)
        if key in cell_indices: continue
        lon360=lon%360.0
        yi=int(np.abs(lats-lat).argmin())
        xi=int(np.abs(lons-lon360).argmin())
        cell_indices[key]=(yi,xi)

    # Each event requires 31 prior local-calendar days. For chunk-footprint purposes,
    # a UTC window from eventDate-32 through eventDate is conservative for Australian offsets.
    chunks=set()
    chunks_by_year=defaultdict(set)
    for _,lat,lon,d in retained:
        yi,xi=cell_indices[(lat,lon)]
        start=np.datetime64(d-timedelta(days=32),"h")
        end=np.datetime64(d+timedelta(days=1),"h")
        i0=int(np.searchsorted(times,start,side="left"))
        i1=max(i0,int(np.searchsorted(times,end,side="right")-1))
        if i0>=len(times) or i1<0: continue
        i0=max(i0,0); i1=min(i1,len(times)-1)
        t0=i0//TIME_CHUNK; t1=i1//TIME_CHUNK
        for tc in range(t0,t1+1):
            cid=(tc,yi//LAT_CHUNK,xi//LON_CHUNK)
            chunks.add(cid)
            chunks_by_year[d.year].add(cid)

    chunk_float_count=TIME_CHUNK*LAT_CHUNK*LON_CHUNK
    raw_bytes_per_chunk=chunk_float_count*4
    result={
      "audit":"frogid_era5_temporal_chunk_footprint_v0_1",
      "frozen_recordings":len(retained),
      "unique_weather_cells":len(cell_indices),
      "era5_time_chunk_hours":TIME_CHUNK,
      "era5_spatial_chunk":[LAT_CHUNK,LON_CHUNK],
      "required_unique_tp_chunks":len(chunks),
      "required_chunks_by_event_year":{str(y):len(v) for y,v in sorted(chunks_by_year.items())},
      "raw_float32_bytes_per_chunk":raw_bytes_per_chunk,
      "raw_uncompressed_upper_bound_gb":len(chunks)*raw_bytes_per_chunk/1e9,
      "feasibility_gate":{
        "max_unique_chunks":2500,
        "max_uncompressed_upper_bound_gb":15,
        "pass":len(chunks)<=2500 and len(chunks)*raw_bytes_per_chunk<=15e9
      },
      "precipitation_values_read":False,
      "validation_effect_opened":False
    }
    ds.close()
    Path("frog_frogid_era5_chunk_footprint_v0_1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
