#!/usr/bin/env python3
"""Resolve the frozen JOS003 control pool against current GBIF taxonomy only."""
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
POOL = ROOT / "registry/product_b_v7_2_jos003_control_pool_v0_1.csv"
OUTPUT = ROOT / "artifacts/product_b_v7_2_jos003_control_taxonomy.json"
MIN_CONTROLS = 5


def _read_json(url: str, timeout: float = 60.0) -> Mapping[str, object]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "zuizui0223-284b-product-b-v7-2-controls/0.1"}, method="GET")
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    decision = evaluate_snapshot_contract(contract)
    if not decision.passed or contract["occurrence_row_reads_allowed"]:
        raise RuntimeError("snapshot contract is not safe for taxonomy-only control audit")

    with POOL.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 8:
        raise RuntimeError("JOS003 frozen control pool must contain exactly 8 taxa")

    admitted = []
    excluded = []
    for row in rows:
        control_id = row["control_id"]
        name = row["scientific_name"]
        request = SnapshotTaxonomyRequest(f"JOS003_{control_id}", "x", name, "Plantae")
        try:
            match = _read_json(GBIF_CURRENT_SPECIES_MATCH_ENDPOINT + "?" + urlencode(build_current_species_match_params(request)))
            usage = match.get("usage")
            if not isinstance(usage, Mapping) or usage.get("key") is None:
                raise ValueError("current match payload has no usage key")
            direct = _read_json(GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=str(usage["key"])))
            result = parse_current_direct_taxonomy_resolution(request=request, match_payload=match, usage_payload=direct)
            admitted.append({"control_id": control_id, **asdict(result)})
        except Exception as exc:
            excluded.append({"control_id": control_id, "scientific_name": name, "error_type": type(exc).__name__, "error_message": str(exc), "rescue_attempted": False})

    status = "control_taxonomy_preflight_passed" if len(admitted) >= MIN_CONTROLS else "unresolved_controls_taxonomy"
    outcome = {
        "result_version": "product_b_v7_2_jos003_control_taxonomy_v0.1",
        "pair_id": "JOS003",
        "status": status,
        "declared_control_count": 8,
        "minimum_required_control_count": MIN_CONTROLS,
        "admitted_count": len(admitted),
        "admitted": admitted,
        "excluded": excluded,
        "synonym_rescue_allowed": False,
        "replacement_after_taxonomy_allowed": False,
        "snapshot_occurrence_rows_opened": False,
        "snapshot_occurrence_counts_opened": False,
        "live_occurrence_search_used": False
    }
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status == "control_taxonomy_preflight_passed" else 1


if __name__ == "__main__":
    sys.exit(main())
