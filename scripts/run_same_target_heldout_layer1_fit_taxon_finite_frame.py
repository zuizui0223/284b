#!/usr/bin/env python3
"""Refit one frozen held-out taxon on an outcome-blind finite comparison frame.

The 2,000 comparison rows per M must have been sealed by the held-out preflight
before any repaired reference discordance was opened. This runner never reads a
reference ceiling or paired outcome and requires every sealed prediction score
to be finite.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from scripts.run_same_target_layer1_baseline_fit_taxon import (
    MODES,
    _procedure_library,
    _retained_source_frames,
    _scan_taxon,
)

ROOT = Path(__file__).resolve().parents[1]
FIT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
FRAME = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
REPAIR = ROOT / "config/product_b_same_target_heldout_finite_frame_repair_contract_v0_1.json"
REGISTRY = ROOT / "registry/product_b_same_target_source_identity_pass_taxa_v0_1.csv"
SAMPLING = ROOT / "results/product_b_same_target_source_mode_sampling_v0_1.json"


def _hash_centers(centers: np.ndarray) -> str:
    return sha256(np.asarray(centers, dtype="<f8").tobytes(order="C")).hexdigest()


def _read_frame(path: Path, expected_sha: str, predictors: tuple[str, ...]) -> pd.DataFrame:
    if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected_sha:
        raise RuntimeError("held-out frozen finite frame bytes changed")
    frame = pd.read_parquet(path)
    required = {"comparison_row_id", "longitude", "latitude", *predictors}
    if required - set(frame.columns):
        raise RuntimeError("held-out finite frame missing required columns")
    if len(frame) != 2000 or frame["comparison_row_id"].astype(str).duplicated().any():
        raise RuntimeError("held-out finite frame denominator/identity changed")
    values = frame.loc[:, list(predictors)].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    if not np.isfinite(values).all():
        raise RuntimeError("held-out finite frame no longer all-predictor finite")
    return frame


def main() -> int:
    from sdmr.data import extract_raster_values, raster_specs_from_chelsa_manifest, thin_to_grid
    from sdmr.model import score_ecological_suitability
    from sdmr.niche_recovery_procedure import cross_validated_recovery_procedure
    from sdmr.recovery_procedure_fit import fit_recovery_procedure
    from sdmr.validation import assign_spatial_blocks, make_presence_spatial_partition

    ap = argparse.ArgumentParser()
    ap.add_argument("--taxon-index", type=int, required=True)
    ap.add_argument("--finite-frame-dir", required=True)
    ap.add_argument("--chelsa-manifest", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    fit_contract = json.loads(FIT.read_text(encoding="utf-8"))
    frame_contract = json.loads(FRAME.read_text(encoding="utf-8"))
    repair = json.loads(REPAIR.read_text(encoding="utf-8"))
    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    registry = pd.read_csv(REGISTRY)
    if len(registry) != 12 or not 0 <= args.taxon_index < 12:
        raise RuntimeError("held-out refit taxon inventory drifted")

    finite_dir = Path(args.finite_frame_dir)
    receipt_path = finite_dir / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("result_version") != "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.1":
        raise RuntimeError("wrong held-out preflight receipt type")
    if receipt.get("all_three_M_frames_frozen") is not True:
        raise RuntimeError("held-out refit forbidden with unresolved finite frame")
    for k in ("model_refit_opened", "prediction_scores_computed", "paired_discordance_opened", "reference_ceiling_read", "heldout_pairing_opened", "process_knockout_opened"):
        if receipt.get(k) is not False:
            raise RuntimeError(f"held-out preflight boundary changed: {k}")
    if repair["preflight"]["model_refit_allowed"] is not False:
        raise RuntimeError("held-out preflight/refit boundary drifted")

    row = registry.iloc[args.taxon_index]
    name = str(row["scientific_name"])
    specieskey = str(row["resolved_snapshot_specieskey"])
    if str(receipt.get("taxon")) != name or str(receipt.get("specieskey")) != specieskey or int(receipt.get("taxon_index", -1)) != args.taxon_index:
        raise RuntimeError("held-out preflight taxon identity mismatch")
    result_by_name = {str(x["requested_name"]): x for x in sampling.get("results", [])}
    if result_by_name.get(name, {}).get("state") != "source_mode_sampling_passed":
        raise RuntimeError("held-out taxon no longer sampling-pass")

    mode_a, mode_b = _scan_taxon(specieskey)
    retained = _retained_source_frames(name, mode_a, mode_b)
    del mode_a, mode_b
    source_thin: dict[str, pd.DataFrame] = {}
    thin_deg = float(frame_contract["shared_frame_coordinate_pooling"]["source_specific_thinning_cell_degrees"])
    for mode in MODES:
        if retained[mode].empty:
            raise RuntimeError(f"no retained held-out rows for {mode}")
        source_thin[mode] = thin_to_grid(retained[mode], cell_size_degrees=thin_deg)
        if len(source_thin[mode]) < 30:
            raise RuntimeError(f"held-out post-thinning source unexpectedly sparse: {mode}")
    pooled = pd.concat([source_thin[MODES[0]], source_thin[MODES[1]]], ignore_index=True)
    common_geometry = thin_to_grid(pooled, cell_size_degrees=float(frame_contract["shared_frame_coordinate_pooling"]["pooled_geometry_thinning_cell_degrees"]))
    partition = make_presence_spatial_partition(
        common_geometry["longitude"].to_numpy(float), common_geometry["latitude"].to_numpy(float),
        n_blocks=int(frame_contract["spatial_blocks"]["n_blocks"]), holdout_fraction=0.5,
        random_state=int(frame_contract["spatial_blocks"]["random_state"]),
    )
    centers = partition.centers_xyz
    if _hash_centers(centers) != str(receipt["common_block_centers_sha256"]):
        raise RuntimeError("held-out common geometry changed since preflight")
    source_blocks = {
        mode: assign_spatial_blocks(source_thin[mode]["longitude"].to_numpy(float), source_thin[mode]["latitude"].to_numpy(float), centers)
        for mode in MODES
    }

    manifest = pd.read_csv(args.chelsa_manifest)
    raster_specs, raster_resolution = raster_specs_from_chelsa_manifest(manifest, include_availability=("current",), strict=True)
    predictors = tuple(spec.predictor for spec in raster_specs)
    if len(predictors) != 43 or list(predictors) != receipt.get("active_predictors"):
        raise RuntimeError("held-out finite-frame predictor identity changed")
    featured_source: dict[str, pd.DataFrame] = {}
    provenance_frames: list[pd.DataFrame] = []
    for mode in MODES:
        featured, provenance = extract_raster_values(source_thin[mode], raster_specs)
        featured_source[mode] = featured
        provenance = provenance.copy(); provenance["role"] = f"heldout_repair_presence_{mode}"
        provenance_frames.append(provenance)

    cells = {int(x["M_km"]): x for x in receipt.get("cells", [])}
    if set(cells) != {150, 300, 500}:
        raise RuntimeError("held-out preflight M inventory changed")
    backgrounds: dict[int, pd.DataFrame] = {}
    for m in (150, 300, 500):
        c = cells[m]
        if c.get("state") != "finite_comparison_frame_frozen" or int(c.get("selected_rows", -1)) != 2000:
            raise RuntimeError("held-out refit attempted on unresolved frame")
        backgrounds[m] = _read_frame(finite_dir / str(c["comparison_frame_file"]), str(c["comparison_frame_sha256"]), predictors)

    procedures = _procedure_library(fit_contract)
    adequacy = fit_contract["prediction_adequacy"]
    outdir = Path(args.output_dir); outdir.mkdir(parents=True, exist_ok=True)
    prediction_rows: list[dict[str, object]] = []
    inventory_rows: list[dict[str, object]] = []
    fold_frames: list[pd.DataFrame] = []
    trace_frames: list[pd.DataFrame] = []
    errors: list[dict[str, object]] = []

    for m in (150, 300, 500):
        background = backgrounds[m]
        bg_blocks = assign_spatial_blocks(background["longitude"].to_numpy(float), background["latitude"].to_numpy(float), centers)
        ids = background["comparison_row_id"].astype(str).tolist()
        for mode in MODES:
            presence = featured_source[mode]
            for procedure in procedures:
                base = {"taxon": name, "specieskey": specieskey, "source": mode, "M_km": m, "procedure": procedure.label}
                try:
                    benchmark = cross_validated_recovery_procedure(
                        presence, background, source_blocks[mode], bg_blocks, predictors, predictors, procedure,
                        outer_folds=int(adequacy["outer_folds"]), chance_auc=float(adequacy["chance_auc"]),
                        minimum_auc_margin=float(adequacy["minimum_auc_margin"]), auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]),
                    )
                    if not benchmark.fold_metrics.empty:
                        f = benchmark.fold_metrics.copy()
                        for k, v in base.items(): f[k] = v
                        fold_frames.append(f)
                    if not benchmark.selection_trace.empty:
                        t = benchmark.selection_trace.copy()
                        for k, v in base.items(): t[k] = v
                        t["stage"] = "outer_cv"; trace_frames.append(t)
                    fitted = fit_recovery_procedure(
                        presence, background, source_blocks[mode], bg_blocks, predictors, predictors, procedure,
                        chance_auc=float(adequacy["chance_auc"]), minimum_auc_margin=float(adequacy["minimum_auc_margin"]),
                        auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]),
                    )
                    scores = score_ecological_suitability(fitted.model, background, fitted.selected_predictors, observation_predictors=())
                    if len(scores) != 2000 or not np.isfinite(scores).all():
                        raise RuntimeError("held-out repaired prediction surface must contain exactly 2000 finite scores")
                    for rid, score in zip(ids, scores, strict=True):
                        prediction_rows.append({**base, "comparison_row_id": rid, "ecological_score": float(score)})
                    model_rel = Path("models") / f"M{m}" / mode / (sha256(procedure.label.encode()).hexdigest()[:12] + ".joblib")
                    model_path = outdir / model_rel; model_path.parent.mkdir(parents=True, exist_ok=True); joblib.dump(fitted.model, model_path)
                    inventory_rows.append({
                        **base, "state": "layer1_model_fit_sealed_finite_frame_repair",
                        "selected_predictors": ",".join(fitted.selected_predictors),
                        "selected_ecological_predictors": ",".join(fitted.selected_ecological_predictors),
                        "n_selected_predictors": len(fitted.selected_predictors), "model_file": str(model_rel),
                        "n_presence_thinned": len(presence), "n_background": 2000,
                        "n_common_geometry_cells": len(common_geometry), "finite_frame_sha256": cells[m]["comparison_frame_sha256"],
                    })
                    if not fitted.selection_trace.empty:
                        t = fitted.selection_trace.copy()
                        for k, v in base.items(): t[k] = v
                        t["stage"] = "final_fit"; trace_frames.append(t)
                except Exception as exc:
                    errors.append({**base, "error_type": type(exc).__name__, "error_message": str(exc)})
                    inventory_rows.append({
                        **base, "state": "layer1_model_fit_unresolved_finite_frame_repair",
                        "selected_predictors": "", "selected_ecological_predictors": "", "n_selected_predictors": 0,
                        "model_file": "", "n_presence_thinned": len(presence), "n_background": 2000,
                        "n_common_geometry_cells": len(common_geometry), "finite_frame_sha256": cells[m]["comparison_frame_sha256"],
                    })

    predictions = pd.DataFrame(prediction_rows)
    inventory = pd.DataFrame(inventory_rows)
    folds = pd.concat(fold_frames, ignore_index=True) if fold_frames else pd.DataFrame()
    traces = pd.concat(trace_frames, ignore_index=True) if trace_frames else pd.DataFrame()
    predictions.to_parquet(outdir / "sealed_prediction_surfaces.parquet", index=False)
    inventory.to_csv(outdir / "fit_inventory.csv", index=False)
    folds.to_csv(outdir / "outer_cv_fold_metrics.csv", index=False)
    traces.to_csv(outdir / "selection_trace.csv", index=False)
    pd.concat(provenance_frames, ignore_index=True).drop_duplicates().to_csv(outdir / "raster_provenance.csv", index=False)
    raster_resolution.to_csv(outdir / "chelsa_resolution_ledger.csv", index=False)
    prediction_sha = sha256((outdir / "sealed_prediction_surfaces.parquet").read_bytes()).hexdigest()
    sealed = int((inventory["state"] == "layer1_model_fit_sealed_finite_frame_repair").sum()) if len(inventory) else 0
    contract = {
        "result_version": "product_b_same_target_source_layer1_baseline_fit_taxon_finite_frame_repair_v0.1",
        "taxon": name, "taxon_index": args.taxon_index, "specieskey": specieskey,
        "source_modes": list(MODES), "M_km": [150, 300, 500], "procedure_count": 8,
        "expected_fit_cells": 48, "sealed_fit_cells": sealed, "unresolved_fit_cells": int(len(inventory)-sealed),
        "prediction_surface_sha256": prediction_sha, "prediction_surfaces_sealed": True,
        "finite_frame_preflight_receipt_sha256": sha256(receipt_path.read_bytes()).hexdigest(),
        "finite_frame_sha256_by_M": {str(m): cells[m]["comparison_frame_sha256"] for m in (150,300,500)},
        "all_prediction_scores_finite_by_contract": True,
        "paired_discordance_computed": False, "reference_ceiling_read": False,
        "heldout_pairing_opened": False, "process_knockout_computed": False,
        "same_frozen_finite_background_rows_used_for_both_sources": True,
        "background_rows_resampled_during_refit": False, "posthoc_prediction_row_drop_used": False,
        "taxon_replaced": False, "procedure_selected_from_outcome": False, "M_selected_from_outcome": False,
        "errors": errors, "counts_as_empirical_conclusion": False,
        "claim_strength": "heldout_repaired_layer1_fit_only_paired_endpoint_still_sealed"
    }
    (outdir / "contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(contract, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
