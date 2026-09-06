#!/usr/bin/env python3
"""Scan one deterministic snapshot fragment shard for fresh species-concept closure.

Only the frozen five taxonomy columns are projected.  The scan persists distinct
taxonomy tuples, never matched row counts, occurrence IDs, coordinates, dates,
datasets, recorders, environmental values, model outputs, or paired outcomes.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

import pyarrow.dataset as ds
import pyarrow.fs as pafs

from product_b_v7_2.snapshot_transport import (
    EXPECTED_BUCKET,
    EXPECTED_OCCURRENCE_PREFIX,
    EXPECTED_REGION,
)
from product_b_v7_3.taxonomy_identity import ALLOWED_COLUMNS, SnapshotTaxonomyTuple

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "results/product_b_same_target_fresh_current_taxonomy_v0_1.json"
CONTRACT = ROOT / "config/product_b_same_target_fresh_calibration_contract_v0_1.json"
DATASET_PATH = f"{EXPECTED_BUCKET}/{EXPECTED_OCCURRENCE_PREFIX.rstrip('/')}"


def _allowed_names(current: dict[str, object]) -> tuple[str, ...]:
    names = []
    for row in current.get("resolutions", []):
        if row.get("state") != "fresh_current_taxonomy_resolved_exact_accepted_species":
            continue
        name = str(row.get("accepted_name") or "").strip()
        if name:
            names.append(name)
    return tuple(sorted(set(names)))


def main() -> int:
    shard_index = int(os.environ.get("SHARD_INDEX", "0"))
    shard_count = int(os.environ.get("SHARD_COUNT", "6"))
    if not (0 <= shard_index < shard_count):
        raise ValueError("invalid shard index/count")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    if current.get("result_version") != "product_b_same_target_fresh_current_taxonomy_v0.1":
        raise RuntimeError("fresh current-taxonomy result is required")
    if current.get("occurrence_counts_opened") is not False or current.get("coordinates_opened") is not False:
        raise RuntimeError("fresh current-taxonomy result crossed occurrence boundary")
    if current.get("paired_discordance_opened") is not False:
        raise RuntimeError("fresh current-taxonomy result crossed paired-outcome boundary")

    names = _allowed_names(current)
    minimum = int(contract["panel_rule"]["minimum_complete_taxa_for_calibration"])
    if len(names) < minimum:
        raise RuntimeError(
            f"fresh current taxonomy leaves {len(names)} taxa, below frozen calibration minimum {minimum}; snapshot access remains closed"
        )

    allowed = tuple(contract["taxonomy_concept_closure"]["snapshot_taxonomy_fields_allowed"])
    if allowed != tuple(ALLOWED_COLUMNS):
        raise RuntimeError("fresh concept-closure projected taxonomy columns drifted")

    filesystem = pafs.S3FileSystem(anonymous=True, region=EXPECTED_REGION)
    infos = filesystem.get_file_info(pafs.FileSelector(DATASET_PATH, recursive=False))
    parquet_paths = tuple(sorted(info.path for info in infos if info.type == pafs.FileType.File))
    if len(parquet_paths) != 9705:
        raise RuntimeError(f"frozen snapshot parquet object count changed: {len(parquet_paths)}")
    selected_paths = parquet_paths[shard_index::shard_count]
    if not selected_paths:
        raise RuntimeError("fresh concept fragment shard is empty")

    dataset = ds.dataset(list(selected_paths), filesystem=filesystem, format="parquet")
    scanner = dataset.scanner(
        columns=list(ALLOWED_COLUMNS),
        filter=ds.field("species").isin(list(names)),
        batch_size=65536,
        use_threads=True,
    )

    tuples_by_name: dict[str, set[SnapshotTaxonomyTuple]] = {name: set() for name in names}
    for batch in scanner.to_batches():
        values = batch.to_pydict()
        for i in range(batch.num_rows):
            species = str(values["species"][i] or "").strip()
            if species not in tuples_by_name:
                raise ValueError("fresh snapshot scanner returned undeclared species name")
            tuples_by_name[species].add(
                SnapshotTaxonomyTuple(
                    species=species,
                    specieskey=str(values["specieskey"][i] or "").strip(),
                    taxonkey=str(values["taxonkey"][i] or "").strip(),
                    scientificname=str(values["scientificname"][i] or "").strip(),
                    taxonrank=str(values["taxonrank"][i] or "").strip().upper(),
                )
            )

    outcome = {
        "result_version": "product_b_same_target_fresh_snapshot_concept_fragment_v0.1",
        "shard_index": shard_index,
        "shard_count": shard_count,
        "snapshot_date": "2026-08-01",
        "projected_columns": list(ALLOWED_COLUMNS),
        "frozen_species_names": list(names),
        "taxonomy_tuples": {
            name: [asdict(item) for item in sorted(tuples)]
            for name, tuples in sorted(tuples_by_name.items())
            if tuples
        },
        "matched_row_counts_persisted": False,
        "per_file_matched_counts_persisted": False,
        "raw_rows_persisted": False,
        "coordinates_opened": False,
        "occurrence_identifiers_opened": False,
        "dates_opened": False,
        "dataset_fields_opened": False,
        "environmental_values_opened": False,
        "current_layer1_paired_discordance_read": False,
        "process_intervention_outcomes_read": False,
    }
    output = ROOT / f"artifacts/product_b_same_target_fresh_snapshot_concept_shard_{shard_index}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "result_version": outcome["result_version"],
                "shard_index": shard_index,
                "shard_count": shard_count,
                "species_with_taxonomy_tuples": sorted(outcome["taxonomy_tuples"]),
                "matched_row_counts_persisted": False,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
