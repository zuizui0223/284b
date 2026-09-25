#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import icechunk
import xarray as xr

def main():
    storage=icechunk.s3_storage(
      bucket="earthmover-icechunk-era5",
      prefix="icechunkV2",
      region="us-east-1",
      anonymous=True,
    )
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)

    variables={}
    for name in ds.variables:
        da=ds[name]
        variables[name]={
          "dims":list(da.dims),
          "shape":[int(x) for x in da.shape],
          "dtype":str(da.dtype),
          "attrs":{k:str(v) for k,v in da.attrs.items()},
          "encoding_chunks":str(da.encoding.get("chunks")),
          "encoding_chunksizes":str(da.encoding.get("chunksizes")),
        }

    result={
      "audit":"frogid_earthmover_era5_temporal_schema_v0_1",
      "group":"single/temporal",
      "dims":{k:int(v) for k,v in ds.sizes.items()},
      "variables":variables,
      "precipitation_candidates":[
        name for name in ds.variables
        if any(t in name.lower() for t in ("precip","rain","tp"))
      ],
      "precipitation_values_read":False,
      "validation_effect_opened":False,
    }
    ds.close()
    Path("frog_frogid_earthmover_era5_schema_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps({
      "dims":result["dims"],
      "precipitation_candidates":result["precipitation_candidates"],
      "n_variables":len(variables)
    },indent=2))

if __name__=="__main__":
    main()
