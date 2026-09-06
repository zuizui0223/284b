#!/usr/bin/env python3
"""Resolve the frozen HTR001 shuffled-host pool without occurrence access."""

from __future__ import annotations

from dataclasses import asdict
import csv
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
CONTRACT_PATH = ROOT / "config/product_b_v6_htr001_control_taxonomy_v0_1.json"
OUTPUT_PATH = ROOT / "artifacts/product_b_v6_htr001_control_taxonomy.json"


def _get_json(url: str, *, timeout_seconds: float = 60.0) -> Mapping[str, object]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "zuizui0223-284b-product-b-v6-htr-control-taxonomy/0.1",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def _resolve(name: str) -> dict[str, object]:
    request = TaxonomyResolutionRequest(
        pair_id="HTR001_CONTROL_POOL",
        partner="x",
        scientific_name=name,
        kingdom="Plantae",
        expected_key_hint="",
    )
    match_payload = _get_json(
        GBIF_SPECIES_MATCH_ENDPOINT + "?" + urlencode(dict(build_species_match_params(request)))
    )
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
    pool_path = ROOT / contract["pool_registry"]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with pool_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    results: list[dict[str, object]] = []
    resolved = 0
    for row in rows:
        try:
            resolution = _resolve(row["scientific_name"])
            results.append(
                {
                    "control_taxon_id": row["control_taxon_id"],
                    "scientific_name": row["scientific_name"],
                    "state": "resolved_direct_exact",
                    **resolution,
                }
            )
            resolved += 1
        except Exception as exc:
            results.append(
                {
                    "control_taxon_id": row["control_taxon_id"],
                    "scientific_name": row["scientific_name"],
                    "state": "excluded_unresolved_taxonomy",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )

    minimum = int(contract["minimum_taxonomy_resolved_candidates_before_any_occurrence_query"])
    pool_state = (
        "control_taxonomy_preflight_passed"
        if resolved >= minimum
        else "unresolved_controls"
    )
    outcome = {
        "status": "completed_control_taxonomy_only",
        "contract_version": contract["contract_version"],
        "pair_id": contract["pair_id"],
        "closed_pool_size": len(rows),
        "resolved_candidate_count": resolved,
        "minimum_required": minimum,
        "pool_state": pool_state,
        "results": results,
        "occurrence_reads_performed": False,
    }
    OUTPUT_PATH.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if resolved >= minimum else 1


if __name__ == "__main__":
    sys.exit(main())
