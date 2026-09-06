#!/usr/bin/env python3
"""Fit one successor Layer-1 taxon independently from two observation modes.

Only successor taxa that already passed the frozen all-key source-mode sampling
contract may enter. All frozen historical specieskeys are scanned together; no
key may be selected or dropped using occurrence abundance. Both source answers
share source-blind M geometry, block centres, target-group background rows, and
the environmental predictor universe. Paired discordance is not computed here.
"""
from __future__ import annotations

from hashlib import sha256
import csv
import json
import os
from pathlib import Path
import sys
from typing import Mapping

import joblib
import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.fs as pafs

from product_b_v5.occurrence_adapter import adapt_gbif_pair_rows
from product_b_v5.occurrence_preprocessing import (
    cross_partner_collision_components,
    occurrence_quality_reasons,
)
from product_b_v7_2.snapshot_transport import (
    EXPECTED_BUCKET,
    EXPECTED_OCCURRENCE_PREFIX,
    EXPECTED_REGION,
)

ROOT = Path(__file__).resolve().parents[1]
BASE_FIT_CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
SUCCESSOR_FIT_CONTRACT = ROOT / "config/product_b_same_target_successor_model_fit_contract_v0_1.json"
FRAME_CONTRACT = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
SAMPLING_RESULT = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"
CANDIDATE_REGISTRY = ROOT / "registry/product_b_same_target_successor_calibration_candidates_v0_1.csv"
DATASET_PATH = f"{EXPECTED_BUCKET}/{EXPECTED_OCCURRENCE_PREFIX.rstrip('/')}"
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")
SELECTED_COLUMNS = (
    "gbifid", "datasetkey", "occurrenceid", "catalognumber", "recordedby",
    "eventdate", "basisofrecord", "occurrencestatus", "decimallatitude",
    "decimallongitude", "coordinateuncertaintyinmeters", "specieskey",
)


def _flatten_people(value: object) -> str:
    parts: list[str] = []
    def visit(item: object) -> None:
        if item is None:
            return
        if isinstance(item, Mapping):
            if "array_element" in item:
                visit(item.get("array_element"))
            else:
                for key in sorted(item):
                    visit(item[key])
            return
        if isinstance(item, (list, tuple)):
            for child in item:
                visit(child)
            return
        text = str(item).strip()
        if text:
            parts.append(text)
    visit(value)
    return "; ".join(parts)


def _adapter_row(values: dict[str, list[object]], i: int) -> dict[str, object]:
    return {
        "key": str(values["gbifid"][i] or "").strip(),
        "datasetKey": str(values["datasetkey"][i] or "").strip(),
        "occurrenceID": str(values["occurrenceid"][i] or "").strip(),
        "eventID": "",
        "catalogNumber": str(values["catalognumber"][i] or "").strip(),
        "otherCatalogNumbers": [],
        "eventDate": "" if values["eventdate"][i] is None else str(values["eventdate"][i]),
        "recordedBy": _flatten_people(values["recordedby"][i]),
        "decimalLatitude": values["decimallatitude"][i],
        "decimalLongitude": values["decimallongitude"][i],
        "coordinateUncertaintyInMeters": values["coordinateuncertaintyinmeters"][i],
    }


