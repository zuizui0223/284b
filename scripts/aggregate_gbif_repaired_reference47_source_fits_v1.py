#!/usr/bin/env python3
"""Audit all 47 repaired-GBIF source fits without opening paired D or q95.

The only permitted inputs are original SHA-qualified 47-reference geometry
metadata, repaired-source *input* audit and each 48-cell model-fit artifact.
The audit checks all frozen 2,256 source/procedure/M fits, 2,000 fixed row
identities per sealed prediction, source-admitted counts, SHA fingerprints and
provenance. It never calculates between-source D or reference envelopes.
"""
from __future__ import annotations

import argparse,csv,hashlib,json
from pathlib import Path
from collections import Counter

MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
MS=(150,300,500)
SOURCE_ARM="repaired_2026-08-01_10215_parquet_files"
FIT_VERSION="284b.gbif_repaired_reference47_fixed_old_centers_fit_v1"

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def _require(condition,message):
    if not condition:raise RuntimeError(message)

def audit_taxon(entry:dict,geometry:dict,source:dict,contract:dict,inventory:list[dict],predictions_path:Path)->dict:
    """Fail-closed source-only structural fit audit for one frozen reference."""
    i=entry["index"]
    _require(contract.get("result_version")==FIT_VERSION,"repaired reference result version drift")
    _require(contract.get("panel")=="successor" and contract.get("taxon_index")==i
             and contract.get("taxon")==entry["taxon"],"repaired reference taxon identity drift")
    _require(contract.get("historical_specieskeys")==entry["historical_specieskeys"],"repaired historical key set changed")
    _require(contract.get("historical_key_count")==len(entry["historical_specieskeys"]),"repaired historical key count changed")
    _require(contract.get("original_qualification_artifact_id")==entry["original_qualification_artifact_id"],"original qualification artifact changed")
    _require(contract.get("original_fit_artifact_id")==entry["original_fit_artifact_id"],"original model artifact changed")
    _require(contract.get("GBIF_source_arm")==SOURCE_ARM and contract.get("added_restored_510_source_objects_included") is True,"repaired GBIF source arm not qualified")
    _require(contract.get("original_12_block_centers_sha256")==geometry["original_center_sha256"],"original spatial centers differ")
    _require(contract.get("core19_frame_sha256_by_M")==geometry["original_comparison_frame_sha256_by_M"],"original frozen comparison frames drift")
    _require(contract.get("repaired_source_thinned_presence_count")==source["repaired_thinned_n"],"repaired source-thinned counts differ")
    _require(contract.get("source_modes")==list(MODES),"source-mode universe changed")
    _require(contract.get("active_predictors")==[f"bio{i}" for i in range(1,20)],"CHELSA bio1..19 design changed")
    _require(contract.get("M_km")==list(MS) and contract.get("procedure_count")==8,"distance or procedure universe changed")
    _require(contract.get("expected_fit_cells")==48,"per-taxon original source cell denominator changed")
    _require(contract.get("sealed_fit_cells",0)+contract.get("unresolved_fit_cells",-1)==48,"sealed/unresolved denominator inconsistent")
    for flag in ("original_signed_comparison_frames_unchanged","same_frozen_core19_background_rows_used_for_both_sources",
                 "all_prediction_scores_finite_for_sealed_cells"):
        _require(contract.get(flag) is True,"fixed scientific condition not met: "+flag)
    for flag in ("background_rows_resampled_during_refit","posthoc_prediction_row_drop_used",
                 "paired_discordance_computed","reference_ceiling_opened_or_read",
                 "heldout_pairing_opened","process_knockout_computed","taxon_replaced",
                 "procedure_selected_from_outcome","M_selected_from_outcome",
                 "counts_as_empirical_conclusion","new_independent_holdout_or_biological_confirmation"):
        _require(contract.get(flag) is False,"source refit crossed information boundary: "+flag)
    _require(len(inventory)==48,"reference fit inventory not exactly 48")
    states={}
    procs=set()
    for r in inventory:
        try:
            key=(str(r["source"]),int(r["M_km"]),str(r["procedure"]))
            n=int(r["n_presence_thinned"])
        except (ValueError,KeyError) as exc:raise RuntimeError("invalid reference fit inventory row") from exc
        _require(key[0] in MODES and key[1] in MS,"reference cell source/M drifted")
        _require(key not in states,"duplicate source/M/procedure cell")
        _require(n==source["repaired_thinned_n"][key[0]],"refit source-thinned input drift")
        _require(int(r["n_background"])==2000,"original fixed comparison denominator changed")
        _require(r["core19_frame_sha256"]==geometry["original_comparison_frame_sha256_by_M"][str(key[1])],"cell comparison frame bytes changed")
        _require(r["state"] in ("core19_layer1_model_fit_sealed","core19_layer1_model_fit_unresolved"),"unrecognized fit state")
        states[key]=r["state"];procs.add(key[2])
    _require(len(procs)==8,"eight frozen procedures incomplete")
    _require(set(states)=={(mode,m,proc) for mode in MODES for m in MS for proc in procs},"source × M × procedure cartesian universe changed")
    sealed=sum(x=="core19_layer1_model_fit_sealed" for x in states.values())
    _require(sealed==contract["sealed_fit_cells"],"model-state signed contract mismatch")
    _require(48-sealed==contract["unresolved_fit_cells"],"model unresolved-count mismatch")
    _require(predictions_path.is_file(),"reference fit missing sealed prediction Parquet")
    _require(sha(predictions_path.read_bytes())==contract["prediction_surface_sha256"],"reference model predictions Parquet SHA changed")

    # Read a single taxon at a time. This is a score *integrity* check only;
    # it never pairs sources, estimates D, or computes a ceiling.
    import numpy as np,pandas as pd
    df=pd.read_parquet(predictions_path)
    required={"source","M_km","procedure","comparison_row_id","ecological_score"}
    _require(required.issubset(df.columns),"sealed prediction schema missing")
    if not df.empty:
        _require(np.isfinite(df["ecological_score"].to_numpy(dtype=float)).all(),"nonfinite model prediction score")
    got={}
    for (mode,m,proc),d in df.groupby(["source","M_km","procedure"]):
        key=(str(mode),int(m),str(proc))
        _require(key in states and states[key]=="core19_layer1_model_fit_sealed","sealed score rows without sealed fit")
        ids=d["comparison_row_id"].astype(str)
        _require(len(d)==2000 and ids.nunique()==2000,"sealed comparison rows not 2000 unique IDs")
        got[key]=len(d)
    _require(set(got)=={k for k,v in states.items() if v=="core19_layer1_model_fit_sealed"},"sealed source cell missing predictions")
    _require(len(df)==2000*sealed,"source prediction row count differs from sealed-cell denominator")
    return {
        "index":i,"taxon":entry["taxon"],"historical_key_count":len(entry["historical_specieskeys"]),
        "sealed_fit_cells":sealed,"unresolved_fit_cells":48-sealed,
        "score_rows_integrity_verified":len(df),
        "original_geometry_sha256":geometry["original_center_sha256"],
        "model_prediction_sha256":contract["prediction_surface_sha256"],
        "repaired_source_thinned_counts":source["repaired_thinned_n"],
        "procedures":sorted(procs),
    }

