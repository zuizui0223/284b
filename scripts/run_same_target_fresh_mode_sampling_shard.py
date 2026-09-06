#!/usr/bin/env python3
"""Run one fresh source-mode sampling shard after species-concept closure.

Only taxa whose complete frozen historical ``specieskey`` set passed taxonomy
concept closure may enter.  All keys for a taxon are queried together; key-level
occurrence counts are never used to choose or drop keys.  PRESERVED_SPECIMEN and
HUMAN_OBSERVATION remain disjoint evidence modes and each must clear the unchanged
50 records / 30 10-km cells / 10 effective-cells gate.

Raw rows, coordinates, and record identifiers are never persisted.
"""
from __future__ import annotations

from dataclasses import asdict
import gc
import json
import os
from pathlib import Path
import sys
from typing import Mapping

import pyarrow.dataset as ds
import pyarrow.fs as pafs

from product_b_v5.occurrence_adapter import adapt_gbif_pair_rows
from product_b_v5.occurrence_preprocessing import build_occurrence_sampling_preflight
from product_b_v5.sampling import SamplingThresholds
from product_b_v5.source_mode_sampling import evaluate_paired_source_mode_adequacy
from product_b_v7_2.snapshot_transport import EXPECTED_BUCKET, EXPECTED_OCCURRENCE_PREFIX, EXPECTED_REGION

ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / "results/product_b_same_target_fresh_snapshot_concept_closure_v0_1.json"
CONTRACT = ROOT / "config/product_b_same_target_fresh_calibration_contract_v0_1.json"
DATASET_PATH = f"{EXPECTED_BUCKET}/{EXPECTED_OCCURRENCE_PREFIX.rstrip('/')}"
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")
SELECTED_COLUMNS = (
    "gbifid", "datasetkey", "occurrenceid", "catalognumber", "recordedby", "eventdate",
    "basisofrecord", "occurrencestatus", "decimallatitude", "decimallongitude",
    "coordinateuncertaintyinmeters", "specieskey",
)
PREPROCESSING_THRESHOLDS = SamplingThresholds(
    minimum_independent_records=50,
    minimum_unique_cells=30,
    minimum_effective_cells=10.0,
    maximum_record_asymmetry_ratio=1.0e12,
    maximum_unique_cell_asymmetry_ratio=1.0e12,
    maximum_effective_cell_asymmetry_ratio=1.0e12,
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


def _snapshot_to_adapter_row(values: dict[str, list[object]], i: int) -> dict[str, object]:
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


def _scan_taxon(dataset: ds.Dataset, historical_keys: tuple[str, ...]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if not historical_keys:
        raise ValueError("historical specieskey set must not be empty")
    key_set = set(historical_keys)
    expression = (
        ds.field("specieskey").isin(list(historical_keys))
        & ds.field("basisofrecord").isin(list(MODES))
        & (ds.field("occurrencestatus") == "PRESENT")
    )
    scanner = dataset.scanner(columns=list(SELECTED_COLUMNS), filter=expression, batch_size=65536, use_threads=True)
    mode_a: list[dict[str, object]] = []
    mode_b: list[dict[str, object]] = []
    for batch in scanner.to_batches():
        values = batch.to_pydict()
        for i in range(batch.num_rows):
            key = str(values["specieskey"][i] or "").strip()
            if key not in key_set:
                raise ValueError("snapshot scanner returned specieskey outside frozen concept set")
            mode = str(values["basisofrecord"][i] or "").strip().upper()
            row = _snapshot_to_adapter_row(values, i)
            if mode == MODES[0]:
                mode_a.append(row)
            elif mode == MODES[1]:
                mode_b.append(row)
            else:
                raise ValueError("snapshot scanner returned undeclared basisofrecord")
    return mode_a, mode_b


def _sanitize_taxon_result(name: str, keys: tuple[str, ...], mode_a: list[dict[str, object]], mode_b: list[dict[str, object]]) -> dict[str, object]:
    adapted = adapt_gbif_pair_rows(x_rows=mode_a, y_rows=mode_b)
    preflight = build_occurrence_sampling_preflight(
        adapted.records,
        taxonomy_eligible=True,
        thresholds=PREPROCESSING_THRESHOLDS,
    )
    adequacy = evaluate_paired_source_mode_adequacy(preflight.x_summary, preflight.y_summary)
    audit = preflight.audit
    return {
        "requested_name": name,
        "frozen_historical_specieskeys": list(keys),
        "historical_key_count": len(keys),
        "state": "fresh_source_mode_sampling_passed" if adequacy.passed else "fresh_source_mode_sampling_unresolved",
        "reasons": list(adequacy.reasons),
        "preserved_specimen": asdict(preflight.x_summary),
        "human_observation": asdict(preflight.y_summary),
        "quality_excluded_preserved_specimen": audit.quality_excluded_x,
        "quality_excluded_human_observation": audit.quality_excluded_y,
        "quality_exclusion_reason_counts": dict(audit.quality_exclusion_reason_counts),
        "missing_uncertainty_preserved_specimen": audit.missing_uncertainty_x,
        "missing_uncertainty_human_observation": audit.missing_uncertainty_y,
        "cross_mode_collision_excluded_preserved_specimen": audit.collision_excluded_x,
        "cross_mode_collision_excluded_human_observation": audit.collision_excluded_y,
        "cross_mode_collision_component_count": len(audit.collision_components),
        "cross_mode_asymmetry_exclusion_applied": False,
        "historical_key_level_sampling_selection_used": False,
        "raw_rows_persisted": False,
        "coordinates_persisted": False,
        "row_identifiers_persisted": False,
    }


def main() -> int:
    shard_index = int(os.environ.get("SHARD_INDEX", "0"))
    shard_count = int(os.environ.get("SHARD_COUNT", "6"))
    if not (0 <= shard_index < shard_count):
        raise ValueError("invalid shard index/count")

    closure = json.loads(CLOSURE.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    minimum = int(contract["panel_rule"]["minimum_complete_taxa_for_calibration"])
    if closure.get("occurrence_sampling_authorized") is not True:
        raise RuntimeError("fresh concept closure did not authorize occurrence sampling")
    if int(closure.get("concept_closure_passed_taxa", -1)) < minimum:
        raise RuntimeError("fresh concept closure is below frozen calibration minimum")
    for flag in (
        "occurrence_endpoint_called", "occurrence_counts_opened", "coordinates_opened",
        "environmental_values_opened", "model_fit_opened", "paired_discordance_opened",
        "current_layer1_paired_discordance_read", "process_intervention_outcomes_read",
    ):
        if closure.get(flag) is not False:
            raise RuntimeError(f"fresh closure crossed pre-sampling boundary: {flag}")
    sampling = contract["source_mode_sampling"]
    if int(sampling["minimum_independent_records_per_mode"]) != 50:
        raise RuntimeError("fresh source-mode record floor changed")
    if int(sampling["minimum_unique_10km_cells_per_mode"]) != 30:
        raise RuntimeError("fresh source-mode unique-cell floor changed")
    if float(sampling["minimum_effective_cells_per_mode"]) != 10.0:
        raise RuntimeError("fresh source-mode effective-cell floor changed")

    passed = [row for row in closure.get("decisions", []) if row.get("passed") is True]
    selected = [row for index, row in enumerate(passed) if index % shard_count == shard_index]
    filesystem = pafs.S3FileSystem(anonymous=True, region=EXPECTED_REGION)
    dataset = ds.dataset(DATASET_PATH, filesystem=filesystem, format="parquet")

    results: list[dict[str, object]] = []
    for row in selected:
        name = str(row["current_accepted_species"])
        keys = tuple(sorted(str(key) for key in row.get("frozen_historical_specieskeys", []) if str(key).strip()))
        try:
            mode_a, mode_b = _scan_taxon(dataset, keys)
            result = _sanitize_taxon_result(name, keys, mode_a, mode_b)
        except Exception as exc:
            result = {
                "requested_name": name,
                "frozen_historical_specieskeys": list(keys),
                "historical_key_count": len(keys),
                "state": "fresh_source_mode_sampling_execution_unresolved",
                "reasons": [f"{type(exc).__name__}:{exc}"],
                "historical_key_level_sampling_selection_used": False,
                "raw_rows_persisted": False,
                "coordinates_persisted": False,
                "row_identifiers_persisted": False,
            }
        results.append(result)
        if "mode_a" in locals():
            del mode_a
        if "mode_b" in locals():
            del mode_b
        gc.collect()

    outcome = {
        "result_version": "product_b_same_target_fresh_source_mode_sampling_shard_v0.1",
        "shard_index": shard_index,
        "shard_count": shard_count,
        "concept_closure_passed_total": len(passed),
        "taxa_assigned_to_shard": len(selected),
        "results": results,
        "raw_rows_persisted": False,
        "coordinates_persisted": False,
        "row_identifiers_persisted": False,
        "paired_discordance_opened": False,
        "model_fit_opened": False,
        "historical_key_level_sampling_selection_used": False,
    }
    output = ROOT / f"artifacts/product_b_same_target_fresh_source_mode_sampling_shard_{shard_index}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
