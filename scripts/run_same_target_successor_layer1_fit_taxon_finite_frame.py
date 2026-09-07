#!/usr/bin/env python3
"""Refit one successor taxon on a preflight-frozen finite comparison frame.

The comparison rows must already have been frozen by the outcome-blind repair
preflight. This runner never resamples, trims, intersects, or otherwise changes
those rows. It refits both observation-mode answers independently using the
unchanged model/procedure contracts and requires every sealed prediction score
to be finite before a repaired prediction surface can be written.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from scripts.run_same_target_successor_layer1_fit_taxon import (
    MODES,
    _procedure_library,
    _retained_source_frames,
    _scan_taxon,
)

ROOT = Path(__file__).resolve().parents[1]
BASE_FIT_CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
SUCCESSOR_FIT_CONTRACT = ROOT / "config/product_b_same_target_successor_model_fit_contract_v0_1.json"
FRAME_CONTRACT = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
REPAIR_CONTRACT = ROOT / "config/product_b_same_target_reference_finite_frame_repair_contract_v0_1.json"
SAMPLING_RESULT = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"


def _hash_centers(centers: np.ndarray) -> str:
    return sha256(np.asarray(centers, dtype="<f8").tobytes(order="C")).hexdigest()


def _read_frame(path: Path, *, expected_sha256: str, predictors: tuple[str, ...], expected_rows: int) -> pd.DataFrame:
    if not path.is_file():
        raise RuntimeError(f"missing frozen finite comparison frame: {path}")
    if sha256(path.read_bytes()).hexdigest() != str(expected_sha256):
        raise RuntimeError("frozen finite comparison frame bytes changed")
    frame = pd.read_parquet(path)
    required = {"comparison_row_id", "longitude", "latitude", *predictors}
    missing = required - set(frame.columns)
    if missing:
        raise RuntimeError(f"finite comparison frame missing columns: {sorted(missing)}")
    if len(frame) != int(expected_rows):
        raise RuntimeError("finite comparison frame denominator changed")
    if frame["comparison_row_id"].astype(str).duplicated().any():
        raise RuntimeError("finite comparison row IDs are not unique")
    values = frame.loc[:, list(predictors)].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    if not np.isfinite(values).all():
        raise RuntimeError("preflight-frozen comparison frame is no longer all-predictor finite")
    return frame


def main() -> int:
    from sdmr.data import extract_raster_values, raster_specs_from_chelsa_manifest, thin_to_grid
    from sdmr.model import score_ecological_suitability
    from sdmr.niche_recovery_procedure import cross_validated_recovery_procedure
    from sdmr.recovery_procedure_fit import fit_recovery_procedure
    from sdmr.validation import assign_spatial_blocks, make_presence_spatial_partition

    p = argparse.ArgumentParser()
    p.add_argument("--taxon-index", type=int, required=True)
    p.add_argument("--finite-frame-dir", required=True)
    p.add_argument("--chelsa-manifest", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()

    fit_contract = json.loads(BASE_FIT_CONTRACT.read_text(encoding="utf-8"))
    successor_fit = json.loads(SUCCESSOR_FIT_CONTRACT.read_text(encoding="utf-8"))
    frame_contract = json.loads(FRAME_CONTRACT.read_text(encoding="utf-8"))
    repair = json.loads(REPAIR_CONTRACT.read_text(encoding="utf-8"))
    sampling = json.loads(SAMPLING_RESULT.read_text(encoding="utf-8"))
    finite_dir = Path(args.finite_frame_dir)
    preflight_path = finite_dir / "receipt.json"
    if not preflight_path.is_file():
        raise RuntimeError("finite-frame preflight receipt missing")
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    if preflight.get("result_version") != "product_b_same_target_successor_finite_frame_preflight_taxon_v0.1":
        raise RuntimeError("wrong finite-frame preflight receipt type")
    if preflight.get("all_three_M_frames_frozen") is not True:
        raise RuntimeError("refit forbidden because one or more M frames are unresolved")
    for key in (
        "model_fit_opened", "prediction_scores_computed", "paired_discordance_opened",
        "reference_ceiling_computed", "heldout_12_paired_discordance_read", "process_knockout_opened",
    ):
        if preflight.get(key) is not False:
            raise RuntimeError(f"preflight information boundary changed: {key}")
    if repair["preflight"]["model_fit_allowed"] is not False:
        raise RuntimeError("repair contract must keep preflight distinct from refit authorization")

    eligible = [row for row in sampling.get("results", []) if row.get("state") == "successor_source_mode_sampling_passed"]
    if len(eligible) != 47:
        raise RuntimeError("repair refit requires frozen 47-taxon sampling-pass inventory")
    if not 0 <= int(args.taxon_index) < len(eligible):
        raise RuntimeError("taxon index outside frozen sampling-pass inventory")
    sampling_row = eligible[int(args.taxon_index)]
    name = str(sampling_row["requested_name"]).strip()
    historical_keys = tuple(sorted(str(x).strip() for x in sampling_row.get("frozen_historical_specieskeys", []) if str(x).strip()))
    if str(preflight.get("taxon")) != name or int(preflight.get("taxon_index", -1)) != int(args.taxon_index):
        raise RuntimeError("preflight taxon identity mismatch")
    if preflight.get("historical_specieskeys") != list(historical_keys):
        raise RuntimeError("preflight historical specieskey identity mismatch")

    mode_a, mode_b = _scan_taxon(historical_keys)
    retained = _retained_source_frames(name, mode_a, mode_b)
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
    common_geometry = thin_to_grid(
        pooled,
        cell_size_degrees=float(frame_contract["shared_frame_coordinate_pooling"]["pooled_geometry_thinning_cell_degrees"]),
    )
    common_partition = make_presence_spatial_partition(
        common_geometry["longitude"].to_numpy(float),
        common_geometry["latitude"].to_numpy(float),
        n_blocks=int(frame_contract["spatial_blocks"]["n_blocks"]),
        holdout_fraction=0.5,
        random_state=int(frame_contract["spatial_blocks"]["random_state"]),
    )
    centers = common_partition.centers_xyz
    if _hash_centers(centers) != str(preflight["common_block_centers_sha256"]):
        raise RuntimeError("source-blind common geometry changed since finite-frame preflight")
    source_blocks = {
        mode: assign_spatial_blocks(source_thin[mode]["longitude"].to_numpy(float), source_thin[mode]["latitude"].to_numpy(float), centers)
        for mode in MODES
    }

    manifest = pd.read_csv(args.chelsa_manifest)
    raster_specs, raster_resolution = raster_specs_from_chelsa_manifest(manifest, include_availability=("current",), strict=True)
    predictors = tuple(spec.predictor for spec in raster_specs)
    if len(predictors) != 43 or len(set(predictors)) != 43:
        raise RuntimeError("repair refit requires 43 unique CHELSA predictors")
    if list(predictors) != preflight.get("active_predictors"):
        raise RuntimeError("finite-frame predictor identity changed")
    if len(raster_specs) != int(fit_contract["environmental_predictor_source"]["active_predictors_required"]):
        raise RuntimeError("CHELSA predictor count differs from frozen base contract")

    featured_source: dict[str, pd.DataFrame] = {}
    provenance_frames: list[pd.DataFrame] = []
    for mode in MODES:
        featured, provenance = extract_raster_values(source_thin[mode], raster_specs)
        featured_source[mode] = featured
        provenance = provenance.copy(); provenance["role"] = f"repair_presence_{mode}"
        provenance_frames.append(provenance)

    frame_receipts = {int(row["M_km"]): row for row in preflight.get("cells", [])}
    if set(frame_receipts) != {150, 300, 500}:
        raise RuntimeError("preflight M inventory changed")
    background_frames: dict[int, pd.DataFrame] = {}
    for m_km in (150, 300, 500):
        cell = frame_receipts[m_km]
        if cell.get("state") != "finite_comparison_frame_frozen" or int(cell.get("selected_rows", -1)) != 2000:
            raise RuntimeError("refit attempted on unresolved finite frame")
        frame_file = cell.get("comparison_frame_file")
        frame_sha = cell.get("comparison_frame_sha256")
        if not frame_file or not frame_sha:
            raise RuntimeError("frozen finite frame lacks file identity")
        background_frames[m_km] = _read_frame(
            finite_dir / str(frame_file),
            expected_sha256=str(frame_sha),
            predictors=predictors,
            expected_rows=2000,
        )

    procedures = _procedure_library(fit_contract)
    adequacy = fit_contract["prediction_adequacy"]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    prediction_rows: list[dict[str, object]] = []
    selected_rows: list[dict[str, object]] = []
    fold_frames: list[pd.DataFrame] = []
    trace_frames: list[pd.DataFrame] = []
    errors: list[dict[str, object]] = []

    for m_km in (150, 300, 500):
        featured_background = background_frames[m_km]
        background_blocks = assign_spatial_blocks(
            featured_background["longitude"].to_numpy(float),
            featured_background["latitude"].to_numpy(float),
            centers,
        )
        comparison_ids = featured_background["comparison_row_id"].astype(str).tolist()
        for mode in MODES:
            presence = featured_source[mode]
            p_blocks = source_blocks[mode]
            for procedure in procedures:
                base = {
                    "taxon": name,
                    "historical_specieskeys": "|".join(historical_keys),
                    "historical_key_count": len(historical_keys),
                    "source": mode,
                    "M_km": int(m_km),
                    "procedure": procedure.label,
                }
                try:
                    benchmark = cross_validated_recovery_procedure(
                        presence, featured_background, p_blocks, background_blocks,
                        predictors, predictors, procedure,
                        outer_folds=int(adequacy["outer_folds"]),
                        chance_auc=float(adequacy["chance_auc"]),
                        minimum_auc_margin=float(adequacy["minimum_auc_margin"]),
                        auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]),
                    )
                    if not benchmark.fold_metrics.empty:
                        folds = benchmark.fold_metrics.copy()
                        for key, value in base.items(): folds[key] = value
                        fold_frames.append(folds)
                    if not benchmark.selection_trace.empty:
                        trace = benchmark.selection_trace.copy()
                        for key, value in base.items(): trace[key] = value
                        trace["stage"] = "outer_cv"; trace_frames.append(trace)

                    fitted = fit_recovery_procedure(
                        presence, featured_background, p_blocks, background_blocks,
                        predictors, predictors, procedure,
                        chance_auc=float(adequacy["chance_auc"]),
                        minimum_auc_margin=float(adequacy["minimum_auc_margin"]),
                        auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]),
                    )
                    scores = score_ecological_suitability(
                        fitted.model, featured_background, fitted.selected_predictors, observation_predictors=()
                    )
                    if len(scores) != 2000 or not np.isfinite(scores).all():
                        raise RuntimeError("repaired sealed prediction surface must contain exactly 2000 finite scores")
                    for comparison_row_id, score in zip(comparison_ids, scores, strict=True):
                        prediction_rows.append({**base, "comparison_row_id": comparison_row_id, "ecological_score": float(score)})

                    model_rel = Path("models") / f"M{m_km}" / mode / (sha256(procedure.label.encode()).hexdigest()[:12] + ".joblib")
                    model_path = output_dir / model_rel
                    model_path.parent.mkdir(parents=True, exist_ok=True)
                    joblib.dump(fitted.model, model_path)
                    selected_rows.append({
                        **base,
                        "state": "successor_layer1_model_fit_sealed_finite_frame_repair",
                        "selected_predictors": ",".join(fitted.selected_predictors),
                        "selected_ecological_predictors": ",".join(fitted.selected_ecological_predictors),
                        "n_selected_predictors": len(fitted.selected_predictors),
                        "model_file": str(model_rel),
                        "n_presence_thinned": len(presence),
                        "n_background": len(featured_background),
                        "n_common_geometry_cells": len(common_geometry),
                        "finite_frame_sha256": frame_receipts[m_km]["comparison_frame_sha256"],
                    })
                    if not fitted.selection_trace.empty:
                        trace = fitted.selection_trace.copy()
                        for key, value in base.items(): trace[key] = value
                        trace["stage"] = "final_fit"; trace_frames.append(trace)
                except Exception as exc:
                    errors.append({**base, "error_type": type(exc).__name__, "error_message": str(exc)})
                    selected_rows.append({
                        **base,
                        "state": "successor_layer1_model_fit_unresolved_finite_frame_repair",
                        "selected_predictors": "",
                        "selected_ecological_predictors": "",
                        "n_selected_predictors": 0,
                        "model_file": "",
                        "n_presence_thinned": len(presence),
                        "n_background": len(featured_background),
                        "n_common_geometry_cells": len(common_geometry),
                        "finite_frame_sha256": frame_receipts[m_km]["comparison_frame_sha256"],
                    })

    predictions = pd.DataFrame(prediction_rows)
    selected = pd.DataFrame(selected_rows)
    folds = pd.concat(fold_frames, ignore_index=True) if fold_frames else pd.DataFrame()
    traces = pd.concat(trace_frames, ignore_index=True) if trace_frames else pd.DataFrame()
    provenance = pd.concat(provenance_frames, ignore_index=True).drop_duplicates().reset_index(drop=True)

    predictions.to_parquet(output_dir / "sealed_prediction_surfaces.parquet", index=False)
    selected.to_csv(output_dir / "fit_inventory.csv", index=False)
    folds.to_csv(output_dir / "outer_cv_fold_metrics.csv", index=False)
    traces.to_csv(output_dir / "selection_trace.csv", index=False)
    provenance.to_csv(output_dir / "raster_provenance.csv", index=False)
    raster_resolution.to_csv(output_dir / "chelsa_resolution_ledger.csv", index=False)
    prediction_sha = sha256((output_dir / "sealed_prediction_surfaces.parquet").read_bytes()).hexdigest()
    fit_complete = int((selected["state"] == "successor_layer1_model_fit_sealed_finite_frame_repair").sum()) if len(selected) else 0
    outcome = {
        "result_version": "product_b_same_target_successor_layer1_fit_taxon_finite_frame_repair_v0.1",
        "taxon": name,
        "taxon_index": int(args.taxon_index),
        "historical_specieskeys": list(historical_keys),
        "historical_key_count": len(historical_keys),
        "source_modes": list(MODES),
        "M_km": [150, 300, 500],
        "procedure_count": len(procedures),
        "expected_fit_cells": 48,
        "sealed_fit_cells": fit_complete,
        "unresolved_fit_cells": int(len(selected) - fit_complete),
        "prediction_surface_sha256": prediction_sha,
        "prediction_surfaces_sealed": True,
        "finite_frame_preflight_receipt_sha256": sha256(preflight_path.read_bytes()).hexdigest(),
        "finite_frame_sha256_by_M": {str(m): frame_receipts[m]["comparison_frame_sha256"] for m in (150, 300, 500)},
        "all_prediction_scores_finite_by_contract": True,
        "paired_discordance_computed": False,
        "reference_ceiling_read": False,
        "process_knockout_computed": False,
        "heldout_12_paired_discordance_read": False,
        "shared_source_blind_M_and_block_geometry": True,
        "same_frozen_finite_background_rows_used_for_both_sources": True,
        "background_rows_resampled_during_refit": False,
        "posthoc_prediction_row_drop_used": False,
        "historical_key_subset_selection_used": False,
        "taxon_replaced": False,
        "procedure_selected_from_discordance": False,
        "M_selected_from_discordance": False,
        "errors": errors,
        "claim_strength": "repaired_layer1_fit_only_not_cross_source_empirical_conclusion",
    }
    (output_dir / "contract.json").write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
