#!/usr/bin/env python3
"""Reproduce source lineage for all seven frozen NEON candidate taxa.

Reads the precisely reconstructed original 9705-file 2026-08-01 GBIF public
snapshot. Verifies source-specific thinning counts against each original
signed 48-fit inventory, then counts known NEON voucher datasetKey incidence.

No NEON plot data or species outcomes. No model refit; no record identifiers,
coordinates or event dates are persisted in the output.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))
CONFIG=ROOT/"config/neon_seven_taxon_gbif_lineage_v1.json"
RECOVERY=ROOT/"results/neon_aug_gbif_missing20_recovery_v1.json"
PILOT=ROOT/"results/neon_original_gbif_historical_replay_v2.json"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")


def signed_source_counts(entry:dict, archive:Path)->dict[str,int]:
    raw=archive.read_bytes()
    if "sha256:"+sha256(raw).hexdigest()!=entry["fit_artifact_digest"]:
        raise RuntimeError("Original signed model archive digest mismatch")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        contract=json.loads(z.read("contract.json"))
        if contract["taxon"]!=entry["taxon"] or contract["taxon_index"]!=entry["original_index"]:
            raise RuntimeError("Signed fit contract taxon/index mismatch")
        inv=list(csv.DictReader(z.read("fit_inventory.csv").decode().splitlines()))
    if len(inv)!=48:
        raise RuntimeError("Signed original fit inventory does not have 48 source/procedure/M cells")
    expected={}
    for mode in MODES:
        values={int(row["n_presence_thinned"]) for row in inv if row["source"]==mode}
        if len(values)!=1:
            raise RuntimeError("Original signed fit presence denominator varies within source")
        expected[mode]=values.pop()
    return expected


def classify_source_replay(entry:dict, expected:dict, counts:dict)->dict:
    matched={m:counts[m]["source_thinned_model_presence_rows"]==expected[m] for m in MODES}
    direct=sum(counts[m]["source_thinned_known_NEON_dataset_rows"] for m in MODES)
    if not all(matched.values()):
        state="historical_model_input_count_parity_FAILED"
        direct_admissible=None
    else:
        state=("known_NEON_voucher_dataset_in_historical_training"
               if direct else "known_NEON_voucher_datasetkey_not_observed")
        direct_admissible=direct
    return {
      "taxon":entry["taxon"],"specieskey":entry["specieskey"],
      "signed_original_fit_artifact_id":entry["fit_artifact_id"],
      "signed_source_n":expected,
      "source_count_reproduced":matched,
      "source_counts":counts,
      "state":state,
      "known_NEON_datasetkey_model_input_rows":direct_admissible,
      "full_independence_of_NEON_plots_verified":False,
    }


def run(archive_dir:Path)->dict:
    import pandas as pd
    import pyarrow.dataset as ds
    import pyarrow.fs as pafs
    import pyarrow as pa
    from sdmr.data import thin_to_grid
    from scripts.audit_original_gbif_neon_datasetkey_pilot_v1 import tally_retained_datasetkeys
    from scripts.audit_original_gbif_neon_historical_replay_v2 import frozen_parquet_paths
    from scripts.run_same_target_layer1_baseline_fit_taxon import (
        _adapter_row,_retained_source_frames,SELECTED_COLUMNS,DATASET_PATH,MODES as MODEL_MODES
    )
    from product_b_v7_2.snapshot_transport import EXPECTED_REGION

    design=json.loads(CONFIG.read_text(encoding="utf-8"))
    recovery=json.loads(RECOVERY.read_text(encoding="utf-8"))
    prior=json.loads(PILOT.read_text(encoding="utf-8"))
    assert design["schema"]=="284b.neon_historical_model_source_lineage7.v1"
    assert design["status"]=="FROZEN_META_AUDIT_OF_ORIGINAL_INPUTS_NO_NEON_PLOT_OUTCOMES"
    assert design["original_source_modes"]==list(MODES)==list(MODEL_MODES)
    assert design["original_parquet_objects"]==9705
    assert recovery["status"]=="historical_9705_parquet_manifest_exactly_recovered"
    assert recovery["candidate_historical_manifest_sha256"]==design["recovered_object_manifest_sha256"]
    assert prior["status"]=="SIGNED_SOURCE_INPUTS_RECONSTRUCTED_WITH_KNOWN_NEON_VOUCHER_DATASET_ROWS"
    original=design["taxon_inventory"]
    if len(original)!=7 or len({e["specieskey"] for e in original})!=7 or len({e["taxon"] for e in original})!=7:
        raise RuntimeError("Seven fixed original taxon identities changed")
    expected={
        entry["taxon"]:signed_source_counts(
            entry,archive_dir/f"fit_{entry['original_index']}.zip"
        ) for entry in original
    }
    prior0=expected["Artemisia tridentata"]
    if prior0 != prior["original_model_expected_source_counts"]:
        raise RuntimeError("First-taxon signed count does not match previously audited source model")
    if "/2026-08-01/" not in DATASET_PATH:
        raise RuntimeError("Original source snapshot pointer changed")
    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    infos=fs.get_file_info(pafs.FileSelector(DATASET_PATH,recursive=False))
    paths=frozen_parquet_paths([x.path for x in infos if x.type==pa.fs.FileType.File])
    source=ds.dataset(paths,filesystem=fs,format="parquet")
    keys={e["specieskey"]:e for e in original}
    expr=(
       ds.field("specieskey").isin(sorted(keys)) &
       ds.field("basisofrecord").isin(list(MODES)) &
       (ds.field("occurrencestatus")=="PRESENT")
    )
    scan=source.scanner(columns=list(SELECTED_COLUMNS),filter=expr,batch_size=65536,use_threads=True)
    raw={key:{mode:[] for mode in MODES} for key in keys}
    for batch in scan.to_batches():
        vals=batch.to_pydict()
        for i in range(batch.num_rows):
            skey=str(vals["specieskey"][i] or "").strip()
            mode=str(vals["basisofrecord"][i] or "").strip().upper()
            if skey not in raw or mode not in MODES:
                raise RuntimeError("Unexpected taxa or source mode in original S3 scanner")
            raw[skey][mode].append(_adapter_row(vals,i))

    reports=[]
    for entry in original:
        source_rows=raw[entry["specieskey"]]
        retained=_retained_source_frames(entry["taxon"],
            source_rows[MODES[0]],source_rows[MODES[1]])
        counts,missing=tally_retained_datasetkeys(
            source_rows,retained,thin_to_grid,
            cell_degrees=design["original_grid_thinning_degrees"]
        )
        rep=classify_source_replay(entry,expected[entry["taxon"]],counts)
        rep["raw_missing_datasetkey_rows"]=missing
        if entry["taxon"]=="Artemisia tridentata":
            if counts!=prior["source_counts"] or rep["known_NEON_datasetkey_model_input_rows"]!=2:
                raise RuntimeError("Seven-taxon replay fails independently validated Artemisia source pilot")
        reports.append(rep)

    parity=all(all(v for v in x["source_count_reproduced"].values()) for x in reports)
    direct=sum(x["known_NEON_datasetkey_model_input_rows"] or 0 for x in reports)
    return {
       "schema":"284b.neon_historical_model_source_lineage7_results.v1",
       "status":"seven_original_source_denominators_reproduced"
          if parity else "ORIGINAL_SOURCE_COUNT_PARITY_FAILURE_STOP",
       "original_source_snapshot":"2026-08-01",
       "recovered_original_object_sha256":design["recovered_object_manifest_sha256"],
       "historical_parquet_objects_scanned":9705,
       "October_restored_files_excluded":510,
       "frozen_candidate_taxa":7,
       "taxa_exactly_matching_both_signed_source_counts":
          sum(all(x["source_count_reproduced"].values()) for x in reports),
       "taxa_with_known_NEON_voucher_dataset_in_training":
          sum((x["known_NEON_datasetkey_model_input_rows"] or 0)>0 for x in reports if all(x["source_count_reproduced"].values())),
       "known_NEON_voucher_dataset_thinned_model_input_rows_total":
          direct if parity else None,
       "taxon_level_source_provenance":reports,
       "NEON_plot_species_labels_read":False,
       "NEON_plant_files_downloaded":False,
       "full_independent_external_validation_authorized":False,
       "original_LevelA_endpoint_unmodified":True,
       "model_refit_performed":False,
       "empirical_ledger_increment":0,
       "interpretation":"A matched source denominator licenses a per-dataset-key dependency audit, not independence from all NEON labels or other GBIF copies. A dataset key found in original model inputs disqualifies blanket unqualified source-level independence; direct plot label overlap remains unknown."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fit-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    res=run(a.fit_dir)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:res[k] for k in [
       "status","taxa_exactly_matching_both_signed_source_counts",
       "taxa_with_known_NEON_voucher_dataset_in_training",
       "known_NEON_voucher_dataset_thinned_model_input_rows_total"
    ]}))
    if res["status"]!="seven_original_source_denominators_reproduced":
        raise SystemExit("Original seven-taxon source model counts are not reproducible")


if __name__=="__main__":
    main()
