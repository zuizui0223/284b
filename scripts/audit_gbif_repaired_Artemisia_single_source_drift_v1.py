#!/usr/bin/env python3
"""Single-source model-prediction drift under repaired GBIF data for one taxon.

Compare the signed original and refitted source-specific models on EXACTLY the
same 2000 comparison-row IDs per M, without computing across-source Schoener D.
This is a post-freeze technical sensitivity pilot; it cannot independently
re-evaluate 284b's 12 held-out taxon confirmation or its 47-taxon q95 reference.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
from io import BytesIO
import csv
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd

MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
ORIGINAL_RESULT="product_b_same_target_heldout_core19_layer1_fit_taxon_v0.4"
REPAIRED_RESULT="284b.gbif_repaired_Artemisia_fixed_old_centers_fit_v1"
SIGNATURE="sha256:43ae62899e3a335a00b3ee666f534aee02cfaf9cab517df13d9eb542092350c8"


def source_drift(old, repaired)->float:
    a,b=np.asarray(old,float),np.asarray(repaired,float)
    if a.shape!=b.shape or a.shape!=(2000,) or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Original and repaired scores must be finite, equal 2000-row length")
    if (a<0).any() or (b<0).any() or a.sum()<=0 or b.sum()<=0:
        raise ValueError("Both source score vectors must be nonnegative with positive total mass")
    return float(.5*np.abs(a/a.sum()-b/b.sum()).sum())


def load_original(path:Path):
    raw=path.read_bytes()
    if "sha256:"+sha256(raw).hexdigest()!=SIGNATURE:
        raise ValueError("Original pre-October fit ZIP is not the signed scientific source")
    with zipfile.ZipFile(BytesIO(raw)) as z:
        contract=json.loads(z.read("contract.json"))
        cells=list(csv.DictReader(z.read("fit_inventory.csv").decode().splitlines()))
        scores_raw=z.read("sealed_prediction_surfaces.parquet")
        if sha256(scores_raw).hexdigest()!=contract["prediction_surface_sha256"]:
            raise ValueError("Original signed prediction Parquet digest differs")
        scores=pd.read_parquet(BytesIO(scores_raw))
    if contract["result_version"]!=ORIGINAL_RESULT or contract["taxon"]!="Artemisia tridentata":
        raise ValueError("Original fitted model is not the intended taxon/result")
    return contract,cells,scores


def inspect(original_zip:Path,repaired_dir:Path)->tuple[dict,list[dict]]:
    oc,old_rows,old=load_original(original_zip)
    rc=json.loads((repaired_dir/"contract.json").read_text(encoding="utf-8"))
    if (rc.get("result_version")!=REPAIRED_RESULT or
            rc.get("GBIF_source_arm")!="repaired_2026-08-01_10215_parquet_files" or
            rc.get("original_12_block_centers_inherited_from_SHA_verified_original") is not True or
            rc.get("taxon")!="Artemisia tridentata" or rc.get("taxon_index")!=0):
        raise ValueError("Repaired fit is not the predeclared single-taxon fixed-geometry arm")
    if rc.get("paired_discordance_computed") is not False or rc.get("reference_ceiling_opened_or_read") is not False:
        raise ValueError("Source fit violated frozen no-paired-outcome boundary")
    if rc.get("core19_frame_sha256_by_M")!=oc["core19_frame_sha256_by_M"]:
        raise ValueError("Repaired and original source fits used different 2000-row evaluation frames")
    new_rows=list(csv.DictReader((repaired_dir/"fit_inventory.csv").read_text(encoding="utf-8").splitlines()))
    new_data=(repaired_dir/"sealed_prediction_surfaces.parquet").read_bytes()
    if sha256(new_data).hexdigest()!=rc["prediction_surface_sha256"]:
        raise ValueError("New source-specific model prediction ZIP inventory digest mismatch")
    new=pd.read_parquet(BytesIO(new_data))
    keycols=["source","M_km","procedure"]
    required=set(keycols+["comparison_row_id","ecological_score"])
    if required-set(old):
        raise ValueError("Original signed model source scores are missing columns")
    if required-set(new):
        # A fully unresolved repaired fit can legitimately have no sealed
        # prediction rows; preserve 48 explicit unresolved inventory states.
        if not new.empty or rc.get("sealed_fit_cells", -1)!=0:
            raise ValueError("Repaired source fit claims sealed predictions but lacks required columns")
    if len(old_rows)!=48 or len(new_rows)!=48:
        raise ValueError("Original or new source fit inventory is not exactly 48")
    old_i={(r["source"],int(r["M_km"]),r["procedure"]):r for r in old_rows}
    new_i={(r["source"],int(r["M_km"]),r["procedure"]):r for r in new_rows}
    if set(old_i)!=set(new_i) or len(old_i)!=48:
        raise ValueError("Source-by-M-by-procedure universe changed")
    old_groups={(source,int(m),proc):x.sort_values("comparison_row_id")
                for (source,m,proc),x in old.groupby(keycols)}
    new_groups=({(source,int(m),proc):x.sort_values("comparison_row_id")
                for (source,m,proc),x in new.groupby(keycols)} if not new.empty else {})
    outcomes=[]
    for (source,m,proc),a in sorted(old_i.items()):
        b=new_i[(source,m,proc)]
        if a["state"]!="core19_layer1_model_fit_sealed":
            raise ValueError("Historical original source-model fit should have been sealed in all 48 cells")
        if a["core19_frame_sha256"]!=b["core19_frame_sha256"]:
            raise ValueError("Original and repaired frame hash mismatch for one source cell")
        if b["state"]!="core19_layer1_model_fit_sealed":
            outcomes.append({"source":source,"M_km":m,"procedure":proc,
                             "state":"repaired_source_model_fit_unresolved",
                             "old_thinned_presence":int(a["n_presence_thinned"]),
                             "repaired_thinned_presence":int(b["n_presence_thinned"]),
                             "source_self_prediction_tv_distance":""})
            continue
        if (source,m,proc) not in old_groups or (source,m,proc) not in new_groups:
            raise ValueError("An expected sealed source score group has no output")
        x,y=old_groups[(source,m,proc)],new_groups[(source,m,proc)]
        ids=x["comparison_row_id"].astype(str).tolist()
        if (len(ids)!=2000 or ids!=y["comparison_row_id"].astype(str).tolist()
                or len(set(ids))!=2000):
            raise ValueError("Original and repaired score prediction row identity changed")
        d=source_drift(x["ecological_score"].to_numpy(float),y["ecological_score"].to_numpy(float))
        outcomes.append({"source":source,"M_km":m,"procedure":proc,
                         "state":"source_self_prediction_comparable",
                         "old_thinned_presence":int(a["n_presence_thinned"]),
                         "repaired_thinned_presence":int(b["n_presence_thinned"]),
                         "source_self_prediction_tv_distance":d})
    if len(outcomes)!=48:raise ValueError("Incomplete source-score drift comparison")
    bymode=defaultdict(list)
    for x in outcomes:bymode[x["source"]].append(x)
    summary={
        "schema":"284b.gbif_repaired_Artemisia_original_center_single_source_prediction_drift.v1",
        "status":"exploratory_within_source_prediction_drift_only",
        "taxon":"Artemisia tridentata",
        "source_modes":list(MODES),
        "source_cells_expected":48,
        "source_cells_safely_comparable":sum(x["state"]=="source_self_prediction_comparable" for x in outcomes),
        "unresolved_source_cells":sum(x["state"]=="repaired_source_model_fit_unresolved" for x in outcomes),
        "source_mode_summaries":{
           mode:{
               "cells_expected":24,
               "comparable":sum(r["state"]=="source_self_prediction_comparable" for r in bymode[mode]),
               "unresolved":sum(r["state"]!="source_self_prediction_comparable" for r in bymode[mode]),
               "median_tv_when_comparable":(
                  float(np.median([r["source_self_prediction_tv_distance"] for r in bymode[mode]
                       if r["state"]=="source_self_prediction_comparable"]))
                  if any(r["state"]=="source_self_prediction_comparable" for r in bymode[mode])
                  else None),
           } for mode in MODES
        },
        "historical_source_fit_SHA256":SIGNATURE,
        "repaired_model_prediction_SHA256":rc["prediction_surface_sha256"],
        "historical_original_core19_frame_SHA256_by_M":oc["core19_frame_sha256_by_M"],
        "NEON_field_outcomes_read":False,
        "cross_source_paired_discordance_computed":False,
        "repaired_47taxon_q95_calibrated":False,
        "full_repaired_12taxon_endpoint_opened":False,
        "original_level_A_0_of_12_unchanged":True,
        "empirical_ledger_increment":0,
        "limitations":[
          "Single predeclared taxon (n=1); 48 correlated source-cell comparisons, no independent taxa.",
          "Original and repaired within-source predictions are evaluated on identical frozen background rows and original spatial block centers.",
          "Comparing each source with itself across two versions is not a test of between-source coherence or biological truth.",
          "The 47-reference repaired q95 and 12-taxon heldout sensitivity remain separate and uncomputed.",
        ],
    }
    return summary,outcomes


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-fit-zip",type=Path,required=True)
    p.add_argument("--repaired-dir",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    p.add_argument("--out-csv",type=Path,required=True)
    a=p.parse_args()
    summary,rows=inspect(a.original_fit_zip,a.repaired_dir)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with a.out_csv.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({key:summary[key] for key in (
        "status","source_cells_safely_comparable","unresolved_source_cells","source_mode_summaries"
    )}))


if __name__=="__main__":
    main()
