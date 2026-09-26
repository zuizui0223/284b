#!/usr/bin/env python3
"""Inspect the JOS001 moth synonym bridge without opening occurrences.

This taxonomy-only review accepts no occurrence input. It requires the legacy
GBIF match for Tegeticula synthetica to be an exact species match and, when the
matched usage is not accepted, requires a direct acceptedKey relation to one
accepted/doubtful species usage. The accepted name is discovered from taxonomy
only and is not preselected from occurrence availability.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from product_b_v5.gbif_taxonomy import (
    GBIF_SPECIES_MATCH_ENDPOINT,
    GBIF_SPECIES_USAGE_ENDPOINT,
    TaxonomyResolutionRequest,
    build_species_match_params,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "artifacts/product_b_v7_1_jos001_manual_taxonomy_review.json"
CHECKLIST_KEY = "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"
REQUESTED_NAME = "Tegeticula synthetica"


def _get_json(url: str, *, timeout_seconds: float = 60.0) -> Mapping[str, object]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "zuizui0223-284b-product-b-v7-1-jos-taxonomy-review/0.1",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def _text(payload: Mapping[str, object], *fields: str) -> str:
    for field in fields:
        value = payload.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _usage_summary(payload: Mapping[str, object]) -> dict[str, object]:
    return {
        "key": str(payload.get("key", "")),
        "canonical_name": _text(payload, "canonicalName", "canonicalNameWithMarker"),
        "scientific_name": _text(payload, "scientificName"),
        "rank": _text(payload, "rank").upper(),
        "status": _text(payload, "taxonomicStatus", "status").upper(),
        "accepted_key": str(payload.get("acceptedKey", payload.get("acceptedTaxonKey", ""))),
        "accepted_name": _text(payload, "accepted", "acceptedNameUsage"),
    }


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    request = TaxonomyResolutionRequest(
        pair_id="JOS001",
        partner="y",
        scientific_name=REQUESTED_NAME,
        kingdom="Animalia",
        expected_key_hint="",
    )
    match_url = GBIF_SPECIES_MATCH_ENDPOINT + "?" + urlencode(dict(build_species_match_params(request)))
    match = _get_json(match_url)
    usage_obj = match.get("usage")
    diagnostics = match.get("diagnostics")
    if not isinstance(usage_obj, Mapping):
        raise ValueError("GBIF match did not return usage")
    if not isinstance(diagnostics, Mapping):
        raise ValueError("GBIF match did not return diagnostics")

    usage_key = str(usage_obj.get("key", "")).strip()
    if not usage_key:
        raise ValueError("GBIF match usage key is blank")
    usage = _usage_summary(_get_json(GBIF_SPECIES_USAGE_ENDPOINT.format(usage_key=usage_key)))

    match_type = _text(diagnostics, "matchType").upper()
    confidence = diagnostics.get("confidence") if isinstance(diagnostics.get("confidence"), int) else None

    reasons: list[str] = []
    if match_type != "EXACT":
        reasons.append("match_not_exact")
    if _text(usage_obj, "rank").upper() != "SPECIES":
        reasons.append("match_usage_not_species")
    match_canonical = _text(usage_obj, "canonicalName", "name")
    if match_canonical.casefold() != REQUESTED_NAME.casefold():
        reasons.append("match_canonical_name_mismatch")
    if usage["rank"] != "SPECIES":
        reasons.append("direct_usage_not_species")

    accepted_key = str(usage["accepted_key"]).strip()
    accepted: dict[str, object] | None = None
    if usage["status"] == "ACCEPTED":
        accepted_key = str(usage["key"])
        accepted = usage
    elif accepted_key:
        accepted = _usage_summary(
            _get_json(GBIF_SPECIES_USAGE_ENDPOINT.format(usage_key=accepted_key))
        )
    else:
        reasons.append("nonaccepted_usage_has_no_accepted_key")

    if accepted is not None:
        if accepted["key"] != accepted_key:
            reasons.append("accepted_usage_key_mismatch")
        if accepted["rank"] != "SPECIES":
            reasons.append("accepted_usage_not_species")
        if accepted["status"] not in {"ACCEPTED", "DOUBTFUL"}:
            reasons.append("accepted_usage_status_inadmissible")

    relation_by_key = bool(accepted is not None and usage["accepted_key"] == accepted_key)
    if usage["status"] != "ACCEPTED" and not relation_by_key:
        reasons.append("legacy_usage_does_not_directly_point_to_accepted_usage")

    state = "resolved_manual_direct_synonym_bridge" if not reasons else "unresolved_taxonomy"
    outcome = {
        "status": "completed_manual_taxonomy_review",
        "pair_id": "JOS001",
        "partner": "y",
        "requested_name": REQUESTED_NAME,
        "checklist_key": CHECKLIST_KEY,
        "state": state,
        "match_type": match_type,
        "confidence": confidence,
        "match_usage": dict(usage_obj),
        "legacy_name_usage": usage,
        "legacy_accepted_usage": accepted,
        "relation_by_accepted_key": relation_by_key,
        "reasons": reasons,
        "occurrence_reads_performed": False,
    }
    OUTPUT_PATH.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not reasons else 1


if __name__ == "__main__":
    sys.exit(main())
