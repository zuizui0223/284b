#!/usr/bin/env python3
"""Compare frozen 12 taxon original GBIF model-input denominators with repaired source.

Reads current 10,215-file GBIF source only after verifying exact repaired S3
object-list fingerprint, reconstructs original source admission/cross-mode
collision/spatial-thinning pipeline, and compares to signed original fit ZIPs.

This is a source-data sensitivity preflight, NOT repaired-SDM refitting,
q95 recomputation, independent-taxon validation or ecological evidence.
No raw IDs, coordinates, or third-party field plot outcomes are saved.
"""
from __future__ import annotations
import argparse
import csv
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))
DESIGN=ROOT/"config/gbif_restored510_heldout12_source_thinning_v1.json"
S3_RECOVERY=ROOT/"results/neon_aug_gbif_missing20_recovery_v1.json"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")


def original_fit_n(entry:dict, fit_dir:Path)->dict:
    zip_path=fit_dir/f"fit_{entry['original_index']}.zip"
    raw=zip_path.read_bytes()
    if "sha256:"+sha256(raw).hexdigest()!=entry["fit_artifact_digest"]:
        raise RuntimeError(f"original signed fit ZIP digest changed: {entry['taxon']}")
    with zipfile.ZipFile(BytesIO(raw)) as z:
        contract=json.loads(z.read("contract.json"))
        if contract["taxon"]!=entry["taxon"] or contract["taxon_index"]!=entry["original_index"]:
            raise RuntimeError("Original signed taxon/index provenance drift")
        rows=list(csv.DictReader(z.read("fit_inventory.csv").decode().splitlines()))
    if len(rows)!=48:raise RuntimeError("Unexpected number of original procedure/source/M fit rows")
    result={}
    for mode in MODES:
        n={int(r["n_presence_thinned"]) for r in rows if r["source"]==mode}
        if len(n)!=1:raise RuntimeError("Original model source input denominators not invariant over procedures")
        result[mode]=n.pop()
    return result


def check_raw_source_row_parity(entry:dict,counts:dict)->dict:
    result={}
    for mode in MODES:
        historical=int(entry["original_raw_present_records_by_mode"][mode])
        added=int(entry["restored_510_raw_present_records_by_mode"][mode])
        got=int(counts[mode]["raw_scanned_records"])
        expected=historical+added
        result[mode]={
            "original_frozen_raw_present":historical,
            "restored_510_raw_present":added,
            "predicted_total_repaired_raw_present":expected,
            "scanner_observed_repaired_raw_present":got,
            "matched":got==expected
        }
    return result


