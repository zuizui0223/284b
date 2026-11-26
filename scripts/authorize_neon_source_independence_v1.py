#!/usr/bin/env python3
"""Fail-closed provenance gate for the proposed NEON field validation.

Source-level NEON voucher input reuse and exact plot/event label leakage are
distinct. This gate records both, and refuses to certify independent field
validation before either has been explicitly ruled out. No NEON plot data read.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PILOT=ROOT/"results/neon_original_gbif_historical_replay_v2.json"
PREDECLARED=ROOT/"config/neon_external_validation_preflight_v1.json"
RELEASE=ROOT/"results/neon_release_site_month_inventory_v2.json"


def assess_source_eligibility(pilot:dict,protocol:dict,release:dict)->dict:
    if pilot.get("schema")!="284b.original_GBIF_NEON_datasetkey_historical_replay.v2":
        raise ValueError("No verified original-GBIF source-lineage receipt")
    if pilot.get("original_model_counts_recovered")!={"HUMAN_OBSERVATION":True,"PRESERVED_SPECIMEN":True}:
        raise ValueError("Original model source inputs not independently replicated")
    if pilot.get("historical_s3_parquet_files_read")!=9705:
        raise ValueError("Historically used Parquet object set not recovered")
    if release.get("status")!="metadata_site_months_confirmed":
        raise ValueError("NEON release inventory mismatch")
    if release.get("release")!=protocol["public_source"]["release"]:
        raise ValueError("NEON release identity drift")
    if protocol["eligibility_rules_prelabel"]["minimum_independent_sites_per_evaluable_taxon"]!=3:
        raise ValueError("Original field holdout rule changed")
    seen=pilot.get("known_NEON_training_rows_in_thinned_sources")
    if not isinstance(seen,int) or seen<0:
        raise ValueError("Unqualified NEON datasetKey model input count")
    if seen:
        state="CONFIRMED_NEON_VOUCHER_DATASET_IN_FROZEN_MODEL_SOURCE"
        source_claim=False
    else:
        state="KNOWN_DATASETKEY_NOT_FOUND_BUT_OTHER_LINEAGE_UNRESOLVED"
        source_claim=None
    return {
      "schema":"284b.neon_independence_authorization_gate.v1",
      "state":state,
      "taxon":pilot["taxon"],
      "historical_model_sources":[ "PRESERVED_SPECIMEN","HUMAN_OBSERVATION"],
      "historical_thinned_model_input_counts":pilot["original_model_expected_source_counts"],
      "verified_known_NEON_voucher_dataset_model_inputs":seen,
      "known_NEON_voucher_inputs_by_source":{
         m:int(pilot["source_counts"][m]["source_thinned_known_NEON_dataset_rows"])
         for m in ("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
      },
      "blanket_independence_from_all_NEON_derived_biological_materials":source_claim,
      "exact_overlap_with_proposed_NEON_plot_bout_labels_established":False,
      "disjoint_plot_event_external_accuracy_evaluation_qualified":False,
      "cleanly_refitted_voucher_excluded_model_qualified":False,
      "authorization_to_open_NEON_plant_outcomes":False,
      "original_284b_Level_A_empirical_endpoint_unchanged":True,
      "NEON_plant_outcomes_read":False,
      "NEON_source_voucher_metadata_from_GBIF_only":True,
      "empirical_ledger_increment":0,
      "stop_rule":"Do not call the original frozen model and NEON independently sampled as entire data sources. This does not establish identity with a particular NEON plot-bout; it must be evaluated separately before source-independent external validation."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    pilot=json.loads(PILOT.read_text(encoding="utf-8"))
    v1=json.loads(PREDECLARED.read_text(encoding="utf-8"))
    release=json.loads(RELEASE.read_text(encoding="utf-8"))
    status=assess_source_eligibility(pilot,v1,release)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(status,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:status[k] for k in [
       "state","verified_known_NEON_voucher_dataset_model_inputs",
       "authorization_to_open_NEON_plant_outcomes"
    ]}))


if __name__=="__main__":
    main()
