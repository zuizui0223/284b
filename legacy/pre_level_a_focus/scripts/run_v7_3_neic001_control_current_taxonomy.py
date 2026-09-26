#!/usr/bin/env python3
"""Resolve the frozen NEIC001 control pool against current GBIF taxonomy only.

This stage is permitted only after focal current taxonomy and the exact frozen-pool
interaction screen pass. It reads no snapshot taxonomy tuples or occurrence rows.
Only direct exact accepted species are admitted; no synonym rescue or replacement
control is allowed.
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
from product_b_v7_2.snapshot_transport import evaluate_snapshot_contract
from product_b_v7_3.pair_admission import ReplacementHostInteractionEvidence, evaluate_replacement_host_interaction_screen
from product_b_v7_3.taxonomy_identity import evaluate_v7_3_contract

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_CONTRACT = ROOT / "config/product_b_v7_2_snapshot_transport_contract_v0_1.json"
IDENTITY_CONTRACT = ROOT / "config/product_b_v7_3_snapshot_taxonomy_identity_contract_v0_1.json"
ADMISSION = ROOT / "config/product_b_v7_3_neic001_admission_v0_1.json"
PAIR = ROOT / "registry/product_b_v7_3_neic001_pair_registry_v0_1.csv"
POOL = ROOT / "registry/product_b_v7_3_neic001_control_pool_v0_1.csv"
INTERACTION = ROOT / "config/product_b_v7_3_neic001_control_interaction_evidence_v0_1.json"
INTERACTION_RESULT = ROOT / "results/product_b_v7_3_neic001_control_interaction_screen_v0_1.json"
OUTPUT = ROOT / "artifacts/product_b_v7_3_neic001_control_current_taxonomy.json"
MIN_CONTROLS = 5


def _read_json(url: str, timeout: float = 60.0) -> Mapping[str, object]:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "zuizui0223-284b-product-b-v7-3-neic-controls/0.1"},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("GBIF taxonomy response must be a JSON object")
    return payload


def _check_preconditions() -> list[dict[str, str]]:
    snapshot = json.loads(SNAPSHOT_CONTRACT.read_text(encoding="utf-8"))
    snapshot_decision = evaluate_snapshot_contract(snapshot)
    if not snapshot_decision.passed or snapshot["occurrence_row_reads_allowed"]:
        raise RuntimeError("snapshot occurrence contract must remain closed")
    identity = json.loads(IDENTITY_CONTRACT.read_text(encoding="utf-8"))
    errors = evaluate_v7_3_contract(identity)
    if errors:
        raise RuntimeError("invalid v7.3 identity contract: " + ",".join(errors))

    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    if admission["current_taxonomy_state"] != "resolved_y_direct_exact_x_manual_homotypic_synonym_bridge":
        raise RuntimeError("NEIC001 focal current taxonomy is not fully resolved")
    if admission["control_interaction_screen_state"] != "passed_exact_frozen_pool":
        raise RuntimeError("NEIC001 frozen control interaction screen has not passed")
    if admission["snapshot_taxonomy_identity_access_started"] or admission["snapshot_occurrence_row_access_started"]:
        raise RuntimeError("snapshot layers must remain unopened")

    interaction = json.loads(INTERACTION.read_text(encoding="utf-8"))
    evidence = tuple(
        ReplacementHostInteractionEvidence(
            control_taxon=item["control_taxon"],
            screen_completed=item["screen_completed"],
            dependent_uses_control_as_host=item["dependent_uses_control_as_host"],
        )
        for item in interaction["controls"]
    )
    decision = evaluate_replacement_host_interaction_screen(
        predeclared_control_taxa=admission["predeclared_control_taxa"], evidence=evidence
    )
    if not decision.passed or decision.screened_control_count != 8:
        raise RuntimeError("NEIC001 frozen control interaction evidence is not admissible")
    interaction_result = json.loads(INTERACTION_RESULT.read_text(encoding="utf-8"))
    if interaction_result["status"] != "control_interaction_screen_passed":
        raise RuntimeError("NEIC001 interaction result is not passed")

    with PAIR.open("r", encoding="utf-8", newline="") as handle:
        pair = list(csv.DictReader(handle))[0]
    if pair["current_taxonomy_state"] != "resolved_y_direct_exact_x_manual_homotypic_synonym_bridge":
        raise RuntimeError("pair registry current taxonomy is not resolved")
    if pair["snapshot_taxonomy_identity_state"] != "snapshot_taxonomy_identity_unopened":
        raise RuntimeError("snapshot taxonomy identity already opened")
    if pair["snapshot_occurrence_rows_opened"] != "false":
        raise RuntimeError("snapshot occurrence rows already opened")

    with POOL.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 8:
        raise RuntimeError("NEIC001 control pool must remain exactly eight taxa")
    if {row["scientific_name"] for row in rows} != set(admission["predeclared_control_taxa"]):
        raise RuntimeError("NEIC001 control pool differs from frozen admission declaration")
    if any(row["interaction_screen_state"] != "passed_complete_life_cycle_nonhost_screen" for row in rows):
        raise RuntimeError("every frozen control must pass the interaction screen")
    if any(row["current_taxonomy_state"] != "taxonomy_unopened" for row in rows):
        raise RuntimeError("NEIC001 control current taxonomy was already opened")
    if any(row["snapshot_taxonomy_identity_state"] != "snapshot_taxonomy_identity_unopened" for row in rows):
        raise RuntimeError("NEIC001 control snapshot identity already opened")
    if any(row["snapshot_occurrence_rows_opened"] != "false" for row in rows):
        raise RuntimeError("NEIC001 control occurrence rows already opened")
    return rows


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = _check_preconditions()
    admitted = []
    excluded = []
    for row in rows:
        control_id = row["control_id"]
        name = row["scientific_name"]
        request = SnapshotTaxonomyRequest("NEIC001_" + control_id, "x", name, "Plantae")
        try:
            match = _read_json(
                GBIF_CURRENT_SPECIES_MATCH_ENDPOINT + "?" + urlencode(build_current_species_match_params(request))
            )
            usage = match.get("usage")
            if not isinstance(usage, Mapping) or usage.get("key") is None:
                raise ValueError("current match payload has no usage key")
            direct = _read_json(GBIF_CURRENT_SPECIES_USAGE_ENDPOINT.format(usage_key=str(usage["key"])))
            resolution = parse_current_direct_taxonomy_resolution(
                request=request, match_payload=match, usage_payload=direct
            )
            admitted.append({"control_id": control_id, **asdict(resolution)})
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
        "result_version": "product_b_v7_3_neic001_control_current_taxonomy_v0.1",
        "pair_id": "NEIC001",
        "status": status,
        "declared_control_count": 8,
        "minimum_required_control_count": MIN_CONTROLS,
        "admitted_count": len(admitted),
        "admitted": admitted,
        "excluded": excluded,
        "interaction_screen_passed_before_taxonomy": True,
        "synonym_rescue_allowed": False,
        "replacement_after_taxonomy_allowed": False,
        "snapshot_taxonomy_identity_rows_opened": False,
        "snapshot_occurrence_rows_opened": False,
        "snapshot_occurrence_counts_opened": False,
        "live_occurrence_search_used": False,
    }
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status == "control_current_taxonomy_preflight_passed" else 1


if __name__ == "__main__":
    sys.exit(main())
