#!/usr/bin/env python3
"""Aggregate all 47 fixed repaired-reference source-input shards.

Fail closed unless eight original fixed shards contain exactly 47 distinct
predeclared taxa / 79 historical specieskeys, all source checksums and
historical raw-count + repaired-only raw-count identities verified.
No ecological model fit/q95 or independent-NEON label inference.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"config/gbif_repaired_reference47_thinning_v1.json"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")


def aggregate(shards:list[dict],config:dict)->dict:
    if config.get("schema")!="284b.gbif_repaired_source_reference47_thinning_contract.v1":
        raise ValueError("No original 47-taxon reference audit contract")
    entries=config["taxon_fit_entries"]
    if len(entries)!=47 or [x["index"] for x in entries]!=list(range(47)):
        raise ValueError("Original 47 calibration-taxon order changed")
    if len(shards)!=8 or sorted(x["shard_index"] for x in shards)!=list(range(8)):
        raise ValueError("All eight predeclared source shards are required")
    by_index={e["index"]:e for e in entries}
    total={}
    for s in shards:
        if s.get("schema")!="284b.gbif_repaired_reference47_thinning_shard.v1":
            raise ValueError("Unknown source-thinning shard schema")
        if s.get("status")!="repaired_reference_source_thinning_shard_qualified":
            raise ValueError("Unqualified or incomplete raw-source reconstruction")
        if s.get("shard_count")!=8 or s.get("original_repair_manifest_verified") is not True:
            raise ValueError("Source object-set identity not verified")
        expected={e["index"] for e in entries if e["index"]%8==s["shard_index"]}
        if (len(s["taxon_results"])!=len(expected) or
            s.get("original_signed_fit_artifacts_verified")!=len(expected) or
            {x["taxon_index"] for x in s["taxon_results"]}!=expected):
            raise ValueError("Missing, extra or swapped taxon in reference shard")
        for row in s["taxon_results"]:
            idx=row["taxon_index"]
            if idx in total or row["taxon"]!=by_index[idx]["taxon"]:
                raise ValueError("Reference taxon duplicated or renamed")
            if row["historical_specieskeys"]!=by_index[idx]["historical_specieskeys"]:
                raise ValueError("Historical reference taxon key concept changed")
            if row["original_signed_fit_artifact_id"]!=by_index[idx]["signed_original_fit_artifact_id"]:
                raise ValueError("Signed original fit artifact changed")
            if not row["repaired_raw_count_parity_passed"]:
                raise ValueError("Repaired source raw-count identity failed")
            if (row["original_raw_present_count"]!=sum(by_index[idx]["original_raw_by_mode"].values())
                or row["restored_510_only_raw_count"]!=by_index[idx]["restored_raw_total_all_modes"]
                or row["actual_repaired_raw_present_count"]!=row["expected_repaired_raw_present_count"]):
                raise ValueError("Source raw counts not comparable with original+510")
            if set(row["repaired_minus_original_thinned_n"])!=set(MODES):
                raise ValueError("Missing source-mode thinned input count")
            for mode in MODES:
                if row["repaired_thinned_n"][mode]-row["original_signed_thinned_n"][mode]!=row["repaired_minus_original_thinned_n"][mode]:
                    raise ValueError("Source thinned inputs inconsistent")
                if row["original_signed_thinned_n"][mode]<=0 or row["repaired_thinned_n"][mode]<=0:
                    raise ValueError("Non-positive source inputs")
            total[idx]=row
    if len(total)!=47 or set(total)!=set(range(47)):
        raise ValueError("Not the complete original 47-taxon reference")
    ordered=[total[i] for i in range(47)]
    totals={mode:{
       "old_signed_inputs":sum(r["original_signed_thinned_n"][mode] for r in ordered),
       "repaired_source_inputs":sum(r["repaired_thinned_n"][mode] for r in ordered),
       "delta_source_inputs":sum(r["repaired_minus_original_thinned_n"][mode] for r in ordered),
       "taxa_with_nonzero_count_delta":sum(r["repaired_minus_original_thinned_n"][mode]!=0 for r in ordered),
       "taxa_with_negative_count_delta":sum(r["repaired_minus_original_thinned_n"][mode]<0 for r in ordered)
    } for mode in MODES}
    for mode,agg in totals.items():
        if agg["repaired_source_inputs"]!=agg["old_signed_inputs"]+agg["delta_source_inputs"]:
            raise RuntimeError("Total source mode accountings differ")
        agg["delta_fraction_of_original"]=agg["delta_source_inputs"]/agg["old_signed_inputs"]
    return {
      "schema":"284b.gbif_repaired_reference47_thinning_results.v1",
      "status":"all_47_original_reference_source_input_parity_and_restoration_qualified",
      "prespecified_reference_taxa":47,
      "prespecified_historical_specieskey_assignments":sum(len(e["historical_specieskeys"]) for e in entries),
      "completed_and_verified_shards":8,
      "signed_original_fit_artifact_inputs_verified":47,
      "source_repair_check_against_exact_9705_and_10215_object_manifests":True,
      "taxa_with_any_repaired_thinned_input_count_change":
          sum(any(r["repaired_minus_original_thinned_n"][m]!=0 for m in MODES) for r in ordered),
      "taxa_with_thinned_input_decrease_in_any_mode":
          sum(any(r["repaired_minus_original_thinned_n"][m]<0 for m in MODES) for r in ordered),
      "source_mode_input_totals":totals,
      "fixed_taxon_input_deltas":ordered,
      "original_24_calibration_q95_refitted":False,
      "original_12_heldout_model_outputs_refitted":False,
      "reference_envelopes_and_heldout_robustness_tested":False,
      "source_restoration_is_not_independent_new_ecological_validation":True,
      "original_signed_level_A_0_of_12_unchanged":True,
      "NEON_plant_plot_outcomes_read":False,
      "empirical_ledger_increment":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shard-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    config=json.loads(CONFIG.read_text(encoding="utf-8"))
    parts=[]
    for k in range(8):
        path=a.shard_dir/f"reference_shard_{k}.json"
        if not path.is_file():
            raise RuntimeError(f"Original fixed reference source shard missing: {k}")
        parts.append(json.loads(path.read_text(encoding="utf-8")))
    out=aggregate(parts,config)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in [
      "status","prespecified_reference_taxa",
      "taxa_with_any_repaired_thinned_input_count_change",
      "source_mode_input_totals"
    ]}))


if __name__=="__main__":
    main()
