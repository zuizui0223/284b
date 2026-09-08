#!/usr/bin/env python3
"""Refit one same-target taxon on a prospectively qualified core19 frame.

The model/procedure/adequacy body is unchanged.  The only endpoint-version
change is the environmental universe, fixed before qualification by the pinned
CHELSA manifest rule candidate_class == core_climate (bio1..bio19).

The 2,000 comparison rows per M must already be frozen by the v0.4 core19
qualification. This runner never resamples or drops those rows and never opens
paired discordance, the reference ceiling, held-out pairing, or process
knockout.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE_FIT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
FRAME = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
CORE19 = ROOT / "config/product_b_same_target_core19_requalification_contract_v0_4.json"
SUCCESSOR_SAMPLING = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"
HELDOUT_SAMPLING = ROOT / "results/product_b_same_target_source_mode_sampling_v0_1.json"
HELDOUT_REGISTRY = ROOT / "registry/product_b_same_target_source_identity_pass_taxa_v0_1.csv"

SUCCESSOR_PREFLIGHT = "product_b_same_target_successor_core19_preflight_taxon_v0.4"
HELDOUT_PREFLIGHT = "product_b_same_target_heldout_core19_preflight_taxon_v0.4"
SUCCESSOR_RESULT = "product_b_same_target_successor_core19_layer1_fit_taxon_v0.4"
HELDOUT_RESULT = "product_b_same_target_heldout_core19_layer1_fit_taxon_v0.4"
CONTRACT_VERSION = "product_b_same_target_core19_requalification_v0.4"


def _hash_centers(centers: np.ndarray) -> str:
    return sha256(np.asarray(centers, dtype="<f8").tobytes(order="C")).hexdigest()


def _helpers(panel: str):
    if panel == "successor":
        from scripts.run_same_target_successor_layer1_fit_taxon import MODES, _procedure_library, _retained_source_frames, _scan_taxon
        return MODES, _procedure_library, _retained_source_frames, _scan_taxon
    if panel == "heldout":
        from scripts.run_same_target_layer1_baseline_fit_taxon import MODES, _procedure_library, _retained_source_frames, _scan_taxon
        return MODES, _procedure_library, _retained_source_frames, _scan_taxon
    raise ValueError("panel must be successor or heldout")


def _read_core19_frame(path: Path, expected_sha: str, predictors: tuple[str, ...]) -> pd.DataFrame:
    if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected_sha:
        raise RuntimeError("core19 frozen comparison frame bytes changed")
    frame = pd.read_parquet(path)
    required = {"comparison_row_id", "longitude", "latitude", *predictors}
    if required - set(frame.columns):
        raise RuntimeError("core19 frame missing required columns")
    if len(frame) != 2000 or frame["comparison_row_id"].astype(str).duplicated().any():
        raise RuntimeError("core19 frame denominator/identity changed")
    values = frame.loc[:, list(predictors)].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    if not np.isfinite(values).all():
        raise RuntimeError("core19 frozen frame contains non-finite predictor")
    return frame


def main() -> int:
    from sdmr.data import extract_raster_values, raster_specs_from_chelsa_manifest, thin_to_grid
    from sdmr.model import score_ecological_suitability
    from sdmr.niche_recovery_procedure import cross_validated_recovery_procedure
    from sdmr.recovery_procedure_fit import fit_recovery_procedure
    from sdmr.validation import assign_spatial_blocks, make_presence_spatial_partition

    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", choices=("successor", "heldout"), required=True)
    ap.add_argument("--taxon-index", type=int, required=True)
    ap.add_argument("--core19-frame-dir", required=True)
    ap.add_argument("--chelsa-manifest", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    panel = str(args.panel)
    fit_contract = json.loads(BASE_FIT.read_text(encoding="utf-8"))
    frame_contract = json.loads(FRAME.read_text(encoding="utf-8"))
    core_contract = json.loads(CORE19.read_text(encoding="utf-8"))
    if core_contract.get("contract_version") != CONTRACT_VERSION:
        raise RuntimeError("wrong core19 contract")
    if core_contract["unchanged_scientific_rules"].get("procedure_library_unchanged") is not True:
        raise RuntimeError("core19 refit requires unchanged procedure library")
    if core_contract["unchanged_scientific_rules"].get("prediction_adequacy_contract_unchanged") is not True:
        raise RuntimeError("core19 refit requires unchanged adequacy rule")

    frame_dir = Path(args.core19_frame_dir)
    receipt_path = frame_dir / "receipt.json"
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes)
    expected_preflight = SUCCESSOR_PREFLIGHT if panel == "successor" else HELDOUT_PREFLIGHT
    result_version = SUCCESSOR_RESULT if panel == "successor" else HELDOUT_RESULT
    if receipt.get("result_version") != expected_preflight or receipt.get("contract_version") != CONTRACT_VERSION:
        raise RuntimeError("core19 refit received wrong qualification receipt")
    if receipt.get("all_three_M_frames_frozen") is not True:
        raise RuntimeError("core19 refit forbidden with unresolved M frame")
    if receipt.get("active_predictors") != [f"bio{i}" for i in range(1, 20)] or receipt.get("active_predictor_count") != 19:
        raise RuntimeError("core19 refit predictor identity drifted")
    if receipt.get("parent_v0_3_frame_bytes_reused") is not False:
        raise RuntimeError("core19 endpoint may not reuse all43 frame bytes")
    for key in ("model_fit_opened", "prediction_scores_computed", "paired_discordance_opened", "reference_ceiling_opened_or_read", "heldout_pairing_opened", "process_knockout_opened"):
        if receipt.get(key) is not False:
            raise RuntimeError(f"core19 qualification crossed information boundary: {key}")

    MODES, procedure_library, retained_fn, scan_fn = _helpers(panel)
    name = str(receipt["taxon"])
    taxon_index = int(args.taxon_index)
    if int(receipt.get("taxon_index", -1)) != taxon_index:
        raise RuntimeError("core19 refit taxon index mismatch")

    if panel == "successor":
        sampling = json.loads(SUCCESSOR_SAMPLING.read_text(encoding="utf-8"))
        eligible = [r for r in sampling.get("results", []) if r.get("state") == "successor_source_mode_sampling_passed"]
        if len(eligible) != 47 or not 0 <= taxon_index < 47:
            raise RuntimeError("successor core19 frozen taxon inventory drifted")
        row = eligible[taxon_index]
        expected_name = str(row["requested_name"]).strip()
        identity = tuple(sorted(str(x).strip() for x in row.get("frozen_historical_specieskeys", []) if str(x).strip()))
        if name != expected_name or receipt.get("historical_specieskeys") != list(identity):
            raise RuntimeError("successor core19 taxon identity mismatch")
        mode_a, mode_b = scan_fn(identity)
        identity_fields = {"historical_specieskeys": list(identity), "historical_key_count": len(identity)}
    else:
        registry = pd.read_csv(HELDOUT_REGISTRY)
        sampling = json.loads(HELDOUT_SAMPLING.read_text(encoding="utf-8"))
        if len(registry) != 12 or not 0 <= taxon_index < 12:
            raise RuntimeError("heldout core19 frozen taxon inventory drifted")
        row = registry.iloc[taxon_index]
        expected_name = str(row["scientific_name"])
        specieskey = str(row["resolved_snapshot_specieskey"])
        by_name = {str(x["requested_name"]): x for x in sampling.get("results", [])}
        if by_name.get(expected_name, {}).get("state") != "source_mode_sampling_passed":
            raise RuntimeError("heldout core19 taxon no longer sampling-pass")
        if name != expected_name or str(receipt.get("specieskey")) != specieskey:
            raise RuntimeError("heldout core19 taxon identity mismatch")
        mode_a, mode_b = scan_fn(specieskey)
        identity_fields = {"specieskey": specieskey}

    retained = retained_fn(name, mode_a, mode_b)
    del mode_a, mode_b
    source_thin: dict[str, pd.DataFrame] = {}
    thin_deg = float(frame_contract["shared_frame_coordinate_pooling"]["source_specific_thinning_cell_degrees"])
    for mode in MODES:
        if retained[mode].empty:
            raise RuntimeError(f"no retained rows for {mode}")
        source_thin[mode] = thin_to_grid(retained[mode], cell_size_degrees=thin_deg)
        if len(source_thin[mode]) < 30:
            raise RuntimeError(f"post-thinning source unexpectedly sparse: {mode}")
    pooled = pd.concat([source_thin[MODES[0]], source_thin[MODES[1]]], ignore_index=True)
    common_geometry = thin_to_grid(pooled, cell_size_degrees=float(frame_contract["shared_frame_coordinate_pooling"]["pooled_geometry_thinning_cell_degrees"]))
    partition = make_presence_spatial_partition(
        common_geometry["longitude"].to_numpy(float), common_geometry["latitude"].to_numpy(float),
        n_blocks=int(frame_contract["spatial_blocks"]["n_blocks"]), holdout_fraction=0.5,
        random_state=int(frame_contract["spatial_blocks"]["random_state"]),
    )
    centers = partition.centers_xyz
    if _hash_centers(centers) != str(receipt["common_block_centers_sha256"]):
        raise RuntimeError("source-blind common geometry changed since core19 qualification")
    source_blocks = {
        mode: assign_spatial_blocks(source_thin[mode]["longitude"].to_numpy(float), source_thin[mode]["latitude"].to_numpy(float), centers)
        for mode in MODES
    }

    manifest = pd.read_csv(args.chelsa_manifest)
    core_manifest = manifest.loc[manifest["candidate_class"].astype(str).str.strip() == "core_climate"].copy()
    raster_specs, raster_resolution = raster_specs_from_chelsa_manifest(core_manifest, include_availability=("current",), strict=True)
    predictors = tuple(spec.predictor for spec in raster_specs)
    if predictors != tuple(f"bio{i}" for i in range(1,20)) or list(predictors) != receipt["active_predictors"]:
        raise RuntimeError("resolved core19 raster identity changed")

    featured_source: dict[str, pd.DataFrame] = {}
    provenance_frames: list[pd.DataFrame] = []
    for mode in MODES:
        featured, provenance = extract_raster_values(source_thin[mode], raster_specs)
        featured_source[mode] = featured
        provenance = provenance.copy(); provenance["role"] = f"core19_v0_4_presence_{mode}"
        provenance_frames.append(provenance)

    cells = {int(c["M_km"]): dict(c) for c in receipt["cells"]}
    if set(cells) != {150,300,500}:
        raise RuntimeError("core19 qualification M inventory drifted")
    backgrounds: dict[int, pd.DataFrame] = {}
    for m in (150,300,500):
        c = cells[m]
        if c.get("state") != "core19_comparison_frame_frozen" or int(c.get("selected_rows", -1)) != 2000:
            raise RuntimeError("core19 refit attempted on unresolved frame")
        backgrounds[m] = _read_core19_frame(frame_dir / str(c["comparison_frame_file"]), str(c["comparison_frame_sha256"]), predictors)

    procedures = procedure_library(fit_contract)
    if len(procedures) != 8:
        raise RuntimeError("procedure library drifted from frozen eight procedures")
    adequacy = fit_contract["prediction_adequacy"]
    outdir = Path(args.output_dir); outdir.mkdir(parents=True, exist_ok=True)
    prediction_rows: list[dict[str, object]] = []
    inventory_rows: list[dict[str, object]] = []
    fold_frames: list[pd.DataFrame] = []
    trace_frames: list[pd.DataFrame] = []
    errors: list[dict[str, object]] = []

    for m in (150,300,500):
        background = backgrounds[m]
        bg_blocks = assign_spatial_blocks(background["longitude"].to_numpy(float), background["latitude"].to_numpy(float), centers)
        ids = background["comparison_row_id"].astype(str).tolist()
        for mode in MODES:
            presence = featured_source[mode]
            for procedure in procedures:
                base = {"taxon":name, "source":mode, "M_km":m, "procedure":procedure.label}
                base.update(identity_fields)
                try:
                    benchmark = cross_validated_recovery_procedure(
                        presence, background, source_blocks[mode], bg_blocks,
                        predictors, predictors, procedure,
                        outer_folds=int(adequacy["outer_folds"]), chance_auc=float(adequacy["chance_auc"]),
                        minimum_auc_margin=float(adequacy["minimum_auc_margin"]), auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]),
                    )
                    if not benchmark.fold_metrics.empty:
                        f=benchmark.fold_metrics.copy()
                        for k,v in base.items(): f[k]=v
                        fold_frames.append(f)
                    if not benchmark.selection_trace.empty:
                        t=benchmark.selection_trace.copy()
                        for k,v in base.items(): t[k]=v
                        t["stage"]="outer_cv"; trace_frames.append(t)
                    fitted = fit_recovery_procedure(
                        presence, background, source_blocks[mode], bg_blocks,
                        predictors, predictors, procedure,
                        chance_auc=float(adequacy["chance_auc"]), minimum_auc_margin=float(adequacy["minimum_auc_margin"]),
                        auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]),
                    )
                    scores = score_ecological_suitability(fitted.model, background, fitted.selected_predictors, observation_predictors=())
                    if len(scores)!=2000 or not np.isfinite(scores).all():
                        raise RuntimeError("core19 sealed prediction surface must contain exactly 2000 finite scores")
                    for rid,score in zip(ids,scores,strict=True):
                        prediction_rows.append({**base,"comparison_row_id":rid,"ecological_score":float(score)})
                    model_rel=Path("models")/f"M{m}"/mode/(sha256(procedure.label.encode()).hexdigest()[:12]+".joblib")
                    model_path=outdir/model_rel; model_path.parent.mkdir(parents=True,exist_ok=True); joblib.dump(fitted.model,model_path)
                    inventory_rows.append({**base,"state":"core19_layer1_model_fit_sealed","selected_predictors":",".join(fitted.selected_predictors),"selected_ecological_predictors":",".join(fitted.selected_ecological_predictors),"n_selected_predictors":len(fitted.selected_predictors),"model_file":str(model_rel),"n_presence_thinned":len(presence),"n_background":2000,"n_common_geometry_cells":len(common_geometry),"core19_frame_sha256":cells[m]["comparison_frame_sha256"]})
                    if not fitted.selection_trace.empty:
                        t=fitted.selection_trace.copy()
                        for k,v in base.items(): t[k]=v
                        t["stage"]="final_fit"; trace_frames.append(t)
                except Exception as exc:
                    errors.append({**base,"error_type":type(exc).__name__,"error_message":str(exc)})
                    inventory_rows.append({**base,"state":"core19_layer1_model_fit_unresolved","selected_predictors":"","selected_ecological_predictors":"","n_selected_predictors":0,"model_file":"","n_presence_thinned":len(presence),"n_background":2000,"n_common_geometry_cells":len(common_geometry),"core19_frame_sha256":cells[m]["comparison_frame_sha256"]})

    predictions=pd.DataFrame(prediction_rows); inventory=pd.DataFrame(inventory_rows)
    folds=pd.concat(fold_frames,ignore_index=True) if fold_frames else pd.DataFrame()
    traces=pd.concat(trace_frames,ignore_index=True) if trace_frames else pd.DataFrame()
    provenance=pd.concat(provenance_frames,ignore_index=True).drop_duplicates().reset_index(drop=True)
    predictions.to_parquet(outdir/"sealed_prediction_surfaces.parquet",index=False)
    inventory.to_csv(outdir/"fit_inventory.csv",index=False)
    folds.to_csv(outdir/"outer_cv_fold_metrics.csv",index=False)
    traces.to_csv(outdir/"selection_trace.csv",index=False)
    provenance.to_csv(outdir/"raster_provenance.csv",index=False)
    raster_resolution.to_csv(outdir/"chelsa_resolution_ledger.csv",index=False)
    sealed=int((inventory["state"]=="core19_layer1_model_fit_sealed").sum()) if len(inventory) else 0
    prediction_sha=sha256((outdir/"sealed_prediction_surfaces.parquet").read_bytes()).hexdigest()
    contract_out={
        "result_version":result_version,"core19_contract_version":CONTRACT_VERSION,"panel":panel,
        "taxon":name,"taxon_index":taxon_index,**identity_fields,"source_modes":list(MODES),
        "active_predictors":list(predictors),"active_predictor_count":19,"M_km":[150,300,500],"procedure_count":8,
        "expected_fit_cells":48,"sealed_fit_cells":sealed,"unresolved_fit_cells":int(len(inventory)-sealed),
        "prediction_surface_sha256":prediction_sha,"prediction_surfaces_sealed":True,
        "core19_preflight_receipt_sha256":sha256(receipt_bytes).hexdigest(),
        "core19_frame_sha256_by_M":{str(m):cells[m]["comparison_frame_sha256"] for m in (150,300,500)},
        "all_prediction_scores_finite_for_sealed_cells":True,
        "paired_discordance_computed":False,"reference_ceiling_opened_or_read":False,
        "heldout_pairing_opened":False,"process_knockout_computed":False,
        "same_frozen_core19_background_rows_used_for_both_sources":True,
        "background_rows_resampled_during_refit":False,"posthoc_prediction_row_drop_used":False,
        "taxon_replaced":False,"procedure_selected_from_outcome":False,"M_selected_from_outcome":False,
        "errors":errors,"counts_as_empirical_conclusion":False,
        "claim_strength":"core19_layer1_refit_only_cross_source_endpoint_still_sealed",
    }
    (outdir/"contract.json").write_text(json.dumps(contract_out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(contract_out,indent=2,sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
