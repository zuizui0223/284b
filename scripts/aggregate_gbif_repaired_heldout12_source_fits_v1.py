#!/usr/bin/env python3
"""Verify all 576 sealed source-specific refit cells for 12 original heldout taxa.

The same 12 historical GBIF specieskeys, 12-block centers, three 2,000-row
background frames, 8 procedures and 2 modes are enforced. No between-mode
Schoener D or restored 12-taxon q95 comparison may be opened here.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
MS=(150,300,500)
FIT_RESULT="284b.gbif_repaired_heldout12_fixed_old_centers_fit_v1"

def require(ok,why):
    if not ok:raise RuntimeError(why)

def check_inputs(manifest,geometry,source_audit):
    e=manifest.get("entries",[])
    require(manifest.get("status")=="PREDECLARED_HELDOUT12_ORIGINAL_GEOMETRY_ONLY"
            and len(e)==12 and [x.get("index") for x in e]==list(range(12)),
            "Original 12 fixed heldout taxonomy manifest drift")
    require(geometry.get("status")=="ALL_12_ORIGINAL_SIGNED_HELDOUT_GEOMETRIES_VERIFIED_NO_REPAIRED_MODELS"
            and geometry.get("original_heldout_geometry_exactly_reproduced")==12
            and geometry.get("historical_source_manifest_sha256")==manifest["original_source_manifest_sha256"]
            and geometry.get("repaired_source_heldout_model_refits_completed")==0
            and geometry.get("repaired_47_reference_q95_calibrated") is False
            and geometry.get("repaired_12_heldout_paired_outcomes_opened") is False,
            "Original 12 heldout spatial geometry not verified or outcomes opened")
    require(source_audit.get("status")=="REPAIRED_SOURCE_THINNING_QUANTIFIED_12_TAXA_NO_MODEL_REFIT"
            and source_audit.get("taxa_qualified_repaired_raw_parity")==12
            and source_audit.get("repaired_SDM_models_fit") is False
            and source_audit.get("repaired_reference_q95_opened") is False,
            "Original heldout12 repaired-source input audit not qualified")
    g=geometry.get("taxa",[]);raw=source_audit.get("per_taxon_source_mode_result",[])
    require(len(g)==len(raw)==12,"Missing heldout12 geometry or source audit rows")
    for i in range(12):
        require(g[i]["index"]==i and g[i]["taxon"]==e[i]["taxon"]
                and g[i]["historical_specieskey"]==e[i]["historical_specieskey"]
                and raw[i]["taxon"]==e[i]["taxon"]
                and raw[i]["original_specieskey"]==e[i]["historical_specieskey"],
                "Heldout12 index/taxon/key alignment changed")
    return e,g,raw

def audit_one(entry,geometry,source,contract,inventory,prediction):
    import numpy as np,pandas as pd
    i=entry["index"]
    require(contract.get("result_version")==FIT_RESULT
            and contract.get("panel")=="heldout"
            and contract.get("taxon_index")==i
            and contract.get("taxon")==entry["taxon"]
            and contract.get("specieskey")==entry["historical_specieskey"],
            "Restored source heldout model identity drift")
    require(contract.get("original_qualification_artifact_id")==entry["original_qualification_artifact_id"]
            and contract.get("original_fit_artifact_id")==entry["original_fit_artifact_id"],
            "Original signed heldout source frame/model provenance drift")
    require(contract.get("GBIF_source_arm")=="repaired_2026-08-01_10215_parquet_files"
            and contract.get("added_restored_510_source_objects_included") is True,
            "GBIF restored 10215-object source arm not verified")
    require(contract.get("core19_frame_sha256_by_M")==geometry["original_comparison_frame_sha256_by_M"]
            and contract.get("original_12_block_centers_sha256")==geometry["original_center_sha256"],
            "Original heldout M frames or 12 spatial centers changed")
    require(contract.get("repaired_source_thinned_presence_count")==source["repaired_source_thinned_presence"],
            "Restored heldout source thinned counts changed")
    require(contract.get("source_modes")==list(MODES) and contract.get("active_predictors")==[f"bio{x}" for x in range(1,20)]
            and contract.get("M_km")==list(MS) and contract.get("procedure_count")==8,
            "Source model ecological predictors, M or procedure universe changed")
    require(contract.get("expected_fit_cells")==48 and len(inventory)==48
            and contract.get("sealed_fit_cells",0)+contract.get("unresolved_fit_cells",-1)==48,
            "Heldout12 source model 48-cell denominator drift")
    for flag in ("original_signed_comparison_frames_unchanged",
                 "same_frozen_core19_background_rows_used_for_both_sources",
                 "all_prediction_scores_finite_for_sealed_cells"):
        require(contract.get(flag) is True,"Heldout source frame invariance not met: "+flag)
    for flag in ("paired_discordance_computed","reference_ceiling_opened_or_read",
                 "heldout_pairing_opened","process_knockout_computed",
                 "counts_as_empirical_conclusion","new_independent_holdout_or_biological_confirmation",
                 "background_rows_resampled_during_refit","posthoc_prediction_row_drop_used",
                 "taxon_replaced","M_selected_from_outcome","procedure_selected_from_outcome"):
        require(contract.get(flag) is False,"Heldout source refit crossed boundary: "+flag)
    state={}
    methods=set()
    for row in inventory:
        key=(str(row["source"]),int(row["M_km"]),str(row["procedure"]))
        require(key[0] in MODES and key[1] in MS and key not in state,
                "Missing/duplicate/non-original heldout source-model state")
        require(row["state"] in ("core19_layer1_model_fit_sealed","core19_layer1_model_fit_unresolved"),
                "Invalid heldout source model state")
        require(int(row["n_background"])==2000
                and int(row["n_presence_thinned"])==source["repaired_source_thinned_presence"][key[0]]
                and row["core19_frame_sha256"]==geometry["original_comparison_frame_sha256_by_M"][str(key[1])],
                "Heldout original 2000-row frame SHA or presence counts changed")
        state[key]=row["state"];methods.add(key[2])
    require(len(methods)==8 and set(state)=={(mode,m,p) for mode in MODES for m in MS for p in methods},
            "Heldout 48 source × M × method cell universe changed")
    sealed=sum(x=="core19_layer1_model_fit_sealed" for x in state.values())
    require(sealed==contract["sealed_fit_cells"] and 48-sealed==contract["unresolved_fit_cells"],
            "Heldout source model signed sealed/unresolved totals mismatch")
    require(prediction.is_file() and hashlib.sha256(prediction.read_bytes()).hexdigest()==contract["prediction_surface_sha256"],
            "Repaired heldout prediction score file digest mismatch")
    score=pd.read_parquet(prediction)
    needed={"source","M_km","procedure","comparison_row_id","ecological_score"}
    require(needed.issubset(score.columns),"Heldout source prediction schema incomplete")
    require(score.empty or np.isfinite(score["ecological_score"].to_numpy(float)).all(),
            "Heldout source model predictions nonfinite")
    sealed_keys={k for k,v in state.items() if v=="core19_layer1_model_fit_sealed"}
    ids_by_m={}
    actual=set()
    for (mode,m,p),frame in score.groupby(["source","M_km","procedure"]):
        key=(str(mode),int(m),str(p))
        require(key in sealed_keys and key not in actual,"Prediction rows from unresolved/unlisted heldout source fit")
        ids=frame["comparison_row_id"].astype(str)
        require(len(ids)==2000 and ids.nunique()==2000,"Heldout frozen 2000-row prediction identity incomplete")
        signature=tuple(sorted(ids))
        if int(m) in ids_by_m:
            require(ids_by_m[int(m)]==signature,"Heldout identical frozen M row IDs differ between methods/modes")
        else:ids_by_m[int(m)]=signature
        actual.add(key)
    require(actual==sealed_keys and len(score)==2000*sealed,
            "Repaired heldout model score surface incomplete")
    return {"index":i,"taxon":entry["taxon"],"sealed_source_cells":sealed,
            "unresolved_source_cells":48-sealed,"score_rows_verified":len(score),
            "original_center_sha256":geometry["original_center_sha256"],
            "repaired_prediction_sha256":contract["prediction_surface_sha256"]}

def aggregate(manifest,geometry,source_audit,root):
    entries,geom,source=check_inputs(manifest,geometry,source_audit)
    all_contracts=list(root.rglob("contract.json"))
    require(len(all_contracts)==12,"Expected exactly 12 repaired source-specific heldout contracts")
    out={}
    for path in all_contracts:
        c=json.loads(path.read_text(encoding="utf-8"))
        i=c.get("taxon_index")
        require(isinstance(i,int) and i in range(12) and i not in out,
                "Duplicate or unknown repaired heldout fit taxon index")
        inventory=list(csv.DictReader((path.parent/"fit_inventory.csv").read_text(encoding="utf-8").splitlines()))
        out[i]=audit_one(entries[i],geom[i],source[i],c,inventory,path.parent/"sealed_prediction_surfaces.parquet")
    require(set(out)==set(range(12)),"Not all original 12 heldout source models sealed")
    sealed=sum(x["sealed_source_cells"] for x in out.values())
    return {"schema":"284b.gbif_repaired_heldout12_source_fit_audit.v1",
            "status":"ALL_12_REPAIRED_HELDOUT_SOURCE_MODELS_INTEGRITY_VERIFIED_PAIRING_CLOSED",
            "heldout_taxa_expected":12,"heldout_taxa_verified":12,
            "source_fit_cells_expected":576,
            "source_fit_cells_sealed":sealed,
            "source_fit_cells_unresolved":576-sealed,
            "source_score_rows_verified":2000*sealed,
            "reference_q95_opened":False,"heldout12_paired_discordance_opened":False,
            "NEON_field_outcomes_read":False,
            "independent_biological_confirmation":False,
            "empirical_ledger_increment":0,"submission_status":"HOLD",
            "taxa":[out[i] for i in range(12)]}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--manifest",required=True,type=Path)
    a.add_argument("--geometry",required=True,type=Path)
    a.add_argument("--source",required=True,type=Path)
    a.add_argument("--fits-root",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    p=a.parse_args()
    data=[json.loads(x.read_text(encoding="utf-8")) for x in (p.manifest,p.geometry,p.source)]
    result=aggregate(*data,p.fits_root)
    p.out.parent.mkdir(parents=True,exist_ok=True)
    p.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","heldout_taxa_verified",
                                      "source_fit_cells_sealed","source_fit_cells_unresolved")}))
if __name__=="__main__":main()
