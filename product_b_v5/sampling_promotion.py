"""Fail-closed promotion of grouped successor sampling to the canonical result schema.

The grouped transport changes only how the frozen occurrence snapshot is scanned.
This module never reads occurrence rows, coordinates, row identifiers, model
outputs, paired discordance, or process outcomes. It promotes only a sanitized
aggregate after the original canonical transport is certified to have produced no
scientific artifacts.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def promote_grouped_successor_sampling(
    grouped: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    if contract.get("transport_only_promotion") is not True:
        raise ValueError("promotion contract is not transport-only")
    if int(contract.get("original_canonical_scientific_artifact_count_verified", -1)) != 0:
        raise ValueError("original canonical transport must have zero scientific artifacts")
    if int(contract.get("original_canonical_sampling_jobs_completed_with_scientific_output", -1)) != 0:
        raise ValueError("original canonical sampling produced scientific output")
    if grouped.get("result_version") != contract.get("required_grouped_result_version"):
        raise ValueError("unexpected grouped result version")
    if grouped.get("scientific_contract_equivalent_to_canonical_sampling") is not True:
        raise ValueError("grouped result lacks scientific-equivalence certification")
    if grouped.get("canonical_result_promoted") is not False:
        raise ValueError("grouped result is not an unpromoted transport audit")

    for field in (
        "raw_rows_persisted",
        "coordinates_persisted",
        "row_identifiers_persisted",
        "paired_discordance_opened",
        "model_fit_opened",
        "historical_key_level_sampling_selection_used",
        "replacement_taxa_selected",
        "current_layer1_paired_discordance_read",
        "process_intervention_outcomes_read",
    ):
        if grouped.get(field) is not False:
            raise ValueError(f"grouped sampling boundary violated: {field}")

    frozen_panel_size = int(contract["frozen_panel_size"])
    if int(grouped.get("frozen_panel_size", -1)) != frozen_panel_size:
        raise ValueError("frozen panel size changed")
    if int(grouped.get("concept_closure_passed_entering_sampling", -1)) != int(
        contract["concept_closure_passed_entering_sampling"]
    ):
        raise ValueError("concept-closure entry set changed")

    results = deepcopy(list(grouped.get("results", [])))
    if len(results) != frozen_panel_size:
        raise ValueError("promotion must preserve the full frozen panel denominator")
    names = [str(row.get("requested_name", "")) for row in results]
    if any(not name for name in names) or len(set(names)) != len(names):
        raise ValueError("promoted result rows must have unique requested_name values")

    passed = sum(row.get("state") == "successor_source_mode_sampling_passed" for row in results)
    unresolved = sum(
        str(row.get("state", "")).startswith("successor_source_mode_sampling_")
        and row.get("state") != "successor_source_mode_sampling_passed"
        for row in results
    )
    if passed != int(grouped.get("source_mode_sampling_passed", -1)):
        raise ValueError("grouped sampling pass count does not match preserved rows")
    if unresolved != int(grouped.get("source_mode_sampling_unresolved", -1)):
        raise ValueError("grouped sampling unresolved count does not match preserved rows")

    minimum = int(contract["minimum_complete_taxa_for_calibration"])
    authorized = passed >= minimum
    if bool(grouped.get("model_fit_would_be_authorized_if_promoted")) != authorized:
        raise ValueError("grouped model-fit authorization disagrees with frozen rule")

    canonical = {
        "result_version": contract["required_canonical_result_version"],
        "frozen_panel_size": frozen_panel_size,
        "current_taxonomy_or_snapshot_tuple_not_entering_closure": int(
            grouped["current_taxonomy_or_snapshot_tuple_not_entering_closure"]
        ),
        "concept_closure_passed_entering_sampling": int(
            grouped["concept_closure_passed_entering_sampling"]
        ),
        "source_mode_sampling_passed": passed,
        "source_mode_sampling_unresolved": unresolved,
        "upstream_concept_closure_unresolved": int(grouped["upstream_concept_closure_unresolved"]),
        "frozen_minimum_complete_taxa_for_calibration": minimum,
        "model_fit_authorized": authorized,
        "if_below_minimum_state": None if authorized else "successor_cross_source_calibration_unresolved",
        "results": results,
        "raw_rows_persisted": False,
        "coordinates_persisted": False,
        "row_identifiers_persisted": False,
        "paired_discordance_opened": False,
        "model_fit_opened": False,
        "historical_key_level_sampling_selection_used": False,
        "replacement_taxa_selected": False,
        "current_layer1_paired_discordance_read": False,
        "process_intervention_outcomes_read": False,
        "promotion_provenance": {
            "transport_only_promotion": True,
            "original_canonical_run_id": int(contract["original_canonical_run_id"]),
            "original_canonical_scientific_artifact_count": 0,
            "grouped_transport_run_id": int(contract["grouped_transport_run_id"]),
            "grouped_result_version": grouped["result_version"],
            "sampling_thresholds_changed": False,
            "taxon_set_changed": False,
            "historical_specieskey_sets_changed": False,
            "sampling_states_recomputed": False,
            "sampling_reasons_recomputed": False,
        },
    }
    return canonical


__all__ = ["promote_grouped_successor_sampling"]
