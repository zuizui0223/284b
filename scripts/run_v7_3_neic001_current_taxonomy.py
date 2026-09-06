#!/usr/bin/env python3
"""Resolve NEIC001 focal taxa against current GBIF taxonomy only."""
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
PAIR = ROOT / "registry/product_b_v7_3_neic001_pair_registry_v0_1.csv"
ADMISSION = ROOT / "config/product_b_v7_3_neic001_admission_v0_1.json"
OUTPUT = ROOT / "artifacts/product_b_v7_3_neic001_current_taxonomy.json"
REQUESTS = (
    SnapshotTaxonomyRequest("NEIC001", "x", "Eichhornia crassipes", "Plantae"),
    SnapshotTaxonomyRequest("NEIC001", "y", "Neochetina eichhorniae", "Animalia"),
)


def _read_json(url: str, timeout: float = 60.0) -> Mapping[str, object]:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "zuizui0223-284b-product-b-v7-3-neic-taxonomy/0.1"},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def _check_preconditions() -> None:
    snapshot_contract = json.loads(SNAPSHOT_CONTRACT.read_text(encoding="utf-8"))
    snapshot_decision = evaluate_snapshot_contract(snapshot_contract)
    if not snapshot_decision.passed:
        raise RuntimeError("invalid frozen snapshot contract: " + ",".join(snapshot_decision.reasons))
    if snapshot_contract["occurrence_row_reads_allowed"]:
        raise RuntimeError("global snapshot occurrence rows must remain closed")

    identity_contract = json.loads(IDENTITY_CONTRACT.read_text(encoding="utf-8"))
    identity_errors = evaluate_v7_3_contract(identity_contract)
    if identity_errors:
        raise RuntimeError("invalid v7.3 identity contract: " + ",".join(identity_errors))

    with PAIR.open("r", encoding="utf-8", newline="") as handle:
        row = list(csv.DictReader(handle))[0]
    if row["current_taxonomy_state"] != "taxonomy_unopened":
        raise RuntimeError("NEIC001 current taxonomy boundary was already crossed")
    if row["snapshot_taxonomy_identity_state"] != "snapshot_taxonomy_identity_unopened":
        raise RuntimeError("NEIC001 snapshot taxonomy identity must remain unopened")
    if row["snapshot_occurrence_rows_opened"] != "false":
        raise RuntimeError("NEIC001 snapshot occurrence rows must remain unopened")

    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    for field in (
        "current_taxonomy_access_started",
        "snapshot_taxonomy_identity_access_started",
        "snapshot_occurrence_row_access_started",
        "model_fit_reads_started",
        "invariant_reads_started",
        "process_knockout_reads_started",
    ):
        if admission[field]:
            raise RuntimeError("NEIC001 admission is not in frozen pre-taxonomy state: " + field)
    if admission["engineering_only"] is not True or admission["confirmatory_promotion_allowed"] is not False:
        raise RuntimeError("NEIC001 engineering-only boundary changed")


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _check_preconditions()
    resolutions = []
    errors = []
    for request in REQUESTS:
        try:
            match = _read_json(
                GBIF_CURRENT_SPECIES_MATCH_ENDPOINT + "?" + urlencode(build_current_species_match_params(request))
            )
            usage = match.get("usage")
            if not isinstance(usage, Mapping) or usage.get("key") is None:
                raise ValueError("current match payload has no usage key")
            usage_payload = _read_json(
                GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=str(usage["key"]))
            )
            resolutions.append(
                asdict(
                    parse_current_direct_taxonomy_resolution(
                        request=request,
                        match_payload=match,
                        usage_payload=usage_payload,
                    )
                )
            )
        except Exception as exc:
            errors.append(
                {
                    "partner": request.partner,
                    "requested_name": request.scientific_name,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )

    status = (
        "resolved_direct_exact_current_taxonomy"
        if len(resolutions) == 2 and not errors
        else "unresolved_current_taxonomy"
    )
    outcome = {
        "result_version": "product_b_v7_3_neic001_current_taxonomy_v0.1",
        "pair_id": "NEIC001",
        "status": status,
        "taxonomy_system": "GBIF current default taxonomy; no legacy checklistKey",
        "resolutions": resolutions,
        "errors": errors,
        "engineering_only": True,
        "confirmatory_promotion_allowed": False,
        "snapshot_taxonomy_identity_rows_opened": False,
        "snapshot_occurrence_rows_opened": False,
        "snapshot_occurrence_counts_opened": False,
        "live_occurrence_search_used": False,
    }
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status == "resolved_direct_exact_current_taxonomy" else 1


if __name__ == "__main__":
    sys.exit(main())
