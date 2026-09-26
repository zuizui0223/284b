#!/usr/bin/env python3
"""Run the frozen v7.3 snapshot-internal taxonomy identity gate for NEIC001 X.

This engineering-only runner projects exactly the five allowlisted taxonomy
columns from the already frozen 2026-08-01 GBIF snapshot. It never projects or
persists coordinates, occurrence identifiers, dataset fields, dates, recorder
fields, or matched-row counts. Raw rows are reduced immediately to distinct
snapshot taxonomy tuples.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Iterable

import pyarrow.dataset as ds
import pyarrow.fs as pafs

from product_b_v7_2.snapshot_transport import EXPECTED_BUCKET, EXPECTED_OCCURRENCE_PREFIX, EXPECTED_REGION
from product_b_v7_3.snapshot_identity_scan import SnapshotIdentityScanPlan, evaluate_snapshot_identity_scan_plan
from product_b_v7_3.taxonomy_identity import (
    ALLOWED_COLUMNS,
    SnapshotIdentityDeclaration,
    SnapshotTaxonomyTuple,
    evaluate_snapshot_taxonomy_identity,
    evaluate_v7_3_contract,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_v7_3_snapshot_taxonomy_identity_contract_v0_1.json"
ADMISSION = ROOT / "config/product_b_v7_3_neic001_admission_v0_1.json"
OUTPUT = ROOT / "artifacts/product_b_v7_3_neic001_snapshot_identity.json"
DATASET_PATH = f"{EXPECTED_BUCKET}/{EXPECTED_OCCURRENCE_PREFIX.rstrip('/')}"


def _declaration(admission: dict[str, object]) -> SnapshotIdentityDeclaration:
    return SnapshotIdentityDeclaration(
        pair_id="NEIC001",
        taxon_role="x",
        biological_name=str(admission["x_biological_name"]),
        current_accepted_name=str(admission["x_current_accepted_name"]),
        admissible_species_names=tuple(str(v) for v in admission["x_snapshot_admissible_species_names"]),
        declaration_frozen=bool(admission["declaration_frozen"]),
        snapshot_taxonomy_access_started=bool(admission["snapshot_taxonomy_identity_access_started"]),
    )


def _scan_distinct_tuples(declaration: SnapshotIdentityDeclaration) -> tuple[SnapshotTaxonomyTuple, ...]:
    filesystem = pafs.S3FileSystem(anonymous=True, region=EXPECTED_REGION)
    dataset = ds.dataset(DATASET_PATH, filesystem=filesystem, format="parquet")
    expression = ds.field("species").isin(list(declaration.admissible_species_names))
    scanner = dataset.scanner(
        columns=list(ALLOWED_COLUMNS),
        filter=expression,
        batch_size=65536,
        use_threads=True,
    )
    tuples: set[SnapshotTaxonomyTuple] = set()
    for batch in scanner.to_batches():
        columns = batch.to_pydict()
        n = batch.num_rows
        for i in range(n):
            tuples.add(
                SnapshotTaxonomyTuple(
                    species=str(columns["species"][i] or "").strip(),
                    specieskey=str(columns["specieskey"][i] or "").strip(),
                    taxonkey=str(columns["taxonkey"][i] or "").strip(),
                    scientificname=str(columns["scientificname"][i] or "").strip(),
                    taxonrank=str(columns["taxonrank"][i] or "").strip().upper(),
                )
            )
    return tuple(sorted(tuples))


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract_errors = evaluate_v7_3_contract(contract)
    if contract_errors:
        raise RuntimeError("invalid v7.3 identity contract: " + ",".join(contract_errors))

    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    if admission.get("engineering_only") is not True or admission.get("confirmatory_promotion_allowed") is not False:
        raise RuntimeError("NEIC001 engineering firewall changed")
    if admission.get("current_taxonomy_state") != "resolved_y_direct_exact_x_manual_homotypic_synonym_bridge":
        raise RuntimeError("NEIC001 current taxonomy bridge is not frozen-resolved")
    if admission.get("snapshot_occurrence_row_access_started") is not False:
        raise RuntimeError("snapshot occurrence rows were already opened")
    if admission.get("model_fit_reads_started") is not False or admission.get("invariant_reads_started") is not False:
        raise RuntimeError("downstream scientific boundary was already crossed")

    declaration = _declaration(admission)
    scan_plan = SnapshotIdentityScanPlan(scan_id="NEIC001_X_SNAPSHOT_IDENTITY_V0_1", declarations=(declaration,))
    plan_decision = evaluate_snapshot_identity_scan_plan(scan_plan)
    if not plan_decision.passed:
        raise RuntimeError("invalid snapshot identity scan plan: " + ",".join(plan_decision.reasons))

    taxonomy_tuples = _scan_distinct_tuples(declaration)
    decision = evaluate_snapshot_taxonomy_identity(declaration=declaration, taxonomy_tuples=taxonomy_tuples)
    outcome = {
        "result_version": "product_b_v7_3_neic001_snapshot_identity_v0.1",
        "pair_id": "NEIC001",
        "taxon_role": "x",
        "status": decision.terminal_state,
        "passed": decision.passed,
        "resolved_specieskey": decision.resolved_specieskey,
        "reasons": list(decision.reasons),
        "distinct_taxonomy_tuples": [asdict(row) for row in decision.distinct_taxonomy_tuples],
        "projected_columns": list(ALLOWED_COLUMNS),
        "matched_row_count_persisted": False,
        "raw_rows_persisted": False,
        "snapshot_occurrence_rows_opened": False,
        "snapshot_occurrence_counts_opened": False,
        "engineering_only": True,
        "confirmatory_promotion_allowed": False,
        "sampling_authorized": False,
    }
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if decision.passed else 1


if __name__ == "__main__":
    sys.exit(main())
