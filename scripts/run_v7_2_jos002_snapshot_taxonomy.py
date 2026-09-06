#!/usr/bin/env python3
"""Resolve JOS002 focal taxa against current GBIF taxonomy without occurrence reads."""
from __future__ import annotations

from dataclasses import asdict
import csv
import json
from pathlib import Path
import sys
from typing import Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from product_b_v7_2.snapshot_taxonomy import (
    GBIF_CURRENT_SPECIES_MATCH_ENDPOINT,
    GBIF_CURRENT_SPECIES_USAGE_ENDPOINT,
    SnapshotTaxonomyRequest,
    build_current_species_match_params,
    parse_current_direct_taxonomy_resolution,
)
from product_b_v7_2.snapshot_transport import evaluate_snapshot_contract

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_v7_2_snapshot_transport_contract_v0_1.json"
PAIR = ROOT / "registry/product_b_v7_2_jos002_pair_registry_v0_1.csv"
OUTPUT = ROOT / "artifacts/product_b_v7_2_jos002_snapshot_taxonomy.json"

REQUESTS = (
    SnapshotTaxonomyRequest("JOS002", "x", "Yucca jaegeriana", "Plantae"),
    SnapshotTaxonomyRequest("JOS002", "y", "Tegeticula antithetica", "Animalia"),
)


def _read_json(url: str, *, timeout: float = 60.0) -> Mapping[str, object]:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "zuizui0223-284b-product-b-v7-2-taxonomy/0.1"},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def _check_preconditions() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    decision = evaluate_snapshot_contract(contract)
    if not decision.passed:
        raise RuntimeError("v7.2 snapshot contract is invalid: " + ",".join(decision.reasons))
    if contract.get("new_pair_selection_allowed") is not True:
        raise RuntimeError("v7.2 pair selection is not open")
    if contract.get("occurrence_row_reads_allowed") is not False:
        raise RuntimeError("occurrence rows must remain closed during taxonomy")

    with PAIR.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1 or rows[0].get("pair_id") != "JOS002":
        raise RuntimeError("JOS002 pair registry is malformed")
    row = rows[0]
    if row.get("taxonomy_state") != "taxonomy_unopened":
        raise RuntimeError("JOS002 taxonomy state is not unopened")
    if row.get("occurrence_reads_performed") != "false":
        raise RuntimeError("JOS002 occurrence boundary was already crossed")


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _check_preconditions()

    results = []
    errors = []
    for request in REQUESTS:
        try:
            params = build_current_species_match_params(request)
            match_payload = _read_json(
                GBIF_CURRENT_SPECIES_MATCH_ENDPOINT + "?" + urlencode(params)
            )
            usage = match_payload.get("usage")
            if not isinstance(usage, Mapping) or usage.get("key") is None:
                raise ValueError("current match payload has no usage key")
            usage_key = str(usage["key"])
            usage_payload = _read_json(
                GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=usage_key)
            )
            resolution = parse_current_direct_taxonomy_resolution(
                request=request,
                match_payload=match_payload,
                usage_payload=usage_payload,
            )
            results.append(asdict(resolution))
        except Exception as exc:
            errors.append(
                {
                    "partner": request.partner,
                    "requested_name": request.scientific_name,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )

    status = "resolved_direct_exact_current_taxonomy" if not errors and len(results) == len(REQUESTS) else "unresolved_snapshot_taxonomy"
    outcome = {
        "result_version": "product_b_v7_2_jos002_snapshot_taxonomy_v0.1",
        "pair_id": "JOS002",
        "status": status,
        "taxonomy_system": "GBIF current default taxonomy; no legacy checklistKey",
        "resolutions": results,
        "errors": errors,
        "snapshot_occurrence_rows_opened": False,
        "snapshot_occurrence_counts_opened": False,
        "live_occurrence_search_used": False,
    }
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status == "resolved_direct_exact_current_taxonomy" else 1


if __name__ == "__main__":
    sys.exit(main())
