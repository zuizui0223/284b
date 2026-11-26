#!/usr/bin/env python3
"""Reconstruct signed original spatial-block centers for frozen 12 heldout taxa.

Uses exactly the historical 9705 GBIF Parquet objects and unchanged v0.4
heldout source-admission, thinning and block-center code. Exact original core19
qualification/model artifact digests and their 2,000-row M frames are required.
No repaired-source model fitting, paired scores, q95, or NEON outcomes.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,sys,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))
MANIFEST=ROOT/"config/gbif_original_heldout12_geometry_manifest_v1.json"
AUDIT=ROOT/"results/gbif_repaired_heldout12_thinning_v1.json"
RECOVERY=ROOT/"results/neon_aug_gbif_missing20_recovery_v1.json"
FRAME=ROOT/"config/product_b_same_target_source_common_frame_contract_v0_1.json"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")

def hash_centers(x):
    import numpy as np
    return hashlib.sha256(np.asarray(x,dtype="<f8").tobytes(order="C")).hexdigest()

def frozen_entry(manifest,audit,index):
    entries=manifest.get("entries",[])
    candidates=audit.get("per_taxon_source_mode_result",[])
    if (manifest.get("status")!="PREDECLARED_HELDOUT12_ORIGINAL_GEOMETRY_ONLY"
        or manifest.get("frozen_taxon_count")!=12 or len(entries)!=12
        or [x.get("index") for x in entries]!=list(range(12))
        or len(candidates)!=12
        or audit.get("taxa_qualified_repaired_raw_parity")!=12
        or audit.get("repaired_SDM_models_fit") is not False
        or audit.get("repaired_reference_q95_opened") is not False
        or audit.get("empirical_ledger_increment")!=0):
        raise RuntimeError("Original 12 heldout source-input population or outcome boundary changed")
    if not isinstance(index,int) or index not in range(12):
        raise ValueError("Original heldout taxon index must be 0..11")
    e=entries[index];r=candidates[index]
    if (e["taxon"]!=r["taxon"]
        or e["historical_specieskey"]!=r["original_specieskey"]
        or e["original_fit_artifact_id"]!=r["original_fit_artifact_id"]
        or e["original_source_thinned_counts"]!=r["original_signed_source_thinned_model_presence"]):
        raise RuntimeError("Frozen heldout taxon, specieskey or signed model source input drift")
    if any(not isinstance(e.get(k),str) or not e[k].startswith("sha256:") or len(e[k])!=71
           for k in ("original_qualification_artifact_digest","original_fit_artifact_digest")):
        raise RuntimeError("Original signed heldout artifact digest invalid")
    return e,r

def zip_signed(path,expected):
    raw=path.read_bytes()
    if "sha256:"+hashlib.sha256(raw).hexdigest()!=expected:
        raise RuntimeError("Original heldout qualification/model ZIP bytes not signed")
    return zipfile.ZipFile(io.BytesIO(raw))

def reconstruct(index,frame_zip,fit_zip,out_centers):
    import numpy as np,pandas as pd
    import pyarrow as pa
    import pyarrow.dataset as ds
    import pyarrow.fs as pafs
    from sdmr.data import thin_to_grid
    from sdmr.validation import make_presence_spatial_partition
    from scripts.audit_original_gbif_neon_historical_replay_v2 import frozen_parquet_paths
    from scripts.run_same_target_layer1_baseline_fit_taxon import (
        DATASET_PATH,SELECTED_COLUMNS,MODES as FIT_MODES,_adapter_row,_retained_source_frames
    )
    from scripts.check_original_gbif_object_manifest_v1 import list_objects
    from scripts.recover_gbif_aug_snapshot_missing20_v1 import partition_historical
    from product_b_v7_2.snapshot_transport import EXPECTED_REGION,object_manifest_sha256

    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit=json.loads(AUDIT.read_text(encoding="utf-8"))
    source=json.loads(RECOVERY.read_text(encoding="utf-8"))
    contract=json.loads(FRAME.read_text(encoding="utf-8"))
    e,r=frozen_entry(manifest,audit,index)
    if (source.get("status")!="historical_9705_parquet_manifest_exactly_recovered"
        or manifest["original_source_manifest_sha256"]!=source["candidate_historical_manifest_sha256"]
        or manifest["original_qualification_run_id"]!=34245807165
        or manifest["original_fit_run_id"]!=34314390923
        or tuple(FIT_MODES)!=MODES or "/2026-08-01/" not in DATASET_PATH
        or contract["spatial_blocks"]["n_blocks"]!=12):
        raise RuntimeError("Heldout historical source, model dependency or 12-center contract changed")

    with zip_signed(frame_zip,e["original_qualification_artifact_digest"]) as z:
        receipt=json.loads(z.read("receipt.json"))
        if (receipt.get("result_version")!="product_b_same_target_heldout_core19_preflight_taxon_v0.4"
            or receipt.get("taxon")!=e["taxon"]
            or receipt.get("taxon_index")!=index
            or str(receipt.get("specieskey"))!=e["historical_specieskey"]
            or receipt.get("all_three_M_frames_frozen") is not True
            or receipt.get("active_predictors")!=[f"bio{i}" for i in range(1,20)]):
            raise RuntimeError("Original heldout preflight taxon/key/core19 predictors changed")
        centers_expected=receipt["common_block_centers_sha256"]
        cells_expected=int(receipt["source_blind_common_geometry_cells"])
        frames={}
        for c in receipt["cells"]:
            m=int(c["M_km"])
            bytes0=z.read(c["comparison_frame_file"])
            if hashlib.sha256(bytes0).hexdigest()!=c["comparison_frame_sha256"]:
                raise RuntimeError("Original heldout frame data SHA changed")
            f=pd.read_parquet(io.BytesIO(bytes0))
            if (m not in (150,300,500) or str(m) in frames or len(f)!=2000
                or f["comparison_row_id"].astype(str).duplicated().any()):
                raise RuntimeError("Original heldout M frame identity/denominator changed")
            frames[str(m)]=c["comparison_frame_sha256"]
        if set(frames)!={"150","300","500"}:raise RuntimeError("Missing original heldout M frame")

    with zip_signed(fit_zip,e["original_fit_artifact_digest"]) as z:
        fit=json.loads(z.read("contract.json"))
        rows=list(csv.DictReader(z.read("fit_inventory.csv").decode().splitlines()))
        if (fit.get("result_version")!="product_b_same_target_heldout_core19_layer1_fit_taxon_v0.4"
            or fit.get("taxon")!=e["taxon"] or fit.get("taxon_index")!=index
            or str(fit.get("specieskey"))!=e["historical_specieskey"]
            or fit.get("core19_frame_sha256_by_M")!=frames
            or len(rows)!=48):
            raise RuntimeError("Original heldout fitted model/result/frame SHA changed")
        old_thinned={}
        for mode in MODES:
            got={int(row["n_presence_thinned"]) for row in rows if row["source"]==mode}
            if len(got)!=1:raise RuntimeError("Original source-thinned count varies over M/method")
            old_thinned[mode]=got.pop()
        if old_thinned!=e["original_source_thinned_counts"]:
            raise RuntimeError("Signed historical heldout input counts not reproduced")

    live=list_objects("occurrence/2026-08-01/")
    if object_manifest_sha256(live)!=source["current_manifest_sha256"]:
        raise RuntimeError("Repaired 10215 object metadata has changed")
    historic,restored,unknown=partition_historical(live)
    if (unknown or len(historic)!=9706 or len(restored)!=510
        or object_manifest_sha256(historic)!=manifest["original_source_manifest_sha256"]):
        raise RuntimeError("Historical/restored S3 object partition changed")
    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    infos=fs.get_file_info(pafs.FileSelector(DATASET_PATH,recursive=False))
    paths=frozen_parquet_paths([x.path for x in infos if x.type==pa.fs.FileType.File])
    if len(paths)!=9705:raise RuntimeError("Source-blind geometry not scanning exact original 9705 files")
    data=ds.dataset(paths,filesystem=fs,format="parquet")
    scan=data.scanner(
        columns=list(SELECTED_COLUMNS),
        filter=(ds.field("specieskey")==e["historical_specieskey"]) &
               ds.field("basisofrecord").isin(list(MODES)) &
               (ds.field("occurrencestatus")=="PRESENT"),
        batch_size=65536,use_threads=True
    )
    sources={m:[] for m in MODES}
    for batch in scan.to_batches():
        v=batch.to_pydict()
        for j in range(batch.num_rows):
            key=str(v["specieskey"][j] or "").strip()
            mode=str(v["basisofrecord"][j] or "").strip().upper()
            if key!=e["historical_specieskey"] or mode not in MODES:
                raise RuntimeError("Original GBIF scan found non-frozen taxon/source")
            sources[mode].append(_adapter_row(v,j))
    if {m:len(sources[m]) for m in MODES}!=e["original_raw_by_mode"]:
        raise RuntimeError("Historical GBIF heldout raw source counts not reproduced")
    retained=_retained_source_frames(e["taxon"],sources[MODES[0]],sources[MODES[1]])
    thinned={}
    for mode in MODES:
        thinned[mode]=thin_to_grid(
            retained[mode],
            cell_size_degrees=float(contract["shared_frame_coordinate_pooling"]["source_specific_thinning_cell_degrees"])
        )
        if len(thinned[mode])!=old_thinned[mode]:
            raise RuntimeError("Historical heldout source thinning not reproduced")
    pooled=pd.concat([thinned[m] for m in MODES],ignore_index=True)
    geometry=thin_to_grid(
        pooled,
        cell_size_degrees=float(contract["shared_frame_coordinate_pooling"]["pooled_geometry_thinning_cell_degrees"])
    )
    if len(geometry)!=cells_expected:raise RuntimeError("Original heldout pooled geometry count not reproduced")
    blocks=contract["spatial_blocks"]
    part=make_presence_spatial_partition(
        geometry["longitude"].to_numpy(float),
        geometry["latitude"].to_numpy(float),
        n_blocks=int(blocks["n_blocks"]),
        holdout_fraction=0.5,random_state=int(blocks["random_state"])
    )
    actual_hash=hash_centers(part.centers_xyz)
    if actual_hash!=centers_expected:raise RuntimeError("Original heldout block centers SHA not reproduced")
    arr=np.asarray(part.centers_xyz,dtype="<f8")
    if arr.shape!=(12,3) or not np.isfinite(arr).all():
        raise RuntimeError("Invalid reconstructed heldout centers")
    out_centers.parent.mkdir(parents=True,exist_ok=True)
    np.save(out_centers,arr,allow_pickle=False)
    return {
      "schema":"284b.gbif_original_heldout12_center_reconstruction.v1",
      "status":"ORIGINAL_SIGNED_HELDOUT_GEOMETRY_EXACTLY_REPRODUCED",
      "taxon":e["taxon"],"taxon_index":index,"historical_specieskey":e["historical_specieskey"],
      "original_qualification_artifact_id":e["original_qualification_artifact_id"],
      "original_fit_artifact_id":e["original_fit_artifact_id"],
      "historical_source_manifest_sha256":manifest["original_source_manifest_sha256"],
      "historical_source_parquet_count":9705,
      "original_source_thinned_counts":old_thinned,
      "original_pooled_geometry_cells":len(geometry),
      "original_center_sha256":centers_expected,
      "reconstructed_center_sha256":actual_hash,
      "original_comparison_frame_sha256_by_M":frames,
      "center_npy_sha256":hashlib.sha256(out_centers.read_bytes()).hexdigest(),
      "source_rows_or_coordinates_exported":False,
      "repaired_model_fit_performed":False,
      "paired_discordance_computed":False,
      "reference_q95_opened":False,"repaired_heldout_endpoint_opened":False,
      "neon_field_outcomes_read":False,"empirical_ledger_increment":0
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--taxon-index",type=int,required=True)
    p.add_argument("--frame-zip",type=Path,required=True)
    p.add_argument("--fit-zip",type=Path,required=True)
    p.add_argument("--out-centers",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()
    o=reconstruct(a.taxon_index,a.frame_zip,a.fit_zip,a.out_centers)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:o[k] for k in ("taxon_index","taxon","status","reconstructed_center_sha256")}))
if __name__=="__main__":main()
