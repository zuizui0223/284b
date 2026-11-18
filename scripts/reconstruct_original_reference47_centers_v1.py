#!/usr/bin/env python3
"""Reconstruct each original reference taxon's signed spatial geometry (no model scores).

Every preflight ZIP and fit ZIP is pinned by the original v0.4 GitHub artifact
digest and locked taxon index. Uses only the reconstructed historical 9705 GBIF
Parquet objects. Fails before writing a center array if the original signed
geometry, fit source counts, comparison rows or species-key set diverges.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,sys,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))
MANIFEST=ROOT/"config/gbif_original_reference47_geometry_manifest_v1.json"
SOURCE_AUDIT=ROOT/"results/gbif_repaired_reference47_thinning_v1.json"
RECOVERY=ROOT/"results/neon_aug_gbif_missing20_recovery_v1.json"
FRAME_CONTRACT=ROOT/"config/product_b_same_target_source_common_frame_contract_v0_1.json"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")

def hash_centers(centers):
    import numpy as np
    return hashlib.sha256(np.asarray(centers,dtype="<f8").tobytes(order="C")).hexdigest()

def select_signed_entry(manifest,source_audit,taxon_index):
    if (manifest.get("status")!="PREDECLARED_REFERENCE47_ORIGINAL_GEOMETRY_ONLY"
            or manifest.get("frozen_taxon_count")!=47 or len(manifest.get("entries",[]))!=47
            or [x["index"] for x in manifest["entries"]]!=list(range(47))):
        raise RuntimeError("Original 47-reference identity manifest is not frozen")
    if (source_audit.get("prespecified_reference_taxa")!=47
            or source_audit.get("signed_original_fit_artifact_inputs_verified")!=47
            or source_audit.get("completed_and_verified_shards")!=8
            or len(source_audit.get("fixed_taxon_input_deltas",[]))!=47):
        raise RuntimeError("Signed original reference model-input inventory not qualified")
    if not 0<=taxon_index<47:
        raise ValueError("original reference index must be in 0..46")
    entry=manifest["entries"][taxon_index]
    prev=source_audit["fixed_taxon_input_deltas"][taxon_index]
    if (prev["taxon_index"]!=taxon_index or prev["taxon"]!=entry["taxon"]
        or prev["historical_specieskeys"]!=entry["historical_specieskeys"]
        or prev["original_signed_fit_artifact_id"]!=entry["original_fit_artifact_id"]):
        raise RuntimeError("Reference taxon name/specieskeys or original fit artifact changed")
    for key in ("original_fit_artifact_digest","original_qualification_artifact_digest"):
        v=entry.get(key,"")
        if not v.startswith("sha256:") or len(v)!=71:
            raise RuntimeError("Missing SHA-256 artifact identity")
    if (source_audit.get("original_24_calibration_q95_refitted") is not False
        or source_audit.get("original_12_heldout_model_outputs_refitted") is not False
        or source_audit.get("empirical_ledger_increment")!=0):
        raise RuntimeError("Source-input audit crossed forbidden endpoint")
    return entry,prev

def signed_zip(path,expected):
    raw=path.read_bytes()
    if "sha256:"+hashlib.sha256(raw).hexdigest()!=expected:
        raise RuntimeError("Signed original ZIP bytes do not match predeclared artifact digest")
    return zipfile.ZipFile(io.BytesIO(raw))

def reconstruct(index:int,frame_zip:Path,fit_zip:Path,out_npy:Path):
    import numpy as np,pandas as pd
    import pyarrow as pa
    import pyarrow.dataset as ds
    import pyarrow.fs as pafs
    from sdmr.data import thin_to_grid
    from sdmr.validation import make_presence_spatial_partition
    from scripts.audit_original_gbif_neon_historical_replay_v2 import frozen_parquet_paths
    from scripts.run_same_target_successor_layer1_fit_taxon import (
        DATASET_PATH,SELECTED_COLUMNS,MODES as ORIGINAL_MODES,_adapter_row,_retained_source_frames
    )
    from product_b_v7_2.snapshot_transport import EXPECTED_REGION

    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit=json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    recovery=json.loads(RECOVERY.read_text(encoding="utf-8"))
    c=json.loads(FRAME_CONTRACT.read_text(encoding="utf-8"))
    entry,prev=select_signed_entry(manifest,audit,index)
    if (recovery.get("status")!="historical_9705_parquet_manifest_exactly_recovered"
        or manifest["original_source_manifest_sha256"]!=recovery["candidate_historical_manifest_sha256"]
        or manifest["original_qualification_run_id"]!=34245807165
        or manifest["original_fit_run_id"]!=34314390923
        or tuple(ORIGINAL_MODES)!=MODES or "/2026-08-01/" not in DATASET_PATH):
        raise RuntimeError("Historical source or frozen reference-run identity changed")
    if c["spatial_blocks"].get("n_blocks")!=12:
        raise RuntimeError("Historical 12-block geometry contract changed")

    with signed_zip(frame_zip,entry["original_qualification_artifact_digest"]) as z:
        receipt=json.loads(z.read("receipt.json"))
        if (receipt.get("result_version")!="product_b_same_target_successor_core19_preflight_taxon_v0.4"
            or receipt.get("taxon")!=entry["taxon"] or receipt.get("taxon_index")!=index
            or receipt.get("historical_specieskeys")!=entry["historical_specieskeys"]
            or receipt.get("all_three_M_frames_frozen") is not True
            or receipt.get("active_predictors")!=[f"bio{i}" for i in range(1,20)]):
            raise RuntimeError("Signed reference qualification identity differs")
        frame_hashes={}
        for cell in receipt["cells"]:
            m=int(cell["M_km"]); data=z.read(cell["comparison_frame_file"])
            if hashlib.sha256(data).hexdigest()!=cell["comparison_frame_sha256"]:
                raise RuntimeError("Signed core19 comparison-frame byte hash changed")
            df=pd.read_parquet(io.BytesIO(data))
            if (len(df)!=2000 or df["comparison_row_id"].astype(str).duplicated().any()
                or m not in (150,300,500) or m in frame_hashes):
                raise RuntimeError("Frozen 2000-row reference M frame invalid")
            frame_hashes[str(m)]=cell["comparison_frame_sha256"]
        if set(frame_hashes)!={"150","300","500"}:
            raise RuntimeError("Original three M frames incomplete")
        expected_geometry=int(receipt["source_blind_common_geometry_cells"])
        expected_center_sha=receipt["common_block_centers_sha256"]

    with signed_zip(fit_zip,entry["original_fit_artifact_digest"]) as z:
        fit=json.loads(z.read("contract.json"))
        inventory=list(csv.DictReader(z.read("fit_inventory.csv").decode().splitlines()))
        if (fit.get("taxon")!=entry["taxon"] or fit.get("taxon_index")!=index
            or fit.get("result_version")!="product_b_same_target_successor_core19_layer1_fit_taxon_v0.4"
            or fit.get("historical_specieskeys")!=entry["historical_specieskeys"]
            or fit.get("core19_frame_sha256_by_M")!=frame_hashes
            or len(inventory)!=48):
            raise RuntimeError("Signed original fit/source inventory identity changed")
        old_thin={}
        for mode in MODES:
            vals={int(x["n_presence_thinned"]) for x in inventory if x["source"]==mode}
            if len(vals)!=1:raise RuntimeError("Original source count inconsistent across methods/M")
            old_thin[mode]=vals.pop()
        if old_thin!=prev["original_signed_thinned_n"]:
            raise RuntimeError("Original signed fit source count differs from original source audit")

    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    infos=fs.get_file_info(pafs.FileSelector(DATASET_PATH,recursive=False))
    paths=frozen_parquet_paths([x.path for x in infos if x.type==pa.fs.FileType.File])
    if len(paths)!=9705:raise RuntimeError("Historical source was not exactly 9705 Parquet objects")
    dataset=ds.dataset(paths,filesystem=fs,format="parquet")
    keys=entry["historical_specieskeys"];keyset=set(keys)
    scan=dataset.scanner(
       columns=list(SELECTED_COLUMNS),
       filter=ds.field("specieskey").isin(keys) &
              ds.field("basisofrecord").isin(list(MODES)) &
              (ds.field("occurrencestatus")=="PRESENT"),
       batch_size=65536,use_threads=True)
    a={mode:[] for mode in MODES}
    for batch in scan.to_batches():
        v=batch.to_pydict()
        for i in range(batch.num_rows):
            key=str(v["specieskey"][i] or "").strip()
            mode=str(v["basisofrecord"][i] or "").strip().upper()
            if key not in keyset or mode not in MODES:
                raise RuntimeError("Historical scan returned non-frozen source/key")
            a[mode].append(_adapter_row(v,i))
    if {m:len(a[m]) for m in MODES}!=entry["original_raw_by_mode"]:
        raise RuntimeError("Historical raw source counts differ from frozen reference source manifest")
    kept=_retained_source_frames(entry["taxon"],a[MODES[0]],a[MODES[1]])
    thin={}
    for mode in MODES:
        thin[mode]=thin_to_grid(
            kept[mode],
            cell_size_degrees=float(c["shared_frame_coordinate_pooling"]["source_specific_thinning_cell_degrees"])
        )
        if len(thin[mode])!=old_thin[mode]:
            raise RuntimeError("Historical source-admitted thinned inputs do not reproduce original signed fit")

    pooled=pd.concat([thin[m] for m in MODES],ignore_index=True)
    common_geometry=thin_to_grid(
        pooled,
        cell_size_degrees=float(c["shared_frame_coordinate_pooling"]["pooled_geometry_thinning_cell_degrees"])
    )
    if len(common_geometry)!=expected_geometry:
        raise RuntimeError("Source-blind original pooled geometry cardinality not reproducible")
    blocks=c["spatial_blocks"]
    partition=make_presence_spatial_partition(
        common_geometry["longitude"].to_numpy(float),
        common_geometry["latitude"].to_numpy(float),
        n_blocks=int(blocks["n_blocks"]),
        holdout_fraction=0.5,
        random_state=int(blocks["random_state"]),
    )
    actual_center_sha=hash_centers(partition.centers_xyz)
    if actual_center_sha!=expected_center_sha:
        raise RuntimeError("Reconstructed reference spatial centers differ from original signed hash")
    centers=np.asarray(partition.centers_xyz,dtype="<f8")
    if centers.shape!=(12,3) or not np.isfinite(centers).all():
        raise RuntimeError("Reference centers invalid")
    out_npy.parent.mkdir(parents=True,exist_ok=True)
    np.save(out_npy,centers,allow_pickle=False)
    return {
        "schema":"284b.gbif_original_reference47_center_reconstruction.v1",
        "status":"ORIGINAL_SIGNED_REFERENCE_GEOMETRY_EXACTLY_REPRODUCED",
        "taxon":entry["taxon"],"taxon_index":index,
        "historical_specieskeys":keys,
        "original_qualification_artifact_id":entry["original_qualification_artifact_id"],
        "original_fit_artifact_id":entry["original_fit_artifact_id"],
        "historical_source_manifest_sha256":manifest["original_source_manifest_sha256"],
        "original_source_thinned_counts":old_thin,
        "original_common_pooled_geometry_cells":len(common_geometry),
        "original_center_sha256":expected_center_sha,
        "reconstructed_center_sha256":actual_center_sha,
        "original_comparison_frame_sha256_by_M":frame_hashes,
        "center_npy_sha256":hashlib.sha256(out_npy.read_bytes()).hexdigest(),
        "historical_source_parquet_count":9705,
        "source_rows_or_coordinates_exported":False,
        "model_refit_performed":False,"paired_discordance_computed":False,
        "reference_q95_computed":False,"heldout12_opened":False,
        "neon_field_outcomes_read":False,"empirical_ledger_increment":0,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--taxon-index",type=int,required=True)
    p.add_argument("--frame-zip",type=Path,required=True)
    p.add_argument("--fit-zip",type=Path,required=True)
    p.add_argument("--out-centers",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    args=p.parse_args()
    receipt=reconstruct(args.taxon_index,args.frame_zip,args.fit_zip,args.out_centers)
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("taxon_index","taxon","status","reconstructed_center_sha256")}))

if __name__=="__main__":main()
