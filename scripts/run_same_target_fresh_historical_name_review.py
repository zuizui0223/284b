#!/usr/bin/env python3
"""Review every represented historical snapshot name against current taxonomy.

Input is the taxonomy-only fresh snapshot concept tuple aggregate.  This stage
never reads occurrence rows/counts/coordinates.  It attempts a current GBIF
species match for every distinct historical ``scientificname``.  Only an EXACT
match is treated as a positive current resolution.  Positive resolutions are
followed to the accepted usage and then to its current species parent.  A
completed non-exact/no-match is recorded as a historical no-match, not silently
converted into a conflict.  Network/parse failures are marked review-incomplete.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from product_b_v7_2.snapshot_taxonomy import (
    GBIF_CURRENT_SPECIES_MATCH_ENDPOINT,
    GBIF_CURRENT_SPECIES_USAGE_ENDPOINT,
)

ROOT = Path(__file__).resolve().parents[1]
TUPLES = ROOT / "results/product_b_same_target_fresh_snapshot_concept_tuples_v0_1.json"
CONTRACT = ROOT / "config/product_b_same_target_fresh_calibration_contract_v0_1.json"
OUTPUT = ROOT / "results/product_b_same_target_fresh_historical_name_review_v0_1.json"
USER_AGENT = "zuizui0223-284b-fresh-historical-taxonomy-review/0.1"


def _read_json(url: str, timeout: float = 60.0) -> Mapping[str, object]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}, method="GET")
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("taxonomy response must be an object")
    return payload


def _text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _current_species_parent_from_usage(usage_payload: Mapping[str, object]) -> tuple[str | None, str | None]:
    rank = _text(usage_payload.get("rank")).upper()
    canonical = _text(usage_payload.get("canonicalName") or usage_payload.get("canonicalNameWithMarker"))
    key = _text(usage_payload.get("key"))
    if rank == "SPECIES" and canonical:
        return canonical, key or None

    species_name = _text(usage_payload.get("species"))
    species_key = _text(usage_payload.get("speciesKey"))
    if species_name:
        return species_name, species_key or None
    if species_key:
        species_payload = _read_json(GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=species_key))
        species_rank = _text(species_payload.get("rank")).upper()
        species_canonical = _text(species_payload.get("canonicalName") or species_payload.get("canonicalNameWithMarker"))
        if species_rank == "SPECIES" and species_canonical:
            return species_canonical, species_key
    return None, None


def _review_name(name: str) -> dict[str, object]:
    params = urlencode({"scientificName": name, "kingdom": "Plantae"})
    match = _read_json(GBIF_CURRENT_SPECIES_MATCH_ENDPOINT + "?" + params)
    diagnostics = match.get("diagnostics")
    match_type = ""
    if isinstance(diagnostics, Mapping):
        match_type = _text(diagnostics.get("matchType")).upper()
    usage = match.get("usage")
    if match_type != "EXACT" or not isinstance(usage, Mapping) or usage.get("key") is None:
        return {
            "snapshot_scientific_name": name,
            "review_complete": True,
            "resolved": False,
            "accepted_species_name": None,
            "accepted_usage_key": None,
            "match_type": match_type or None,
            "reason": "completed_no_exact_current_match",
        }

    accepted_usage = match.get("acceptedUsage")
    selected = accepted_usage if isinstance(accepted_usage, Mapping) and accepted_usage.get("key") is not None else usage
    accepted_key = _text(selected.get("key"))
    if not accepted_key:
        return {
            "snapshot_scientific_name": name,
            "review_complete": True,
            "resolved": False,
            "accepted_species_name": None,
            "accepted_usage_key": None,
            "match_type": match_type,
            "reason": "completed_exact_match_without_accepted_usage_key",
        }

    accepted_payload = _read_json(GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=accepted_key))
    species_name, species_key = _current_species_parent_from_usage(accepted_payload)
    if not species_name:
        return {
            "snapshot_scientific_name": name,
            "review_complete": True,
            "resolved": False,
            "accepted_species_name": None,
            "accepted_usage_key": accepted_key,
            "match_type": match_type,
            "reason": "completed_exact_match_without_resolvable_current_species_parent",
        }
    return {
        "snapshot_scientific_name": name,
        "review_complete": True,
        "resolved": True,
        "accepted_species_name": species_name,
        "accepted_usage_key": species_key or accepted_key,
        "match_type": match_type,
        "reason": None,
    }


def main() -> int:
    tuples = json.loads(TUPLES.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    minimum = int(contract["panel_rule"]["minimum_complete_taxa_for_calibration"])
    if tuples.get("current_name_review_authorized") is not True:
        raise RuntimeError("fresh historical-name review is not authorized")
    if int(tuples.get("taxa_with_nonempty_snapshot_taxonomy_tuples", -1)) < minimum:
        raise RuntimeError("fresh taxonomy tuple panel is below frozen calibration minimum")
    for flag in (
        "matched_row_counts_persisted",
        "raw_occurrence_rows_persisted",
        "coordinates_opened",
        "occurrence_identifiers_opened",
        "dates_opened",
        "dataset_fields_opened",
        "occurrence_sampling_authorized",
        "environmental_values_opened",
        "current_layer1_paired_discordance_read",
        "process_intervention_outcomes_read",
    ):
        if tuples.get(flag) is not False:
            raise RuntimeError(f"fresh tuple aggregate crossed forbidden boundary: {flag}")

    names = tuple(str(x).strip() for x in tuples.get("distinct_snapshot_scientific_names_for_review", []) if str(x).strip())
    if not names or len(set(names)) != len(names):
        raise RuntimeError("fresh historical-name review list is empty or duplicated")

    reviews = []
    for name in names:
        try:
            reviews.append(_review_name(name))
        except Exception as exc:
            reviews.append(
                {
                    "snapshot_scientific_name": name,
                    "review_complete": False,
                    "resolved": False,
                    "accepted_species_name": None,
                    "accepted_usage_key": None,
                    "match_type": None,
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )

    incomplete = sum(not bool(row["review_complete"]) for row in reviews)
    resolved = sum(bool(row["resolved"]) for row in reviews)
    completed_no_match = sum(bool(row["review_complete"]) and not bool(row["resolved"]) for row in reviews)
    outcome = {
        "result_version": "product_b_same_target_fresh_historical_name_review_v0.1",
        "taxonomy_tuple_result": str(TUPLES.relative_to(ROOT)),
        "distinct_historical_names_reviewed": len(reviews),
        "positive_current_species_resolutions": int(resolved),
        "completed_historical_no_match_reviews": int(completed_no_match),
        "incomplete_reviews": int(incomplete),
        "all_review_attempts_complete": incomplete == 0,
        "reviews": reviews,
        "occurrence_endpoint_called": False,
        "occurrence_counts_opened": False,
        "coordinates_opened": False,
        "environmental_values_opened": False,
        "current_layer1_paired_discordance_read": False,
        "process_intervention_outcomes_read": False,
        "occurrence_sampling_authorized": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "result_version": outcome["result_version"],
                "distinct_historical_names_reviewed": outcome["distinct_historical_names_reviewed"],
                "positive_current_species_resolutions": outcome["positive_current_species_resolutions"],
                "completed_historical_no_match_reviews": outcome["completed_historical_no_match_reviews"],
                "incomplete_reviews": outcome["incomplete_reviews"],
                "occurrence_counts_opened": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
