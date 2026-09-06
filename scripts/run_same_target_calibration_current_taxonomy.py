#!/usr/bin/env python3
"""Resolve the frozen 36-taxon same-target calibration panel against current GBIF taxonomy.

This gate is taxonomy-only. It must not call occurrence endpoints, inspect occurrence
counts, coordinates, maps, or paired-discordance outcomes. All 36 taxa enter because
the panel was frozen before this audit.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
from typing import Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "registry/product_b_same_target_source_calibration_taxa_v0_1.csv"
OUTPUT = ROOT / "results/product_b_same_target_source_current_taxonomy_v0_1.json"
MATCH_ENDPOINT = "https://api.gbif.org/v1/species/match"
USAGE_ENDPOINT = "https://api.gbif.org/v1/species/{key}"
USER_AGENT = "zuizui0223-284b-same-target-calibration-taxonomy/0.1"


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


def _resolve(name: str) -> dict[str, object]:
    match = _read_json(MATCH_ENDPOINT + "?" + urlencode({"name": name, "kingdom": "Plantae"}))
    usage = match.get("usage")
    if not isinstance(usage, Mapping) or usage.get("key") is None:
        return {
            "requested_name": name,
            "state": "unresolved_current_taxonomy_no_usage",
            "match_type": match.get("matchType"),
            "confidence": match.get("confidence"),
            "diagnostics": match.get("diagnostics"),
        }

    usage_key = str(usage["key"])
    usage_payload = _read_json(USAGE_ENDPOINT.format(key=usage_key))
    accepted_usage = match.get("acceptedUsage")
    accepted_key = None
    accepted_payload: Mapping[str, object] | None = None
    if isinstance(accepted_usage, Mapping) and accepted_usage.get("key") is not None:
        accepted_key = str(accepted_usage["key"])
        accepted_payload = _read_json(USAGE_ENDPOINT.format(key=accepted_key))
    elif str(usage_payload.get("taxonomicStatus", "")).upper() == "ACCEPTED":
        accepted_key = usage_key
        accepted_payload = usage_payload
    elif usage_payload.get("acceptedKey") is not None:
        accepted_key = str(usage_payload["acceptedKey"])
        accepted_payload = _read_json(USAGE_ENDPOINT.format(key=accepted_key))

    match_type = str(match.get("matchType", ""))
    confidence = match.get("confidence")
    rank = str(usage_payload.get("rank", usage.get("rank", ""))).upper()
    status = str(usage_payload.get("taxonomicStatus", usage.get("status", ""))).upper()
    accepted_name = ""
    if accepted_payload is not None:
        accepted_name = str(
            accepted_payload.get("canonicalName")
            or accepted_payload.get("scientificName")
            or ""
        ).strip()

    direct_species = match_type == "EXACT" and rank in {"SPECIES", "SUBSPECIES", "VARIETY", "FORM"}
    resolved = direct_species and accepted_key is not None and bool(accepted_name)
    state = "resolved_current_taxonomy" if resolved else "unresolved_current_taxonomy"

    admissible_names: list[str] = []
    for candidate in (name, accepted_name):
        candidate = str(candidate).strip()
        if candidate and candidate not in admissible_names:
            admissible_names.append(candidate)

    return {
        "requested_name": name,
        "state": state,
        "match_type": match_type,
        "confidence": confidence,
        "usage_key": usage_key,
        "usage_rank": rank,
        "usage_taxonomic_status": status,
        "accepted_key": accepted_key,
        "accepted_name": accepted_name,
        "snapshot_admissible_species_names": admissible_names,
        "diagnostics": match.get("diagnostics"),
    }


def main() -> int:
    rows = _load_panel()
    results: list[dict[str, object]] = []
    for row in rows:
        name = row["scientific_name"].strip()
        try:
            resolution = _resolve(name)
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
        "result_version": "product_b_same_target_source_current_taxonomy_v0.1",
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
        "resolutions": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    # Taxonomy ambiguity is a scientific outcome, not a workflow failure. The
    # next gate will include only prospectively resolved taxa and retain all
    # unresolved taxa as terminal for this calibration pass.
    return 0


if __name__ == "__main__":
    sys.exit(main())
