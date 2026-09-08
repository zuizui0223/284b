#!/usr/bin/env python3
"""Lightweight outcome-blind core19 readiness diagnostic for v0.3 unresolved cells.

Only the prospectively fixed CHELSA manifest class ``core_climate`` (bio1..19)
is extracted. Candidate coordinates, M geometry and seed metadata are reproduced
from the exact v0.3 parent receipt. No model fit, score, D, reference or held-out
pairing is read or computed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
CORE19=ROOT/"config/product_b_same_target_core19_requalification_contract_v0_4.json"
FRAME=ROOT/"config/product_b_same_target_source_common_frame_contract_v0_1.json"
SUCCESSOR_PARENT="product_b_same_target_successor_finite_frame_preflight_taxon_v0.3"
HELDOUT_PARENT="product_b_same_target_heldout_finite_frame_preflight_taxon_v0.3"
RESULT="product_b_same_target_core19_readiness_diagnostic_taxon_v0.4"


def _hash_centers(x: np.ndarray)->str:
    return sha256(np.asarray(x,dtype="<f8").tobytes(order="C")).hexdigest()


def _helpers(panel:str):
    if panel=="successor":
        from scripts.run_same_target_successor_layer1_fit_taxon import MODES,_retained_source_frames,_scan_taxon
        return MODES,_retained_source_frames,_scan_taxon
    from scripts.run_same_target_layer1_baseline_fit_taxon import MODES,_retained_source_frames,_scan_taxon
    return MODES,_retained_source_frames,_scan_taxon


def main()->int:
    from sdmr.data import OccurrenceAdmissionConfig,admit_occurrences,extract_raster_values,load_gbif_download,raster_specs_from_chelsa_manifest,thin_to_grid
    from sdmr.data.background import occurrence_buffer_membership,sample_target_group_background
    from sdmr.validation import make_presence_spatial_partition
    ap=argparse.ArgumentParser(); ap.add_argument("--panel",choices=("successor","heldout"),required=True); ap.add_argument("--taxon-index",type=int,required=True); ap.add_argument("--parent-v0-3-dir",required=True); ap.add_argument("--target-group",required=True); ap.add_argument("--chelsa-manifest",required=True); ap.add_argument("--output-dir",required=True); args=ap.parse_args()
    panel=str(args.panel); contract=json.loads(CORE19.read_text()); frame=json.loads(FRAME.read_text())
    if contract.get("contract_version")!="product_b_same_target_core19_requalification_v0.4": raise RuntimeError("wrong core19 prospective contract")
    parent_path=Path(args.parent_v0_3_dir)/"receipt.json"; parent_bytes=parent_path.read_bytes(); parent=json.loads(parent_bytes)
    expected=SUCCESSOR_PARENT if panel=="successor" else HELDOUT_PARENT
    if parent.get("result_version")!=expected or int(parent.get("taxon_index",-1))!=int(args.taxon_index): raise RuntimeError("wrong exact v0.3 parent")
    for k in (("model_fit_opened","prediction_scores_computed","paired_discordance_opened","reference_ceiling_computed","heldout_12_paired_discordance_read","process_knockout_opened") if panel=="successor" else ("model_refit_opened","prediction_scores_computed","paired_discordance_opened","reference_ceiling_read","heldout_pairing_opened","process_knockout_opened")):
        if parent.get(k) is not False: raise RuntimeError(f"v0.3 parent crossed boundary: {k}")
    cells={int(c["M_km"]):dict(c) for c in parent["cells"]}; unresolved=[m for m in (150,300,500) if cells[m].get("state")!="finite_comparison_frame_frozen"]
    if not unresolved: raise RuntimeError("lightweight readiness diagnostic may run only for v0.3-unresolved taxa")
    seeds={int(c["candidate_sampling_random_state"]) for c in cells.values()}
    if len(seeds)!=1: raise RuntimeError("v0.3 candidate seed drifted"); seed=seeds.pop()
    seed=next(iter(seeds)) if seeds else int(cells[150]["candidate_sampling_random_state"])

    MODES,retained_fn,scan_fn=_helpers(panel); name=str(parent["taxon"])
    if panel=="successor": mode_a,mode_b=scan_fn(tuple(str(x) for x in parent["historical_specieskeys"]))
    else: mode_a,mode_b=scan_fn(str(parent["specieskey"]))
    retained=retained_fn(name,mode_a,mode_b); del mode_a,mode_b
    thin=float(frame["shared_frame_coordinate_pooling"]["source_specific_thinning_cell_degrees"]); source={}
    for mode in MODES:
        source[mode]=thin_to_grid(retained[mode],cell_size_degrees=thin)
        if len(source[mode])<30: raise RuntimeError("source unexpectedly sparse")
    pooled=pd.concat([source[MODES[0]],source[MODES[1]]],ignore_index=True); geometry=thin_to_grid(pooled,cell_size_degrees=float(frame["shared_frame_coordinate_pooling"]["pooled_geometry_thinning_cell_degrees"]))
    part=make_presence_spatial_partition(geometry["longitude"].to_numpy(float),geometry["latitude"].to_numpy(float),n_blocks=int(frame["spatial_blocks"]["n_blocks"]),holdout_fraction=0.5,random_state=int(frame["spatial_blocks"]["random_state"]))
    if _hash_centers(part.centers_xyz)!=str(parent["common_block_centers_sha256"]): raise RuntimeError("geometry hash mismatch")
    target=admit_occurrences(load_gbif_download(Path(args.target_group)).records,config=OccurrenceAdmissionConfig()).accepted.dropna(subset=["longitude","latitude"]).reset_index(drop=True)
    manifest=pd.read_csv(args.chelsa_manifest); core=manifest.loc[manifest["candidate_class"].astype(str).str.strip()=="core_climate"].copy(); expected_core=[f"bio{i}" for i in range(1,20)]
    if core["predictor"].astype(str).tolist()!=expected_core: raise RuntimeError("manifest-defined core19 drifted")
    specs,_=raster_specs_from_chelsa_manifest(core,include_availability=("current",),strict=True)
    rows=[]
    for m in unresolved:
        mask=occurrence_buffer_membership(target,geometry,buffer_km=float(m)); candidates=sample_target_group_background(geometry,target,m_mask=mask,n_points=max(1,len(target)),cell_size_degrees=0.05,focal_species=name,random_state=seed)
        featured,_=extract_raster_values(candidates,specs); values=featured.loc[:,expected_core].apply(pd.to_numeric,errors="coerce").to_numpy(float); finite=int(np.isfinite(values).all(axis=1).sum())
        if len(featured)!=int(cells[m]["candidate_rows_materialized"]): raise RuntimeError(f"candidate denominator mismatch M{m}")
        rows.append({"panel":panel,"taxon":name,"taxon_index":int(args.taxon_index),"M_km":m,"candidate_rows_materialized":len(featured),"core19_finite_rows":finite,"core19_ready_for_2000":bool(finite>=2000)})
    outdir=Path(args.output_dir); outdir.mkdir(parents=True,exist_ok=True); pd.DataFrame(rows).to_csv(outdir/"core19_readiness_cells.csv",index=False)
    summary={"result_version":RESULT,"panel":panel,"taxon":name,"taxon_index":int(args.taxon_index),"parent_v0_3_result_version":expected,"parent_v0_3_receipt_sha256":sha256(parent_bytes).hexdigest(),"unresolved_cell_count":len(rows),"core_predictor_rule":"CHELSA manifest candidate_class == core_climate","active_predictors":expected_core,"active_predictor_count":19,"core19_cells_ready_for_2000":sum(int(r["core19_ready_for_2000"]) for r in rows),"all_unresolved_cells_core19_ready_for_2000":all(bool(r["core19_ready_for_2000"]) for r in rows),"minimum_core19_finite_rows":min(int(r["core19_finite_rows"]) for r in rows),"model_fit_opened":False,"prediction_scores_computed":False,"paired_discordance_opened":False,"reference_ceiling_opened_or_read":False,"heldout_pairing_opened":False,"process_knockout_opened":False,"counts_as_empirical_conclusion":False}
    (outdir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n"); print(json.dumps(summary,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
