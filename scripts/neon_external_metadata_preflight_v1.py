#!/usr/bin/env python3
"""Read only public NEON product RELEASE metadata; NEVER request species outcomes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"config/neon_external_validation_preflight_v1.json"


def summarize_metadata(payload:dict, source_url:str, raw:bytes, cfg:dict)->dict:
    data=payload.get("data")
    if not isinstance(data,dict):
        raise ValueError("NEON metadata lacked a product data object")
    observed=str(data.get("productCode",""))
    expected=cfg["public_source"]["product_code"]
    if observed!=expected:
        raise ValueError(f"Wrong product: {observed} != {expected}")
    sites=data.get("siteCodes",[])
    if not isinstance(sites,list):
        raise ValueError("NEON product siteCodes not a list")
    unique_codes=set()
    month_counts=[]
    for rec in sites:
        if isinstance(rec,str):
            code=rec
            months=[]
        elif isinstance(rec,dict):
            code=rec.get("siteCode",rec.get("site",rec.get("code","")))
            months=rec.get("availableMonths",rec.get("availableDataMonths",[]))
        else:
            raise ValueError("Unknown NEON site metadata entry")
        if code:
            unique_codes.add(str(code))
        if isinstance(months,list):
            month_counts.append(len(months))
    release=data.get("releases",[])
    return {
        "schema":"284b.neon_external_source_metadata_receipt.v1",
        "state":"product_metadata_qualified_only" if unique_codes else "site_availability_unresolved",
        "product_code":observed,
        "product_title":str(data.get("productName","")),
        "requested_release":cfg["public_source"]["release"],
        "metadata_source_url":source_url,
        "raw_response_sha256":hashlib.sha256(raw).hexdigest(),
        "reported_site_entries":len(sites),
        "unique_site_codes":len(unique_codes),
        "sites_sorted":sorted(unique_codes),
        "month_counts_reported":len(month_counts),
        "release_field_type":type(release).__name__,
        "returned_product_status":str(data.get("productStatus","")),
        "taxon_record_counts_read":False,
        "species_outcomes_read":False,
        "biological_endpoint_opened":False,
        "empirical_ledger_increment":0,
        "all_focal_taxa_evaluable":None,
        "independent_from_GBIF_training_verified":False,
    }


def preflight()->dict:
    cfg=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if cfg["status"]!="SOURCE_METADATA_ONLY_NO_ECOLOGICAL_LABELS_OPENED":
        raise RuntimeError("NEON preflight contract not metadata-only")
    urls=[cfg["public_source"]["api_metadata_url"],
          cfg["public_source"]["backup_api_metadata_url"]]
    errors=[]
    for url in urls:
        try:
            req=Request(url,headers={"User-Agent":"284b-scientific-metadata-preflight/1.0",
                                     "Accept":"application/json"})
            with urlopen(req,timeout=35) as r:
                raw=r.read(8_000_000)
            data=json.loads(raw)
            return summarize_metadata(data,url,raw,cfg)
        except (HTTPError,URLError,TimeoutError,OSError,ValueError,json.JSONDecodeError) as e:
            errors.append({"url":url,"error_type":type(e).__name__,
                           "detail":str(e)[:160]})
    return {
        "schema":"284b.neon_external_source_metadata_receipt.v1",
        "state":"metadata_unavailable_stop",
        "requested_product":cfg["public_source"]["product_code"],
        "requested_release":cfg["public_source"]["release"],
        "attempted_metadata_sources":errors,
        "taxon_record_counts_read":False,
        "species_outcomes_read":False,
        "biological_endpoint_opened":False,
        "independent_from_GBIF_training_verified":False,
        "empirical_ledger_increment":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    v=preflight()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(v,indent=2,ensure_ascii=False,sort_keys=True)+"\n",
                       encoding="utf-8")
    print(json.dumps({k:v.get(k) for k in ("state","unique_site_codes","taxon_record_counts_read",
                         "species_outcomes_read","independent_from_GBIF_training_verified")}))
    if v["state"] not in ("product_metadata_qualified_only","site_availability_unresolved",
                         "metadata_unavailable_stop"):
        raise RuntimeError("unexpected NEON metadata state")


if __name__=="__main__":
    main()
