#!/usr/bin/env python3
"""Resolve the frozen 36-taxon same-target calibration panel against current GBIF taxonomy.

This gate is taxonomy-only. It must not call occurrence endpoints, inspect occurrence
counts, coordinates, maps, or paired-discordance outcomes. All 36 taxa enter because
the panel was frozen before this audit.
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
PANEL = ROOT / "registry/product_b_same_target_source_calibration_taxa_v0_1.csv"
OUTPUT = ROOT / "results/product_b_same_target_source_current_taxonomy_v0_1.json"
USER_AGENT = "zuizui0223-284b-same-target-calibration-taxonomy/0.2"


def _read_json(url: str, timeout: float = 60.0) -> Mapping[str, object]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}, method="GET")
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def _load_panel() -> list[dict[str, str]]:
    with PANEL.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 36:
        raise RuntimeError(f"frozen calibration panel must contain 36 taxa, found {len(rows)}")
    if any(row.get("snapshot_taxonomy_state") != "unopened" for row in rows):
        raise RuntimeError("snapshot taxonomy was already opened for one or more calibration taxa")
    if any(row.get("mode_sampling_state") != "unopened" for row in rows):
        raise RuntimeError("mode sampling was already opened for one or more calibration taxa")
    if any(row.get("paired_discordance_state") != "unopened" for row in rows):
        raise RuntimeError("paired discordance was already opened for one or more calibration taxa")
    return rows


def _resolve(index: int, name: str) -> dict[str, object]:
    request = SnapshotTaxonomyRequest(
        pair_id=f"CAL{index:03d}",
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
            "state": "unresolved_current_taxonomy_no_usage",
            "diagnostics": diagnostics,
            "snapshot_admissible_species_names": [name],
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
        # Synonyms or non-direct concepts stop here. We do not add new names after
        # seeing taxonomy outcomes in this calibration pass.
        accepted_usage = match.get("acceptedUsage")
        accepted_name = ""
        accepted_key = None
        if isinstance(accepted_usage, Mapping):
            accepted_name = str(accepted_usage.get("canonicalName") or accepted_usage.get("name") or "").strip()
            if accepted_usage.get("key") is not None:
                accepted_key = str(accepted_usage["key"])
        return {
            "requested_name": name,
            "state": "unresolved_current_taxonomy_direct_contract",
            "reason": str(exc),
            "usage": dict(usage),
            "accepted_usage": dict(accepted_usage) if isinstance(accepted_usage, Mapping) else None,
            "accepted_name_seen_but_not_admitted": accepted_name,
            "accepted_key_seen_but_not_admitted": accepted_key,
            "diagnostics": dict(diagnostics) if isinstance(diagnostics, Mapping) else diagnostics,
            "snapshot_admissible_species_names": [name],
        }

    payload = asdict(resolution)
    return {
        "requested_name": name,
        "state": "resolved_current_taxonomy",
        "match_type": payload["match_type"],
        "confidence": payload["confidence"],
        "usage_key": payload["usage_key"],
        "usage_rank": payload["rank"],
        "usage_taxonomic_status": payload["status"],
        "accepted_key": payload["direct_usage_key"],
        "accepted_name": payload["direct_usage_canonical_name"],
        "snapshot_admissible_species_names": [payload["direct_usage_canonical_name"]],
        "diagnostics": diagnostics,
    }


def main() -> int:
    rows = _load_panel()
    results: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        name = row["scientific_name"].strip()
        try:
            resolution = _resolve(index, name)
        except Exception as exc:
            resolution = {
                "requested_name": name,
                "state": "unresolved_current_taxonomy_transport_or_parse",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "snapshot_admissible_species_names": [name],
            }
        resolution.update(
            {
                "validation_stratum": row["validation_stratum"],
                "candidate_rank": int(row["candidate_rank"]),
            }
        )
        results.append(resolution)

    resolved = sum(item["state"] == "resolved_current_taxonomy" for item in results)
    unresolved = len(results) - resolved
    outcome = {
        "result_version": "product_b_same_target_source_current_taxonomy_v0.2",
        "taxonomy_endpoint": GBIF_CURRENT_SPECIES_MATCH_ENDPOINT,
        "panel_size": len(results),
        "resolved_taxa": resolved,
        "unresolved_taxa": unresolved,
        "all_36_entered": True,
        "selection_used_occurrence_information": False,
        "occurrence_endpoint_called": False,
        "occurrence_counts_opened": False,
        "coordinates_opened": False,
        "paired_discordance_opened": False,
        "sampling_authorized": False,
        "previous_v0_1_all_unresolved_was_parser_endpoint_mismatch": True,
        "resolutions": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
