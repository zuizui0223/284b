#!/usr/bin/env python3
"""Resolve the frozen calibration panel inside the 2026-08-01 GBIF snapshot.

Input is the committed current-taxonomy audit. Only taxa already resolved there
enter this gate. The scanner projects only the five v7.3 allowlisted taxonomy
columns and persists only distinct taxonomy tuples, never occurrence counts,
coordinates, dates, record identifiers, dataset frequencies, or raw rows.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys

import pyarrow.dataset as ds
import pyarrow.fs as pafs

from product_b_v7_2.snapshot_transport import EXPECTED_BUCKET, EXPECTED_OCCURRENCE_PREFIX, EXPECTED_REGION
from product_b_v7_3.taxonomy_identity import (
    ALLOWED_COLUMNS,
    SnapshotIdentityDeclaration,
    SnapshotTaxonomyTuple,
    evaluate_snapshot_taxonomy_identity,
    evaluate_v7_3_contract,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_v7_3_snapshot_taxonomy_identity_contract_v0_1.json"
CURRENT = ROOT / "results/product_b_same_target_source_current_taxonomy_v0_1.json"
OUTPUT = ROOT / "results/product_b_same_target_source_snapshot_identity_v0_1.json"
DATASET_PATH = f"{EXPECTED_BUCKET}/{EXPECTED_OCCURRENCE_PREFIX.rstrip('/')}"


def _declaration(index: int, row: dict[str, object]) -> SnapshotIdentityDeclaration:
    names = tuple(str(v).strip() for v in row.get("snapshot_admissible_species_names", []) if str(v).strip())
    return SnapshotIdentityDeclaration(
        pair_id=f"CAL{index:03d}",
        taxon_role="x",
        biological_name=str(row["requested_name"]),
        current_accepted_name=str(row["accepted_name"]),
        admissible_species_names=names,
        declaration_frozen=True,
        snapshot_taxonomy_access_started=False,
    )


def _scan_all(declarations: list[SnapshotIdentityDeclaration]) -> dict[str, set[SnapshotTaxonomyTuple]]:
    all_names = sorted({name for declaration in declarations for name in declaration.admissible_species_names})
    filesystem = pafs.S3FileSystem(anonymous=True, region=EXPECTED_REGION)
    dataset = ds.dataset(DATASET_PATH, filesystem=filesystem, format="parquet")
    expression = ds.field("species").isin(all_names)
    scanner = dataset.scanner(
        columns=list(ALLOWED_COLUMNS),
        filter=expression,
        batch_size=65536,
        use_threads=True,
    )
    by_species_name: dict[str, set[SnapshotTaxonomyTuple]] = {name: set() for name in all_names}
    for batch in scanner.to_batches():
        values = batch.to_pydict()
        for i in range(batch.num_rows):
            species = str(values["species"][i] or "").strip()
            if species not in by_species_name:
                raise ValueError("snapshot scanner returned undeclared species name")
            by_species_name[species].add(
                SnapshotTaxonomyTuple(
                    species=species,
                    specieskey=str(values["specieskey"][i] or "").strip(),
                    taxonkey=str(values["taxonkey"][i] or "").strip(),
                    scientificname=str(values["scientificname"][i] or "").strip(),
                    taxonrank=str(values["taxonrank"][i] or "").strip().upper(),
                )
            )
    return by_species_name


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract_errors = evaluate_v7_3_contract(contract)
    if contract_errors:
        raise RuntimeError("invalid v7.3 snapshot identity contract: " + ",".join(contract_errors))

    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    if current.get("panel_size") != 36 or current.get("all_36_entered") is not True:
        raise RuntimeError("current-taxonomy audit does not represent the frozen 36-taxon panel")
    if current.get("occurrence_endpoint_called") is not False or current.get("occurrence_counts_opened") is not False:
        raise RuntimeError("current-taxonomy audit crossed an occurrence boundary")
    if current.get("paired_discordance_opened") is not False:
        raise RuntimeError("paired discordance was opened before snapshot identity")

    resolved_rows = [
        row for row in current["resolutions"]
        if row.get("state") == "resolved_current_taxonomy"
    ]
    declarations = [_declaration(i + 1, row) for i, row in enumerate(resolved_rows)]
    scanned = _scan_all(declarations) if declarations else {}

    output_rows: list[dict[str, object]] = []
    for declaration in declarations:
        tuples: set[SnapshotTaxonomyTuple] = set()
        for name in declaration.admissible_species_names:
            tuples.update(scanned.get(name, set()))
        decision = evaluate_snapshot_taxonomy_identity(
            declaration=declaration,
            taxonomy_tuples=tuple(sorted(tuples)),
        )
        output_rows.append(
            {
                "requested_name": declaration.biological_name,
                "current_accepted_name": declaration.current_accepted_name,
                "admissible_species_names": list(declaration.admissible_species_names),
                "status": decision.terminal_state,
                "passed": decision.passed,
                "resolved_specieskey": decision.resolved_specieskey,
                "reasons": list(decision.reasons),
                "distinct_taxonomy_tuples": [asdict(item) for item in decision.distinct_taxonomy_tuples],
            }
        )

    unresolved_current = [
        {
            "requested_name": row.get("requested_name"),
            "current_taxonomy_state": row.get("state"),
            "snapshot_identity_state": "not_entered_due_to_current_taxonomy_unresolved",
        }
        for row in current["resolutions"]
        if row.get("state") != "resolved_current_taxonomy"
    ]
    passed = sum(bool(row["passed"]) for row in output_rows)
    unresolved_snapshot = len(output_rows) - passed
    outcome = {
        "result_version": "product_b_same_target_source_snapshot_identity_v0.1",
        "panel_size": 36,
        "current_taxonomy_resolved_entering_gate": len(declarations),
        "current_taxonomy_unresolved_not_entered": len(unresolved_current),
        "snapshot_identity_passed": passed,
        "snapshot_identity_unresolved": unresolved_snapshot,
        "projected_columns": list(ALLOWED_COLUMNS),
        "matched_row_counts_persisted": False,
        "raw_rows_persisted": False,
        "coordinates_opened": False,
        "occurrence_identifiers_opened": False,
        "dataset_fields_opened": False,
        "sampling_authorized_by_identity_gate": False,
        "paired_discordance_opened": False,
        "identity_results": output_rows,
        "not_entered": unresolved_current,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
