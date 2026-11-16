#!/usr/bin/env python3
"""Repaired-source input-only audit for fixed 47 original reference taxa.

Eight predeclared shards (taxon index modulo 8), using the original
same-target successor source/admission pipeline. Compares signed historic
core19 fit-inventory thinned-presence counts with repaired 10215-Parquet
GBIF 2026-08-01 source inputs. No SDM refitting, q95, pairing or NEON
field labels. Raw coordinates/IDs never written to the output.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
from io import BytesIO
import csv
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))
DESIGN=ROOT/"config/gbif_repaired_reference47_thinning_v1.json"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")


def original_fit_source_counts(entry:dict,root:Path)->dict:
    path=root/f"ref_fit_{entry['index']}.zip"
    raw=path.read_bytes()
    if "sha256:"+sha256(raw).hexdigest()!=entry["signed_original_fit_artifact_digest"]:
        raise RuntimeError("Signed original reference-fit ZIP digest changed")
    with zipfile.ZipFile(BytesIO(raw)) as z:
        contract=json.loads(z.read("contract.json"))
        if contract.get("taxon")!=entry["taxon"] or int(contract.get("taxon_index",-1))!=entry["index"]:
            raise RuntimeError("Original reference-fit contract taxon/index differs")
        inventory=list(csv.DictReader(z.read("fit_inventory.csv").decode().splitlines()))
    if len(inventory)!=48:raise RuntimeError("Expected original 3 M × 8 procedures × 2 sources")
    n={}
    for mode in MODES:
        got={int(r["n_presence_thinned"]) for r in inventory if r["source"]==mode}
        if len(got)!=1:raise RuntimeError("Signed fit-source presence count not invariant over all M/procedure")
        n[mode]=got.pop()
    return n


def choose_shard(entries:list[dict], shard:int, count:int)->list[dict]:
    if count!=8 or shard<0 or shard>=count or len(entries)!=47:
        raise ValueError("Reference47 sharding manifest must stay 8-way")
    if [x["index"] for x in entries]!=list(range(47)):
        raise ValueError("Frozen reference47 index order changed")
    by=[x for x in entries if x["index"]%count==shard]
    if len(by) not in (5,6):
        raise ValueError("Expected exactly 5 or 6 signed reference taxa per shard")
    return by


def run(shard:int, root:Path):
    import pyarrow as pa
    import pyarrow.dataset as ds
    import pyarrow.fs as pafs
    from sdmr.data import thin_to_grid
    from product_b_v7_2.snapshot_transport import EXPECTED_REGION
    from scripts.run_same_target_successor_layer1_fit_taxon import (
        DATASET_PATH, MODES as FIT_MODES, SELECTED_COLUMNS,
        _adapter_row, _retained_source_frames
    )
    from scripts.audit_original_gbif_neon_datasetkey_pilot_v1 import tally_retained_datasetkeys
    from scripts.check_original_gbif_object_manifest_v1 import list_objects
    from scripts.recover_gbif_aug_snapshot_missing20_v1 import partition_historical
    from product_b_v7_2.snapshot_transport import object_manifest_sha256

    cfg=json.loads(DESIGN.read_text(encoding="utf-8"))
    if cfg["schema"]!="284b.gbif_repaired_source_reference47_thinning_contract.v1":
        raise RuntimeError("Wrong fixed source-thinning contract")
    if tuple(cfg["modes"])!=MODES or tuple(FIT_MODES)!=MODES:
        raise RuntimeError("Original source mode set drift")
    all_entries=cfg["taxon_fit_entries"]
    subset=choose_shard(all_entries,shard,cfg["fixed_shards"])
    reference_n={x["taxon"]:original_fit_source_counts(x,root) for x in subset}

    current=list_objects("occurrence/2026-08-01/")
    current_sha=object_manifest_sha256(current)
    if current_sha!=cfg["repaired_source_manifest_sha256"]:
        raise RuntimeError("GBIF repaired S3 object metadata changed")
    historic,restored,unknown=partition_historical(current)
    if unknown or len(historic)!=9706 or len(restored)!=510:
        raise RuntimeError("GBIF historical/restored object groups drifted")
    if object_manifest_sha256(historic)!=cfg["historical_source_manifest_sha256"]:
        raise RuntimeError("Historical frozen S3 object metadata changed")

    if "/2026-08-01/" not in DATASET_PATH:
        raise RuntimeError("Original GBIF source path is not 2026-08-01")
    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    infos=fs.get_file_info(pafs.FileSelector(DATASET_PATH,recursive=False))
    objects=sorted(x.path for x in infos if x.type==pa.fs.FileType.File)
    if len(objects)!=10215 or not all(x.rsplit("/",1)[-1].isdigit() for x in objects):
        raise RuntimeError("Unexpected repaired Parquet inventory")
    original_key_map={}
    for entry in subset:
        for k in entry["historical_specieskeys"]:
            if k in original_key_map:
                raise RuntimeError("Historical source key maps to multiple reference taxa")
            original_key_map[k]=entry["index"]
    if not original_key_map:raise RuntimeError("No qualified fixed historical source keys")
    dataset=ds.dataset(objects,filesystem=fs,format="parquet")
    scanner=dataset.scanner(
        columns=list(SELECTED_COLUMNS),
        filter=ds.field("specieskey").isin(sorted(original_key_map)) &
               ds.field("basisofrecord").isin(list(MODES)) &
               (ds.field("occurrencestatus")=="PRESENT"),
        batch_size=65536,use_threads=True
    )
    by_index={x["index"]:{mode:[] for mode in MODES} for x in subset}
    for batch in scanner.to_batches():
        val=batch.to_pydict()
        for i in range(batch.num_rows):
            k=str(val["specieskey"][i] or "").strip()
            m=str(val["basisofrecord"][i] or "").strip().upper()
            if k not in original_key_map or m not in MODES:
                raise RuntimeError("Unexpected historical taxon key/source mode")
            by_index[original_key_map[k]][m].append(_adapter_row(val,i))

    reports=[]
    for entry in subset:
        old=reference_n[entry["taxon"]]
        row=by_index[entry["index"]]
        retained=_retained_source_frames(entry["taxon"],row[MODES[0]],row[MODES[1]])
        aggregate,missing=tally_retained_datasetkeys(row,retained,thin_to_grid,
                                                       cell_degrees=cfg["original_source_grid_degrees"])
        original_raw=sum(entry["original_raw_by_mode"].values())
        repaired_raw=sum(aggregate[m]["raw_scanned_records"] for m in MODES)
        added_repair_raw=entry["restored_raw_total_all_modes"]
        parity=repaired_raw==original_raw+added_repair_raw
        changed={mode:aggregate[mode]["source_thinned_model_presence_rows"]-old[mode] for mode in MODES}
        reports.append({
           "taxon":entry["taxon"],"taxon_index":entry["index"],
           "historical_specieskeys":entry["historical_specieskeys"],
           "original_signed_fit_artifact_id":entry["signed_original_fit_artifact_id"],
           "original_raw_present_count":original_raw,
           "restored_510_only_raw_count":added_repair_raw,
           "expected_repaired_raw_present_count":original_raw+added_repair_raw,
           "actual_repaired_raw_present_count":repaired_raw,
           "repaired_raw_count_parity_passed":parity,
           "original_signed_thinned_n":old,
           "repaired_thinned_n":{mode:int(aggregate[mode]["source_thinned_model_presence_rows"]) for mode in MODES},
           "repaired_minus_original_thinned_n":changed,
           "repaired_source_datasetkey_count":{mode:aggregate[mode]["distinct_dataset_keys_post_thin"] for mode in MODES},
           "raw_missing_datasetkey_rows":missing,
        })
    state=("repaired_reference_source_thinning_shard_qualified"
           if all(x["repaired_raw_count_parity_passed"] for x in reports)
           else "repaired_reference_source_raw_parity_STOP")
    return {
      "schema":"284b.gbif_repaired_reference47_thinning_shard.v1",
      "status":state,
      "shard_index":shard,
      "shard_count":cfg["fixed_shards"],
      "original_repair_manifest_verified":True,
      "original_signed_fit_artifacts_verified":len(subset),
      "historical_reference_taxa_in_shard":len(subset),
      "total_repaired_raw_parity_passed":sum(x["repaired_raw_count_parity_passed"] for x in reports),
      "taxa_with_thinned_count_change":sum(any(v!=0 for v in x["repaired_minus_original_thinned_n"].values()) for x in reports),
      "taxon_results":reports,
      "NEON_field_labels_opened":False,
      "model_refitting_performed":False,
      "q95_recalibration_performed":False,
      "ecological_endpoint_opened":False,
      "empirical_ledger_increment":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fit-dir",required=True,type=Path)
    p.add_argument("--shard-index",required=True,type=int)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    o=run(args.shard_index,args.fit_dir)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:o[k] for k in ("shard_index","status","historical_reference_taxa_in_shard",
                                      "taxa_with_thinned_count_change")}))
    if o["status"]!="repaired_reference_source_thinning_shard_qualified":
        raise SystemExit("Repaired reference source raw parity failed; do not aggregate this shard")


if __name__=="__main__":
    main()
