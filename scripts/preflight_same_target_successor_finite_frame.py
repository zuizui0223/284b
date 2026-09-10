#!/usr/bin/env python3
"""Preflight repaired successor comparison frames before any model refit.

This stage reconstructs the frozen source-blind M geometry and target-group
background, oversamples a fixed candidate pool, extracts the unchanged 43
CHELSA predictors, and freezes exactly 2,000 all-predictor-finite comparison
rows when possible.  It does not fit a model, compute a prediction score,
open Schoener D, read held-out outcomes, or run process knockouts.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from product_b_v5.finite_comparison_frame import freeze_finite_comparison_frame
from scripts.run_same_target_successor_layer1_fit_taxon import (
    MODES,
    _comparison_ids,
    _frozen_candidate_names,
    _retained_source_frames,
    _scan_taxon,
)

ROOT = Path(__file__).resolve().parents[1]
REPAIR = ROOT / "config/product_b_same_target_reference_finite_frame_repair_contract_v0_1.json"
BASE_FIT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
FRAME = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
SAMPLING = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"


def _hash_centers(centers: np.ndarray) -> str:
    arr = np.asarray(centers, dtype="<f8")
    return sha256(arr.tobytes(order="C")).hexdigest()


def main() -> int:
    from sdmr.data import (
        OccurrenceAdmissionConfig,
        admit_occurrences,
        extract_raster_values,
        load_gbif_download,
        raster_specs_from_chelsa_manifest,
        thin_to_grid,
    )
    from sdmr.data.background import occurrence_buffer_membership, sample_target_group_background
    from sdmr.validation import make_presence_spatial_partition

    p = argparse.ArgumentParser()
    p.add_argument("--taxon-index", type=int, required=True)
    p.add_argument("--target-group", required=True)
    p.add_argument("--chelsa-manifest", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()

    repair = json.loads(REPAIR.read_text(encoding="utf-8"))
    fit_contract = json.loads(BASE_FIT.read_text(encoding="utf-8"))
    frame_contract = json.loads(FRAME.read_text(encoding="utf-8"))
    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    preflight = repair["preflight"]
    finite_contract = repair["finite_frame"]
    if any(bool(preflight[key]) for key in (
        "model_fit_allowed",
        "prediction_score_computation_allowed",
        "schoener_d_computation_allowed",
        "reference_ceiling_computation_allowed",
        "heldout_opening_allowed",
        "process_knockout_allowed",
    )):
        raise RuntimeError("repair preflight information boundary drifted")
    if int(finite_contract["active_predictors_required"]) != 43:
        raise RuntimeError("finite-frame predictor denominator drifted")
    if int(finite_contract["candidate_background_points_per_taxon_M"]) != 8000:
        raise RuntimeError("finite-frame candidate denominator drifted")
    if int(finite_contract["final_background_points_per_taxon_M"]) != 2000:
        raise RuntimeError("finite-frame final denominator drifted")

    eligible = [
        row for row in sampling.get("results", [])
        if row.get("state") == "successor_source_mode_sampling_passed"
    ]
    if len(eligible) != 47 or int(sampling.get("source_mode_sampling_passed", -1)) != 47:
        raise RuntimeError("finite-frame preflight requires the frozen 47 sampling-pass taxa")
    if not 0 <= int(args.taxon_index) < len(eligible):
        raise RuntimeError("taxon index outside frozen sampling-pass inventory")
    row = eligible[int(args.taxon_index)]
    name = str(row["requested_name"]).strip()
    historical_keys = tuple(
        sorted(str(x).strip() for x in row.get("frozen_historical_specieskeys", []) if str(x).strip())
    )
    if not historical_keys:
        raise RuntimeError("sampling-pass taxon lacks frozen historical key set")

    # Source information is used only to reconstruct the already-declared,
    # source-symmetric M geometry. No environmental value or model outcome from
    # either source can trim or weight this geometry.
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
    centers_sha = _hash_centers(common_partition.centers_xyz)

    target = load_gbif_download(Path(args.target_group)).records
    target = admit_occurrences(target, config=OccurrenceAdmissionConfig()).accepted
    target = target.dropna(subset=["longitude", "latitude"]).reset_index(drop=True)
    if target.empty:
        raise RuntimeError("target-group artifact has no admissible coordinates")

    manifest = pd.read_csv(args.chelsa_manifest)
    raster_specs, raster_resolution = raster_specs_from_chelsa_manifest(
        manifest, include_availability=("current",), strict=True
    )
    predictors = tuple(spec.predictor for spec in raster_specs)
    if len(predictors) != 43 or len(set(predictors)) != 43:
        raise RuntimeError("repair preflight requires 43 unique CHELSA predictors")
    if len(raster_specs) != int(fit_contract["environmental_predictor_source"]["active_predictors_required"]):
        raise RuntimeError("CHELSA predictor count differs from frozen base contract")

    frozen_names = sorted(_frozen_candidate_names())
    if name not in frozen_names or len(frozen_names) != 72:
        raise RuntimeError("taxon absent from frozen 72-candidate registry")
    seed_index = frozen_names.index(name)
    candidate_seed = int(frame_contract["background"]["background_random_state_base"]) + seed_index
    final_seed = candidate_seed + 1_000_000
    requested_candidates = int(finite_contract["candidate_background_points_per_taxon_M"])
    required_final = int(finite_contract["final_background_points_per_taxon_M"])

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    provenance_frames: list[pd.DataFrame] = []
    for m_km in [150, 300, 500]:
        m_mask = occurrence_buffer_membership(target, common_geometry, buffer_km=float(m_km))
        candidates = sample_target_group_background(
            common_geometry,
            target,
            m_mask=m_mask,
            n_points=requested_candidates,
            cell_size_degrees=float(finite_contract["grid_cell_degrees"]),
            focal_species=name,
            random_state=candidate_seed,
        )
        featured, provenance = extract_raster_values(candidates, raster_specs)
        provenance = provenance.copy()
        provenance["role"] = f"repair_candidate_background_{m_km}km"
        provenance_frames.append(provenance)
        selected, audit = freeze_finite_comparison_frame(
            featured,
            predictors,
            required_rows=required_final,
            random_state=final_seed,
        )
        frame_sha = None
        frame_file = None
        if audit.state == "finite_comparison_frame_frozen":
            if len(selected) != required_final:
                raise RuntimeError("finite-frame freezer returned wrong final denominator")
            ids = _comparison_ids(name, m_km, selected)
            selected = selected.copy()
            selected.insert(0, "comparison_row_id", ids)
            keep = ["comparison_row_id", "longitude", "latitude", *predictors]
            selected = selected.loc[:, keep]
            if selected["comparison_row_id"].duplicated().any():
                raise RuntimeError("repair comparison row IDs are not unique")
            out = output_dir / f"M{m_km}_finite_comparison_frame.parquet"
            selected.to_parquet(out, index=False)
            frame_sha = sha256(out.read_bytes()).hexdigest()
            frame_file = out.name
        results.append({
            "M_km": int(m_km),
            "state": audit.state,
            "candidate_rows_materialized": audit.candidate_rows,
            "all_43_predictor_finite_rows": audit.all_predictor_finite_rows,
            "finite_fraction": (
                None if audit.candidate_rows == 0
                else float(audit.all_predictor_finite_rows / audit.candidate_rows)
            ),
            "selected_rows": audit.selected_rows,
            "required_rows": audit.required_rows,
            "candidate_sampling_random_state": candidate_seed,
            "final_selection_random_state": final_seed,
            "comparison_frame_file": frame_file,
            "comparison_frame_sha256": frame_sha,
        })

    provenance = pd.concat(provenance_frames, ignore_index=True).drop_duplicates().reset_index(drop=True)
    provenance.to_csv(output_dir / "repair_raster_provenance.csv", index=False)
    raster_resolution.to_csv(output_dir / "repair_chelsa_resolution_ledger.csv", index=False)
    receipt = {
        "result_version": "product_b_same_target_successor_finite_frame_preflight_taxon_v0.1",
        "taxon": name,
        "taxon_index": int(args.taxon_index),
        "historical_specieskeys": list(historical_keys),
        "source_modes": list(MODES),
        "source_blind_common_geometry_cells": int(len(common_geometry)),
        "common_block_centers_sha256": centers_sha,
        "active_predictors": list(predictors),
        "active_predictor_count": len(predictors),
        "candidate_background_points_requested": requested_candidates,
        "final_background_points_required": required_final,
        "cells": results,
        "all_three_M_frames_frozen": bool(all(r["state"] == "finite_comparison_frame_frozen" for r in results)),
        "model_fit_opened": False,
        "prediction_scores_computed": False,
        "paired_discordance_opened": False,
        "reference_ceiling_computed": False,
        "heldout_12_paired_discordance_read": False,
        "process_knockout_opened": False,
        "taxon_replaced": False,
        "M_selected_from_outcome": False,
        "procedure_selected_from_outcome": False,
        "claim_strength": "environmental_availability_preflight_only_not_empirical_evidence",
    }
    (output_dir / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