def _scan_taxon(historical_keys: tuple[str, ...]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if not historical_keys:
        raise ValueError("frozen historical specieskey set must not be empty")
    key_set = set(historical_keys)
    filesystem = pafs.S3FileSystem(anonymous=True, region=EXPECTED_REGION)
    dataset = ds.dataset(DATASET_PATH, filesystem=filesystem, format="parquet")
    expression = (
        ds.field("specieskey").isin(list(historical_keys))
        & ds.field("basisofrecord").isin(list(MODES))
        & (ds.field("occurrencestatus") == "PRESENT")
    )
    scanner = dataset.scanner(columns=list(SELECTED_COLUMNS), filter=expression, batch_size=65536, use_threads=True)
    a: list[dict[str, object]] = []
    b: list[dict[str, object]] = []
    for batch in scanner.to_batches():
        values = batch.to_pydict()
        for i in range(batch.num_rows):
            key = str(values["specieskey"][i] or "").strip()
            if key not in key_set:
                raise ValueError("snapshot scanner returned specieskey outside frozen concept set")
            mode = str(values["basisofrecord"][i] or "").strip().upper()
            row = _adapter_row(values, i)
            if mode == MODES[0]:
                a.append(row)
            elif mode == MODES[1]:
                b.append(row)
            else:
                raise ValueError("snapshot scanner returned undeclared observation mode")
    return a, b


def _retained_source_frames(name: str, mode_a: list[dict[str, object]], mode_b: list[dict[str, object]]) -> dict[str, pd.DataFrame]:
    adapted = adapt_gbif_pair_rows(x_rows=mode_a, y_rows=mode_b)
    quality_ok = [
        record for record in adapted.records
        if not occurrence_quality_reasons(record, maximum_known_uncertainty_m=10_000.0)
    ]
    collisions = cross_partner_collision_components(quality_ok)
    excluded = {row_id for component in collisions for row_id in component.row_ids}
    retained = [record for record in quality_ok if record.row_id not in excluded]
    frames: dict[str, list[dict[str, object]]] = {MODES[0]: [], MODES[1]: []}
    for record in retained:
        if record.decimal_longitude is None or record.decimal_latitude is None:
            continue
        mode = MODES[0] if record.partner == "x" else MODES[1]
        frames[mode].append({
            "species": name,
            "longitude": float(record.decimal_longitude),
            "latitude": float(record.decimal_latitude),
            "gbifID": str(record.row_id),
        })
    return {mode: pd.DataFrame(rows) for mode, rows in frames.items()}


def _procedure_library(contract: dict[str, object]):
    from sdmr.model import ModelSpec
    from sdmr.niche_recovery_procedure import RecoveryProcedure
    frozen = contract["procedure_library"]
    procedures = []
    for spec in frozen["model_specs"]:
        model_spec = ModelSpec(C=float(spec["C"]), degree=int(spec["degree"]), penalty=str(spec["penalty"]), random_state=None)
        for strategy in frozen["strategies"]:
            procedures.append(RecoveryProcedure(
                strategy=str(strategy), model_spec=model_spec,
                inner_folds=int(frozen["inner_folds"]), max_predictors=int(frozen["max_predictors"]),
                vif_threshold=float(frozen["vif_threshold"]), predictive_min_gain=float(frozen["predictive_min_gain"]),
                observation_predictors=tuple(frozen["observation_predictors"]),
            ))
    if len(procedures) != 8 or len({p.label for p in procedures}) != 8:
        raise RuntimeError("frozen procedure library must contain eight unique procedures")
    return tuple(procedures)


def _comparison_ids(name: str, m_km: int, background: pd.DataFrame) -> list[str]:
    values: list[str] = []
    for i, row in background.reset_index(drop=True).iterrows():
        payload = f"{name}|{int(m_km)}|{i}|{float(row['longitude']):.7f}|{float(row['latitude']):.7f}"
        values.append(sha256(payload.encode("utf-8")).hexdigest())
    return values


def _frozen_candidate_names() -> list[str]:
    with CANDIDATE_REGISTRY.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    names = [str(row["scientific_name"]).strip() for row in rows]
    if len(names) != 72 or len(set(names)) != 72:
        raise RuntimeError("successor candidate registry is no longer frozen 72 unique taxa")
    return names


def main() -> int:
    from sdmr.data import OccurrenceAdmissionConfig, admit_occurrences, extract_raster_values, load_gbif_download, raster_specs_from_chelsa_manifest, thin_to_grid
    from sdmr.data.background import occurrence_buffer_membership, sample_target_group_background
    from sdmr.model import score_ecological_suitability
    from sdmr.niche_recovery_procedure import cross_validated_recovery_procedure
    from sdmr.recovery_procedure_fit import fit_recovery_procedure
    from sdmr.validation import assign_spatial_blocks, make_presence_spatial_partition

    taxon_index = int(os.environ["TAXON_INDEX"])
    target_path = Path(os.environ["TARGET_GROUP_PATH"])
    manifest_path = Path(os.environ["CHELSA_MANIFEST"])
    output_dir = Path(os.environ.get("OUTPUT_DIR", f"artifacts/successor_layer1_fit_taxon_{taxon_index}"))
    output_dir.mkdir(parents=True, exist_ok=True)

    fit_contract = json.loads(BASE_FIT_CONTRACT.read_text(encoding="utf-8"))
    successor_fit = json.loads(SUCCESSOR_FIT_CONTRACT.read_text(encoding="utf-8"))
    frame_contract = json.loads(FRAME_CONTRACT.read_text(encoding="utf-8"))
    sampling = json.loads(SAMPLING_RESULT.read_text(encoding="utf-8"))
    if sampling.get("model_fit_authorized") is not True:
        raise RuntimeError("successor source-mode sampling did not authorize model fitting")
    if int(sampling.get("source_mode_sampling_passed", -1)) < int(successor_fit["minimum_taxa_required_before_fit"]):
        raise RuntimeError("successor sampling panel below frozen model-fit minimum")
    if sampling.get("paired_discordance_opened") is not False or sampling.get("model_fit_opened") is not False:
        raise RuntimeError("successor upstream information boundary changed")
    eligible = [row for row in sampling.get("results", []) if row.get("state") == "successor_source_mode_sampling_passed"]
    if len(eligible) != int(sampling["source_mode_sampling_passed"]):
        raise RuntimeError("successor sampling-pass inventory mismatch")
    if not 0 <= taxon_index < len(eligible):
        raise RuntimeError("successor taxon index outside sampling-pass inventory")
    row = eligible[taxon_index]
    name = str(row["requested_name"]).strip()
    historical_keys = tuple(sorted(str(key).strip() for key in row.get("frozen_historical_specieskeys", []) if str(key).strip()))
    if not historical_keys:
        raise RuntimeError("successor sampling-passed taxon lacks frozen historical key set")

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
    source_blocks = {
        mode: assign_spatial_blocks(source_thin[mode]["longitude"].to_numpy(float), source_thin[mode]["latitude"].to_numpy(float), centers)
        for mode in MODES
    }

    target = load_gbif_download(target_path).records
    target = admit_occurrences(target, config=OccurrenceAdmissionConfig()).accepted
    target = target.dropna(subset=["longitude", "latitude"]).reset_index(drop=True)
    if target.empty:
        raise RuntimeError("successor target-group artifact has no admissible coordinates")

    manifest = pd.read_csv(manifest_path)
    raster_specs, raster_resolution = raster_specs_from_chelsa_manifest(manifest, include_availability=("current",), strict=True)
    if len(raster_specs) != int(fit_contract["environmental_predictor_source"]["active_predictors_required"]):
        raise RuntimeError("CHELSA predictor count differs from frozen base contract")
    predictors = tuple(spec.predictor for spec in raster_specs)
    if len(predictors) != 43 or len(set(predictors)) != 43:
        raise RuntimeError("CHELSA predictor identities are not 43 unique names")

    featured_source: dict[str, pd.DataFrame] = {}
    provenance_frames: list[pd.DataFrame] = []
    for mode in MODES:
        featured, provenance = extract_raster_values(source_thin[mode], raster_specs)
        featured_source[mode] = featured
        provenance = provenance.copy(); provenance["role"] = f"presence_{mode}"
        provenance_frames.append(provenance)

    procedures = _procedure_library(fit_contract)
    adequacy = fit_contract["prediction_adequacy"]
    frozen_names = sorted(_frozen_candidate_names())
    seed_index = frozen_names.index(name)
    bg_seed = int(frame_contract["background"]["background_random_state_base"]) + seed_index

    prediction_rows: list[dict[str, object]] = []
    selected_rows: list[dict[str, object]] = []
    fold_frames: list[pd.DataFrame] = []
    trace_frames: list[pd.DataFrame] = []
    errors: list[dict[str, object]] = []

    for m_km in [int(v) for v in fit_contract["M_km"]]:
        m_mask = occurrence_buffer_membership(target, common_geometry, buffer_km=float(m_km))
        background = sample_target_group_background(
            common_geometry, target, m_mask=m_mask,
            n_points=int(fit_contract["background_points_per_taxon_M"]),
            cell_size_degrees=float(fit_contract["background_cell_size_degrees"]),
            focal_species=name, random_state=bg_seed,
        )
        if len(background) < 100:
            raise RuntimeError(f"insufficient successor common target-group background for M={m_km}")
        comparison_ids = _comparison_ids(name, m_km, background)
        featured_background, provenance = extract_raster_values(background, raster_specs)
        provenance = provenance.copy(); provenance["role"] = f"background_{m_km}km"
        provenance_frames.append(provenance)
        background_blocks = assign_spatial_blocks(featured_background["longitude"].to_numpy(float), featured_background["latitude"].to_numpy(float), centers)

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
                        outer_folds=int(adequacy["outer_folds"]), chance_auc=float(adequacy["chance_auc"]),
                        minimum_auc_margin=float(adequacy["minimum_auc_margin"]), auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]),
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
                        chance_auc=float(adequacy["chance_auc"]), minimum_auc_margin=float(adequacy["minimum_auc_margin"]),
                        auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]),
                    )
                    scores = score_ecological_suitability(fitted.model, featured_background, fitted.selected_predictors, observation_predictors=())
                    if not np.isfinite(scores).any():
                        raise RuntimeError("sealed successor prediction surface contains no finite scores")
                    for comparison_row_id, score in zip(comparison_ids, scores, strict=True):
                        prediction_rows.append({**base, "comparison_row_id": comparison_row_id, "ecological_score": None if not np.isfinite(score) else float(score)})
                    model_rel = Path("models") / f"M{m_km}" / mode / (sha256(procedure.label.encode()).hexdigest()[:12] + ".joblib")
                    model_path = output_dir / model_rel; model_path.parent.mkdir(parents=True, exist_ok=True)
                    joblib.dump(fitted.model, model_path)
                    selected_rows.append({
                        **base, "state": "successor_layer1_model_fit_sealed",
                        "selected_predictors": ",".join(fitted.selected_predictors),
                        "selected_ecological_predictors": ",".join(fitted.selected_ecological_predictors),
                        "n_selected_predictors": len(fitted.selected_predictors), "model_file": str(model_rel),
                        "n_presence_thinned": len(presence), "n_background": len(featured_background),
                        "n_common_geometry_cells": len(common_geometry),
                    })
                    if not fitted.selection_trace.empty:
                        trace = fitted.selection_trace.copy()
                        for key, value in base.items(): trace[key] = value
                        trace["stage"] = "final_fit"; trace_frames.append(trace)
                except Exception as exc:
                    errors.append({**base, "error_type": type(exc).__name__, "error_message": str(exc)})
                    selected_rows.append({
                        **base, "state": "successor_layer1_model_fit_unresolved",
                        "selected_predictors": "", "selected_ecological_predictors": "", "n_selected_predictors": 0,
                        "model_file": "", "n_presence_thinned": len(presence), "n_background": len(featured_background),
                        "n_common_geometry_cells": len(common_geometry),
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
    fit_complete = int((selected["state"] == "successor_layer1_model_fit_sealed").sum()) if len(selected) else 0
    outcome = {
        "result_version": "product_b_same_target_successor_layer1_fit_taxon_v0.1",
        "taxon": name, "taxon_index": taxon_index,
        "historical_specieskeys": list(historical_keys), "historical_key_count": len(historical_keys),
        "source_modes": list(MODES), "M_km": [int(v) for v in fit_contract["M_km"]],
        "procedure_count": len(procedures), "expected_fit_cells": 2 * len(fit_contract["M_km"]) * len(procedures),
        "sealed_fit_cells": fit_complete, "unresolved_fit_cells": len(selected) - fit_complete,
        "prediction_surface_sha256": prediction_sha, "prediction_surfaces_sealed": True,
        "paired_discordance_computed": False, "reference_ceiling_read": False, "process_knockout_computed": False,
        "raw_occurrence_rows_persisted": False, "occurrence_coordinates_persisted": False,
        "shared_source_blind_M_and_block_geometry": True, "same_background_rows_used_for_both_sources": True,
        "background_seed_index_derived_from_frozen_72_candidate_registry": True,
        "historical_key_subset_selection_used": False,
        "errors": errors,
    }
    (output_dir / "contract.json").write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
