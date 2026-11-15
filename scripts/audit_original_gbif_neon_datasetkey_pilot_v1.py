#!/usr/bin/env python3
"""Source-only provenance reconstruction for ONE frozen plant taxon.

Scans the exact original August 2026 GBIF snapshot already used to fit Level A.
No NEON plot table, occurrence outcomes, source model refit or new target selection.
Only aggregate counts are output; raw occurrence IDs and coordinates are never saved.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
CONTRACT=ROOT/"config/original_gbif_neon_datasetkey_pilot_v1.json"
REGISTRY=ROOT/"registry/product_b_same_target_source_identity_pass_taxa_v0_1.csv"


def tally_retained_datasetkeys(raw, retained, thin_func, *, cell_degrees:float):
    """Only aggregate counts; never return identifiers/coordinates to caller."""
    raw_lookup={}
    raw_counts=Counter()
    missing_key=0
    known=("3fed506c-d04f-4cd4-b373-bd602572f39b",)
    for mode,rows in raw.items():
        for rec in rows:
            key=str(rec.get("key") or "").strip()
            datasetkey=str(rec.get("datasetKey") or "").strip().lower()
            if not key:
                raise ValueError("source row missing immutable gbifID")
            label=(mode,key)
            if label in raw_lookup and raw_lookup[label]!=datasetkey:
                raise ValueError("same source row has conflicting GBIF dataset keys")
            raw_lookup[label]=datasetkey
            raw_counts[(mode,"all")]+=1
            raw_counts[(mode,"known_NEON")]+=int(datasetkey in known)
            missing_key+=int(not datasetkey)

    report={}
    for mode,frame in retained.items():
        selected=thin_func(frame,cell_size_degrees=cell_degrees)
        retained_datasetkeys=[]
        for gid in selected["gbifID"].astype(str):
            label=(mode,str(gid))
            if label not in raw_lookup:
                raise RuntimeError("admitted row ID could not be mapped to source GBIF datasetKey")
            retained_datasetkeys.append(raw_lookup[label])
        report[mode]={
            "raw_scanned_records":raw_counts[(mode,"all")],
            "raw_known_NEON_dataset_rows":raw_counts[(mode,"known_NEON")],
            "quality_retained_before_thinning":len(frame),
            "source_thinned_model_presence_rows":len(selected),
            "source_thinned_known_NEON_dataset_rows":sum(k in known for k in retained_datasetkeys),
            "source_thinned_missing_datasetkey_rows":sum(not k for k in retained_datasetkeys),
            "distinct_dataset_keys_post_thin":len({k for k in retained_datasetkeys if k}),
        }
    return report,missing_key


def run():
    import pandas as pd
    from sdmr.data import thin_to_grid
    from scripts.run_same_target_layer1_baseline_fit_taxon import (
        _scan_taxon,_retained_source_frames,MODES,DATASET_PATH
    )
    c=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"]!="PREREGISTERED_PROVENANCE_ONLY_NO_NEON_BIOLOGICAL_OUTCOME":
        raise RuntimeError("wrong source provenance contract")
    if c["pilot"]["original_registry_index"]!=0:
        raise RuntimeError("only taxon index 0 pilot is preauthorized")
    registry=pd.read_csv(REGISTRY)
    if len(registry)!=12 or registry.iloc[0]["scientific_name"]!=c["pilot"]["taxon"]:
        raise RuntimeError("model taxon drift")
    skey=str(registry.iloc[0]["resolved_snapshot_specieskey"])
    if skey!=c["pilot"]["specieskey"]:
        raise RuntimeError("frozen snapshot specieskey drift")
    if "2026-08-01" not in str(DATASET_PATH):
        raise RuntimeError("original GBIF source snapshot path differs from 2026-08-01")
    raw_a,raw_b=_scan_taxon(skey)
    raw={MODES[0]:raw_a,MODES[1]:raw_b}
    retained=_retained_source_frames(c["pilot"]["taxon"],raw_a,raw_b)
    report,missing=tally_retained_datasetkeys(
        raw,retained,thin_to_grid,cell_degrees=c["pilot"]["source_thinning_cell_size_degrees"])
    for mode,expected in c["pilot"]["expected_thinned_model_presence_counts"].items():
        got=report[mode]["source_thinned_model_presence_rows"]
        if int(got)!=int(expected):
            raise RuntimeError(f"frozen model thinned presence count mismatch {mode}: {got} != {expected}")
    knownkey="3fed506c-d04f-4cd4-b373-bd602572f39b"
    total_neon=sum(x["source_thinned_known_NEON_dataset_rows"] for x in report.values())
    status=("direct_known_NEON_voucher_dataset_records_in_original_model_presence"
            if total_neon>0 else "known_NEON_voucher_datasetkey_not_in_thinned_model_presence__other_overlap_unresolved")
    return {
        "schema":"284b.original_GBIF_NEON_datasetkey_pilot.v1",
        "status":status,
        "taxon":c["pilot"]["taxon"],
        "source_specieskey":skey,
        "original_snapshot":"2026-08-01",
        "original_dataset_path_in_code_SHA256":sha256(str(DATASET_PATH).encode()).hexdigest(),
        "original_model_count_gate_passed":True,
        "known_NEON_datasetKey":knownkey,
        "counts_by_source":report,
        "raw_missing_dataset_key_rows_across_modes":missing,
        "all_original_training_sources_independent_of_NEON":False,
        "complete_historical_data_independence_audit":False,
        "metadata_only_aggregate_output":True,
        "no_GBIF_occurrence_ID_saved":True,
        "no_coordinates_saved":True,
        "NEON_plot_species_outcomes_read":False,
        "refit_or_new_ecological_endpoint_opened":False,
        "empirical_ledger_increment":0,
        "caveat":"Only one known NEON datasetKey and one predeclared plant taxon are checked; other GBIF re-publication and voucher/plot overlap remain possible."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"taxon":result["taxon"],
                      "status":result["status"],
                      "counts_by_source":result["counts_by_source"]}))


if __name__=="__main__":
    main()
