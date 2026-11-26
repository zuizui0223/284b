#!/usr/bin/env python3
"""Evaluate source-level independence for the seven *predeclared* NEON taxa.

The identity of the NEON voucher *publisher dataset* is verified, but whether
a source occurrence is the same as a future 400m2 plot outcome is NOT known.
Zero input rows for that one dataset is never treated as independence.
No NEON field responses, plots or new taxon selections are accessed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results/neon_seven_taxon_original_source_lineage_v1.json"
DESIGN=ROOT/"config/neon_external_validation_preflight_v1.json"
SINGLE=ROOT/"results/neon_original_gbif_historical_replay_v2.json"
DATASET_KEY="3fed506c-d04f-4cd4-b373-bd602572f39b"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")


def classify(seven:dict, design:dict, single:dict)->dict:
    if seven.get("schema")!="284b.neon_historical_model_source_lineage7_results.v1":
        raise ValueError("Verified seven-taxon historical input replay missing")
    if seven.get("status")!="seven_original_source_denominators_reproduced":
        raise ValueError("Seven historical source admissions not reproduced")
    if seven.get("recovered_original_object_sha256")!="1b5b2dde8a23e78beafac1d122830e0552c2fbdac4086e9d9d8c161814a7163e":
        raise ValueError("Original source manifest identity changed")
    if seven.get("historical_parquet_objects_scanned")!=9705:
        raise ValueError("Original historical parquet scan was not strictly 9705")
    if seven.get("October_restored_files_excluded")!=510:
        raise ValueError("Repaired files inadvertently entered model-origin audit")
    names=design["focal_taxa_predeclared_from_existing_heldout_for_US_range_only"]
    taxa=seven["taxon_level_source_provenance"]
    if len(names)!=7 or [x["taxon"] for x in taxa]!=names:
        raise ValueError("Source audit changed or re-ordered frozen taxa")
    if seven["taxa_exactly_matching_both_signed_source_counts"]!=7:
        raise ValueError("Signed source denominators failed for a taxon")
    if single.get("schema")!="284b.original_GBIF_NEON_datasetkey_historical_replay.v2":
        raise ValueError("Pilot source history unavailable")
    if single.get("known_NEON_training_rows_in_thinned_sources")!=2:
        raise ValueError("Original Artemisia pilot did not reproduce two known inputs")

    states=[]
    total_by_mode={mode:0 for mode in MODES}
    old_total_by_mode={mode:0 for mode in MODES}
    known_raw_by_mode={mode:0 for mode in MODES}
    for tax in taxa:
        matching=tax["source_count_reproduced"]
        if set(matching)!=set(MODES) or not all(matching.values()):
            raise ValueError("Seven-taxon original source parity altered")
        mode_count={}
        for mode in MODES:
            sub=tax["source_counts"][mode]
            n=int(sub["source_thinned_model_presence_rows"])
            voucher=int(sub["source_thinned_known_NEON_dataset_rows"])
            raw=int(sub["raw_known_NEON_dataset_rows"])
            if voucher<0 or voucher>n or raw<0 or voucher>raw:
                raise ValueError("NEON voucher raw/admitted count inconsistent")
            total_by_mode[mode]+=voucher
            old_total_by_mode[mode]+=n
            known_raw_by_mode[mode]+=raw
            mode_count[mode]={"reproduced_original_thinned_n":n,
                              "known_NEON_voucher_dataset_model_inputs":voucher,
                              "raw_NEON_voucher_dataset_records":raw}
        total=sum(x["known_NEON_voucher_dataset_model_inputs"] for x in mode_count.values())
        state=("CONFIRMED_KNOWN_NEON_SOURCE_DATASET_REUSE"
               if total>0 else "NO_KNOWN_DATASETKEY_IN_MODEL_INPUT__OTHER_LEAKAGE_UNRESOLVED")
        states.append({
            "taxon":tax["taxon"],"state":state,
            "known_NEON_datasetkey_thinned_source_input_rows":total,
            "known_NEON_voucher_input_counts":mode_count,
            "all_NEON_publications_absent_from_training_proven":False,
            "same_plot_bout_reuse_known":False,
            "eligible_for_unqualified_NEON_external_accuracy_claim":False
        })
    if states[0]["known_NEON_datasetkey_thinned_source_input_rows"]!=2:
        raise ValueError("First-taxon pilot and seven-taxon results disagree")
    count=sum(x["known_NEON_datasetkey_thinned_source_input_rows"]>0 for x in states)
    total=sum(x["known_NEON_datasetkey_thinned_source_input_rows"] for x in states)
    if (count,total)!=(seven["taxa_with_known_NEON_voucher_dataset_in_training"],
                      seven["known_NEON_voucher_dataset_thinned_model_input_rows_total"]):
        raise ValueError("Aggregate NEON voucher incidence does not match signed source audit")
    return {
        "schema":"284b.neon_seven_taxon_independence_authorization.v1",
        "status":"SOURCE_LEVEL_INDEPENDENCE_NOT_ESTABLISHED__LABEL_GATE_CLOSED",
        "known_NEON_voucher_GBIF_datasetkey":DATASET_KEY,
        "all_seven_original_source_counts_verified":True,
        "original_source_snapshot":"2026-08-01__9705_frozen_S3_Parquet_objects",
        "predeclared_taxa":7,
        "taxa_with_known_NEON_voucher_datasetkey_inputs":count,
        "taxa_without_that_one_datasetkey_after_thinning":7-count,
        "known_NEON_voucher_datasetkey_total_input_rows":total,
        "known_NEON_voucher_model_inputs_by_mode":total_by_mode,
        "known_NEON_voucher_raw_records_by_mode":known_raw_by_mode,
        "source_thinned_original_model_inputs_by_mode":old_total_by_mode,
        "taxon_results":states,
        "actual_identity_overlap_with_NEON_DP1_plot_events_verified":False,
        "other_NEON_publication_channels_excluded":False,
        "source_independence_overall_qualified":False,
        "authorized_to_open_NEON_taxon_plot_labels":False,
        "eligible_taxa_established_for_external_validation":0,
        "extra_claims_prohibited":[
            "Species with zero rows from this one dataset are independent of all NEON observation records",
            "The six NEON vouchers are necessarily the same records as 2020-2024 vegetation plot outcomes",
            "Six inputs establish a large impact on fitted ecological distributions",
            "A successful source lineage audit implies source-independent ecological prediction correctness",
        ],
        "original_level_A_frozen_0_of_12_unchanged":True,
        "NEON_field_outcomes_read":False,
        "empirical_ledger_increment":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    j=classify(
        json.loads(SOURCE.read_text(encoding="utf-8")),
        json.loads(DESIGN.read_text(encoding="utf-8")),
        json.loads(SINGLE.read_text(encoding="utf-8")))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:j[k] for k in ["status","taxa_with_known_NEON_voucher_datasetkey_inputs",
                                     "known_NEON_voucher_datasetkey_total_input_rows",
                                     "authorized_to_open_NEON_taxon_plot_labels"]}))


if __name__=="__main__":
    main()
