#!/usr/bin/env python3
"""Resolve the fresh 36-taxon paired-calibration panel against current GBIF taxonomy.

This is taxonomy-only engineering. It does not call occurrence endpoints, inspect
occurrence counts/coordinates, read current Layer-1 paired outcomes, or use
process interventions. All 36 predeclared candidates enter and none is replaced.
"""
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

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "registry/product_b_same_target_fresh_calibration_candidates_v0_1.csv"
CONTRACT = ROOT / "config/product_b_same_target_fresh_calibration_contract_v0_1.json"
OUTPUT = ROOT / "results/product_b_same_target_fresh_current_taxonomy_v0_1.json"
USER_AGENT = "zuizui0223-284b-fresh-same-target-taxonomy/0.1"


def _read_json(url: str, timeout: float = 60.0) -> Mapping[str, object]:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def _load_panel() -> list[dict[str, str]]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    with PANEL.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 36 or len({row["scientific_name"] for row in rows}) != 36:
        raise RuntimeError("fresh calibration registry must contain exactly 36 unique taxa")
    if int(contract["candidate_count"]) != 36:
        raise RuntimeError("fresh calibration contract denominator drifted")
    if contract["panel_rule"]["use_all_36_predeclared_candidates"] is not True:
        raise RuntimeError("fresh calibration contract no longer requires all 36 candidates")
    if contract["information_barrier"]["current_12_taxon_layer1_paired_D_may_not_select_taxa"] is not True:
        raise RuntimeError("current Layer-1 outcome firewall is not closed")
    strata: dict[str, list[int]] = {}
    for row in rows:
        strata.setdefault(row["validation_stratum"], []).append(int(row["candidate_rank"]))
    if len(strata) != 12 or any(sorted(values) != [1, 2, 3] for values in strata.values()):
        raise RuntimeError("fresh 12-stratum x rank1-3 panel structure drifted")
    return rows


def _resolve(index: int, name: str) -> dict[str, object]:
    request = SnapshotTaxonomyRequest(
        pair_id=f"FRESH_CAL{index:03d}",
        partner="x",
        scientific_name=name,
        kingdom="Plantae",
    )
    match = _read_json(
        GBIF_CURRENT_SPECIES_MATCH_ENDPOINT
        + "?"
        + urlencode(build_current_species_match_params(request))
    )
    usage = match.get("usage")
    diagnostics = match.get("diagnostics")
    if not isinstance(usage, Mapping) or usage.get("key") is None:
        return {
            "requested_name": name,
            "state": "fresh_current_taxonomy_unresolved_no_usage",
            "diagnostics": diagnostics,
        }

    usage_payload = _read_json(
        GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=str(usage["key"]))
    )
    try:
        resolution = parse_current_direct_taxonomy_resolution(
            request=request,
            match_payload=match,
            usage_payload=usage_payload,
        )
    except ValueError as exc:
        accepted_usage = match.get("acceptedUsage")
        return {
            "requested_name": name,
            "state": "fresh_current_taxonomy_unresolved_direct_contract",
            "reason": str(exc),
            "usage": dict(usage),
            "accepted_usage_seen_but_not_admitted": (
                dict(accepted_usage) if isinstance(accepted_usage, Mapping) else None
            ),
            "diagnostics": dict(diagnostics) if isinstance(diagnostics, Mapping) else diagnostics,
        }

    payload = asdict(resolution)
    accepted_name = str(payload["direct_usage_canonical_name"]).strip()
    if accepted_name.casefold() != name.strip().casefold():
        return {
            "requested_name": name,
            "state": "fresh_current_taxonomy_unresolved_name_changed",
            "resolved_direct_usage_name_seen_but_not_admitted": accepted_name,
            "resolved_direct_usage_key_seen_but_not_admitted": payload["direct_usage_key"],
            "diagnostics": diagnostics,
        }
    return {
        "requested_name": name,
        "state": "fresh_current_taxonomy_resolved_exact_accepted_species",
        "match_type": payload["match_type"],
        "confidence": payload["confidence"],
        "usage_key": payload["usage_key"],
        "usage_rank": payload["rank"],
        "usage_taxonomic_status": payload["status"],
        "accepted_key": payload["direct_usage_key"],
        "accepted_name": accepted_name,
        "diagnostics": diagnostics,
    }


def main() -> int:
    rows = _load_panel()
    results: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        name = row["scientific_name"].strip()
        try:
            result = _resolve(index, name)
        except Exception as exc:
            result = {
                "requested_name": name,
                "state": "fresh_current_taxonomy_unresolved_transport_or_parse",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
        result.update(
            {
                "validation_stratum": row["validation_stratum"],
                "candidate_rank": int(row["candidate_rank"]),
            }
        )
        results.append(result)

    resolved = sum(
        item["state"] == "fresh_current_taxonomy_resolved_exact_accepted_species"
        for item in results
    )
    outcome = {
        "result_version": "product_b_same_target_fresh_current_taxonomy_v0.1",
        "panel_size": 36,
        "resolved_exact_accepted_species": int(resolved),
        "unresolved_current_taxonomy": int(36 - resolved),
        "all_36_entered": True,
        "taxa_replaced": False,
        "selection_used_current_layer1_paired_outcomes": False,
        "selection_used_process_intervention_outcomes": False,
        "occurrence_endpoint_called": False,
        "occurrence_counts_opened": False,
        "coordinates_opened": False,
        "snapshot_taxonomy_opened": False,
        "paired_discordance_opened": False,
        "sampling_authorized": False,
        "resolutions": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
