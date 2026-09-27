#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
import boto3
from botocore import UNSIGNED
from botocore.config import Config

BUCKET="nsf-ncar-era5"
REGION="us-west-2"
PREFIXES=[
  "e5.oper.fc.sfc.accumu/201710/",
  "e5.oper.fc.sfc.accumu/201711/",
  "e5.oper.fc.sfc.accumu/201801/",
  "e5.oper.fc.sfc.accumu/202401/",
  "e5.oper.fc.sfc.accumu/202411/",
]

def main():
    s3=boto3.client(
      "s3",region_name=REGION,
      config=Config(signature_version=UNSIGNED,connect_timeout=20,read_timeout=60,retries={"max_attempts":5})
    )
    result={"audit":"frogid_era5_s3_precip_layout_v0_1","prefixes":{},"precipitation_values_read":False}
    for prefix in PREFIXES:
        page=s3.list_objects_v2(Bucket=BUCKET,Prefix=prefix,MaxKeys=1000)
        objs=[{"key":x["Key"],"size":x["Size"]} for x in page.get("Contents",[])]
        candidates=[]
        for x in objs:
            lk=x["key"].lower()
            if any(tok in lk for tok in ("228","tp","precip")):
                candidates.append(x)
        result["prefixes"][prefix]={
          "count":len(objs),
          "is_truncated":bool(page.get("IsTruncated")),
          "first_objects":objs[:80],
          "precipitation_name_candidates":candidates[:80],
        }
    Path("frog_frogid_era5_s3_precip_layout_v0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
