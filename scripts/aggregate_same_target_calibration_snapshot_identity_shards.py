#!/usr/bin/env python3
"""Aggregate six fragment-sharded snapshot taxonomy scans and apply v7.3 identity rules.

The aggregation sees only distinct allowlisted taxonomy tuples from each shard.
No occurrence counts, raw rows, spatial fields, identifiers, or dataset fields are
available to this script.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys

from product_b_v7_3.taxonomy_identity import (
    ALLOWED_COLUMNS,
    SnapshotIdentityDeclaration,
    SnapshotTaxonomyTuple,
    evaluate_snapshot_taxonomy_identity,
    evaluate_v7_3_contract,
)

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "results/product_b_same_target_source_current_taxonomy_v0_1.json"
CONTRACT = ROOT / "config/product_b_v7_3_snapshot_taxonomy_identity_contract_v0_1.json"
SHARD_DIR = ROOT / "artifacts/snapshot_identity_shards"
OUTPUT = ROOT / "results/product_b_same_target_source_snapshot_identity_sharded_v0_1.json"


def _tuple(payload: dict[str, object]) -> SnapshotTaxonomyTuple:
    return SnapshotTaxonomyTuple(
        species=str(payload.get("species") or "").strip(),
        specieskey=str(payload.get("specieskey") or "").strip(),
        taxonkey=str(payload.get("taxonkey") or "").strip(),
        scientificname=str(payload.get("scientificname") or "").strip(),
        taxonrank=str(payload.get("taxonrank") or "").strip().upper(),
    )


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    contract_errors = evaluate_v7_3_contract(contract)
    if contract_errors:
        raise RuntimeError("invalid v7.3 snapshot identity contract: " + ",".join(contract_errors))

    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    if current.get("result_version") != "product_b_same_target_source_current_taxonomy_v0.2":
        raise RuntimeError("corrected current-taxonomy v0.2 result is required")
    if current.get("resolved_taxa") != 36 or current.get("unresolved_taxa") != 0:
        raise RuntimeError("expected frozen 36/36 current-taxonomy resolution")

    files = sorted(SHARD_DIR.glob("product_b_same_target_source_snapshot_identity_shard_*.json"))
    if len(files) != 6:
        raise RuntimeError(f"expected 6 snapshot identity shard summaries, found {len(files)}")

    seen: set[int] = set()
    union_by_name: dict[str, set[SnapshotTaxonomyTuple]] = {}
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        shard = int(payload["shard_index"])
        if shard in seen:
            raise RuntimeError("duplicate snapshot identity shard index")
        seen.add(shard)
        if payload.get("shard_count") != 6:
            raise RuntimeError("snapshot identity shard count mismatch")
        for field in (
            "matched_row_counts_persisted",
            "per_file_matched_counts_persisted",
            "raw_rows_persisted",
            "coordinates_opened",
            "occurrence_identifiers_opened",
            "dataset_fields_opened",
            "paired_discordance_opened",
        ):
            if payload.get(field) is not False:
                raise RuntimeError(f"shard violated firewall: {field}")
        for name, rows in payload.get("taxonomy_tuples", {}).items():
            target = union_by_name.setdefault(str(name), set())
            for row in rows:
                target.add(_tuple(row))

    results: list[dict[str, object]] = []
    for index, row in enumerate(current["resolutions"], start=1):
        name = str(row["requested_name"])
        names = tuple(
            str(v).strip()
            for v in row.get("snapshot_admissible_species_names", [])
            if str(v).strip()
        )
        declaration = SnapshotIdentityDeclaration(
            pair_id=f"CAL{index:03d}",
            taxon_role="x",
            biological_name=name,
            current_accepted_name=str(row["accepted_name"]),
            admissible_species_names=names,
            declaration_frozen=True,
            snapshot_taxonomy_access_started=False,
        )
        tuples: set[SnapshotTaxonomyTuple] = set()
        for allowed_name in names:
            tuples.update(union_by_name.get(allowed_name, set()))
        decision = evaluate_snapshot_taxonomy_identity(
            declaration=declaration,
            taxonomy_tuples=tuple(sorted(tuples)),
        )
        results.append(
            {
                "requested_name": name,
                "validation_stratum": row.get("validation_stratum"),
                "candidate_rank": row.get("candidate_rank"),
                "current_accepted_name": declaration.current_accepted_name,
                "admissible_species_names": list(names),
                "status": decision.terminal_state,
                "passed": decision.passed,
                "resolved_specieskey": decision.resolved_specieskey,
                "reasons": list(decision.reasons),
                "distinct_taxonomy_tuples": [asdict(item) for item in decision.distinct_taxonomy_tuples],
            }
        )

    passed = sum(bool(row["passed"]) for row in results)
    outcome = {
        "result_version": "product_b_same_target_source_snapshot_identity_sharded_v0.1",
        "transport_equivalence": "same_snapshot_same_names_same_five_columns_fragment_partition_only",
        "source_current_taxonomy_result_version": current.get("result_version"),
        "panel_size": 36,
        "current_taxonomy_resolved_entering_gate": 36,
        "current_taxonomy_unresolved_not_entered": 0,
        "snapshot_identity_passed": passed,
        "snapshot_identity_unresolved": 36 - passed,
        "projected_columns": list(ALLOWED_COLUMNS),
        "matched_row_counts_persisted": False,
        "per_file_matched_counts_persisted": False,
        "raw_rows_persisted": False,
        "coordinates_opened": False,
        "occurrence_identifiers_opened": False,
        "dataset_fields_opened": False,
        "sampling_authorized_by_identity_gate": False,
        "paired_discordance_opened": False,
        "identity_results": results,
        "not_entered": [],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
