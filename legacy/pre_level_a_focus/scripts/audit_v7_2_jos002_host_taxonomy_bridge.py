#!/usr/bin/env python3
"""Audit the current-GBIF concept bridge for Yucca jaegeriana without occurrence access."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts/product_b_v7_2_jos002_host_taxonomy_bridge.json"
MATCH_ENDPOINT = "https://api.gbif.org/v2/species/match"
USAGE_ENDPOINT = "https://api.gbif.org/v1/species/{key}"


def _read_json(url: str, *, timeout: float = 60.0) -> Mapping[str, object]:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "zuizui0223-284b-product-b-v7-2-host-bridge/0.1"},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("taxonomy response must be an object")
    return payload


def _compact(obj: object) -> object:
    if not isinstance(obj, Mapping):
        return obj
    keep = (
        "key",
        "canonicalName",
        "name",
        "scientificName",
        "rank",
        "status",
        "taxonomicStatus",
        "acceptedKey",
        "acceptedUsageKey",
        "accepted",
    )
    return {key: obj.get(key) for key in keep if key in obj}


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    params = {
        "scientificName": "Yucca jaegeriana",
        "taxonRank": "SPECIES",
        "kingdom": "Plantae",
    }
    match = _read_json(MATCH_ENDPOINT + "?" + urlencode(params))
    usage = match.get("usage")
    accepted_usage = match.get("acceptedUsage")
    if not isinstance(usage, Mapping) or usage.get("key") is None:
        raise ValueError("current match has no usage key")

    usage_key = str(usage["key"])
    direct_usage = _read_json(USAGE_ENDPOINT.format(key=usage_key))

    accepted_key = None
    candidates = []
    if isinstance(accepted_usage, Mapping):
        candidates.append(accepted_usage.get("key"))
    candidates.extend(
        [
            usage.get("acceptedKey"),
            direct_usage.get("acceptedKey"),
            direct_usage.get("acceptedUsageKey"),
        ]
    )
    for candidate in candidates:
        if candidate not in (None, ""):
            accepted_key = str(candidate)
            break

    direct_accepted = None
    if accepted_key is not None:
        direct_accepted = _read_json(USAGE_ENDPOINT.format(key=accepted_key))

    diagnostics = match.get("diagnostics") if isinstance(match.get("diagnostics"), Mapping) else {}
    outcome = {
        "result_version": "product_b_v7_2_jos002_host_taxonomy_bridge_v0.1",
        "pair_id": "JOS002",
        "requested_name": "Yucca jaegeriana",
        "taxonomy_system": "GBIF current default taxonomy; no legacy checklistKey",
        "match_synonym": bool(match.get("synonym")),
        "match_type": diagnostics.get("matchType"),
        "match_confidence": diagnostics.get("confidence"),
        "match_usage": _compact(usage),
        "match_accepted_usage": _compact(accepted_usage),
        "direct_usage": _compact(direct_usage),
        "accepted_key": accepted_key,
        "direct_accepted_usage": _compact(direct_accepted),
        "snapshot_occurrence_rows_opened": False,
        "snapshot_occurrence_counts_opened": False,
        "live_occurrence_search_used": False,
    }
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
