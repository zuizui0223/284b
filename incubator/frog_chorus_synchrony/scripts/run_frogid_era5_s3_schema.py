#!/usr/bin/env python3
"""Schema-only audit of the public NSF NCAR ERA5 S3 bucket.

No precipitation values are read. The script only discovers object structure and
candidate total-precipitation files/metadata needed to implement the frozen
FrogID validation exposure without an API-rate-limit dependency.
"""
from __future__ import annotations
import json, re
from pathlib import Path

import boto3
from botocore import UNSIGNED
from botocore.config import Config

BUCKET="nsf-ncar-era5"
REGION="us-west-2"


def client():
    return boto3.client(
        "s3",
        region_name=REGION,
        config=Config(signature_version=UNSIGNED, connect_timeout=20, read_timeout=60, retries={"max_attempts":5}),
    )


def list_level(s3,prefix="",delimiter="/",max_keys=1000):
    r=s3.list_objects_v2(Bucket=BUCKET,Prefix=prefix,Delimiter=delimiter,MaxKeys=max_keys)
    return {
        "prefixes":[x["Prefix"] for x in r.get("CommonPrefixes",[])],
        "objects":[{"key":x["Key"],"size":x["Size"]} for x in r.get("Contents",[])],
        "is_truncated":bool(r.get("IsTruncated")),
    }


def main():
    s3=client()
    root=list_level(s3)
    # Probe a small fixed number of likely precipitation-related prefixes/keys by name only.
    candidate_prefixes=[]
    for p in root["prefixes"]:
        if any(tok in p.lower() for tok in ("precip","surface","single","e5","era5")):
            candidate_prefixes.append(p)
    # If names are opaque, inspect at most first 12 root prefixes one level deeper.
    probes={}
    for p in (candidate_prefixes[:12] or root["prefixes"][:12]):
        probes[p]=list_level(s3,prefix=p)

    # Search key names using paginated listing, but stop after finding enough schema candidates.
    paginator=s3.get_paginator("list_objects_v2")
    matches=[]
    scanned=0
    for page in paginator.paginate(Bucket=BUCKET,PaginationConfig={"PageSize":1000,"MaxItems":50000}):
        for obj in page.get("Contents",[]):
            scanned+=1
            k=obj["Key"]
            lk=k.lower()
            if any(tok in lk for tok in ("total_precipitation","precipitation","/tp","_tp","tp.")):
                matches.append({"key":k,"size":obj["Size"]})
                if len(matches)>=40:
                    break
        if len(matches)>=40:
            break

    result={
        "audit":"frogid_era5_s3_schema_v0_1",
        "bucket":BUCKET,
        "region":REGION,
        "anonymous":True,
        "root":root,
        "probes":probes,
        "objects_scanned_before_stop":scanned,
        "precipitation_name_matches":matches,
        "precipitation_values_read":False,
        "validation_effect_opened":False
    }
    Path("frog_frogid_era5_s3_schema_v0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
