#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import s3fs, xarray as xr

BUCKET="nsf-ncar-era5"
REGION="us-west-2"
FILES={
  "lsp":"e5.oper.fc.sfc.accumu/201710/e5.oper.fc.sfc.accumu.128_142_lsp.ll025sc.2017100106_2017101606.nc",
  "cp":"e5.oper.fc.sfc.accumu/201710/e5.oper.fc.sfc.accumu.128_143_cp.ll025sc.2017100106_2017101606.nc",
}

def summarize(name,key):
    fs=s3fs.S3FileSystem(anon=True,client_kwargs={"region_name":REGION})
    with fs.open(f"{BUCKET}/{key}","rb",block_size=16*1024*1024) as f:
        ds=xr.open_dataset(f,engine="h5netcdf",decode_cf=False,chunks=None)
        out={
          "key":key,
          "dims":{k:int(v) for k,v in ds.sizes.items()},
          "variables":{},
          "coords":{},
          "global_attrs":{k:str(v) for k,v in ds.attrs.items()},
        }
        for v in ds.variables:
            da=ds[v]
            rec={
              "dims":list(da.dims),
              "shape":[int(x) for x in da.shape],
              "dtype":str(da.dtype),
              "attrs":{k:str(val) for k,val in da.attrs.items()},
              "encoding_chunks":str(da.encoding.get("chunksizes")),
            }
            out["variables"][v]=rec
        # Coordinate arrays are schema/identity, not precipitation values.
        for c in ("latitude","longitude","time","forecast_initial_time","forecast_hour"):
            if c in ds.variables:
                da=ds[c]
                vals=da.values
                flat=vals.ravel()
                out["coords"][c]={
                  "count":int(flat.size),
                  "first":str(flat[0]) if flat.size else None,
                  "last":str(flat[-1]) if flat.size else None,
                }
        ds.close()
        return out

def main():
    result={
      "audit":"frogid_era5_s3_netcdf_schema_v0_1",
      "files":{name:summarize(name,key) for name,key in FILES.items()},
      "precipitation_values_read":False,
      "validation_effect_opened":False,
    }
    Path("frog_frogid_era5_s3_netcdf_schema_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
