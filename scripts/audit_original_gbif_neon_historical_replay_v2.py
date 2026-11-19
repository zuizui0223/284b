#!/usr/bin/env python3
"""Reconstruct Artemisia historical GBIF model-input provenance from exact file set.

This replays the ORIGINAL 9705-file 2026-08-01 occurrence snapshot after
independent SHA-verified recovery of the October-2026 510-file backfill.
Do not scan the current 10215-file directory as though it were historical.
Only aggregate datasetKey counts are persisted; no occurrence IDs/coordinates.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))

DESIGN=ROOT/"config/original_gbif_neon_datasetkey_pilot_v1.json"
RECOVERY=ROOT/"results/neon_aug_gbif_missing20_recovery_v1.json"
REGISTRY=ROOT/"registry/product_b_same_target_source_identity_pass_taxa_v0_1.csv"
EXPECTED_SET_SHA="1b5b2dde8a23e78beafac1d122830e0552c2fbdac4086e9d9d8c161814a7163e"
EXPECTED_COUNT=9705
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")


def frozen_parquet_paths(paths:list[str])->list[str]:
    """Reject uncertain S3 listings; choose exactly nonmultiples of 20."""
    all_parquet=sorted(paths)
    if len(all_parquet)!=10215 or len(set(all_parquet))!=10215:
        raise RuntimeError("expected repaired 10215-file current snapshot listing")
    allowed=[]
    backfilled=[]
    for path in all_parquet:
        name=path.rsplit("/",1)[-1]
        if (not name.isdecimal() or len(name)!=6 or
                not path.endswith("/occurrence.parquet/"+name)):
            raise RuntimeError("unexpected path outside frozen Aug2026 parquet snapshot")
        (backfilled if int(name)%20==0 else allowed).append(path)
    if len(allowed)!=EXPECTED_COUNT or len(backfilled)!=510:
        raise RuntimeError("frozen historical file-set selection inconsistent with recovery receipt")
    return allowed


def run():
    import pandas as pd
    import pyarrow.dataset as ds
    import pyarrow.fs as pafs
    from sdmr.data import thin_to_grid
    from scripts.audit_original_gbif_neon_datasetkey_pilot_v1 import tally_retained_datasetkeys
    from scripts.run_same_target_layer1_baseline_fit_taxon import (
        _adapter_row, _retained_source_frames, MODES as MODEL_MODES,
        SELECTED_COLUMNS, DATASET_PATH
    )
    from product_b_v7_2.snapshot_transport import EXPECTED_REGION

    cfg=json.loads(DESIGN.read_text(encoding="utf-8"))
    recovered=json.loads(RECOVERY.read_text(encoding="utf-8"))
    if recovered.get("status")!="historical_9705_parquet_manifest_exactly_recovered":
        raise RuntimeError("cannot use unverified historical S3 snapshot")
    if recovered.get("candidate_historical_manifest_sha256")!=EXPECTED_SET_SHA:
        raise RuntimeError("historic object fingerprint changed")
    if cfg["pilot"]["taxon"]!="Artemisia tridentata" or cfg["pilot"]["specieskey"]!="GX2B":
        raise RuntimeError("predeclared source taxon changed")
    if tuple(MODEL_MODES)!=MODES:
        raise RuntimeError("source-mode identity drift")
    reg=pd.read_csv(REGISTRY)
    if len(reg)!=12 or reg.iloc[0]["scientific_name"]!=cfg["pilot"]["taxon"] or str(reg.iloc[0]["resolved_snapshot_specieskey"])!="GX2B":
        raise RuntimeError("frozen taxonomic registry drift")
    if "/2026-08-01/" not in DATASET_PATH:
        raise RuntimeError("not the original GBIF August 2026 snapshot")
    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    infos=fs.get_file_info(pafs.FileSelector(DATASET_PATH,recursive=False))
    import pyarrow as pa
    files=[info.path for info in infos if info.type==pa.fs.FileType.File]
    allowed=frozen_parquet_paths(files)
    # Explicit object list avoids auto-including the 510 repaired files.
    dataset=ds.dataset(allowed,filesystem=fs,format="parquet")
    scanner=dataset.scanner(
        columns=list(SELECTED_COLUMNS),
        filter=(ds.field("specieskey")=="GX2B") &
               ds.field("basisofrecord").isin(list(MODES)) &
               (ds.field("occurrencestatus")=="PRESENT"),
        batch_size=65536,use_threads=True
    )
    raw={mode:[] for mode in MODES}
    for batch in scanner.to_batches():
        vals=batch.to_pydict()
        for i in range(batch.num_rows):
            if str(vals["specieskey"][i] or "").strip()!="GX2B":
                raise RuntimeError("frozen source taxon key drift in scan")
            mode=str(vals["basisofrecord"][i] or "").strip().upper()
            if mode not in raw:
                raise RuntimeError("unexpected observation mode")
            raw[mode].append(_adapter_row(vals,i))
    retained=_retained_source_frames(cfg["pilot"]["taxon"],raw[MODES[0]],raw[MODES[1]])
    counts,missing=tally_retained_datasetkeys(
        raw,retained,thin_to_grid,
        cell_degrees=cfg["pilot"]["source_thinning_cell_size_degrees"]
    )
    expected=cfg["pilot"]["expected_thinned_model_presence_counts"]
    matched={mode:counts[mode]["source_thinned_model_presence_rows"]==expected[mode]
             for mode in MODES}
    known=sum(counts[mode]["source_thinned_known_NEON_dataset_rows"] for mode in MODES)
    if not all(matched.values()):
        status="HISTORICAL_OBJECT_SET_MATCHED_BUT_MODEL_INPUT_COUNTS_UNRESOLVED_STOP"
    elif known:
        status="SIGNED_SOURCE_INPUTS_RECONSTRUCTED_WITH_KNOWN_NEON_VOUCHER_DATASET_ROWS"
    else:
        status="SIGNED_SOURCE_INPUTS_RECONSTRUCTED_KNOWN_NEON_DATASET_NOT_SEEN"
    return {
      "schema":"284b.original_GBIF_NEON_datasetkey_historical_replay.v2",
      "status":status,
      "original_12taxon_endpoint_unchanged":True,
      "taxon":"Artemisia tridentata",
      "original_specieskey":"GX2B",
      "GBIF_public_snapshot_date":"2026-08-01",
      "frozen_historical_object_manifest_SHA256":EXPECTED_SET_SHA,
      "historical_s3_parquet_files_read":len(allowed),
      "current_repaired_s3_parquet_files_EXCLUDED":510,
      "original_model_counts_recovered":matched,
      "original_model_expected_source_counts":expected,
      "source_counts":counts,
      "raw_missing_dataset_keys":missing,
      "known_NEON_datasetkey":"3fed506c-d04f-4cd4-b373-bd602572f39b",
      "known_NEON_training_rows_in_thinned_sources":known if all(matched.values()) else None,
      "full_external_source_independence_verified":False,
      "possible_other_voucher_publishing_paths_remain":True,
      "NEON_plot_species_outcomes_read":False,
      "NEON_plant_dataset_downloaded":False,
      "biological_endpoint_opened":False,
      "empirical_ledger_increment":0,
      "raw_GBIF_record_identifiers_persisted":False,
      "raw_GBIF_coordinates_persisted":False,
      "why_no_external_accuracy_result":"No independently verified source/target leakage exclusions and no authorized plot outcomes have been evaluated.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({key:result[key] for key in
            ("status","historical_s3_parquet_files_read","original_model_counts_recovered",
             "known_NEON_training_rows_in_thinned_sources")}))
    if result["status"]=="HISTORICAL_OBJECT_SET_MATCHED_BUT_MODEL_INPUT_COUNTS_UNRESOLVED_STOP":
        raise SystemExit("Original model counts still differ after exact file-set recovery")


if __name__=="__main__":
    main()
