#!/usr/bin/env python3
"""Resolve the frozen 72-taxon successor calibration panel in current GBIF taxonomy.

Taxonomy-only stage. Candidate names and the 84-name freshness firewall were frozen
before this script was authorized. No occurrence endpoint/count/coordinate, paired
Layer-1 outcome, environmental value, or process intervention is read here.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import csv
import hashlib
import json
from pathlib import Path
import time
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
PANEL = ROOT / "registry/product_b_same_target_successor_calibration_candidates_v0_1.csv"
CONSUMED = ROOT / "registry/product_b_same_target_prior_consumed_taxa_v0_1.csv"
CONTRACT = ROOT / "config/product_b_same_target_successor_calibration_contract_v0_1.json"
OUTPUT = ROOT / "results/product_b_same_target_successor_current_taxonomy_v0_1.json"
USER_AGENT = "zuizui0223-284b-successor-taxonomy/0.1"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _read_json(url: str, timeout: float = 60.0) -> Mapping[str, object]:
    last: Exception | None = None
    for attempt in range(4):
        try:
            req = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}, method="GET")
            with urlopen(req, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, Mapping):
                raise ValueError("taxonomy response must be a JSON object")
            return payload
        except Exception as exc:
            last = exc
            if attempt < 3:
                time.sleep(0.5 * (2**attempt))
    assert last is not None
    raise last


def _load_and_validate_panel() -> list[dict[str, str]]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("contract_version") != "product_b_same_target_successor_calibration_v0.1":
        raise RuntimeError("successor calibration contract version mismatch")
    if _git_blob_sha(PANEL) != contract["candidate_registry_git_blob_sha"]:
        raise RuntimeError("successor candidate registry blob SHA mismatch")
    if _git_blob_sha(CONSUMED) != contract["freshness_firewall"]["local_prior_consumed_registry_git_blob_sha"]:
        raise RuntimeError("prior-consumed firewall blob SHA mismatch")
    with PANEL.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    with CONSUMED.open(newline="", encoding="utf-8") as handle:
        consumed = list(csv.DictReader(handle))
    names = [r["scientific_name"].strip() for r in rows]
    prior = {r["scientific_name"].strip() for r in consumed}
    if len(rows) != 72 or len(set(names)) != 72:
        raise RuntimeError("successor panel must contain 72 unique taxa")
    if len(consumed) != 84 or len(prior) != 84:
        raise RuntimeError("prior-consumed firewall must contain 84 unique taxa")
    overlap = sorted(set(names) & prior)
    if overlap:
        raise RuntimeError(f"successor freshness firewall overlap: {overlap}")
    strata: dict[str, list[int]] = {}
    for row in rows:
        strata.setdefault(row["validation_stratum"], []).append(int(row["candidate_rank"]))
    if len(strata) != 12 or any(sorted(v) != [1,2,3,4,5,6] for v in strata.values()):
        raise RuntimeError("successor panel must be 12 strata x six frozen candidates")
    return rows


def _resolve(index: int, row: dict[str, str]) -> dict[str, object]:
    name = row["scientific_name"].strip()
    request = SnapshotTaxonomyRequest(
        pair_id=f"SUCCESSOR_CAL{index:03d}", partner="x", scientific_name=name, kingdom="Plantae"
    )
    match = _read_json(GBIF_CURRENT_SPECIES_MATCH_ENDPOINT + "?" + urlencode(build_current_species_match_params(request)))
    usage = match.get("usage")
    diagnostics = match.get("diagnostics")
    if not isinstance(usage, Mapping) or usage.get("key") is None:
        result: dict[str, object] = {"requested_name": name, "state": "successor_current_taxonomy_unresolved_no_usage", "diagnostics": diagnostics}
    else:
        usage_payload = _read_json(GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=str(usage["key"])))
        try:
            resolution = parse_current_direct_taxonomy_resolution(request=request, match_payload=match, usage_payload=usage_payload)
            payload = asdict(resolution)
            result = {
                "requested_name": name,
                "state": "successor_current_taxonomy_resolved_exact_accepted_species",
                "match_type": payload["match_type"],
                "confidence": payload["confidence"],
                "usage_key": payload["usage_key"],
                "accepted_key": payload["direct_usage_key"],
                "accepted_name": payload["direct_usage_canonical_name"],
            }
        except ValueError as exc:
            result = {
                "requested_name": name,
                "state": "successor_current_taxonomy_unresolved_direct_contract",
                "reason": str(exc),
                "diagnostics": dict(diagnostics) if isinstance(diagnostics, Mapping) else diagnostics,
            }
    result["validation_stratum"] = row["validation_stratum"]
    result["candidate_rank"] = int(row["candidate_rank"])
    return result


def _safe_resolve(args: tuple[int, dict[str, str]]) -> dict[str, object]:
    index, row = args
    try:
        return _resolve(index, row)
    except Exception as exc:
        return {
            "requested_name": row["scientific_name"].strip(),
            "validation_stratum": row["validation_stratum"],
            "candidate_rank": int(row["candidate_rank"]),
            "state": "successor_current_taxonomy_unresolved_transport_or_parse",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }


def main() -> int:
    rows = _load_and_validate_panel()
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(_safe_resolve, list(enumerate(rows, start=1))))
    resolved = sum(r["state"] == "successor_current_taxonomy_resolved_exact_accepted_species" for r in results)
    outcome = {
        "result_version": "product_b_same_target_successor_current_taxonomy_v0.1",
        "panel_size": 72,
        "resolved_exact_accepted_species": int(resolved),
        "unresolved_current_taxonomy": int(72-resolved),
        "all_72_entered": True,
        "prior_84_exact_name_overlap": 0,
        "taxa_replaced": False,
        "occurrence_endpoint_called": False,
        "occurrence_counts_opened": False,
        "coordinates_opened": False,
        "snapshot_taxonomy_opened": False,
        "paired_discordance_opened": False,
        "process_intervention_outcomes_read": False,
        "sampling_authorized": False,
        "resolutions": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({k:outcome[k] for k in ("result_version","panel_size","resolved_exact_accepted_species","unresolved_current_taxonomy","prior_84_exact_name_overlap")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