def run(fit_dir:Path)->dict:
    import pyarrow as pa
    import pyarrow.dataset as ds
    import pyarrow.fs as pafs
    from sdmr.data import thin_to_grid
    from scripts.audit_original_gbif_neon_datasetkey_pilot_v1 import tally_retained_datasetkeys
    from scripts.run_same_target_layer1_baseline_fit_taxon import (
        DATASET_PATH,MODES as MODEL_MODES,SELECTED_COLUMNS,_adapter_row,_retained_source_frames
    )
    from product_b_v7_2.snapshot_transport import EXPECTED_REGION

    cfg=json.loads(DESIGN.read_text(encoding="utf-8"))
    prior=json.loads(S3_RECOVERY.read_text(encoding="utf-8"))
    if cfg["schema"]!="284b.gbif_repaired_source_input_thinning_v1":raise RuntimeError("Wrong protocol")
    assert prior["status"]=="historical_9705_parquet_manifest_exactly_recovered"
    assert prior["current_manifest_sha256"]==cfg["repaired_full_object_manifest_sha256"]
    assert prior["candidate_historical_manifest_sha256"]==cfg["original_manifest_sha256"]
    assert list(MODES)==cfg["source_modes"]==list(MODEL_MODES)
    entries=cfg["all_12_original_taxa"]
    if len(entries)!=12 or [x["original_index"] for x in entries]!=list(range(12)):
        raise RuntimeError("Taxon inventory or order changed after predeclaration")
    keymap={e["specieskey"]:e for e in entries}
    if len(keymap)!=12:raise RuntimeError("Duplicate or missing frozen specieskeys")
    old_n={e["taxon"]:original_fit_n(e,fit_dir) for e in entries}
    if "/2026-08-01/" not in DATASET_PATH:
        raise RuntimeError("Original GBIF snapshot path drift")
    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    infos=fs.get_file_info(pafs.FileSelector(DATASET_PATH,recursive=False))
    files=[info.path for info in infos if info.type==pa.fs.FileType.File]
    if len(files)!=cfg["repaired_parquet_count"] or len(set(files))!=len(files):
        raise RuntimeError("Current repaired GBIF source file count or uniqueness changed")
    original_missing20=sum(int(path.rsplit("/",1)[-1])%20!=0 for path in files)
    if original_missing20!=cfg["original_parquet_count"]:
        raise RuntimeError("Repaired source is no longer original-plus-510-missing20")
    source=ds.dataset(sorted(files),filesystem=fs,format="parquet")
    scanner=source.scanner(
        columns=list(SELECTED_COLUMNS),
        filter=ds.field("specieskey").isin(sorted(keymap)) &
               ds.field("basisofrecord").isin(list(MODES)) &
               (ds.field("occurrencestatus")=="PRESENT"),
        batch_size=65536,use_threads=True
    )
    raw={k:{m:[] for m in MODES} for k in keymap}
    for batch in scanner.to_batches():
        vals=batch.to_pydict()
        for i in range(batch.num_rows):
            key=str(vals["specieskey"][i] or "").strip()
            mode=str(vals["basisofrecord"][i] or "").strip().upper()
            if key not in raw or mode not in MODES:raise RuntimeError("Unexpected source label")
            raw[key][mode].append(_adapter_row(vals,i))
    outcomes=[]
    for e in entries:
        old=old_n[e["taxon"]]
        raw_source=raw[e["specieskey"]]
        retained=_retained_source_frames(e["taxon"],
            raw_source[MODES[0]],raw_source[MODES[1]])
        counts,missing=tally_retained_datasetkeys(
            raw_source,retained,thin_to_grid,cell_degrees=.05
        )
        raw_check=check_raw_source_row_parity(e,counts)
        revised={mode:int(counts[mode]["source_thinned_model_presence_rows"]) for mode in MODES}
        delta={m:revised[m]-old[m] for m in MODES}
        outcomes.append({
           "taxon":e["taxon"],"original_specieskey":e["specieskey"],
           "original_fit_artifact_id":e["fit_artifact_id"],
           "raw_reconstruction_integrity":raw_check,
           "original_signed_source_thinned_model_presence":old,
           "repaired_source_thinned_presence":revised,
           "repaired_minus_original_source_thinned_presence":delta,
           "repaired_over_original_thinned_presence_ratio":{m:revised[m]/old[m] if old[m]>0 else None for m in MODES},
           "known_NEON_datasetkey_in_repaired_thinned_source":{m:int(counts[m]["source_thinned_known_NEON_dataset_rows"]) for m in MODES},
           "raw_missing_dataset_key_rows":missing,
        })
    aligned=all(all(y["matched"] for y in x["raw_reconstruction_integrity"].values()) for x in outcomes)
    if not aligned:
        state="FAIL_REPAIRED_RAW_SOURCE_PARITY_STOP"
    else:
        state="REPAIRED_SOURCE_THINNING_QUANTIFIED_12_TAXA_NO_MODEL_REFIT"
    return {
       "schema":"284b.gbif_repaired_source_input_thinning_results.v1",
       "status":state,
       "historical_complete_S3_subset_file_count":cfg["original_parquet_count"],
       "repaired_S3_file_count":cfg["repaired_parquet_count"],
       "repaired_restored_file_count":510,
       "frozen_original_heldout_taxa":len(entries),
       "original_fit_ZIP_SHA_verified":len(old_n),
       "taxa_qualified_repaired_raw_parity":
           sum(all(v["matched"] for v in x["raw_reconstruction_integrity"].values()) for x in outcomes),
       "taxa_with_any_admitted_thinned_count_change":
           sum(any(v!=0 for v in x["repaired_minus_original_source_thinned_presence"].values()) for x in outcomes),
       "taxa_with_thinned_input_decrease_in_any_mode":
           sum(any(v<0 for v in x["repaired_minus_original_source_thinned_presence"].values()) for x in outcomes),
       "per_taxon_source_mode_result":outcomes,
       "repaired_SDM_models_fit":False,
       "repaired_prediction_scores_opened":False,
       "repaired_reference_q95_opened":False,
       "original_Level_A_0_of_12_unchanged":True,
       "external_NEON_independence_verified":False,
       "NEON_plot_species_outcomes_read":False,
       "GBIF_raw_occurrence_identifiers_or_coords_saved":False,
       "new_confirmatory_biological_result":False,
       "empirical_ledger_increment":0,
       "interpretation":"Changes in retained and spatially thinned source inputs are not model fit changes, cross-source coherence, or biological truth. Both source modes, taxon panel and historical procedures remain fixed."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fit-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=run(a.fit_dir)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in [
       "status","taxa_qualified_repaired_raw_parity",
       "taxa_with_any_admitted_thinned_count_change",
       "taxa_with_thinned_input_decrease_in_any_mode"
    ]}))
    if result["status"]!="REPAIRED_SOURCE_THINNING_QUANTIFIED_12_TAXA_NO_MODEL_REFIT":
        raise SystemExit("Repaired GBIF source did not reproduce expected original-plus-restored raw counts")


if __name__=="__main__":
    main()
