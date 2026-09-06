#!/usr/bin/env python3
"""Resolve the frozen CROT001 control pool against current GBIF taxonomy only."""
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
from product_b_v7_3.taxonomy_identity import evaluate_v7_3_contract

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_CONTRACT = ROOT / "config/product_b_v7_2_snapshot_transport_contract_v0_1.json"
IDENTITY_CONTRACT = ROOT / "config/product_b_v7_3_snapshot_taxonomy_identity_contract_v0_1.json"
PAIR = ROOT / "registry/product_b_v7_3_crot001_pair_registry_v0_1.csv"
POOL = ROOT / "registry/product_b_v7_3_crot001_control_pool_v0_1.csv"
OUTPUT = ROOT / "artifacts/product_b_v7_3_crot001_control_current_taxonomy.json"
MIN_CONTROLS = 5


def _read_json(url: str, timeout: float = 60.0) -> Mapping[str, object]:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "zuizui0223-284b-product-b-v7-3-controls/0.1"},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def _check_preconditions() -> list[dict[str, str]]:
    snapshot_contract = json.loads(SNAPSHOT_CONTRACT.read_text(encoding="utf-8"))
    snapshot_decision = evaluate_snapshot_contract(snapshot_contract)
    if not snapshot_decision.passed or snapshot_contract["occurrence_row_reads_allowed"]:
        raise RuntimeError("snapshot contract is not closed for taxonomy-only control audit")
    identity_contract = json.loads(IDENTITY_CONTRACT.read_text(encoding="utf-8"))
    errors = evaluate_v7_3_contract(identity_contract)
    if errors:
        raise RuntimeError("invalid v7.3 identity contract: " + ",".join(errors))

    with PAIR.open("r", encoding="utf-8", newline="") as handle:
        pair = list(csv.DictReader(handle))[0]
    if pair["current_taxonomy_state"] != "resolved_direct_exact_current_taxonomy":
        raise RuntimeError("CROT001 focal current taxonomy must be resolved first")
    if pair["snapshot_taxonomy_identity_state"] != "snapshot_taxonomy_identity_unopened":
        raise RuntimeError("snapshot taxonomy identity must remain unopened")
    if pair["snapshot_occurrence_rows_opened"] != "false":
        raise RuntimeError("snapshot occurrence rows must remain unopened")

    with POOL.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 8:
        raise RuntimeError("CROT001 control pool must remain exactly 8 predeclared taxa")
    if any(row["current_taxonomy_state"] != "taxonomy_unopened" for row in rows):
        raise RuntimeError("CROT001 control current-taxonomy gate was already crossed")
    if any(row["snapshot_taxonomy_identity_state"] != "snapshot_taxonomy_identity_unopened" for row in rows):
        raise RuntimeError("CROT001 control snapshot identities must remain unopened")
    if any(row["snapshot_occurrence_rows_opened"] != "false" for row in rows):
        raise RuntimeError("CROT001 control occurrence rows must remain unopened")
    return rows


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = _check_preconditions()
    admitted = []
    excluded = []
    for row in rows:
        control_id = row["control_id"]
        name = row["scientific_name"]
        request = SnapshotTaxonomyRequest("CROT001_" + control_id, "x", name, "Plantae")
        try:
            match = _read_json(
                GBIF_CURRENT_SPECIES_MATCH_ENDPOINT + "?" + urlencode(build_current_species_match_params(request))
            )
            usage = match.get("usage")
            if not isinstance(usage, Mapping) or usage.get("key") is None:
                raise ValueError("current match payload has no usage key")
            direct = _read_json(
                GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=str(usage["key"]))
            )
            result = parse_current_direct_taxonomy_resolution(
                request=request, match_payload=match, usage_payload=direct
            )
            admitted.append({"control_id": control_id, **asdict(result)})
        except Exception as exc:
            excluded.append(
                {
                    "control_id": control_id,
                    "scientific_name": name,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "rescue_attempted": False,
                }
            )

    status = "control_current_taxonomy_preflight_passed" if len(admitted) >= MIN_CONTROLS else "unresolved_controls_taxonomy"
    outcome = {
        "result_version": "product_b_v7_3_crot001_control_current_taxonomy_v0.1",
        "pair_id": "CROT001",
        "status": status,
        "declared_control_count": 8,
        "minimum_required_control_count": MIN_CONTROLS,
        "admitted_count": len(admitted),
        "admitted": admitted,
        "excluded": excluded,
        "synonym_rescue_allowed": False,
        "replacement_after_taxonomy_allowed": False,
        "snapshot_taxonomy_identity_rows_opened": False,
        "snapshot_occurrence_rows_opened": False,
        "snapshot_occurrence_counts_opened": False,
        "live_occurrence_search_used": False,
    }
    OUTPUT.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status == "control_current_taxonomy_preflight_passed" else 1


if __name__ == "__main__":
    sys.exit(main())
