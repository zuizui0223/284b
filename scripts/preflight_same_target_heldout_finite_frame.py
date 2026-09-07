#!/usr/bin/env python3
"""Freeze held-out finite comparison frames before repaired reference opening.

This stage reconstructs the already-frozen source-blind held-out geometry,
oversamples target-group background cells, extracts the unchanged 43 CHELSA
predictors, and freezes exactly 2,000 all-predictor-finite rows per taxon x M
when possible. It does not fit models, compute prediction scores, read a
reference ceiling, compute paired discordance, or open process knockouts.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pandas as pd

from product_b_v5.finite_comparison_frame import freeze_finite_comparison_frame
from scripts.run_same_target_layer1_baseline_fit_taxon import (
    MODES,
    _comparison_ids,
    _retained_source_frames,
    _scan_taxon,
)

ROOT = Path(__file__).resolve().parents[1]
REPAIR = ROOT / "config/product_b_same_target_heldout_finite_frame_repair_contract_v0_1.json"
FIT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
FRAME = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
REGISTRY = ROOT / "registry/product_b_same_target_source_identity_pass_taxa_v0_1.csv"
SAMPLING = ROOT / "results/product_b_same_target_source_mode_sampling_v0_1.json"


def _hash_centers(centers: np.ndarray) -> str:
    return sha256(np.asarray(centers, dtype="<f8").tobytes(order="C")).hexdigest()


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
    fit_contract = json.loads(FIT.read_text(encoding="utf-8"))
    frame_contract = json.loads(FRAME.read_text(encoding="utf-8"))
    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    registry = pd.read_csv(REGISTRY)
    if len(registry) != 12 or not 0 <= int(args.taxon_index) < 12:
        raise RuntimeError("held-out finite-frame taxon inventory drifted")
    if int(repair["heldout_taxa"]) != 12 or int(repair["taxon_M_cells"]) != 36:
        raise RuntimeError("held-out repair denominator drifted")
    if int(repair["active_predictors_required"]) != 43:
        raise RuntimeError("held-out repair predictor count drifted")
    if int(repair["candidate_background_points_per_taxon_M"]) != 8000:
        raise RuntimeError("held-out repair candidate background count drifted")
    if int(repair["final_background_points_per_taxon_M"]) != 2000:
        raise RuntimeError("held-out repair final background count drifted")
    if any(bool(repair["preflight"][k]) for k in (
        "model_refit_allowed",
        "prediction_score_computation_allowed",
        "paired_discordance_computation_allowed",
        "reference_ceiling_read_allowed",
        "heldout_pairing_allowed",
        "process_knockout_allowed",
    )):
        raise RuntimeError("held-out preflight information boundary drifted")

    row = registry.iloc[int(args.taxon_index)]
    name = str(row["scientific_name"])
    specieskey = str(row["resolved_snapshot_specieskey"])
    result_by_name = {str(x["requested_name"]): x for x in sampling.get("results", [])}
    if result_by_name.get(name, {}).get("state") != "source_mode_sampling_passed":
        raise RuntimeError("held-out taxon no longer passes frozen source-mode sampling")
    if sampling.get("paired_discordance_opened") is not False:
        raise RuntimeError("held-out paired discordance already opened before frame repair")

    mode_a, mode_b = _scan_taxon(specieskey)
    retained = _retained_source_frames(name, mode_a, mode_b)
    del mode_a, mode_b
    thin_deg = float(frame_contract["shared_frame_coordinate_pooling"]["source_specific_thinning_cell_degrees"])
    source_thin: dict[str, pd.DataFrame] = {}
    for mode in MODES:
        if retained[mode].empty:
            raise RuntimeError(f"no retained held-out rows for {mode}")
        source_thin[mode] = thin_to_grid(retained[mode], cell_size_degrees=thin_deg)
        if len(source_thin[mode]) < 30:
            raise RuntimeError(f"held-out post-thinning source unexpectedly sparse: {mode}")
    pooled = pd.concat([source_thin[MODES[0]], source_thin[MODES[1]]], ignore_index=True)
    common_geometry = thin_to_grid(
        pooled,
        cell_size_degrees=float(frame_contract["shared_frame_coordinate_pooling"]["pooled_geometry_thinning_cell_degrees"]),
    )
    partition = make_presence_spatial_partition(
        common_geometry["longitude"].to_numpy(float),
        common_geometry["latitude"].to_numpy(float),
        n_blocks=int(frame_contract["spatial_blocks"]["n_blocks"]),
        holdout_fraction=0.5,
        random_state=int(frame_contract["spatial_blocks"]["random_state"]),
    )
    centers_sha = _hash_centers(partition.centers_xyz)

    target = load_gbif_download(Path(args.target_group)).records
    target = admit_occurrences(target, config=OccurrenceAdmissionConfig()).accepted
    target = target.dropna(subset=["longitude", "latitude"]).reset_index(drop=True)
    if target.empty:
        raise RuntimeError("held-out target-group artifact has no admissible coordinates")

    manifest = pd.read_csv(args.chelsa_manifest)
    raster_specs, raster_resolution = raster_specs_from_chelsa_manifest(
        manifest, include_availability=("current",), strict=True
    )
    predictors = tuple(spec.predictor for spec in raster_specs)
    if len(predictors) != 43 or len(set(predictors)) != 43:
        raise RuntimeError("held-out finite-frame preflight requires 43 unique predictors")
    if len(raster_specs) != int(fit_contract["environmental_predictor_source"]["active_predictors_required"]):
        raise RuntimeError("held-out CHELSA predictor count differs from frozen fit contract")

    alphabetical = sorted(registry["scientific_name"].astype(str))
    seed_index = alphabetical.index(name)
    candidate_seed = int(frame_contract["background"]["background_random_state_base"]) + seed_index
    final_seed = candidate_seed + int(repair["final_selection_seed_offset"])
    requested = int(repair["candidate_background_points_per_taxon_M"])
    required = int(repair["final_background_points_per_taxon_M"])

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    cells: list[dict[str, object]] = []
    provenance_frames: list[pd.DataFrame] = []
    for m_km in (150, 300, 500):
        m_mask = occurrence_buffer_membership(target, common_geometry, buffer_km=float(m_km))
        candidates = sample_target_group_background(
            common_geometry,
            target,
            m_mask=m_mask,
            n_points=requested,
            cell_size_degrees=float(repair["grid_cell_degrees"]),
            focal_species=name,
            random_state=candidate_seed,
        )
        featured, provenance = extract_raster_values(candidates, raster_specs)
        provenance = provenance.copy()
        provenance["role"] = f"heldout_repair_candidate_background_{m_km}km"
        provenance_frames.append(provenance)
        selected, audit = freeze_finite_comparison_frame(
            featured, predictors, required_rows=required, random_state=final_seed
        )
        frame_file = None
        frame_sha = None
        if audit.state == "finite_comparison_frame_frozen":
            ids = _comparison_ids(name, m_km, selected)
            selected = selected.copy()
            selected.insert(0, "comparison_row_id", ids)
            selected = selected.loc[:, ["comparison_row_id", "longitude", "latitude", *predictors]]
            if len(selected) != required or selected["comparison_row_id"].duplicated().any():
                raise RuntimeError("held-out frozen finite comparison frame integrity failed")
            path = outdir / f"M{m_km}_finite_comparison_frame.parquet"
            selected.to_parquet(path, index=False)
            frame_file = path.name
            frame_sha = sha256(path.read_bytes()).hexdigest()
        cells.append({
            "M_km": m_km,
            "state": audit.state,
            "candidate_rows_materialized": audit.candidate_rows,
            "all_43_predictor_finite_rows": audit.all_predictor_finite_rows,
            "finite_fraction": None if audit.candidate_rows == 0 else float(audit.all_predictor_finite_rows / audit.candidate_rows),
            "selected_rows": audit.selected_rows,
            "required_rows": audit.required_rows,
            "candidate_sampling_random_state": candidate_seed,
            "final_selection_random_state": final_seed,
            "comparison_frame_file": frame_file,
            "comparison_frame_sha256": frame_sha,
        })

    pd.concat(provenance_frames, ignore_index=True).drop_duplicates().to_csv(
        outdir / "repair_raster_provenance.csv", index=False
    )
    raster_resolution.to_csv(outdir / "repair_chelsa_resolution_ledger.csv", index=False)
    receipt = {
        "result_version": "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.1",
        "taxon": name,
        "taxon_index": int(args.taxon_index),
        "specieskey": specieskey,
        "source_modes": list(MODES),
        "source_blind_common_geometry_cells": int(len(common_geometry)),
        "common_block_centers_sha256": centers_sha,
        "active_predictors": list(predictors),
        "active_predictor_count": 43,
        "cells": cells,
        "all_three_M_frames_frozen": bool(all(x["state"] == "finite_comparison_frame_frozen" for x in cells)),
        "model_refit_opened": False,
        "prediction_scores_computed": False,
        "paired_discordance_opened": False,
        "reference_ceiling_read": False,
        "heldout_pairing_opened": False,
        "process_knockout_opened": False,
        "counts_as_empirical_conclusion": False,
        "claim_strength": "heldout_environmental_availability_preflight_only_not_empirical_evidence",
    }
    (outdir / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
