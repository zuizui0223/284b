#!/usr/bin/env python3
"""Outcome-blind held-out finite-frame preflight v0.3.

Every v0.2-frozen taxon x M frame is inherited byte-for-byte.  Only a
v0.2-unresolved cell is repaired by exhaustively enumerating the eligible
frozen target-group grid cells, filtering to rows where all 43 predictors are
finite, and freezing exactly 2,000 rows if available.

No model fit, prediction score, paired discordance, reference ceiling,
held-out pairing, or process knockout is opened here.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil

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
REPAIR = ROOT / "config/product_b_same_target_heldout_finite_frame_repair_contract_v0_3.json"
FIT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
FRAME = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
REGISTRY = ROOT / "registry/product_b_same_target_source_identity_pass_taxa_v0_1.csv"
SAMPLING = ROOT / "results/product_b_same_target_source_mode_sampling_v0_1.json"

PARENT_RESULT = "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.2"
RESULT = "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.3"
CONTRACT = "product_b_same_target_heldout_finite_frame_repair_v0.3"


def _hash_centers(centers: np.ndarray) -> str:
    return sha256(np.asarray(centers, dtype="<f8").tobytes(order="C")).hexdigest()


def _verify_parent_frame(
    parent_dir: Path,
    cell: dict[str, object],
    predictors: tuple[str, ...],
) -> tuple[str, str]:
    if cell.get("state") != "finite_comparison_frame_frozen":
        raise RuntimeError("attempted to inherit a non-frozen held-out v0.2 cell")
    if int(cell.get("selected_rows", -1)) != 2000:
        raise RuntimeError("held-out v0.2 frozen denominator drifted")
    name = str(cell.get("comparison_frame_file") or "")
    expected = str(cell.get("comparison_frame_sha256") or "")
    if not name or len(expected) != 64:
        raise RuntimeError("held-out v0.2 frozen cell lacks frame identity")
    path = parent_dir / name
    if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError("held-out v0.2 frozen frame bytes changed")
    frame = pd.read_parquet(path)
    required = {"comparison_row_id", "longitude", "latitude", *predictors}
    if len(frame) != 2000 or required - set(frame.columns):
        raise RuntimeError("held-out v0.2 inherited frame schema/denominator drifted")
    if frame["comparison_row_id"].astype(str).duplicated().any():
        raise RuntimeError("held-out inherited comparison row IDs are not unique")
    values = frame.loc[:, list(predictors)].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    if not np.isfinite(values).all():
        raise RuntimeError("held-out inherited frame is no longer all-43 finite")
    return name, expected


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
    ap.add_argument("--taxon-index", type=int, required=True)
    ap.add_argument("--parent-finite-frame-dir", required=True)
    ap.add_argument("--target-group", required=True)
    ap.add_argument("--chelsa-manifest", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    repair = json.loads(REPAIR.read_text(encoding="utf-8"))
    fit_contract = json.loads(FIT.read_text(encoding="utf-8"))
    frame_contract = json.loads(FRAME.read_text(encoding="utf-8"))
    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    registry = pd.read_csv(REGISTRY)

    if repair.get("contract_version") != CONTRACT:
        raise RuntimeError("wrong held-out v0.3 repair contract")
    if len(registry) != 12 or not 0 <= args.taxon_index < 12:
        raise RuntimeError("held-out v0.3 taxon inventory drifted")
    if int(repair["final_background_points_per_taxon_M"]) != 2000:
        raise RuntimeError("held-out v0.3 final denominator drifted")
    if int(repair["active_predictors_required"]) != 43:
        raise RuntimeError("held-out v0.3 predictor denominator drifted")
    if any(bool(repair["preflight"][k]) for k in ("model_refit_allowed","prediction_score_computation_allowed","paired_discordance_computation_allowed","reference_ceiling_read_allowed","heldout_pairing_allowed","process_knockout_allowed")):
        raise RuntimeError("held-out v0.3 information boundary drifted")

    row = registry.iloc[args.taxon_index]
    name = str(row["scientific_name"])
    specieskey = str(row["resolved_snapshot_specieskey"])
    result_by_name = {str(x["requested_name"]): x for x in sampling.get("results", [])}
    if result_by_name.get(name, {}).get("state") != "source_mode_sampling_passed":
        raise RuntimeError("held-out taxon no longer sampling-pass")
    if sampling.get("paired_discordance_opened") is not False:
        raise RuntimeError("held-out paired endpoint already opened")

    parent_dir = Path(args.parent_finite_frame_dir)
    parent_path = parent_dir / "receipt.json"
    parent_bytes = parent_path.read_bytes()
    parent = json.loads(parent_bytes)
    if parent.get("result_version") != PARENT_RESULT:
        raise RuntimeError("held-out v0.3 received wrong parent receipt type")
    if parent.get("repair_contract_version") != "product_b_same_target_heldout_finite_frame_repair_v0.2":
        raise RuntimeError("held-out v0.3 parent repair contract mismatch")
    if int(parent.get("taxon_index", -1)) != args.taxon_index:
        raise RuntimeError("held-out v0.3 parent taxon index mismatch")
    if str(parent.get("taxon")) != name or str(parent.get("specieskey")) != specieskey:
        raise RuntimeError("held-out v0.3 parent taxon identity mismatch")
    for key in ("model_refit_opened","prediction_scores_computed","paired_discordance_opened","reference_ceiling_read","heldout_pairing_opened","process_knockout_opened"):
        if parent.get(key) is not False:
            raise RuntimeError(f"held-out v0.2 parent crossed information boundary: {key}")

    predictors = tuple(str(x) for x in parent.get("active_predictors", []))
    if len(predictors) != 43 or len(set(predictors)) != 43:
        raise RuntimeError("held-out v0.3 parent predictor identity drifted")
    parent_cells = {int(c["M_km"]): dict(c) for c in parent.get("cells", [])}
    if set(parent_cells) != {150, 300, 500}:
        raise RuntimeError("held-out v0.3 parent M inventory drifted")

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    for ancillary in ("repair_raster_provenance.csv", "repair_chelsa_resolution_ledger.csv"):
        src = parent_dir / ancillary
        if src.is_file():
            shutil.copy2(src, outdir / f"parent_v0_2_{ancillary}")

    unresolved_m = [m for m in (150, 300, 500) if parent_cells[m].get("state") != "finite_comparison_frame_frozen"]
    runtime = None
    if unresolved_m:
        mode_a, mode_b = _scan_taxon(specieskey)
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
        partition = make_presence_spatial_partition(common_geometry["longitude"].to_numpy(float), common_geometry["latitude"].to_numpy(float), n_blocks=int(frame_contract["spatial_blocks"]["n_blocks"]), holdout_fraction=0.5, random_state=int(frame_contract["spatial_blocks"]["random_state"]))
        if _hash_centers(partition.centers_xyz) != str(parent.get("common_block_centers_sha256")):
            raise RuntimeError("held-out source-blind common geometry changed since v0.2")

        target = load_gbif_download(Path(args.target_group)).records
        target = admit_occurrences(target, config=OccurrenceAdmissionConfig()).accepted
        target = target.dropna(subset=["longitude", "latitude"]).reset_index(drop=True)
        if target.empty:
            raise RuntimeError("held-out target-group artifact empty")

        manifest = pd.read_csv(args.chelsa_manifest)
        raster_specs, raster_resolution = raster_specs_from_chelsa_manifest(manifest, include_availability=("current",), strict=True)
        actual_predictors = tuple(spec.predictor for spec in raster_specs)
        if actual_predictors != predictors:
            raise RuntimeError("held-out v0.3 CHELSA predictor identity differs from parent")
        if len(raster_specs) != int(fit_contract["environmental_predictor_source"]["active_predictors_required"]):
            raise RuntimeError("held-out v0.3 predictor count differs from fit contract")

        candidate_seeds = {int(c["candidate_sampling_random_state"]) for c in parent_cells.values()}
        final_seeds = {int(c["final_selection_random_state"]) for c in parent_cells.values()}
        if len(candidate_seeds) != 1 or len(final_seeds) != 1:
            raise RuntimeError("held-out v0.2 seed identity drifted across M")
        runtime = {"candidate_seed":candidate_seeds.pop(),"final_seed":final_seeds.pop(),"common_geometry":common_geometry,"target":target,"raster_specs":raster_specs,"raster_resolution":raster_resolution}

    cells: list[dict[str, object]] = []
    provenance_frames: list[pd.DataFrame] = []
    for m in (150, 300, 500):
        parent_cell = parent_cells[m]
        if parent_cell.get("state") == "finite_comparison_frame_frozen":
            frame_file, frame_sha = _verify_parent_frame(parent_dir, parent_cell, predictors)
            shutil.copy2(parent_dir / frame_file, outdir / frame_file)
            cells.append({"M_km":m,"state":"finite_comparison_frame_frozen","repair_action":"inherit_v0_2_frozen_frame_byte_identical","frame_source_result_version":PARENT_RESULT,"parent_candidate_rows_materialized":int(parent_cell["candidate_rows_materialized"]),"candidate_rows_materialized":int(parent_cell["candidate_rows_materialized"]),"all_43_predictor_finite_rows":int(parent_cell["all_43_predictor_finite_rows"]),"finite_fraction":parent_cell.get("finite_fraction"),"selected_rows":2000,"required_rows":2000,"candidate_sampling_random_state":int(parent_cell["candidate_sampling_random_state"]),"final_selection_random_state":int(parent_cell["final_selection_random_state"]),"comparison_frame_file":frame_file,"comparison_frame_sha256":frame_sha,"exhaustive_eligible_target_group_enumeration":False})
            continue

        if runtime is None:
            raise RuntimeError("held-out unresolved v0.2 cell lacks v0.3 runtime")
        common_geometry = runtime["common_geometry"]
        target = runtime["target"]
        m_mask = occurrence_buffer_membership(target, common_geometry, buffer_km=float(m))
        candidates = sample_target_group_background(common_geometry, target, m_mask=m_mask, n_points=max(1, len(target)), cell_size_degrees=float(repair["grid_cell_degrees"]), focal_species=name, random_state=int(runtime["candidate_seed"]))
        featured, provenance = extract_raster_values(candidates, runtime["raster_specs"])
        provenance = provenance.copy()
        provenance["role"] = f"heldout_repair_v0_3_exhaustive_candidate_background_{m}km"
        provenance_frames.append(provenance)
        selected, audit = freeze_finite_comparison_frame(featured, predictors, required_rows=2000, random_state=int(runtime["final_seed"]))
        frame_file = None
        frame_sha = None
        if audit.state == "finite_comparison_frame_frozen":
            ids = _comparison_ids(name, m, selected)
            selected = selected.copy()
            selected.insert(0, "comparison_row_id", ids)
            selected = selected.loc[:, ["comparison_row_id", "longitude", "latitude", *predictors]]
            if len(selected) != 2000 or selected["comparison_row_id"].duplicated().any():
                raise RuntimeError("held-out v0.3 frozen frame integrity failed")
            frame_path = outdir / f"M{m}_finite_comparison_frame.parquet"
            selected.to_parquet(frame_path, index=False)
            frame_file = frame_path.name
            frame_sha = sha256(frame_path.read_bytes()).hexdigest()
        cells.append({"M_km":m,"state":audit.state,"repair_action":"exhaustive_eligible_target_group_enumeration_for_v0_2_unresolved_cell","frame_source_result_version":RESULT,"parent_state":parent_cell.get("state"),"parent_candidate_rows_materialized":int(parent_cell.get("candidate_rows_materialized",0)),"parent_all_43_predictor_finite_rows":int(parent_cell.get("all_43_predictor_finite_rows",0)),"candidate_rows_materialized":int(audit.candidate_rows),"all_43_predictor_finite_rows":int(audit.all_predictor_finite_rows),"finite_fraction":None if audit.candidate_rows==0 else float(audit.all_predictor_finite_rows/audit.candidate_rows),"selected_rows":int(audit.selected_rows),"required_rows":int(audit.required_rows),"candidate_sampling_random_state":int(runtime["candidate_seed"]),"final_selection_random_state":int(runtime["final_seed"]),"comparison_frame_file":frame_file,"comparison_frame_sha256":frame_sha,"exhaustive_eligible_target_group_enumeration":True})

    if provenance_frames:
        pd.concat(provenance_frames, ignore_index=True).drop_duplicates().to_csv(outdir / "repair_v0_3_raster_provenance.csv", index=False)
        runtime["raster_resolution"].to_csv(outdir / "repair_v0_3_chelsa_resolution_ledger.csv", index=False)

    inherited = sum(c["repair_action"] == "inherit_v0_2_frozen_frame_byte_identical" for c in cells)
    exhaustive = len(cells) - inherited
    receipt = {"result_version":RESULT,"repair_contract_version":CONTRACT,"parent_preflight_result_version":PARENT_RESULT,"parent_preflight_receipt_sha256":sha256(parent_bytes).hexdigest(),"taxon":name,"taxon_index":args.taxon_index,"specieskey":specieskey,"source_modes":list(MODES),"source_blind_common_geometry_cells":int(parent["source_blind_common_geometry_cells"]),"common_block_centers_sha256":str(parent["common_block_centers_sha256"]),"active_predictors":list(predictors),"active_predictor_count":43,"final_background_points_required":2000,"cells":cells,"v0_2_frozen_cells_inherited":int(inherited),"v0_2_unresolved_cells_exhaustively_repaired":int(exhaustive),"all_three_M_frames_frozen":bool(all(c["state"]=="finite_comparison_frame_frozen" for c in cells)),"model_refit_opened":False,"prediction_scores_computed":False,"paired_discordance_opened":False,"reference_ceiling_read":False,"heldout_pairing_opened":False,"process_knockout_opened":False,"taxon_replaced":False,"M_selected_from_outcome":False,"procedure_selected_from_outcome":False,"counts_as_empirical_conclusion":False,"claim_strength":"heldout_exhaustive_environmental_availability_repair_preflight_only_not_empirical_evidence"}
    (outdir / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