def audit_all(manifest:dict,geometry:dict,source:dict,fit_root:Path)->dict:
    entries=manifest.get("entries",[])
    _require(manifest.get("status")=="PREDECLARED_REFERENCE47_ORIGINAL_GEOMETRY_ONLY"
             and len(entries)==47 and [x.get("index") for x in entries]==list(range(47)),"original reference47 model/geometry population not frozen")
    _require(geometry.get("status")=="ALL_47_ORIGINAL_SIGNED_REFERENCE_GEOMETRIES_VERIFIED_NO_MODELS"
             and geometry.get("reference_taxa_original_geometry_exactly_reproduced")==47,"47 original geometries are not all verified")
    _require(geometry.get("historical_source_manifest_sha256")==manifest["original_source_manifest_sha256"],"original source snapshot manifest changed")
    _require(geometry.get("repaired_source_reference_model_refits_completed")==0
             and geometry.get("calibration_reference_q95_opened") is False,"geometry metadata crossed scientific endpoint")
    _require(source.get("status")=="all_47_original_reference_source_input_parity_and_restoration_qualified"
             and source.get("prespecified_reference_taxa")==47
             and source.get("completed_and_verified_shards")==8,"repaired reference47 source audit not qualified")
    _require(source.get("original_24_calibration_q95_refitted") is False,"input audit opened reference q95")
    g={r["index"]:r for r in geometry["reference_taxa"]}
    s={r["taxon_index"]:r for r in source["fixed_taxon_input_deltas"]}
    _require(set(g)==set(s)==set(range(47)) and len(g)==len(s)==47,"reference taxon indexes not uniquely complete")
    found=list(fit_root.rglob("contract.json"))
    _require(len(found)==47,"exactly 47 repaired reference source-fit contracts required")
    reports={}
    for path in found:
        root=path.parent
        c=json.loads(path.read_text(encoding="utf-8"))
        idx=c.get("taxon_index")
        _require(isinstance(idx,int) and 0<=idx<47 and idx not in reports,"duplicate/unrecognized source-fit taxon index")
        inv=list(csv.DictReader((root/"fit_inventory.csv").read_text(encoding="utf-8").splitlines()))
        reports[idx]=audit_taxon(entries[idx],g[idx],s[idx],c,inv,root/"sealed_prediction_surfaces.parquet")
    _require(set(reports)==set(range(47)),"missing fixed source-fit reference taxon")
    allprocs={tuple(r["procedures"]) for r in reports.values()}
    _require(len(allprocs)==1,"48-cell procedure library changed across reference taxa")
    cells=47*48;sealed=sum(r["sealed_fit_cells"] for r in reports.values())
    return {
        "schema":"284b.gbif_repaired_reference47_source_fit_audit.v1",
        "status":"ALL_47_REPAIRED_REFERENCE_SOURCE_FITS_INTEGRITY_VERIFIED_NO_Q95",
        "source_arm":SOURCE_ARM,"reference_taxa_expected":47,"reference_taxa_verified":47,
        "fit_cells_expected":cells,"fit_cells_sealed":sealed,"fit_cells_unresolved":cells-sealed,
        "source_prediction_rows_integrity_verified":sum(r["score_rows_integrity_verified"] for r in reports.values()),
        "predictor_count":19,"procedure_count":8,"M_km":list(MS),
        "calibration_24_q95_opened":False,"heldout12_paired_discordance_opened":False,
        "independent_empirical_biological_evidence":False,"empirical_ledger_increment":0,
        "submission_status":"HOLD",
        "taxa":[reports[i] for i in range(47)],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--geometry",type=Path,required=True)
    p.add_argument("--source-audit",type=Path,required=True)
    p.add_argument("--fits-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    o=audit_all(*(json.loads(x.read_text(encoding="utf-8")) for x in (a.manifest,a.geometry,a.source_audit)),a.fits_root)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:o[k] for k in ("status","reference_taxa_verified","fit_cells_sealed","fit_cells_unresolved","submission_status")}))

if __name__=="__main__":main()
