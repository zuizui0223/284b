#!/usr/bin/env python3
"""Metadata-only NEON released site-geometry audit.

No plot coordinates, NEON species outcomes, or model predictions are read.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import radians, sin, cos, atan2, sqrt
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT/"config/neon_site_geography_preflight_v1.json"
INVENTORY = ROOT/"results/neon_release_site_month_inventory_v2.json"
EARTH_RADIUS_KM=6371.009


def great_circle_km(lat1, lon1, lat2, lon2):
    phi1,phi2=radians(lat1),radians(lat2)
    dlat=phi2-phi1
    dlon=radians(lon2-lon1)
    a=sin(dlat/2)**2+cos(phi1)*cos(phi2)*sin(dlon/2)**2
    return 2*EARTH_RADIUS_KM*atan2(sqrt(a),sqrt(max(0,1-a)))


def summarize(data:dict, cfg:dict, inventory:dict, raw:bytes)->dict:
    if not isinstance(data.get("data"),list):
        raise ValueError("expected NEON sites list")
    wanted=set(inventory["site_month_by_site"])
    if len(wanted)!=47:
        raise RuntimeError("frozen DP1.10058.001 site inventory changed")
    found={}
    for record in data["data"]:
        if not isinstance(record,dict):
            raise ValueError("site not dict")
        code=record.get("siteCode")
        if code not in wanted:
            continue
        if code in found:
            raise ValueError("duplicate code in NEON site metadata")
        la=record.get("siteLatitude");lo=record.get("siteLongitude")
        if not isinstance(la,(int,float)) or not isinstance(lo,(int,float)):
            raise ValueError(f"site {code} lacks numeric metadata centroid")
        if not -90<=la<=90 or not -180<=lo<=180:
            raise ValueError("invalid location coordinate range")
        found[code]={
            "siteLatitude":float(la), "siteLongitude":float(lo),
            "domainCode":str(record.get("domainCode") or ""),
            "stateCode":str(record.get("stateCode") or ""),
            "siteType":str(record.get("siteType") or "")
        }
    missing=sorted(wanted-set(found))
    if missing: raise ValueError(f"frozen plant-product sites absent from site metadata: {missing}")
    distances=[
        great_circle_km(a["siteLatitude"],a["siteLongitude"],
                        b["siteLatitude"],b["siteLongitude"])
        for a,b in combinations(found.values(),2)
    ]
    if len(distances)!=47*46//2:
        raise RuntimeError("site pair distance denominator changed")
    # Site-point latitude/longitude are NOT plot positions, so this is
    # descriptive geography only; never treat as a plot-level adequacy gate.
    r={
       "schema":"284b.neon_site_geography_preflight.v1",
       "state":"site_centroid_metadata_confirmed",
       "metadata_url":cfg["site_metadata_url"],
       "metadata_raw_sha256":sha256(raw).hexdigest(),
       "product_site_count":len(found),
       "released_product_site_count":len(wanted),
       "pairwise_site_distances_count":len(distances),
       "min_site_centroid_distance_km":min(distances),
       "site_centroid_pairs_below_1km":sum(v<1 for v in distances),
       "site_centroid_pairs_below_10km":sum(v<10 for v in distances),
       "site_centroid_pairs_below_50km":sum(v<50 for v in distances),
       "domain_counts":dict(sorted(Counter(v["domainCode"] for v in found.values()).items())),
       "state_counts":dict(sorted(Counter(v["stateCode"] for v in found.values()).items())),
       "site_centroid_reference":dict(sorted(found.items())),
       "raw_data_and_plant_labels_opened":False,
       "NEON_plot_coordinates_opened":False,
       "GBIF_source_independence_verified":False,
       "external_validation_authorized":False,
       "empirical_ledger_increment":0,
       "interpretation":"A product-wide set of site centroids is available. Model rank identifiability on NEON plots and species-specific survey eligibility are still unknown; site centroid distance is not itself predictor contrast.",
    }
    return r


def run():
    c=json.loads(CONFIG.read_text(encoding="utf-8"))
    i=json.loads(INVENTORY.read_text(encoding="utf-8"))
    assert c["status"]=="PREDECLARED_SITE_METADATA_ONLY_NO_NEON_SPECIES_OUTCOMES"
    assert i["status"]=="metadata_site_months_confirmed"
    req=Request(c["site_metadata_url"],
                headers={"Accept":"application/json",
                         "User-Agent":"284b-site-metadata-only-spatial-grain-audit/1.0"})
    with urlopen(req,timeout=40) as h:
        raw=h.read(8_000_000)
    return summarize(json.loads(raw),c,i,raw)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    obj=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:obj[k] for k in [
        "state","product_site_count","pairwise_site_distances_count",
        "min_site_centroid_distance_km","site_centroid_pairs_below_1km"
    ]}))


if __name__=="__main__":
    main()
