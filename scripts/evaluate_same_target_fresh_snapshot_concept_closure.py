#!/usr/bin/env python3
"""Apply the frozen fresh species-concept closure after taxonomy-only review.

This stage consumes only sanitized snapshot taxonomy tuples and the completed
current-taxonomy review.  It freezes a complete historical ``specieskey`` set for
each taxon whose snapshot parent species is coherent and has no explicit current
species conflict.  No occurrence rows/counts/coordinates are opened here.
"""
from __future__ import annotations

import csv
from dataclasses import asdict
import json
from pathlib import Path
import sys

from product_b_v7_3.concept_closure import (
    CurrentConceptResolution,
    evaluate_snapshot_species_concept_closure,
)
from product_b_v7_3.taxonomy_identity import SnapshotTaxonomyTuple

ROOT = Path(__file__).resolve().parents[1]
TUPLES = ROOT / "results/product_b_same_target_fresh_snapshot_concept_tuples_v0_1.json"
REVIEWS = ROOT / "results/product_b_same_target_fresh_historical_name_review_v0_1.json"
CONTRACT = ROOT / "config/product_b_same_target_fresh_calibration_contract_v0_1.json"
OUTPUT = ROOT / "results/product_b_same_target_fresh_snapshot_concept_closure_v0_1.json"
KEYSETS = ROOT / "registry/product_b_same_target_fresh_snapshot_keysets_v0_1.csv"


def _tuple(row: dict[str, object]) -> SnapshotTaxonomyTuple:
    return SnapshotTaxonomyTuple(
        species=str(row.get("species") or "").strip(),
        specieskey=str(row.get("specieskey") or "").strip(),
        taxonkey=str(row.get("taxonkey") or "").strip(),
        scientificname=str(row.get("scientificname") or "").strip(),
        taxonrank=str(row.get("taxonrank") or "").strip().upper(),
    )


def main() -> int:
    tuples = json.loads(TUPLES.read_text(encoding="utf-8"))
    reviews = json.loads(REVIEWS.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    minimum = int(contract["panel_rule"]["minimum_complete_taxa_for_calibration"])

    if tuples.get("current_name_review_authorized") is not True:
        raise RuntimeError("fresh concept tuple aggregate did not authorize taxonomy review")
    if reviews.get("result_version") != "product_b_same_target_fresh_historical_name_review_v0.1":
        raise RuntimeError("fresh historical-name review result is missing")
    for payload, flags in (
        (tuples, (
            "matched_row_counts_persisted", "raw_occurrence_rows_persisted", "coordinates_opened",
            "occurrence_identifiers_opened", "dates_opened", "dataset_fields_opened",
            "occurrence_sampling_authorized", "environmental_values_opened",
            "current_layer1_paired_discordance_read", "process_intervention_outcomes_read",
        )),
        (reviews, (
            "occurrence_endpoint_called", "occurrence_counts_opened", "coordinates_opened",
            "environmental_values_opened", "current_layer1_paired_discordance_read",
            "process_intervention_outcomes_read", "occurrence_sampling_authorized",
        )),
    ):
        for flag in flags:
            if payload.get(flag) is not False:
                raise RuntimeError(f"taxonomy-only closure boundary violated: {flag}")

    review_map: dict[str, CurrentConceptResolution] = {}
    for row in reviews.get("reviews", []):
        name = str(row.get("snapshot_scientific_name") or "").strip()
        if not name or name in review_map:
            raise RuntimeError("historical-name review contains blank/duplicate name")
        review_map[name] = CurrentConceptResolution(
            snapshot_scientific_name=name,
            review_complete=bool(row.get("review_complete")),
            resolved=bool(row.get("resolved")),
            accepted_species_name=(
                None if row.get("accepted_species_name") is None
                else str(row.get("accepted_species_name")).strip() or None
            ),
            accepted_usage_key=(
                None if row.get("accepted_usage_key") is None
                else str(row.get("accepted_usage_key")).strip() or None
            ),
            match_type=(
                None if row.get("match_type") is None
                else str(row.get("match_type")).strip() or None
            ),
            reason=(None if row.get("reason") is None else str(row.get("reason"))),
        )

    decisions = []
    key_rows: list[dict[str, object]] = []
    passed_count = 0
    for taxon in tuples.get("taxa", []):
        focal = str(taxon.get("current_accepted_species") or "").strip()
        rows = tuple(_tuple(row) for row in taxon.get("taxonomy_tuples", []))
        decision = evaluate_snapshot_species_concept_closure(
            current_accepted_species=focal,
            taxonomy_tuples=rows,
            current_name_resolutions=review_map,
        )
        if decision.passed:
            passed_count += 1
            for index, key in enumerate(decision.frozen_historical_specieskeys):
                key_rows.append(
                    {
                        "current_accepted_species": focal,
                        "historical_specieskey": key,
                        "key_index": index,
                        "historical_key_count": len(decision.frozen_historical_specieskeys),
                        "closure_state": decision.terminal_state,
                    }
                )
        decisions.append(
            {
                "current_accepted_species": focal,
                "passed": bool(decision.passed),
                "state": decision.terminal_state,
                "reasons": list(decision.reasons),
                "frozen_historical_specieskeys": list(decision.frozen_historical_specieskeys),
                "reviewed_snapshot_scientific_names": list(decision.reviewed_snapshot_scientific_names),
                "current_unresolved_historical_names": list(decision.current_unresolved_historical_names),
                "distinct_taxonomy_tuples": [asdict(row) for row in decision.distinct_taxonomy_tuples],
            }
        )

    sampling_authorized = passed_count >= minimum
    outcome = {
        "result_version": "product_b_same_target_fresh_snapshot_concept_closure_v0.1",
        "candidate_taxa": len(decisions),
        "concept_closure_passed_taxa": int(passed_count),
        "concept_closure_unresolved_taxa": int(len(decisions) - passed_count),
        "frozen_calibration_minimum_taxa": minimum,
        "occurrence_sampling_authorized": bool(sampling_authorized),
        "if_below_minimum_state": None if sampling_authorized else "fresh_cross_source_calibration_unresolved",
        "taxa_replaced": False,
        "historical_key_subset_rescue_used": False,
        "decisions": decisions,
        "occurrence_endpoint_called": False,
        "occurrence_counts_opened": False,
        "coordinates_opened": False,
        "environmental_values_opened": False,
        "model_fit_opened": False,
        "paired_discordance_opened": False,
        "current_layer1_paired_discordance_read": False,
        "process_intervention_outcomes_read": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    KEYSETS.parent.mkdir(parents=True, exist_ok=True)
    with KEYSETS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "current_accepted_species", "historical_specieskey", "key_index",
                "historical_key_count", "closure_state",
            ],
        )
        writer.writeheader()
        writer.writerows(key_rows)

    print(
        json.dumps(
            {
                "result_version": outcome["result_version"],
                "candidate_taxa": outcome["candidate_taxa"],
                "concept_closure_passed_taxa": outcome["concept_closure_passed_taxa"],
                "concept_closure_unresolved_taxa": outcome["concept_closure_unresolved_taxa"],
                "occurrence_sampling_authorized": outcome["occurrence_sampling_authorized"],
                "occurrence_counts_opened": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
