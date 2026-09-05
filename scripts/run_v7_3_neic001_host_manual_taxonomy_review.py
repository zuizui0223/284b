#!/usr/bin/env python3
"""Verify the NEIC001 Eichhornia -> Pontederia current-taxonomy bridge only.

No snapshot taxonomy tuples, occurrence rows, occurrence counts, model outputs, or
invariant outcomes are read here.  The accepted name is predeclared from an
independent nomenclatural source before this current-GBIF review.
"""
from __future__ import annotations

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
)
from product_b_v7_2.snapshot_transport import evaluate_snapshot_contract
from product_b_v7_3.taxonomy_identity import evaluate_v7_3_contract

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_CONTRACT = ROOT / "config/product_b_v7_2_snapshot_transport_contract_v0_1.json"
IDENTITY_CONTRACT = ROOT / "config/product_b_v7_3_snapshot_taxonomy_identity_contract_v0_1.json"
REVIEW = ROOT / "config/product_b_v7_3_neic001_host_manual_taxonomy_review_v0_1.json"
ADMISSION = ROOT / "config/product_b_v7_3_neic001_admission_v0_1.json"
PAIR = ROOT / "registry/product_b_v7_3_neic001_pair_registry_v0_1.csv"
OUTPUT = ROOT / "artifacts/product_b_v7_3_neic001_host_manual_taxonomy_review.json"


def _read_json(url: str, timeout: float = 60.0) -> Mapping[str, object]:
    req = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "zuizui0223-284b-product-b-v7-3-neic-host-review/0.1"},
        method="GET",
    )
    with urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be an object")
    return payload


def _text(payload: Mapping[str, object], *fields: str) -> str:
    for field in fields:
        value = payload.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _summary(payload: Mapping[str, object]) -> dict[str, object]:
    return {
        "key": str(payload.get("key", "")).strip(),
        "canonical_name": _text(payload, "canonicalName", "canonicalNameWithMarker"),
        "scientific_name": _text(payload, "scientificName"),
        "rank": _text(payload, "rank").upper(),
        "status": _text(payload, "taxonomicStatus", "status").upper(),
        "accepted_key": str(payload.get("acceptedKey", payload.get("acceptedTaxonKey", ""))).strip(),
    }


