#!/usr/bin/env python3
"""Count restored GBIF raw records within frozen 47-taxon reference calibration.

This is descriptive source-completeness information only. The 47 taxa and all
historical keys were fixed BEFORE reference calibration; no taxon is chosen
based on restored counts. No ecological predictions or Level-A outcomes opened.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))
from check_original_gbif_object_manifest_v1 import list_objects
from recover_gbif_aug_snapshot_missing20_v1 import partition_historical
from audit_gbif_restored510_focal_taxa_v1 import aggregate_batch,MODES,NEON_VOUCHER
from product_b_v7_2.snapshot_transport import (
    EXPECTED_SNAPSHOT_DATE,EXPECTED_BUCKET,EXPECTED_REGION,
    EXPECTED_OBJECT_MANIFEST_SHA256,object_manifest_sha256
)

FROZEN_REFERENCE=ROOT/"results/product_b_same_target_successor_source_mode_sampling_v0_1.json"
RECOVERY=ROOT/"results/neon_aug_gbif_missing20_recovery_v1.json"


def fixed_reference_key_map():
    x=json.loads(FROZEN_REFERENCE.read_text(encoding="utf-8"))
    if x["result_version"]!="product_b_same_target_successor_source_mode_sampling_v0.1":
        raise RuntimeError("frozen reference sampling provenance changed")
    group=[v for v in x["results"] if v["state"]=="successor_source_mode_sampling_passed"]
    if len(group)!=47 or x["source_mode_sampling_passed"]!=47:
        raise RuntimeError("47 fixed reference taxa changed")
    mapping={}
    for tax in group:
        keys=tax["frozen_historical_specieskeys"]
        if not keys or len(keys)!=len(set(keys)):
            raise RuntimeError("empty/duplicate historical specieskey set")
        for key in keys:
            if key in mapping:
                raise RuntimeError("historical specieskey assigned to multiple calibration taxa")
            mapping[key]=tax["requested_name"]
    if len(mapping)!=79:
        raise RuntimeError("frozen 47 taxa historical key total changed")
    return mapping


def run():
    import pyarrow.dataset as ds
    import pyarrow.fs as pafs

    key_taxon=fixed_reference_key_map()
    recovered=json.loads(RECOVERY.read_text(encoding="utf-8"))
    if recovered["status"]!="historical_9705_parquet_manifest_exactly_recovered":
        raise RuntimeError("GBIF missing20 recovery evidence not confirmed")
    current=list_objects(f"occurrence/{EXPECTED_SNAPSHOT_DATE}/")
    if object_manifest_sha256(current)!=recovered["current_manifest_sha256"]:
        raise RuntimeError("current GBIF restored 510 object metadata drift")
    old,restored,unknown=partition_historical(current)
    if len(old)!=9706 or len(restored)!=510 or unknown:
        raise RuntimeError("restored 510 objects no longer identifiable")
    if recovered["candidate_historical_manifest_sha256"]!=EXPECTED_OBJECT_MANIFEST_SHA256:
        raise RuntimeError("historical GBIF fingerprint not frozen")
    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    d=ds.dataset([f"{EXPECTED_BUCKET}/{z.key}" for z in restored],
                 filesystem=fs,format="parquet")
    where=(
        ds.field("specieskey").isin(sorted(key_taxon)) &
        ds.field("basisofrecord").isin(list(MODES)) &
        (ds.field("occurrencestatus")=="PRESENT")
    )
    scan=d.scanner(columns=["specieskey","basisofrecord","occurrencestatus","datasetkey"],
                   filter=where,batch_size=65536,use_threads=True)
    count=Counter()
    for batch in scan.to_batches():
        aggregate_batch(batch.to_pydict(),set(key_taxon),count)
    taxon_counts=Counter()
    mode_counts=Counter()
    neon_counts=Counter()
    for (key,mode,state),n in count.items():
        if state=="raw_present":
            taxon_counts[key_taxon[key]]+=n
            mode_counts[mode]+=n
        if state=="known_NEON_voucher_datasetkey":
            neon_counts[mode]+=n
    by_taxon=[
      {"taxon":taxon,"historical_key_count":sum(name==taxon for name in key_taxon.values()),
       "raw_restored_present_rows":taxon_counts[taxon]}
       for taxon in sorted(set(key_taxon.values()))
    ]
    return {
      "schema":"284b.gbif_restored510_successor_reference47_exposure.v1",
      "status":"restored_files_scanned_for_frozen_47_reference_taxa",
      "historical_reference_group_taxa":47,
      "historical_specieskey_values":79,
      "source_reference_file":"results/product_b_same_target_successor_source_mode_sampling_v0_1.json",
      "restored_october_parquet_objects_scanned":510,
      "original_parquet_objects_not_scanned":9705,
      "raw_restored_present_counts_by_source":dict(sorted(mode_counts.items())),
      "taxa_with_raw_restored_present_rows":sum(r["raw_restored_present_rows"]>0 for r in by_taxon),
      "taxon_level_raw_restored_counts":by_taxon,
      "known_NEON_datasetkey_in_restored_reference_rows":dict(sorted(neon_counts.items())),
      "historical_47taxon_reference_q95_recomputed":False,
      "historical_47taxon_source_prediction_fits_recomputed":False,
      "original_level_a_endpoint_unchanged":True,
      "GBIF_occurrence_identifiers_saved":False,
      "NEON_plot_species_outcomes_read":False,
      "new_empirical_conclusion_count":0,
      "interpretation":"Raw restored-source exposure of 47 fixed reference taxa, not model-admitted counts or q95 reference calibration sensitivity.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "taxa":report["historical_reference_group_taxa"],
      "taxa_with_restored_rows":report["taxa_with_raw_restored_present_rows"],
      "modes":report["raw_restored_present_counts_by_source"]}))


if __name__=="__main__":
    main()
