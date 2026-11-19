#!/usr/bin/env python3
"""Replay original frozen source-blind spatial block centers for one predeclared taxon.

This proves that the historical 12-block geometry can be reconstructed from the
SHA-verified 9705-file historical GBIF source and original source-processing
code *before* any proposed repaired-source model fitting.

Only block-center metadata (and a separate signed artifact .npy) are written;
no GBIF occurrence rows, exact coordinates or NEON observations are exported.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))
CONFIG=ROOT/"config/gbif_original_reference_centers_Abies_grandis_v1.json"
RECOVERY=ROOT/"results/neon_aug_gbif_missing20_recovery_v1.json"
FRAME_CONTRACT=ROOT/"config/product_b_same_target_source_common_frame_contract_v0_1.json"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")


def hash_centers(centers)->str:
    import numpy as np
    return hashlib.sha256(np.asarray(centers,dtype="<f8").tobytes(order="C")).hexdigest()


def reconstruct(frozen_frame_zip:Path,out_npy:Path)->dict:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.dataset as ds
    import pyarrow.fs as pafs
    from sdmr.data import thin_to_grid
    from sdmr.validation import make_presence_spatial_partition
    from scripts.audit_original_gbif_neon_historical_replay_v2 import frozen_parquet_paths
    from scripts.run_same_target_successor_layer1_fit_taxon import (
        DATASET_PATH,SELECTED_COLUMNS,MODES as OLD_MODES,
        _adapter_row,_retained_source_frames
    )
    from product_b_v7_2.snapshot_transport import EXPECTED_REGION

    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    rec=json.loads(RECOVERY.read_text(encoding="utf-8"))
    frame_contract=json.loads(FRAME_CONTRACT.read_text(encoding="utf-8"))
    if cfg["original_taxon"]!="Abies grandis" or cfg["original_index"]!=1 or cfg["original_historical_specieskeys"]!=["2685361","8KCY"]:
        raise RuntimeError("Predeclared taxon was replaced")
    if cfg["original_full_object_metadata_sha256"]!=rec["candidate_historical_manifest_sha256"]:
        raise RuntimeError("Recovered GBIF object manifest identity not frozen")
    if rec["status"]!="historical_9705_parquet_manifest_exactly_recovered":
        raise RuntimeError("No complete recovery of original data source")
    if cfg["original_parquet_object_count"]!=9705 or tuple(OLD_MODES)!=MODES:
        raise RuntimeError("Original modes or frozen S3 source count changed")
    raw_zip=frozen_frame_zip.read_bytes()
    if "sha256:"+hashlib.sha256(raw_zip).hexdigest()!=cfg["original_signed_qualification_digest"]:
        raise RuntimeError("Original signed qualification ZIP fingerprint mismatch")
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as z:
        receipt=json.loads(z.read("receipt.json"))
        if receipt["taxon"]!=cfg["original_taxon"] or receipt["taxon_index"]!=cfg["original_index"]:
            raise RuntimeError("Old core19 frame identity mismatch")
        if receipt.get("historical_specieskeys") != cfg["original_historical_specieskeys"]:
            raise RuntimeError("Original reference taxonomic-concept key set changed")
        if receipt["common_block_centers_sha256"]!=cfg["original_12block_centers_sha256"]:
            raise RuntimeError("Old core19 block-center source receipt changed")
        if receipt["source_blind_common_geometry_cells"]!=cfg["original_common_pooled_cells"]:
            raise RuntimeError("Old pooled geometry source receipt changed")
        for c in receipt["cells"]:
            inner=z.read(c["comparison_frame_file"])
            if hashlib.sha256(inner).hexdigest()!=c["comparison_frame_sha256"]:
                raise RuntimeError("One original source-blind 2000-row M frame changed")
            df=pd.read_parquet(io.BytesIO(inner))
            if len(df)!=2000 or df["comparison_row_id"].astype(str).duplicated().any():
                raise RuntimeError("Original comparison frame not 2000 unique keys")
    if "/2026-08-01/" not in DATASET_PATH:
        raise RuntimeError("Historical snapshot source URI drift")
    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    infos=fs.get_file_info(pafs.FileSelector(DATASET_PATH,recursive=False))
    pathlist=frozen_parquet_paths([p.path for p in infos if p.type==pa.fs.FileType.File])
    dataset=ds.dataset(pathlist,filesystem=fs,format="parquet")
    scanner=dataset.scanner(
        columns=list(SELECTED_COLUMNS),
        filter=ds.field("specieskey").isin(list(cfg["original_historical_specieskeys"])) &
               ds.field("basisofrecord").isin(list(MODES)) &
               (ds.field("occurrencestatus")=="PRESENT"),
        batch_size=65536,use_threads=True
    )
    source={m:[] for m in MODES}
    for batch in scanner.to_batches():
        vals=batch.to_pydict()
        for i in range(batch.num_rows):
            if str(vals["specieskey"][i] or "").strip() not in set(cfg["original_historical_specieskeys"]):
                raise RuntimeError("Wrong historical taxon")
            mode=str(vals["basisofrecord"][i] or "").strip().upper()
            if mode not in source:raise RuntimeError("Wrong historical source")
            source[mode].append(_adapter_row(vals,i))
    retained=_retained_source_frames(cfg["original_taxon"],source[MODES[0]],source[MODES[1]])
    thin={}
    thin_deg=float(frame_contract["shared_frame_coordinate_pooling"]["source_specific_thinning_cell_degrees"])
    for mode in MODES:
        thin[mode]=thin_to_grid(retained[mode],cell_size_degrees=thin_deg)
        if len(thin[mode])!=cfg["original_model_thinned_presence"][mode]:
            raise RuntimeError("Historical source-thinning counts disagree with signed fit receipt")
    pooled=pd.concat([thin[MODES[0]],thin[MODES[1]]],ignore_index=True)
    common_geometry=thin_to_grid(
        pooled,
        cell_size_degrees=float(frame_contract["shared_frame_coordinate_pooling"]["pooled_geometry_thinning_cell_degrees"])
    )
    if len(common_geometry)!=cfg["original_common_pooled_cells"]:
        raise RuntimeError(f"Original source-blind pooled geometry size not reproduced: {len(common_geometry)}")
    blocks=frame_contract["spatial_blocks"]
    partition=make_presence_spatial_partition(
        common_geometry["longitude"].to_numpy(float),
        common_geometry["latitude"].to_numpy(float),
        n_blocks=int(blocks["n_blocks"]),holdout_fraction=0.5,
        random_state=int(blocks["random_state"])
    )
    computed=hash_centers(partition.centers_xyz)
    if computed!=cfg["original_12block_centers_sha256"]:
        raise RuntimeError(f"Frozen historical spatial centers cannot be reconstructed: {computed}")
    import numpy as np
    centers=np.asarray(partition.centers_xyz,dtype="<f8")
    if centers.shape!=(12,3):
        raise RuntimeError("Expected twelve 3-dimensional unit-sphere spatial block centers")
    out_npy.parent.mkdir(parents=True,exist_ok=True)
    np.save(out_npy,centers,allow_pickle=False)
    # numpy .npy is deliberately an Actions artifact, not automatically
    # promoted into the main Git history or the original Level-A outcome.
    return {
      "schema":"284b.gbif_original_reference_block_centers_reconstruction_pilot.v1",
      "status":"historical_Abies_grandis_reference_center_hash_reconstructed",
      "historical_snapshot_object_manifest_sha256":cfg["original_full_object_metadata_sha256"],
      "historical_9705_S3_objects_used":True,
      "original_historical_source_thinned_counts":{m:len(thin[m]) for m in MODES},
      "original_source_blind_geometry_cells":len(common_geometry),
      "original_signed_12block_centers_SHA256":cfg["original_12block_centers_sha256"],
      "recomputed_centers_SHA256":computed,
      "original_frozen_comparison_frame_SHA256_by_M":{
         str(c["M_km"]):c["comparison_frame_sha256"] for c in receipt["cells"]
      },
      "centers_np_array_SHA256":hashlib.sha256(out_npy.read_bytes()).hexdigest(),
      "model_training_or_refitting_performed":False,
      "ecological_prediction_scores_opened":False,
      "NEON_plant_outcomes_read":False,
      "original_LevelA_endpoint_unchanged":True,
      "empirical_ledger_increment":0
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frame-zip",required=True,type=Path)
    p.add_argument("--out-centers",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    obj=reconstruct(a.frame_zip,a.out_centers)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:obj[k] for k in [
        "status","original_source_blind_geometry_cells","recomputed_centers_SHA256"
    ]}))


if __name__=="__main__":
    main()
