#!/usr/bin/env python3
"""Resolve the KIM001 host name bridge without occurrence access."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from product_b_v5.gbif_taxonomy import GBIF_SPECIES_MATCH_ENDPOINT, build_species_match_params, TaxonomyResolutionRequest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config/product_b_v7_kim001_manual_taxonomy_review_v0_1.json"
OUTPUT_PATH = ROOT / "artifacts/product_b_v7_kim001_manual_taxonomy_review.json"


def _get_json(url: str, *, timeout_seconds: float = 60.0) -> Mapping[str, object]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "zuizui0223-284b-product-b-v7-kim-manual-taxonomy/0.1"}, method="GET")
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


def _summary(payload: Mapping[str, object]) -> dict[str, object]:
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
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    request = TaxonomyResolutionRequest(
        pair_id=contract["pair_id"],
        partner=contract["partner"],
        scientific_name=contract["literature_name"],
        kingdom="Plantae",
        expected_key_hint="",
    )
    match_url = GBIF_SPECIES_MATCH_ENDPOINT + "?" + urlencode(dict(build_species_match_params(request)))
    match_payload = _get_json(match_url)
    usage = match_payload.get("usage")
    if not isinstance(usage, Mapping) or not str(usage.get("key", "")).strip():
        raise ValueError("GBIF match did not return a usage key")
    name_key = str(usage["key"]).strip()
    name_payload = _get_json(f"https://api.gbif.org/v1/species/{name_key}")
    name = _summary(name_payload)
    accepted_key = str(name.get("accepted_key", "")).strip()
    if not accepted_key:
        raise ValueError("legacy synonym usage did not expose an accepted key")
    accepted_payload = _get_json(f"https://api.gbif.org/v1/species/{accepted_key}")
    accepted = _summary(accepted_payload)

    reasons: list[str] = []
    if name["key"] != name_key:
        reasons.append("literature_name_key_mismatch")
    if str(name["canonical_name"]).casefold() != contract["literature_name"].casefold():
        reasons.append("literature_name_canonical_mismatch")
    if name["rank"] != "SPECIES":
        reasons.append("literature_name_not_species_rank")
    if name["status"] not in {"SYNONYM", "DOUBTFUL"}:
        reasons.append("literature_name_not_synonym_like")
    if accepted["key"] != accepted_key:
        reasons.append("accepted_key_mismatch")
    if str(accepted["canonical_name"]).casefold() != contract["expected_legacy_accepted_name"].casefold():
        reasons.append("accepted_canonical_mismatch")
    if accepted["rank"] != "SPECIES":
        reasons.append("accepted_name_not_species_rank")
    if accepted["status"] not in {"ACCEPTED", "DOUBTFUL"}:
        reasons.append("accepted_usage_status_inadmissible")

    state = "resolved_manual_homotypic_synonym_bridge" if not reasons else "unresolved_taxonomy"
    outcome = {
        "status": "completed_manual_taxonomy_review",
        "contract_version": contract["contract_version"],
        "pair_id": contract["pair_id"],
        "partner": contract["partner"],
        "state": state,
        "literature_name_usage": name,
        "legacy_accepted_usage": accepted,
        "reasons": reasons,
        "occurrence_reads_performed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not reasons else 1


if __name__ == "__main__":
    sys.exit(main())
