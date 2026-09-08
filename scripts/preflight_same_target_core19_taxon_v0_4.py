#!/usr/bin/env python3
"""Uniform outcome-blind core19 comparison-frame qualification v0.4.

This is a distinct endpoint version, not a repair of the all-43 v0.3 frame.
Every successor or held-out taxon is reconstructed from its frozen source-blind
coordinate geometry and frozen target-group source.  No all-43 frame rows are
inherited.  The only v0.3 metadata reused are the source-blind geometry hash and
pre-outcome deterministic seed metadata.

The predictor universe is defined semantically before execution by the pinned
CHELSA manifest rule ``candidate_class == core_climate`` and must equal bio1..19
in manifest order.  All eligible target-group grid cells are enumerated before
core19 finite filtering.  Exactly 2,000 rows are frozen per taxon x M only when
available.  No model fit or cross-source outcome is opened.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pandas as pd

from product_b_v5.finite_comparison_frame import freeze_finite_comparison_frame

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config/product_b_same_target_core19_requalification_contract_v0_4.json"
FRAME_CONTRACT_PATH = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
CONTRACT_VERSION = "product_b_same_target_core19_requalification_v0.4"
SUCCESSOR_PARENT = "product_b_same_target_successor_finite_frame_preflight_taxon_v0.3"
HELDOUT_PARENT = "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.3"
SUCCESSOR_RESULT = "product_b_same_target_successor_core19_preflight_taxon_v0.4"
HELDOUT_RESULT = "product_b_same_target_heldout_core19_preflight_taxon_v0.4"


def _hash_centers(centers: np.ndarray) -> str:
    return sha256(np.asarray(centers, dtype="<f8").tobytes(order="C")).hexdigest()


def _panel_helpers(panel: str):
    if panel == "successor":
        from scripts.run_same_target_successor_layer1_fit_taxon import (
            MODES,
            _comparison_ids,
            _retained_source_frames,
            _scan_taxon,
        )
        return MODES, _comparison_ids, _retained_source_frames, _scan_taxon
    if panel == "heldout":
        from scripts.run_same_target_layer1_baseline_fit_taxon import (
            MODES,
            _comparison_ids,
            _retained_source_frames,
            _scan_taxon,
        )
        return MODES, _comparison_ids, _retained_source_frames, _scan_taxon
    raise ValueError("panel must be successor or heldout")


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

    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", choices=("successor", "heldout"), required=True)
    ap.add_argument("--taxon-index", type=int, required=True)
    ap.add_argument("--parent-v0-3-dir", required=True)
    ap.add_argument("--target-group", required=True)
    ap.add_argument("--chelsa-manifest", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    panel = str(args.panel)
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    frame_contract = json.loads(FRAME_CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("contract_version") != CONTRACT_VERSION:
        raise RuntimeError("wrong core19 v0.4 contract")
    q = contract["uniform_requalification"]
    if int(q["final_background_points_per_taxon_M"]) != 2000:
        raise RuntimeError("core19 background denominator drifted")
    if [int(x) for x in q["M_km"]] != [150, 300, 500]:
        raise RuntimeError("core19 M grid drifted")
    if q.get("all_taxa_are_requalified_from_coordinates_not_only_v0_3_unresolved_taxa") is not True:
        raise RuntimeError("core19 qualification must be uniform over all taxa")
    if q.get("all43_v0_3_frame_bytes_are_not_reused_as_core19_frames") is not True:
        raise RuntimeError("core19 qualification may not inherit all-43 frame bytes")
    for k in (
        "qualification_model_fit_allowed",
        "qualification_prediction_scores_allowed",
        "qualification_paired_discordance_allowed",
        "qualification_reference_ceiling_allowed",
        "qualification_heldout_pairing_allowed",
        "qualification_process_knockout_allowed",
    ):
        if contract["information_boundary"].get(k) is not False:
            raise RuntimeError(f"core19 qualification boundary drifted: {k}")

    parent_dir = Path(args.parent_v0_3_dir)
    parent_path = parent_dir / "receipt.json"
    parent_bytes = parent_path.read_bytes()
    parent = json.loads(parent_bytes)
    expected_parent = SUCCESSOR_PARENT if panel == "successor" else HELDOUT_PARENT
    result_version = SUCCESSOR_RESULT if panel == "successor" else HELDOUT_RESULT
    if parent.get("result_version") != expected_parent:
        raise RuntimeError("core19 qualification received wrong v0.3 parent receipt")
    if int(parent.get("taxon_index", -1)) != int(args.taxon_index):
        raise RuntimeError("core19 qualification taxon index mismatch")
    if parent.get("counts_as_empirical_conclusion") is not False:
        raise RuntimeError("v0.3 parent was incorrectly marked empirical")
    parent_boundary = (
        ("model_fit_opened", "prediction_scores_computed", "paired_discordance_opened", "reference_ceiling_computed", "heldout_12_paired_discordance_read", "process_knockout_opened")
        if panel == "successor"
        else ("model_refit_opened", "prediction_scores_computed", "paired_discordance_opened", "reference_ceiling_read", "heldout_pairing_opened", "process_knockout_opened")
    )
    for key in parent_boundary:
        if parent.get(key) is not False:
            raise RuntimeError(f"v0.3 parent crossed outcome boundary: {key}")

    old_predictors = tuple(str(x) for x in parent.get("active_predictors", []))
    if len(old_predictors) != 43 or len(set(old_predictors)) != 43:
        raise RuntimeError("v0.3 parent must retain its frozen 43-predictor identity")
    parent_cells = {int(c["M_km"]): dict(c) for c in parent.get("cells", [])}
    if set(parent_cells) != {150, 300, 500}:
        raise RuntimeError("v0.3 parent M inventory drifted")
    candidate_seeds = {int(c["candidate_sampling_random_state"]) for c in parent_cells.values()}
    final_seeds = {int(c["final_selection_random_state"]) for c in parent_cells.values()}
    if len(candidate_seeds) != 1 or len(final_seeds) != 1:
        raise RuntimeError("v0.3 pre-outcome seed metadata drifted across M")
    candidate_seed = candidate_seeds.pop()
    final_seed = final_seeds.pop()

    MODES, comparison_ids, retained_fn, scan_fn = _panel_helpers(panel)
    name = str(parent["taxon"])
    if panel == "successor":
        identity = tuple(str(x) for x in parent.get("historical_specieskeys", []))
        if not identity:
            raise RuntimeError("successor v0.3 parent lacks frozen historical key set")
        mode_a, mode_b = scan_fn(identity)
        identity_payload = {"historical_specieskeys": list(identity)}
    else:
        specieskey = str(parent.get("specieskey") or "")
        if not specieskey:
            raise RuntimeError("held-out v0.3 parent lacks specieskey")
        mode_a, mode_b = scan_fn(specieskey)
        identity_payload = {"specieskey": specieskey}
    retained = retained_fn(name, mode_a, mode_b)
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
    geometry_sha = _hash_centers(partition.centers_xyz)
    if geometry_sha != str(parent.get("common_block_centers_sha256")):
        raise RuntimeError("source-blind common geometry changed from frozen v0.3 provenance")

    target = load_gbif_download(Path(args.target_group)).records
    target = admit_occurrences(target, config=OccurrenceAdmissionConfig()).accepted
    target = target.dropna(subset=["longitude", "latitude"]).reset_index(drop=True)
    if target.empty:
        raise RuntimeError("frozen target-group artifact has no admissible coordinates")

    manifest = pd.read_csv(args.chelsa_manifest)
    core_manifest = manifest.loc[manifest["candidate_class"].astype(str).str.strip() == "core_climate"].copy()
    expected_core = tuple(str(x) for x in contract["predictor_universe"]["expected_predictors_in_manifest_order"])
    actual_core = tuple(core_manifest["predictor"].astype(str).tolist())
    if actual_core != expected_core or actual_core != tuple(f"bio{i}" for i in range(1, 20)):
        raise RuntimeError(f"manifest-defined core19 identity drifted: {actual_core}")
    if len(actual_core) != int(contract["predictor_universe"]["expected_predictor_count"]):
        raise RuntimeError("core19 predictor denominator drifted")
    raster_specs, raster_resolution = raster_specs_from_chelsa_manifest(
        core_manifest,
        include_availability=("current",),
        strict=True,
    )
    if tuple(spec.predictor for spec in raster_specs) != actual_core:
        raise RuntimeError("resolved core19 raster order differs from frozen semantic rule")

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    cell_rows: list[dict[str, object]] = []
    provenance_frames: list[pd.DataFrame] = []
    for m in (150, 300, 500):
        m_mask = occurrence_buffer_membership(target, common_geometry, buffer_km=float(m))
        candidates = sample_target_group_background(
            common_geometry,
            target,
            m_mask=m_mask,
            n_points=max(1, len(target)),
            cell_size_degrees=float(q["grid_cell_degrees"]),
            focal_species=name,
            random_state=candidate_seed,
        )
        featured, provenance = extract_raster_values(candidates, raster_specs)
        provenance = provenance.copy()
        provenance["role"] = f"core19_v0_4_exhaustive_candidate_background_{m}km"
        provenance_frames.append(provenance)
        selected, audit = freeze_finite_comparison_frame(
            featured,
            actual_core,
            required_rows=2000,
            random_state=final_seed,
        )
        state = "core19_comparison_frame_frozen" if audit.state == "finite_comparison_frame_frozen" else "core19_comparison_frame_unresolved"
        frame_file = None
        frame_sha = None
        if state == "core19_comparison_frame_frozen":
            ids = comparison_ids(name, m, selected)
            selected = selected.copy()
            selected.insert(0, "comparison_row_id", ids)
            selected = selected.loc[:, ["comparison_row_id", "longitude", "latitude", *actual_core]]
            if len(selected) != 2000 or selected["comparison_row_id"].astype(str).duplicated().any():
                raise RuntimeError("core19 frozen frame integrity failed")
            values = selected.loc[:, list(actual_core)].apply(pd.to_numeric, errors="coerce").to_numpy(float)
            if not np.isfinite(values).all():
                raise RuntimeError("core19 frozen frame contains non-finite predictor")
            path = outdir / f"M{m}_core19_comparison_frame.parquet"
            selected.to_parquet(path, index=False)
            frame_file = path.name
            frame_sha = sha256(path.read_bytes()).hexdigest()
        cell_rows.append({
            "M_km": int(m),
            "state": state,
            "candidate_rows_materialized": int(audit.candidate_rows),
            "core19_finite_rows": int(audit.all_predictor_finite_rows),
            "finite_fraction": None if audit.candidate_rows == 0 else float(audit.all_predictor_finite_rows / audit.candidate_rows),
            "selected_rows": int(audit.selected_rows),
            "required_rows": 2000,
            "candidate_sampling_random_state": int(candidate_seed),
            "final_selection_random_state": int(final_seed),
            "comparison_frame_file": frame_file,
            "comparison_frame_sha256": frame_sha,
            "exhaustive_eligible_target_group_enumeration": True,
        })

    pd.concat(provenance_frames, ignore_index=True).drop_duplicates().to_csv(outdir / "core19_raster_provenance.csv", index=False)
    raster_resolution.to_csv(outdir / "core19_chelsa_resolution_ledger.csv", index=False)
    all_three = all(c["state"] == "core19_comparison_frame_frozen" for c in cell_rows)
    receipt = {
        "result_version": result_version,
        "contract_version": CONTRACT_VERSION,
        "panel": panel,
        "taxon": name,
        "taxon_index": int(args.taxon_index),
        **identity_payload,
        "parent_v0_3_result_version": expected_parent,
        "parent_v0_3_receipt_sha256": sha256(parent_bytes).hexdigest(),
        "parent_v0_3_frame_bytes_reused": False,
        "parent_v0_3_geometry_and_seed_metadata_only_reused": True,
        "source_modes": list(MODES),
        "source_blind_common_geometry_cells": int(len(common_geometry)),
        "common_block_centers_sha256": geometry_sha,
        "predictor_selection_rule": "CHELSA manifest candidate_class == core_climate",
        "active_predictors": list(actual_core),
        "active_predictor_count": 19,
        "M_km": [150, 300, 500],
        "cells": cell_rows,
        "all_three_M_frames_frozen": bool(all_three),
        "model_fit_opened": False,
        "prediction_scores_computed": False,
        "paired_discordance_opened": False,
        "reference_ceiling_opened_or_read": False,
        "heldout_pairing_opened": False,
        "process_knockout_opened": False,
        "counts_as_empirical_conclusion": False,
        "claim_strength": "core19_uniform_comparison_frame_qualification_only_not_empirical_evidence",
    }
    (outdir / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
