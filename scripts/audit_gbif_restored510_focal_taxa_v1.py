#!/usr/bin/env python3
"""Descriptive restoration exposure for all 12 *predeclared* Level-A held-out taxa.

Scan only the 510 October-2026 restored August-2026 GBIF parquet objects, not
the 9705 previously scanned historical objects. Project only specieskey,
basisofrecord, occurrencestatus, datasetkey. No occurrence IDs, locations,
NEON plant plot responses or model predictions.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))
from check_original_gbif_object_manifest_v1 import list_objects
from recover_gbif_aug_snapshot_missing20_v1 import partition_historical
from product_b_v7_2.snapshot_transport import (
    EXPECTED_SNAPSHOT_DATE,EXPECTED_BUCKET,EXPECTED_REGION,
    EXPECTED_OBJECT_MANIFEST_SHA256,object_manifest_sha256
)

REGISTRY=ROOT/"registry/product_b_same_target_source_identity_pass_taxa_v0_1.csv"
RECOVERY=ROOT/"results/neon_aug_gbif_missing20_recovery_v1.json"
NEON_VOUCHER="3fed506c-d04f-4cd4-b373-bd602572f39b"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
N_PARQUET_RESTORED=510


def aggregate_batch(values:dict,registry_keys:set[str],counter:Counter):
    n=len(values["specieskey"])
    if any(len(v)!=n for v in values.values()):
        raise ValueError("unaligned scan columns")
    for i in range(n):
        key=str(values["specieskey"][i] or "").strip()
        mode=str(values["basisofrecord"][i] or "").strip().upper()
        state=str(values["occurrencestatus"][i] or "").strip().upper()
        datasetkey=str(values["datasetkey"][i] or "").strip().lower()
        if key not in registry_keys or mode not in MODES or state!="PRESENT":
            raise RuntimeError("restored scanner returned an unexpected record")
        counter[(key,mode,"raw_present")]+=1
        if datasetkey==NEON_VOUCHER:
            counter[(key,mode,"known_NEON_voucher_datasetkey")]+=1
        if not datasetkey:
            counter[(key,mode,"missing_datasetkey")]+=1


def run():
    import pyarrow.dataset as ds
    import pyarrow.fs as pafs

    with REGISTRY.open(encoding="utf-8",newline="") as f:
        registry=list(csv.DictReader(f))
    if len(registry)!=12:
        raise RuntimeError("expected all 12 historical Level A taxa")
    keys={str(x["resolved_snapshot_specieskey"]).strip():x["scientific_name"]
          for x in registry}
    if len(keys)!=12 or not all(keys):
        raise RuntimeError("frozen specieskey identity collision")
    receipt=json.loads(RECOVERY.read_text(encoding="utf-8"))
    if receipt["status"]!="historical_9705_parquet_manifest_exactly_recovered":
        raise RuntimeError("historical GBIF missing20 source metadata not verified")
    if receipt["candidate_historical_manifest_sha256"]!=EXPECTED_OBJECT_MANIFEST_SHA256:
        raise RuntimeError("historical source SHA mismatch")
    prefix=f"occurrence/{EXPECTED_SNAPSHOT_DATE}/"
    current=list_objects(prefix)
    if object_manifest_sha256(current)!=receipt["current_manifest_sha256"]:
        raise RuntimeError("current GBIF S3 listing drift after recovered source fingerprint")
    historical,repaired,unknown=partition_historical(current)
    if unknown or len(historical)!=9706 or len(repaired)!=N_PARQUET_RESTORED:
        raise RuntimeError("exact 510 restored object set changed")
    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    paths=[f"{EXPECTED_BUCKET}/{x.key}" for x in repaired]
    dataset=ds.dataset(paths,filesystem=fs,format="parquet")
    select=ds.field("specieskey").isin(sorted(keys))
    select=select & ds.field("basisofrecord").isin(list(MODES)) & (ds.field("occurrencestatus")=="PRESENT")
    scanner=dataset.scanner(
        columns=["specieskey","basisofrecord","occurrencestatus","datasetkey"],
        filter=select,batch_size=65536,use_threads=True
    )
    counts=Counter()
    for batch in scanner.to_batches():
        aggregate_batch(batch.to_pydict(),set(keys),counts)

    taxa=[]
    for key,name in sorted(keys.items(),key=lambda kv:kv[1]):
        by_mode={
          mode:{
            "restored_raw_present_occurrence_rows":counts[(key,mode,"raw_present")],
            "restored_raw_known_NEON_voucher_rows":counts[(key,mode,"known_NEON_voucher_datasetkey")],
            "restored_raw_missing_datasetkey_rows":counts[(key,mode,"missing_datasetkey")]
          } for mode in MODES
        }
        taxa.append({"taxon":name,"frozen_specieskey":key,"modes":by_mode,
           "total_restored_raw_present_occurrence_rows":
              sum(by_mode[m]["restored_raw_present_occurrence_rows"] for m in MODES)})
    per_mode={
        mode:sum(counts[(key,mode,"raw_present")] for key in keys) for mode in MODES
    }
    return {
      "schema":"284b.gbif_restored510_heldout12_source_exposure.v1",
      "status":"restored_510_focal_occurrence_exposure_scanned",
      "old_frozen_manifest_sha256":EXPECTED_OBJECT_MANIFEST_SHA256,
      "current_repaired_object_manifest_sha256":receipt["current_manifest_sha256"],
      "restored_parquet_objects_scanned":len(repaired),
      "historical_parquet_objects_not_scanned":9705,
      "taxa_predeclared":12,
      "specieskey_mode_raw_row_counts":taxa,
      "totals_by_source_mode":per_mode,
      "taxa_with_any_restored_raw_present_rows":sum(x["total_restored_raw_present_occurrence_rows"]>0 for x in taxa),
      "known_NEON_datasetkey_rows_inside_restored_files_only":
         sum(counts[(key,mode,"known_NEON_voucher_datasetkey")] for key in keys for mode in MODES),
      "original_signed_model_admitted_rows_reconstructed":False,
      "original_model_fit_completeness_comparison_resolved":False,
      "repaired_source_models_refitted":False,
      "historical_level_a_endpoint_unchanged":True,
      "NEON_plant_plot_species_outcomes_opened":False,
      "GBIF_record_identifiers_persisted":False,
      "raw_coordinates_persisted":False,
      "external_validation_authorized":False,
      "empirical_ledger_increment":0,
      "interpretation":"These are only raw occurrence records present in restored files for frozen specieskeys and basis-of-record modes. They cannot be interpreted as model-admitted/thinned counts, biological presences, or a sensitivity estimate for the original 0/12 source-coherence endpoint.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    v=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
       "status":v["status"],"restored":v["restored_parquet_objects_scanned"],
       "taxa_with_any_restored_rows":v["taxa_with_any_restored_raw_present_rows"],
       "totals":v["totals_by_source_mode"]}))


if __name__=="__main__":
    main()
