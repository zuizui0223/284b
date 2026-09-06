#!/usr/bin/env python3
"""Compare canonical and grouped successor sampling transports exactly.

This stage compares only already-sanitized sampling audits. It never reopens
occurrence rows. A grouped transport may be considered scientifically equivalent
only when every frozen taxon has exactly the same key set, state, reasons,
source-mode summaries, and exclusion audit as the canonical taxon-by-taxon run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


SCIENTIFIC_FIELDS = (
    "requested_name",
    "frozen_historical_specieskeys",
    "historical_key_count",
    "state",
    "reasons",
    "preserved_specimen",
    "human_observation",
    "quality_excluded_preserved_specimen",
    "quality_excluded_human_observation",
    "quality_exclusion_reason_counts",
    "missing_uncertainty_preserved_specimen",
    "missing_uncertainty_human_observation",
    "cross_mode_collision_excluded_preserved_specimen",
    "cross_mode_collision_excluded_human_observation",
    "cross_mode_collision_component_count",
    "cross_mode_asymmetry_exclusion_applied",
    "historical_key_level_sampling_selection_used",
    "raw_rows_persisted",
    "coordinates_persisted",
    "row_identifiers_persisted",
)


def _normalize_result(row: dict[str, object]) -> dict[str, object]:
    return {field: row.get(field) for field in SCIENTIFIC_FIELDS}


def _by_name(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    rows = list(payload.get("results", []))
    result = {str(row["requested_name"]): _normalize_result(row) for row in rows}
    if len(result) != len(rows):
        raise RuntimeError("sampling transport result contains duplicate taxon names")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", required=True)
    parser.add_argument("--grouped", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    canonical = json.loads(Path(args.canonical).read_text(encoding="utf-8"))
    grouped = json.loads(Path(args.grouped).read_text(encoding="utf-8"))
    if canonical.get("result_version") != "product_b_same_target_successor_source_mode_sampling_v0.1":
        raise RuntimeError("canonical successor sampling result version unexpected")
    if grouped.get("result_version") != "product_b_same_target_successor_source_mode_sampling_grouped_v0.1":
        raise RuntimeError("grouped successor sampling result version unexpected")
    if grouped.get("scientific_contract_equivalent_to_canonical_sampling") is not True:
        raise RuntimeError("grouped result lacks prospective equivalence declaration")
    for payload in (canonical, grouped):
        for flag in (
            "raw_rows_persisted", "coordinates_persisted", "row_identifiers_persisted",
            "paired_discordance_opened", "model_fit_opened", "historical_key_level_sampling_selection_used",
            "replacement_taxa_selected", "current_layer1_paired_discordance_read",
            "process_intervention_outcomes_read",
        ):
            if payload.get(flag) is not False:
                raise RuntimeError(f"sampling transport boundary violated before comparison: {flag}")

    canonical_rows = _by_name(canonical)
    grouped_rows = _by_name(grouped)
    if set(canonical_rows) != set(grouped_rows) or len(canonical_rows) != 72:
        raise RuntimeError("sampling transports do not cover the same frozen 72-candidate denominator")

    mismatches: list[dict[str, object]] = []
    for name in sorted(canonical_rows):
        a = canonical_rows[name]
        b = grouped_rows[name]
        if a != b:
            fields = [field for field in SCIENTIFIC_FIELDS if a.get(field) != b.get(field)]
            mismatches.append({"requested_name": name, "differing_fields": fields})

    scalar_fields = (
        "frozen_panel_size",
        "current_taxonomy_or_snapshot_tuple_not_entering_closure",
        "concept_closure_passed_entering_sampling",
        "source_mode_sampling_passed",
        "source_mode_sampling_unresolved",
        "upstream_concept_closure_unresolved",
        "frozen_minimum_complete_taxa_for_calibration",
    )
    scalar_mismatches = [field for field in scalar_fields if canonical.get(field) != grouped.get(field)]
    equivalent = not mismatches and not scalar_mismatches
    outcome = {
        "result_version": "product_b_same_target_successor_sampling_transport_comparison_v0.1",
        "canonical_result": str(args.canonical),
        "grouped_result": str(args.grouped),
        "frozen_taxa_compared": 72,
        "scientific_fields_compared_per_taxon": list(SCIENTIFIC_FIELDS),
        "taxa_with_mismatch": len(mismatches),
        "scalar_mismatch_fields": scalar_mismatches,
        "mismatches": mismatches,
        "scientifically_equivalent": bool(equivalent),
        "occurrence_rows_reopened": False,
        "paired_discordance_opened": False,
        "model_fit_opened": False,
        "process_knockout_opened": False,
        "grouped_transport_promoted_by_this_script": False,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    if not equivalent:
        raise SystemExit(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
