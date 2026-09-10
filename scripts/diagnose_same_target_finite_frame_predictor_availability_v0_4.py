#!/usr/bin/env python3
"""Outcome-blind predictor-availability diagnostic for v0.3 unresolved frames.

This script is strictly upstream of model fitting and cross-source outcomes. It
reconstructs only v0.3-unresolved taxon x M candidate backgrounds, verifies the
published all-43 finite count exactly, and audits whether the manifest-defined
19 core BIOCLIM predictors have adequate complete-case support. It also emits
per-predictor missingness and leave-one-predictor-out complete-case counts.

No model fit, prediction score, Schoener D, reference ceiling, held-out pairing,
or process-knockout result is read or computed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FRAME_CONTRACT = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
SUCCESSOR_REPAIR = ROOT / "config/product_b_same_target_reference_finite_frame_repair_contract_v0_3.json"
HELDOUT_REPAIR = ROOT / "config/product_b_same_target_heldout_finite_frame_repair_contract_v0_3.json"

SUCCESSOR_RESULT = "product_b_same_target_successor_finite_frame_preflight_taxon_v0.3"
HELDOUT_RESULT = "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.3"
SUCCESSOR_CONTRACT = "product_b_same_target_reference_finite_frame_repair_v0.3"
HELDOUT_CONTRACT = "product_b_same_target_heldout_finite_frame_repair_v0.3"
RESULT = "product_b_same_target_finite_frame_predictor_availability_diagnostic_v0.4"


def _hash_centers(centers: np.ndarray) -> str:
    return sha256(np.asarray(centers, dtype="<f8").tobytes(order="C")).hexdigest()


def _load_panel_helpers(panel: str):
    if panel == "successor":
        from scripts.run_same_target_successor_layer1_fit_taxon import (
            MODES,
            _retained_source_frames,
            _scan_taxon,
        )
        return MODES, _retained_source_frames, _scan_taxon
    if panel == "heldout":
        from scripts.run_same_target_layer1_baseline_fit_taxon import (
            MODES,
            _retained_source_frames,
            _scan_taxon,
        )
        return MODES, _retained_source_frames, _scan_taxon
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
    parent_dir = Path(args.parent_v0_3_dir)
    parent_path = parent_dir / "receipt.json"
    parent_bytes = parent_path.read_bytes()
    parent = json.loads(parent_bytes)
    expected_result = SUCCESSOR_RESULT if panel == "successor" else HELDOUT_RESULT
    expected_contract = SUCCESSOR_CONTRACT if panel == "successor" else HELDOUT_CONTRACT
    if parent.get("result_version") != expected_result:
        raise RuntimeError("diagnostic received wrong v0.3 receipt type")
    if parent.get("repair_contract_version") != expected_contract:
        raise RuntimeError("diagnostic received wrong v0.3 repair contract")
    if int(parent.get("taxon_index", -1)) != int(args.taxon_index):
        raise RuntimeError("diagnostic taxon index mismatch")

    boundary_keys = (
        ("model_fit_opened", "prediction_scores_computed", "paired_discordance_opened", "reference_ceiling_computed", "heldout_12_paired_discordance_read", "process_knockout_opened")
        if panel == "successor"
        else ("model_refit_opened", "prediction_scores_computed", "paired_discordance_opened", "reference_ceiling_read", "heldout_pairing_opened", "process_knockout_opened")
    )
    for key in boundary_keys:
        if parent.get(key) is not False:
            raise RuntimeError(f"v0.3 parent crossed information boundary: {key}")
    if parent.get("counts_as_empirical_conclusion") is not False:
        raise RuntimeError("v0.3 parent must remain non-empirical")

    cells = {int(c["M_km"]): dict(c) for c in parent.get("cells", [])}
    if set(cells) != {150, 300, 500}:
        raise RuntimeError("v0.3 parent M inventory drifted")
    unresolved = [m for m in (150, 300, 500) if cells[m].get("state") != "finite_comparison_frame_frozen"]
    if not unresolved:
        raise RuntimeError("predictor-availability diagnostic may run only for v0.3-unresolved taxa")

    active = tuple(str(x) for x in parent.get("active_predictors", []))
    if len(active) != 43 or len(set(active)) != 43:
        raise RuntimeError("v0.3 parent predictor universe is not frozen 43")

    frame_contract = json.loads(FRAME_CONTRACT.read_text(encoding="utf-8"))
    repair_path = SUCCESSOR_REPAIR if panel == "successor" else HELDOUT_REPAIR
    repair = json.loads(repair_path.read_text(encoding="utf-8"))
    grid_cell_degrees = float(
        repair["finite_frame"]["grid_cell_degrees"] if panel == "successor" else repair["grid_cell_degrees"]
    )

    MODES, retained_fn, scan_fn = _load_panel_helpers(panel)
    name = str(parent["taxon"])
    if panel == "successor":
        historical_keys = tuple(str(x) for x in parent.get("historical_specieskeys", []))
        if not historical_keys:
            raise RuntimeError("successor v0.3 receipt lacks historical specieskeys")
        mode_a, mode_b = scan_fn(historical_keys)
    else:
        specieskey = str(parent.get("specieskey") or "")
        if not specieskey:
            raise RuntimeError("held-out v0.3 receipt lacks specieskey")
        mode_a, mode_b = scan_fn(specieskey)
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
    if _hash_centers(partition.centers_xyz) != str(parent.get("common_block_centers_sha256")):
        raise RuntimeError("source-blind common geometry changed since v0.3")

    target = load_gbif_download(Path(args.target_group)).records
    target = admit_occurrences(target, config=OccurrenceAdmissionConfig()).accepted
    target = target.dropna(subset=["longitude", "latitude"]).reset_index(drop=True)
    if target.empty:
        raise RuntimeError("target-group artifact has no admissible coordinates")

    manifest = pd.read_csv(args.chelsa_manifest)
    raster_specs, _ = raster_specs_from_chelsa_manifest(manifest, include_availability=("current",), strict=True)
    actual = tuple(spec.predictor for spec in raster_specs)
    if actual != active:
        raise RuntimeError("diagnostic CHELSA predictor identity differs from v0.3 parent")
    manifest_by_predictor = manifest.set_index("predictor", drop=False)
    core = tuple(
        p for p in active
        if str(manifest_by_predictor.loc[p, "candidate_class"]).strip() == "core_climate"
    )
    if core != tuple(f"bio{i}" for i in range(1, 20)):
        raise RuntimeError(f"manifest-defined core climate universe drifted: {core}")

    candidate_seeds = {int(c["candidate_sampling_random_state"]) for c in cells.values()}
    if len(candidate_seeds) != 1:
        raise RuntimeError("v0.3 candidate seed identity drifted across M")
    candidate_seed = candidate_seeds.pop()

    cell_rows: list[dict[str, object]] = []
    predictor_rows: list[dict[str, object]] = []
    for m in unresolved:
        parent_cell = cells[m]
        m_mask = occurrence_buffer_membership(target, common_geometry, buffer_km=float(m))
        candidates = sample_target_group_background(
            common_geometry,
            target,
            m_mask=m_mask,
            n_points=max(1, len(target)),
            cell_size_degrees=grid_cell_degrees,
            focal_species=name,
            random_state=candidate_seed,
        )
        featured, provenance = extract_raster_values(candidates, raster_specs)
        values = featured.loc[:, list(active)].apply(pd.to_numeric, errors="coerce").to_numpy(float)
        finite = np.isfinite(values)
        missing_per_row = (~finite).sum(axis=1)
        all43 = int(np.sum(missing_per_row == 0))
        if all43 != int(parent_cell.get("all_43_predictor_finite_rows", -1)):
            raise RuntimeError(
                f"diagnostic reconstruction mismatch for {name} M{m}: {all43} != {parent_cell.get('all_43_predictor_finite_rows')}"
            )
        if len(featured) != int(parent_cell.get("candidate_rows_materialized", -1)):
            raise RuntimeError("diagnostic candidate denominator does not reproduce v0.3")

        core_idx = [active.index(p) for p in core]
        core19 = int(np.sum(finite[:, core_idx].all(axis=1)))
        cell_rows.append({
            "panel": panel,
            "taxon": name,
            "taxon_index": int(args.taxon_index),
            "M_km": int(m),
            "candidate_rows_materialized": int(len(featured)),
            "all_43_finite_rows_reproduced": all43,
            "core19_finite_rows": core19,
            "core19_ready_for_2000": bool(core19 >= 2000),
            "missing_rows_any_of_43": int(np.sum(missing_per_row > 0)),
            "rows_missing_exactly_one_predictor": int(np.sum(missing_per_row == 1)),
        })

        prov = provenance.drop_duplicates(subset=["predictor"]).set_index("predictor")
        for j, predictor in enumerate(active):
            miss = ~finite[:, j]
            all_except = int(np.sum((missing_per_row - miss.astype(int)) == 0))
            row = manifest_by_predictor.loc[predictor]
            predictor_rows.append({
                "panel": panel,
                "taxon": name,
                "taxon_index": int(args.taxon_index),
                "M_km": int(m),
                "predictor": predictor,
                "candidate_class": str(row.get("candidate_class", "")),
                "process": str(row.get("process", "")),
                "mechanism": str(row.get("mechanism", "")),
                "finite_rows": int(np.sum(finite[:, j])),
                "missing_rows": int(np.sum(miss)),
                "missing_fraction": float(np.mean(miss)) if len(miss) else None,
                "all_other_42_finite_rows": all_except,
                "gain_if_only_this_predictor_removed": int(all_except - all43),
                "raster_nodata": None if predictor not in prov.index or pd.isna(prov.loc[predictor, "nodata"]) else float(prov.loc[predictor, "nodata"]),
            })

    cell_frame = pd.DataFrame(cell_rows).sort_values(["M_km"]).reset_index(drop=True)
    predictor_frame = pd.DataFrame(predictor_rows).sort_values(["M_km", "missing_rows", "predictor"], ascending=[True, False, True]).reset_index(drop=True)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cell_frame.to_csv(out / "cell_availability.csv", index=False)
    predictor_frame.to_csv(out / "predictor_missingness.csv", index=False)
    summary = {
        "result_version": RESULT,
        "panel": panel,
        "taxon": name,
        "taxon_index": int(args.taxon_index),
        "parent_v0_3_result_version": expected_result,
        "parent_v0_3_repair_contract_version": expected_contract,
        "parent_v0_3_receipt_sha256": sha256(parent_bytes).hexdigest(),
        "unresolved_M_km": [int(x) for x in unresolved],
        "unresolved_cell_count": int(len(unresolved)),
        "core_predictor_rule": "manifest candidate_class == core_climate",
        "core_predictors": list(core),
        "core_predictor_count": 19,
        "all_unresolved_cells_core19_ready_for_2000": bool(cell_frame["core19_ready_for_2000"].all()),
        "minimum_core19_finite_rows": int(cell_frame["core19_finite_rows"].min()),
        "model_fit_opened": False,
        "prediction_scores_computed": False,
        "paired_discordance_opened": False,
        "reference_ceiling_opened_or_read": False,
        "heldout_pairing_opened": False,
        "process_knockout_opened": False,
        "counts_as_empirical_conclusion": False,
        "claim_strength": "predictor_availability_diagnostic_only_not_empirical_evidence",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