def _preconditions(review: Mapping[str, object]) -> None:
    snapshot = json.loads(SNAPSHOT_CONTRACT.read_text(encoding="utf-8"))
    decision = evaluate_snapshot_contract(snapshot)
    if not decision.passed:
        raise RuntimeError("invalid frozen snapshot contract: " + ",".join(decision.reasons))
    if snapshot["occurrence_row_reads_allowed"]:
        raise RuntimeError("snapshot occurrence rows must remain closed")
    identity = json.loads(IDENTITY_CONTRACT.read_text(encoding="utf-8"))
    errors = evaluate_v7_3_contract(identity)
    if errors:
        raise RuntimeError("invalid v7.3 identity contract: " + ",".join(errors))
    if identity["taxonomy_identity_reads_allowed"]:
        raise RuntimeError("snapshot taxonomy identity rows must remain closed")

    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    if admission["current_taxonomy_state"] != "unresolved_host_synonym_bridge_pending":
        raise RuntimeError("NEIC001 is not in the frozen host-bridge-pending state")
    if admission["snapshot_taxonomy_identity_access_started"] or admission["snapshot_occurrence_row_access_started"]:
        raise RuntimeError("downstream snapshot layers must remain unopened")

    with PAIR.open("r", encoding="utf-8", newline="") as handle:
        row = list(csv.DictReader(handle))[0]
    if row["current_taxonomy_state"] != "unresolved_host_synonym_bridge_pending":
        raise RuntimeError("pair registry is not bridge-pending")
    if row["snapshot_taxonomy_identity_state"] != "snapshot_taxonomy_identity_unopened":
        raise RuntimeError("snapshot taxonomy identity boundary already crossed")
    if row["snapshot_occurrence_rows_opened"] != "false":
        raise RuntimeError("snapshot occurrence rows already opened")

    if review.get("requested_biological_name") != "Eichhornia crassipes":
        raise RuntimeError("requested biological name changed")
    if review.get("predeclared_accepted_name") != "Pontederia crassipes":
        raise RuntimeError("predeclared accepted name changed")
    if review.get("occurrence_information_used_to_choose_accepted_name") is not False:
        raise RuntimeError("accepted name must be occurrence-blind")


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    _preconditions(review)

    request = SnapshotTaxonomyRequest("NEIC001", "x", "Eichhornia crassipes", "Plantae")
    match = _read_json(
        GBIF_CURRENT_SPECIES_MATCH_ENDPOINT + "?" + urlencode(build_current_species_match_params(request))
    )
    usage_obj = match.get("usage")
    diagnostics = match.get("diagnostics")
    if not isinstance(usage_obj, Mapping) or not isinstance(diagnostics, Mapping):
        raise ValueError("current match must contain usage and diagnostics objects")

    usage_key = str(usage_obj.get("key", "")).strip()
    if not usage_key:
        raise ValueError("matched usage key is blank")
    matched_direct = _summary(_read_json(GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=usage_key)))
    accepted_obj = match.get("acceptedUsage")
    accepted_key_from_match = ""
    accepted_name_from_match = ""
    if isinstance(accepted_obj, Mapping):
        accepted_key_from_match = str(accepted_obj.get("key", "")).strip()
        accepted_name_from_match = _text(accepted_obj, "canonicalName", "name")

    accepted_key = str(matched_direct.get("accepted_key", "")).strip() or accepted_key_from_match
    if not accepted_key:
        raise ValueError("nonaccepted current usage has no direct accepted key")
    accepted_direct = _summary(_read_json(GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=accepted_key)))

    reasons: list[str] = []
    match_type = _text(diagnostics, "matchType").upper()
    confidence = diagnostics.get("confidence") if isinstance(diagnostics.get("confidence"), int) else None
    if match_type != "EXACT":
        reasons.append("match_not_exact")
    if _text(usage_obj, "rank").upper() != "SPECIES":
        reasons.append("match_usage_not_species")
    if _text(usage_obj, "canonicalName", "name").casefold() != "Eichhornia crassipes".casefold():
        reasons.append("match_canonical_name_mismatch")
    if matched_direct["key"] != usage_key:
        reasons.append("direct_synonym_usage_key_mismatch")
    if matched_direct["rank"] != "SPECIES":
        reasons.append("direct_synonym_usage_not_species")
    if matched_direct["status"] == "ACCEPTED":
        reasons.append("requested_name_unexpectedly_accepted")
    if matched_direct["accepted_key"] != accepted_key:
        reasons.append("direct_synonym_usage_does_not_point_to_accepted_key")
    if accepted_key_from_match and accepted_key_from_match != accepted_key:
        reasons.append("match_accepted_usage_key_disagrees_with_direct_usage")
    if accepted_name_from_match and accepted_name_from_match.casefold() != "Pontederia crassipes".casefold():
        reasons.append("match_accepted_name_not_predeclared_name")
    if accepted_direct["key"] != accepted_key:
        reasons.append("accepted_usage_key_mismatch")
    if accepted_direct["canonical_name"].casefold() != "Pontederia crassipes".casefold():
        reasons.append("accepted_canonical_name_not_predeclared_name")
    if accepted_direct["rank"] != "SPECIES":
        reasons.append("accepted_usage_not_species")
    if accepted_direct["status"] != "ACCEPTED":
        reasons.append("accepted_usage_not_accepted")

    state = "resolved_manual_direct_homotypic_synonym_bridge" if not reasons else "unresolved_taxonomy"
    outcome = {
        "result_version": "product_b_v7_3_neic001_host_manual_taxonomy_review_v0.1",
        "pair_id": "NEIC001",
        "partner": "x",
        "requested_name": "Eichhornia crassipes",
        "predeclared_accepted_name": "Pontederia crassipes",
        "state": state,
        "match_type": match_type,
        "confidence": confidence,
        "match_usage": dict(usage_obj),
        "matched_direct_usage": matched_direct,
        "match_accepted_usage": dict(accepted_obj) if isinstance(accepted_obj, Mapping) else None,
        "accepted_direct_usage": accepted_direct,
        "relation_by_direct_accepted_key": matched_direct["accepted_key"] == accepted_key,
        "external_nomenclatural_relation": "Kew POWO 2026 homotypic synonym",
        "reasons": reasons,
        "snapshot_taxonomy_identity_rows_opened": False,
        "snapshot_occurrence_rows_opened": False,
        "snapshot_occurrence_counts_opened": False,
        "live_occurrence_search_used": False,
    }
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not reasons else 1


if __name__ == "__main__":
    sys.exit(main())
