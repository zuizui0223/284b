#!/usr/bin/env python3
"""Metadata-only GBIF/NEON voucher publication-path risk check.

Does NOT access GBIF occurrence rows, a NEON species record or a historical
model's training observations. Historical overlap remains unresolved.
"""
from __future__ import annotations
import argparse
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"config/neon_external_metadata_dependency_gate_v2.json"


def check_dataset_metadata(obj:dict, raw:bytes, cfg:dict)->dict:
    db=cfg["independence_risk"]["identified_public_GBIF_dataset"]
    snapshot=cfg["independence_risk"]["original_GBIF_snapshot_date"]
    key=db["datasetKey"]
    if obj.get("key")!=key:
        raise ValueError("GBIF dataset registry key changed")
    title=str(obj.get("title") or "")
    if "NEON" not in title.upper() and "Neon" not in title:
        raise ValueError("GBIF publisher dataset is not the expected NEON title")
    created=str(obj.get("created") or "")[:10]
    registered_before=None
    try:
        registered_before=bool(date.fromisoformat(created)<=date.fromisoformat(snapshot))
    except ValueError:
        pass
    return {
        "schema":"284b.neon_gbif_registry_risk.v1",
        "state":"GBIF_dataset_publication_path_confirmed_training_overlap_unresolved",
        "datasetKey":key,
        "dataset_title":title,
        "dataset_created":created or None,
        "registered_on_or_before_source_snapshot":registered_before,
        "dataset_type":obj.get("type"),
        "license":obj.get("license"),
        "doi":obj.get("doi"),
        "publisher_organization_key":obj.get("publishingOrganizationKey"),
        "original_GBIF_snapshot_date":snapshot,
        "original_training_code":cfg["independence_risk"]["original_model_code"],
        "original_GBIF_datasetkey_field_used_in_memory":True,
        "original_training_row_identifiers_persisted":False,
        "confirmed_source_snapshot_contains_dataset":False,
        "confirmed_NEON_voucher_used_in_focal_model":False,
        "independence_from_NEON_data_verified":False,
        "gbif_occurrence_records_read":False,
        "NEON_species_outcomes_read":False,
        "registry_response_sha256":sha256(raw).hexdigest(),
        "empirical_ledger_increment":0,
        "stop_reason":"Potential GBIF reuse path; historical model fitting source rows must be reconstructed and audited before external validation.",
    }


def run():
    cfg=json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert cfg["scope"]=="metadata_only_no_species_records_no_NEON_outcomes"
    item=cfg["independence_risk"]["identified_public_GBIF_dataset"]
    url="https://api.gbif.org/v1/dataset/"+item["datasetKey"]
    req=Request(url,headers={"Accept":"application/json",
                             "User-Agent":"284b-independent-source-metadata-audit/1.0"})
    with urlopen(req,timeout=40) as r:
        raw=r.read(4_000_000)
    return check_dataset_metadata(json.loads(raw),raw,cfg)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",
                     encoding="utf-8")
    print(json.dumps({k:result[k] for k in [
        "state","datasetKey","dataset_created",
        "registered_on_or_before_source_snapshot","independence_from_NEON_data_verified"
    ]}))


if __name__=="__main__":
    main()
