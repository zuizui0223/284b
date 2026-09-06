#!/usr/bin/env python3
"""Scan one deterministic fragment shard for calibration snapshot taxonomy identity.

This is transport-equivalent to the single-run v7.3 identity scan: same frozen
snapshot, same predeclared species names, same five taxonomy columns, and no
occurrence counts or spatial fields. The only change is deterministic partitioning
of the 9705 Parquet objects to reduce wall-clock time.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

import pyarrow.dataset as ds
import pyarrow.fs as pafs

from product_b_v7_2.snapshot_transport import EXPECTED_BUCKET, EXPECTED_OCCURRENCE_PREFIX, EXPECTED_REGION
from product_b_v7_3.taxonomy_identity import ALLOWED_COLUMNS, SnapshotTaxonomyTuple

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "results/product_b_same_target_source_current_taxonomy_v0_1.json"
DATASET_PATH = f"{EXPECTED_BUCKET}/{EXPECTED_OCCURRENCE_PREFIX.rstrip('/')}"


def _allowed_names(current: dict[str, object]) -> tuple[str, ...]:
    names: set[str] = set()
    for row in current.get("resolutions", []):
        if row.get("state") != "resolved_current_taxonomy":
            continue
        for name in row.get("snapshot_admissible_species_names", []):
            text = str(name).strip()
            if text:
                names.add(text)
    return tuple(sorted(names))


def main() -> int:
    shard_index = int(os.environ.get("SHARD_INDEX", "0"))
    shard_count = int(os.environ.get("SHARD_COUNT", "6"))
    if not (0 <= shard_index < shard_count):
        raise ValueError("invalid shard index/count")

    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    if current.get("result_version") != "product_b_same_target_source_current_taxonomy_v0.2":
        raise RuntimeError("corrected current-taxonomy v0.2 result is required")
    if current.get("resolved_taxa") != 36 or current.get("unresolved_taxa") != 0:
        raise RuntimeError("sharded identity execution requires the frozen 36/36 current-taxonomy result")
    if current.get("occurrence_counts_opened") is not False or current.get("coordinates_opened") is not False:
        raise RuntimeError("current-taxonomy result crossed a forbidden occurrence boundary")

    names = _allowed_names(current)
    if len(names) != 36:
        raise RuntimeError(f"expected 36 frozen admissible species names, found {len(names)}")

    filesystem = pafs.S3FileSystem(anonymous=True, region=EXPECTED_REGION)
    infos = filesystem.get_file_info(pafs.FileSelector(DATASET_PATH, recursive=False))
    parquet_paths = tuple(sorted(info.path for info in infos if info.type == pafs.FileType.File))
    if len(parquet_paths) != 9705:
        raise RuntimeError(f"frozen snapshot parquet object count changed: {len(parquet_paths)}")
    selected_paths = parquet_paths[shard_index::shard_count]
    if not selected_paths:
        raise RuntimeError("fragment shard is empty")

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
                raise ValueError("snapshot scanner returned undeclared species name")
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
        "result_version": "product_b_same_target_source_snapshot_identity_fragment_shard_v0.1",
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
        "dataset_fields_opened": False,
        "paired_discordance_opened": False,
    }
    output = ROOT / f"artifacts/product_b_same_target_source_snapshot_identity_shard_{shard_index}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "result_version": outcome["result_version"],
        "shard_index": shard_index,
        "shard_count": shard_count,
        "species_with_distinct_taxonomy_tuples": sorted(outcome["taxonomy_tuples"]),
        "matched_row_counts_persisted": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
