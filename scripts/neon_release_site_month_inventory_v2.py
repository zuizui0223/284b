#!/usr/bin/env python3
"""Metadata-only NEON RELEASE-2026 site-month coverage and leakage-gate audit.

NO NEON occurrence/plot files. NO plant detections/absences or record counts.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"config/neon_external_metadata_dependency_gate_v2.json"
ORIGINAL=ROOT/"results/neon_external_metadata_preflight_v1.json"
MONTH=re.compile(r"^(20\d{2})-(0[1-9]|1[0-2])$")


def summarize_public_metadata(payload:dict, raw:bytes, prior:dict, cfg:dict)->dict:
    data=payload.get("data")
    if not isinstance(data,dict):
        raise ValueError("product metadata data object missing")
    prod=cfg["fixed_release"]
    if data.get("productCode")!=prod["product_code"]:
        raise ValueError("wrong NEON data product")
    entries=data.get("siteCodes")
    if not isinstance(entries,list):
        raise ValueError("siteCodes not list")
    by_site={}
    invalid={}
    duplicates=[]
    for entry in entries:
        if not isinstance(entry,dict):
            raise ValueError("siteCodes entries must be dict with siteCode/availableMonths")
        site=entry.get("siteCode")
        months=entry.get("availableMonths")
        if not isinstance(site,str) or not site:
            raise ValueError("siteCode missing")
        if not isinstance(months,list):
            raise ValueError("availableMonths unavailable")
        if site in by_site:
            duplicates.append(site)
        dates=sorted({str(m) for m in months})
        bad=[date for date in dates if not MONTH.fullmatch(date)]
        if bad:
            invalid[site]=bad
        by_site[site]=dates
    original_sites=prior["sites_sorted"]
    actual_sites=sorted(by_site)
    all_dates=sorted({date for dates in by_site.values() for date in dates if MONTH.fullmatch(date)})
    year_counts=Counter(date[:4] for dates in by_site.values()
                        for date in dates if MONTH.fullmatch(date))
    expected_min,expected_max=prod["expected_date_range"]
    in_range=all(expected_min<=d<=expected_max for d in all_dates)
    actual_span=[all_dates[0],all_dates[-1]] if all_dates else []
    same_hash=sha256(raw).hexdigest()==prod["original_metadata_sha256"]
    sites_match=(actual_sites==original_sites and len(actual_sites)==prod["expected_site_count"])
    status=("metadata_site_months_confirmed"
            if not duplicates and not invalid and sites_match and in_range and all_dates and same_hash
            else "metadata_drift_or_incomplete_STOP")
    result={
      "schema":"284b.neon_release_site_month_inventory.v2",
      "status":status,
      "productCode":prod["product_code"],
      "release":prod["label"],
      "release_doi":prod["doi"],
      "release_published":prod["publication_date"],
      "raw_response_sha256":sha256(raw).hexdigest(),
      "matches_initial_v1_sha256":same_hash,
      "expected_release_date_range":prod["expected_date_range"],
      "actual_site_month_span":actual_span,
      "actual_span_matches_official_range":actual_span==prod["expected_date_range"],
      "all_site_months_within_official_range":bool(in_range),
      "unique_site_count":len(actual_sites),
      "site_inventory_matches_initial_receipt":sites_match,
      "duplicate_site_codes":duplicates,
      "invalid_month_values":invalid,
      "site_month_memberships":sum(len(v) for v in by_site.values()),
      "unique_months":len(all_dates),
      "year_site_month_memberships":dict(sorted(year_counts.items())),
      "sites_with_any_months":sum(bool(v) for v in by_site.values()),
      "site_month_by_site":{
        site:{"n_months":len(months),"first_month":months[0] if months else None,
              "last_month":months[-1] if months else None,
              "years":sorted({m[:4] for m in months if MONTH.fullmatch(m)})}
        for site,months in sorted(by_site.items())
      },
      "published_availability_only":True,
      "species_outcomes_read":False,
      "species_occurrence_counts_read":False,
      "NEON_plot_files_downloaded":False,
      "original_GBIF_training_contamination_excluded":False,
      "external_validation_authorized":False,
      "empirical_ledger_increment":0,
    }
    return result


def run()->dict:
    cfg=json.loads(CONTRACT.read_text(encoding="utf-8"))
    prior=json.loads(ORIGINAL.read_text(encoding="utf-8"))
    assert cfg["scope"]=="metadata_only_no_species_records_no_NEON_outcomes"
    assert prior["schema"]=="284b.neon_external_source_metadata_receipt.v1"
    assert prior["biological_endpoint_opened"] is False
    url=cfg["fixed_release"]["metadata_endpoint"]
    req=Request(url,headers={"User-Agent":"284b-NEON-metadata-feasibility/2.0","Accept":"application/json"})
    with urlopen(req,timeout=50) as reply:
        raw=reply.read(8_000_000)
    return summarize_public_metadata(json.loads(raw),raw,prior,cfg)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ["status","unique_site_count",
                                          "site_month_memberships","actual_site_month_span",
                                          "matches_initial_v1_sha256"]}))
    if result["status"]!="metadata_site_months_confirmed":
        raise RuntimeError("NEON release metadata identity/availableMonths drift; stop before outcomes")


if __name__=="__main__":
    main()
