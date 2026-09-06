#!/usr/bin/env python3
"""Aggregate fresh snapshot taxonomy-only shards without opening occurrences.

The output is still pre-occurrence evidence.  It unions distinct five-column
taxonomy tuples across six deterministic snapshot fragment shards and derives the
complete historical ``specieskey`` set and represented scientific names for each
fresh current-taxonomy-resolved species.  No matched-row count is computed or
persisted.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys

from product_b_v7_3.taxonomy_identity import SnapshotTaxonomyTuple

ROOT = Path(__file__).resolve().parents[1]
INPUT_ROOT = ROOT / "artifacts/fresh_snapshot_concept_shards"
CURRENT = ROOT / "results/product_b_same_target_fresh_current_taxonomy_v0_1.json"
CONTRACT = ROOT / "config/product_b_same_target_fresh_calibration_contract_v0_1.json"
OUTPUT = ROOT / "results/product_b_same_target_fresh_snapshot_concept_tuples_v0_1.json"


def _tuple(payload: dict[str, object]) -> SnapshotTaxonomyTuple:
    return SnapshotTaxonomyTuple(
        species=str(payload.get("species") or "").strip(),
        specieskey=str(payload.get("specieskey") or "").strip(),
        taxonkey=str(payload.get("taxonkey") or "").strip(),
        scientificname=str(payload.get("scientificname") or "").strip(),
        taxonrank=str(payload.get("taxonrank") or "").strip().upper(),
    )


def main() -> int:
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    minimum = int(contract["panel_rule"]["minimum_complete_taxa_for_calibration"])
    if int(current.get("resolved_exact_accepted_species", -1)) < minimum:
        raise RuntimeError("fresh current-taxonomy panel fell below frozen minimum before snapshot aggregation")
    if current.get("snapshot_taxonomy_opened") is not False:
        raise RuntimeError("fresh current-taxonomy result already crossed snapshot boundary")
    resolved_names = tuple(
        sorted(
            str(row["accepted_name"]).strip()
            for row in current["resolutions"]
            if row.get("state") == "fresh_current_taxonomy_resolved_exact_accepted_species"
        )
    )
    if len(resolved_names) != int(current["resolved_exact_accepted_species"]):
        raise RuntimeError("fresh current-taxonomy denominator mismatch")

    paths = sorted(INPUT_ROOT.glob("product_b_same_target_fresh_snapshot_concept_shard_*.json"))
    if len(paths) != 6:
        raise RuntimeError(f"expected 6 fresh snapshot taxonomy shards, found {len(paths)}")
    seen_indices: set[int] = set()
    tuples: dict[str, set[SnapshotTaxonomyTuple]] = {name: set() for name in resolved_names}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("result_version") != "product_b_same_target_fresh_snapshot_concept_fragment_v0.1":
            raise RuntimeError("unexpected fresh snapshot shard result version")
        index = int(payload["shard_index"])
        if index in seen_indices or int(payload["shard_count"]) != 6:
            raise RuntimeError("fresh snapshot shard index/count mismatch")
        seen_indices.add(index)
        if payload.get("projected_columns") != ["species", "specieskey", "taxonkey", "scientificname", "taxonrank"]:
            raise RuntimeError("fresh snapshot shard projected columns drifted")
        for flag in (
            "matched_row_counts_persisted",
            "per_file_matched_counts_persisted",
            "raw_rows_persisted",
            "coordinates_opened",
            "occurrence_identifiers_opened",
            "dates_opened",
            "dataset_fields_opened",
            "environmental_values_opened",
            "current_layer1_paired_discordance_read",
            "process_intervention_outcomes_read",
        ):
            if payload.get(flag) is not False:
                raise RuntimeError(f"fresh taxonomy shard crossed forbidden boundary: {flag}")
        for name, rows in payload.get("taxonomy_tuples", {}).items():
            if name not in tuples:
                raise RuntimeError("fresh snapshot shard returned undeclared current species")
            for row in rows:
                item = _tuple(row)
                if item.species != name:
                    raise RuntimeError("taxonomy tuple parent species differs from shard key")
                tuples[name].add(item)
    if seen_indices != set(range(6)):
        raise RuntimeError("fresh snapshot taxonomy shard coverage incomplete")

    taxa = []
    taxa_with_nonempty_tuples = 0
    all_historical_names: set[str] = set()
    for name in resolved_names:
        ordered = tuple(sorted(tuples[name]))
        keys = tuple(sorted({row.specieskey for row in ordered if row.specieskey}))
        scientific_names = tuple(sorted({row.scientificname for row in ordered if row.scientificname}))
        if ordered:
            taxa_with_nonempty_tuples += 1
        all_historical_names.update(scientific_names)
        taxa.append(
            {
                "current_accepted_species": name,
                "taxonomy_tuples": [asdict(row) for row in ordered],
                "historical_specieskeys_preclosure": list(keys),
                "snapshot_scientific_names_for_review": list(scientific_names),
                "taxonomy_tuple_present": bool(ordered),
            }
        )

    review_authorized = taxa_with_nonempty_tuples >= minimum
    outcome = {
        "result_version": "product_b_same_target_fresh_snapshot_concept_tuples_v0.1",
        "snapshot_date": "2026-08-01",
        "fresh_current_taxonomy_resolved": len(resolved_names),
        "taxa_with_nonempty_snapshot_taxonomy_tuples": int(taxa_with_nonempty_tuples),
        "taxa_without_snapshot_taxonomy_tuple": int(len(resolved_names) - taxa_with_nonempty_tuples),
        "frozen_calibration_minimum_taxa": minimum,
        "current_name_review_authorized": bool(review_authorized),
        "if_below_minimum_state": (
            None if review_authorized else "fresh_cross_source_calibration_unresolved"
        ),
        "taxa": taxa,
        "distinct_snapshot_scientific_names_for_review": sorted(all_historical_names),
        "matched_row_counts_persisted": False,
        "raw_occurrence_rows_persisted": False,
        "coordinates_opened": False,
        "occurrence_identifiers_opened": False,
        "dates_opened": False,
        "dataset_fields_opened": False,
        "occurrence_sampling_authorized": False,
        "environmental_values_opened": False,
        "current_layer1_paired_discordance_read": False,
        "process_intervention_outcomes_read": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "result_version": outcome["result_version"],
                "fresh_current_taxonomy_resolved": outcome["fresh_current_taxonomy_resolved"],
                "taxa_with_nonempty_snapshot_taxonomy_tuples": outcome["taxa_with_nonempty_snapshot_taxonomy_tuples"],
                "taxa_without_snapshot_taxonomy_tuple": outcome["taxa_without_snapshot_taxonomy_tuple"],
                "current_name_review_authorized": outcome["current_name_review_authorized"],
                "matched_row_counts_persisted": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
