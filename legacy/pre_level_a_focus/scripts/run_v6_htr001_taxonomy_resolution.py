#!/usr/bin/env python3
"""Resolve v6 HTR001 taxonomy without opening occurrences."""

from __future__ import annotations

from dataclasses import asdict
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
    parse_direct_taxonomy_resolution,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config/product_b_v6_htr001_taxonomy_resolution_v0_1.json"
OUTPUT_PATH = ROOT / "artifacts/product_b_v6_htr001_taxonomy_resolution.json"


def _get_json(url: str, *, timeout_seconds: float = 60.0) -> Mapping[str, object]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "zuizui0223-284b-product-b-v6-htr-taxonomy/0.1",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def _resolve(request: TaxonomyResolutionRequest) -> dict[str, object]:
    match_url = GBIF_SPECIES_MATCH_ENDPOINT + "?" + urlencode(
        dict(build_species_match_params(request))
    )
    match_payload = _get_json(match_url)
    usage = match_payload.get("usage")
    if not isinstance(usage, Mapping) or not str(usage.get("key", "")).strip():
        raise ValueError("GBIF match did not return a usage key")
    usage_key = str(usage["key"]).strip()
    usage_payload = _get_json(GBIF_SPECIES_USAGE_ENDPOINT.format(usage_key=usage_key))
    return asdict(
        parse_direct_taxonomy_resolution(
            request=request,
            match_payload=match_payload,
            usage_payload=usage_payload,
        )
    )


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    resolutions: list[dict[str, object]] = []
    partner_states: dict[str, str] = {}

    for spec in contract["requests"]:
        request = TaxonomyResolutionRequest(
            pair_id=contract["pair_id"],
            partner=spec["partner"],
            scientific_name=spec["scientific_name"],
            kingdom=spec["kingdom"],
            expected_key_hint=spec.get("expected_key_hint", ""),
        )
        try:
            resolution = _resolve(request)
            resolutions.append({"state": "resolved_direct_exact", **resolution})
            partner_states[request.partner] = "resolved_direct_exact"
        except Exception as exc:
            resolutions.append(
                {
                    "state": "unresolved_taxonomy",
                    "pair_id": request.pair_id,
                    "partner": request.partner,
                    "requested_name": request.scientific_name,
                    "requested_kingdom": request.kingdom,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )
            partner_states[request.partner] = "unresolved_taxonomy"

    pair_state = (
        "eligible_for_confirmatory_preflight"
        if partner_states.get("x") == partner_states.get("y") == "resolved_direct_exact"
        else "unresolved_taxonomy"
    )
    outcome = {
        "status": "completed_taxonomy_only",
        "contract_version": contract["contract_version"],
        "pair_id": contract["pair_id"],
        "checklist_key": contract["checklist_key"],
        "pair_taxonomy_state": pair_state,
        "resolutions": resolutions,
        "occurrence_reads_performed": False,
    }
    OUTPUT_PATH.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
