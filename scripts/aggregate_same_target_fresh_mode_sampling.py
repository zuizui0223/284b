#!/usr/bin/env python3
"""Aggregate sanitized fresh source-mode sampling shards.

This script never reads raw occurrence rows.  It preserves all 36 predeclared
fresh taxa, including concept-closure failures and source-mode sampling failures,
and never replaces taxa after outcomes.  Model fitting is authorized only if at
least the frozen 30 taxa clear both source-mode 50/30/10 gates.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / "results/product_b_same_target_fresh_snapshot_concept_closure_v0_1.json"
CONTRACT = ROOT / "config/product_b_same_target_fresh_calibration_contract_v0_1.json"
SHARD_DIR = ROOT / "artifacts/fresh_mode_sampling_shards"
OUTPUT = ROOT / "results/product_b_same_target_fresh_source_mode_sampling_v0_1.json"


def main() -> int:
    closure = json.loads(CLOSURE.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    minimum = int(contract["panel_rule"]["minimum_complete_taxa_for_calibration"])
    files = sorted(SHARD_DIR.glob("product_b_same_target_fresh_source_mode_sampling_shard_*.json"))
    if len(files) != 6:
        raise RuntimeError(f"expected 6 fresh sampling shard summaries, found {len(files)}")

    seen: set[int] = set()
    sampled: list[dict[str, object]] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("result_version") != "product_b_same_target_fresh_source_mode_sampling_shard_v0.1":
            raise RuntimeError("unexpected fresh sampling shard result version")
        shard = int(payload["shard_index"])
        if shard in seen or int(payload["shard_count"]) != 6:
            raise RuntimeError("fresh sampling shard index/count mismatch")
        seen.add(shard)
        for flag in (
            "raw_rows_persisted", "coordinates_persisted", "row_identifiers_persisted",
            "paired_discordance_opened", "model_fit_opened", "historical_key_level_sampling_selection_used",
        ):
            if payload.get(flag) is not False:
                raise RuntimeError(f"fresh sampling shard boundary violated: {flag}")
        sampled.extend(payload.get("results", []))
    if seen != set(range(6)):
        raise RuntimeError("fresh source-mode sampling shard coverage incomplete")

    closure_passed = {
        str(row["current_accepted_species"])
        for row in closure.get("decisions", [])
        if row.get("passed") is True
    }
    sampled_names = {str(row["requested_name"]) for row in sampled}
    if sampled_names != closure_passed:
        raise RuntimeError(
            f"fresh sampling coverage mismatch missing={sorted(closure_passed-sampled_names)} extra={sorted(sampled_names-closure_passed)}"
        )
    by_name = {str(row["requested_name"]): row for row in sampled}
    if len(by_name) != len(sampled):
        raise RuntimeError("fresh sampling contains duplicate taxon results")

    ordered = []
    for decision in closure.get("decisions", []):
        name = str(decision["current_accepted_species"])
        if name in by_name:
            ordered.append(dict(by_name[name]))
        else:
            ordered.append(
                {
                    "requested_name": name,
                    "state": str(decision.get("state") or "fresh_snapshot_species_concept_closure_unresolved"),
                    "reasons": list(decision.get("reasons", [])),
                    "frozen_historical_specieskeys": list(decision.get("frozen_historical_specieskeys", [])),
                }
            )
    if len(ordered) != 36:
        raise RuntimeError(f"fresh aggregate must preserve 36 candidates, found {len(ordered)}")

    sampling_passed = sum(row.get("state") == "fresh_source_mode_sampling_passed" for row in ordered)
    sampling_unresolved = sum(
        str(row.get("state", "")).startswith("fresh_source_mode_sampling_")
        and row.get("state") != "fresh_source_mode_sampling_passed"
        for row in ordered
    )
    upstream_unresolved = len(ordered) - sampling_passed - sampling_unresolved
    model_fit_authorized = sampling_passed >= minimum
    outcome = {
        "result_version": "product_b_same_target_fresh_source_mode_sampling_v0.1",
        "panel_size": 36,
        "concept_closure_passed_entering_sampling": int(len(closure_passed)),
        "source_mode_sampling_passed": int(sampling_passed),
        "source_mode_sampling_unresolved": int(sampling_unresolved),
        "upstream_concept_closure_unresolved": int(upstream_unresolved),
        "frozen_minimum_complete_taxa_for_calibration": minimum,
        "model_fit_authorized": bool(model_fit_authorized),
        "if_below_minimum_state": None if model_fit_authorized else "fresh_cross_source_calibration_unresolved",
        "results": ordered,
        "raw_rows_persisted": False,
        "coordinates_persisted": False,
        "row_identifiers_persisted": False,
        "paired_discordance_opened": False,
        "model_fit_opened": False,
        "historical_key_level_sampling_selection_used": False,
        "replacement_taxa_selected": False,
        "current_layer1_paired_discordance_read": False,
        "process_intervention_outcomes_read": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "result_version": outcome["result_version"],
                "concept_closure_passed_entering_sampling": outcome["concept_closure_passed_entering_sampling"],
                "source_mode_sampling_passed": outcome["source_mode_sampling_passed"],
                "source_mode_sampling_unresolved": outcome["source_mode_sampling_unresolved"],
                "upstream_concept_closure_unresolved": outcome["upstream_concept_closure_unresolved"],
                "model_fit_authorized": outcome["model_fit_authorized"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
