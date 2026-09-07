#!/usr/bin/env python3
"""Outcome-blind successor finite-frame preflight v0.2.

Identical scientific design to v0.1, except the engineering candidate pool is
32,000 target-group cells per taxon x M before all-43-predictor finite filtering.
No model score, paired discordance, reference ceiling, held-out outcome, or
process knockout is opened.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
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
REPAIR = ROOT / "config/product_b_same_target_reference_finite_frame_repair_contract_v0_2.json"
FIT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
FRAME = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
SAMPLING = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"


def _hash_centers(centers: np.ndarray) -> str:
    return sha256(np.asarray(centers, dtype="<f8").tobytes(order="C")).hexdigest()


def main() -> int:
    from sdmr.data import OccurrenceAdmissionConfig, admit_occurrences, extract_raster_values, load_gbif_download, raster_specs_from_chelsa_manifest, thin_to_grid
    from sdmr.data.background import occurrence_buffer_membership, sample_target_group_background
    from sdmr.validation import make_presence_spatial_partition

    ap = argparse.ArgumentParser()
    ap.add_argument("--taxon-index", type=int, required=True)
    ap.add_argument("--target-group", required=True)
    ap.add_argument("--chelsa-manifest", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    repair = json.loads(REPAIR.read_text(encoding="utf-8"))
    fit_contract = json.loads(FIT.read_text(encoding="utf-8"))
    frame_contract = json.loads(FRAME.read_text(encoding="utf-8"))
    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    if repair.get("contract_version") != "product_b_same_target_reference_finite_frame_repair_v0.2":
        raise RuntimeError("wrong repair contract version")
    finite = repair["finite_frame"]
    if int(finite["active_predictors_required"]) != 43 or int(finite["candidate_background_points_per_taxon_M"]) != 32000 or int(finite["final_background_points_per_taxon_M"]) != 2000:
        raise RuntimeError("v0.2 finite-frame denominator drifted")
    if any(bool(repair["preflight"][k]) for k in ("model_fit_allowed","prediction_score_computation_allowed","schoener_d_computation_allowed","reference_ceiling_computation_allowed","heldout_opening_allowed","process_knockout_allowed")):
        raise RuntimeError("v0.2 preflight information boundary drifted")

    eligible = [r for r in sampling.get("results", []) if r.get("state") == "successor_source_mode_sampling_passed"]
    if len(eligible) != 47 or not 0 <= args.taxon_index < 47:
        raise RuntimeError("v0.2 preflight requires frozen 47 taxa")
    row = eligible[args.taxon_index]
    name = str(row["requested_name"]).strip()
    historical_keys = tuple(sorted(str(x).strip() for x in row.get("frozen_historical_specieskeys", []) if str(x).strip()))
    if not historical_keys:
        raise RuntimeError("sampling-pass taxon lacks frozen historical keys")

    mode_a, mode_b = _scan_taxon(historical_keys)
    retained = _retained_source_frames(name, mode_a, mode_b)
    del mode_a, mode_b
    thin_deg = float(frame_contract["shared_frame_coordinate_pooling"]["source_specific_thinning_cell_degrees"])
    source_thin: dict[str, pd.DataFrame] = {}
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
    centers_sha = _hash_centers(partition.centers_xyz)

    target = load_gbif_download(Path(args.target_group)).records
    target = admit_occurrences(target, config=OccurrenceAdmissionConfig()).accepted
    target = target.dropna(subset=["longitude", "latitude"]).reset_index(drop=True)
    if target.empty:
        raise RuntimeError("target-group artifact has no admissible coordinates")

    manifest = pd.read_csv(args.chelsa_manifest)
    raster_specs, raster_resolution = raster_specs_from_chelsa_manifest(manifest, include_availability=("current",), strict=True)
    predictors = tuple(spec.predictor for spec in raster_specs)
    if len(predictors) != 43 or len(set(predictors)) != 43:
        raise RuntimeError("v0.2 preflight requires 43 unique CHELSA predictors")
    if len(raster_specs) != int(fit_contract["environmental_predictor_source"]["active_predictors_required"]):
        raise RuntimeError("CHELSA predictor count differs from frozen fit contract")

    frozen_names = sorted(_frozen_candidate_names())
    if len(frozen_names) != 72 or name not in frozen_names:
        raise RuntimeError("taxon absent from frozen 72-candidate registry")
    candidate_seed = int(frame_contract["background"]["background_random_state_base"]) + frozen_names.index(name)
    final_seed = candidate_seed + 1_000_000
    requested = 32000
    required = 2000

    outdir = Path(args.output_dir); outdir.mkdir(parents=True, exist_ok=True)
    cells: list[dict[str, object]] = []
    provenance_frames: list[pd.DataFrame] = []
    for m in (150, 300, 500):
        m_mask = occurrence_buffer_membership(target, common_geometry, buffer_km=float(m))
        candidates = sample_target_group_background(
            common_geometry, target, m_mask=m_mask, n_points=requested,
            cell_size_degrees=float(finite["grid_cell_degrees"]), focal_species=name, random_state=candidate_seed,
        )
        featured, provenance = extract_raster_values(candidates, raster_specs)
        provenance = provenance.copy(); provenance["role"] = f"repair_v0_2_candidate_background_{m}km"; provenance_frames.append(provenance)
        selected, audit = freeze_finite_comparison_frame(featured, predictors, required_rows=required, random_state=final_seed)
        frame_file = None; frame_sha = None
        if audit.state == "finite_comparison_frame_frozen":
            ids = _comparison_ids(name, m, selected)
            selected = selected.copy(); selected.insert(0, "comparison_row_id", ids)
            selected = selected.loc[:, ["comparison_row_id", "longitude", "latitude", *predictors]]
            if len(selected) != 2000 or selected["comparison_row_id"].duplicated().any():
                raise RuntimeError("v0.2 frozen frame integrity failed")
            path = outdir / f"M{m}_finite_comparison_frame.parquet"
            selected.to_parquet(path, index=False)
            frame_file = path.name; frame_sha = sha256(path.read_bytes()).hexdigest()
        cells.append({
            "M_km": m, "state": audit.state,
            "candidate_rows_materialized": audit.candidate_rows,
            "all_43_predictor_finite_rows": audit.all_predictor_finite_rows,
            "finite_fraction": None if audit.candidate_rows == 0 else float(audit.all_predictor_finite_rows / audit.candidate_rows),
            "selected_rows": audit.selected_rows, "required_rows": audit.required_rows,
            "candidate_sampling_random_state": candidate_seed, "final_selection_random_state": final_seed,
            "comparison_frame_file": frame_file, "comparison_frame_sha256": frame_sha,
        })

    pd.concat(provenance_frames, ignore_index=True).drop_duplicates().to_csv(outdir / "repair_raster_provenance.csv", index=False)
    raster_resolution.to_csv(outdir / "repair_chelsa_resolution_ledger.csv", index=False)
    receipt = {
        "result_version": "product_b_same_target_successor_finite_frame_preflight_taxon_v0.2",
        "repair_contract_version": repair["contract_version"],
        "taxon": name, "taxon_index": args.taxon_index, "historical_specieskeys": list(historical_keys),
        "source_modes": list(MODES), "source_blind_common_geometry_cells": int(len(common_geometry)),
        "common_block_centers_sha256": centers_sha, "active_predictors": list(predictors), "active_predictor_count": 43,
        "candidate_background_points_requested": requested, "final_background_points_required": required,
        "cells": cells, "all_three_M_frames_frozen": bool(all(c["state"] == "finite_comparison_frame_frozen" for c in cells)),
        "model_fit_opened": False, "prediction_scores_computed": False, "paired_discordance_opened": False,
        "reference_ceiling_computed": False, "heldout_12_paired_discordance_read": False, "process_knockout_opened": False,
        "taxon_replaced": False, "M_selected_from_outcome": False, "procedure_selected_from_outcome": False,
        "counts_as_empirical_conclusion": False,
        "claim_strength": "environmental_availability_preflight_v0_2_only_not_empirical_evidence"
    }
    (outdir / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
