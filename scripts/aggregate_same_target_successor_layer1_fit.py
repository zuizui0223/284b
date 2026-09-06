#!/usr/bin/env python3
"""Aggregate successor Layer-1 fit contracts without opening paired surfaces.

Every sampling-passed taxon and every frozen source × procedure × M cell remains
in the denominator. Final-fit failures are retained as unresolved identifiability
outcomes and are never repaired or used to select the future reference panel.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLING = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"


def _strategy(procedure: object) -> str:
    text = str(procedure or "").strip()
    return text.split("|", 1)[0] if text else "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    expected_taxa = int(sampling.get("source_mode_sampling_passed", -1))
    if sampling.get("model_fit_authorized") is not True or expected_taxa < 30:
        raise RuntimeError("successor sampling result does not authorize model fitting")
    root = Path(args.input_root)
    contracts = sorted(root.rglob("contract.json"))
    if len(contracts) != expected_taxa:
        raise RuntimeError(f"expected {expected_taxa} successor taxon fit contracts, found {len(contracts)}")
    rows = [json.loads(path.read_text(encoding="utf-8")) for path in contracts]
    names = [str(row["taxon"]) for row in rows]
    if len(set(names)) != expected_taxa:
        raise RuntimeError("successor fit aggregate contains duplicate/missing taxa")
    expected_names = {
        str(row["requested_name"])
        for row in sampling.get("results", [])
        if row.get("state") == "successor_source_mode_sampling_passed"
    }
    if set(names) != expected_names:
        raise RuntimeError("successor fit taxon inventory differs from frozen sampling-pass inventory")

    for row in rows:
        if row.get("result_version") != "product_b_same_target_successor_layer1_fit_taxon_v0.1":
            raise RuntimeError("unexpected successor taxon fit contract version")
        if row.get("prediction_surfaces_sealed") is not True:
            raise RuntimeError("successor prediction surfaces are not sealed")
        if row.get("paired_discordance_computed") is not False or row.get("process_knockout_computed") is not False:
            raise RuntimeError("successor fit crossed paired/process boundary")
        if row.get("raw_occurrence_rows_persisted") is not False or row.get("occurrence_coordinates_persisted") is not False:
            raise RuntimeError("successor fit persisted forbidden occurrence evidence")
        if row.get("shared_source_blind_M_and_block_geometry") is not True or row.get("same_background_rows_used_for_both_sources") is not True:
            raise RuntimeError("successor source-symmetric geometry contract violated")
        if row.get("background_seed_index_derived_from_frozen_72_candidate_registry") is not True:
            raise RuntimeError("successor background seed depended on post-sampling panel")
        if row.get("historical_key_subset_selection_used") is not False:
            raise RuntimeError("successor fit used historical-key subset selection")
        expected = int(row["expected_fit_cells"])
        sealed = int(row["sealed_fit_cells"])
        unresolved = int(row["unresolved_fit_cells"])
        if sealed + unresolved != expected:
            raise RuntimeError("successor taxon fit inventory does not preserve frozen denominator")
        errors = list(row.get("errors", []))
        if len(errors) != unresolved:
            raise RuntimeError("successor taxon error audit does not match unresolved fit count")

    expected_cells = sum(int(row["expected_fit_cells"]) for row in rows)
    sealed_cells = sum(int(row["sealed_fit_cells"]) for row in rows)
    unresolved_cells = sum(int(row["unresolved_fit_cells"]) for row in rows)
    if sealed_cells + unresolved_cells != expected_cells:
        raise RuntimeError("successor aggregate fit denominator changed")

    unresolved_rows = [error for row in rows for error in row.get("errors", [])]
    by_strategy = Counter(_strategy(error.get("procedure")) for error in unresolved_rows)
    by_source = Counter(str(error.get("source") or "unknown") for error in unresolved_rows)
    by_m = Counter(str(int(error["M_km"])) if error.get("M_km") is not None else "unknown" for error in unresolved_rows)
    by_type = Counter(str(error.get("error_type") or "unknown") for error in unresolved_rows)
    by_message = Counter(str(error.get("error_message") or "unknown") for error in unresolved_rows)
    taxa_with_unresolved = sorted(
        str(row["taxon"]) for row in rows if int(row["unresolved_fit_cells"]) > 0
    )

    outcome = {
        "result_version": "product_b_same_target_successor_layer1_fit_v0.2",
        "taxa_expected_from_sampling_pass": expected_taxa,
        "taxa_with_prediction_artifacts": len(rows),
        "expected_fit_cells": expected_cells,
        "sealed_fit_cells": sealed_cells,
        "unresolved_fit_cells": unresolved_cells,
        "all_fit_cells_sealed": sealed_cells == expected_cells and unresolved_cells == 0,
        "taxa_with_any_unresolved_fit_cells": len(taxa_with_unresolved),
        "taxa_with_unresolved_fit_cells": taxa_with_unresolved,
        "unresolved_final_fit_audit": {
            "by_strategy": dict(sorted(by_strategy.items())),
            "by_source": dict(sorted(by_source.items())),
            "by_M_km": dict(sorted(by_m.items(), key=lambda kv: (kv[0] == "unknown", kv[0]))),
            "by_error_type": dict(sorted(by_type.items())),
            "by_error_message": dict(sorted(by_message.items())),
            "failed_cells_repaired_or_refit": False,
            "failed_cells_dropped_from_reference_denominator": False,
            "paired_discordance_used_to_select_fit_cells": False,
        },
        "taxa": sorted(rows, key=lambda x: int(x["taxon_index"])),
        "prediction_surfaces_opened_for_pairing": False,
        "paired_discordance_opened": False,
        "reference_ceiling_opened": False,
        "process_knockout_opened": False,
        "sampling_or_taxonomy_reopened": False,
        "claim_strength": "reference_panel_final_fit_identifiability_audit_before_paired_reference_calibration"
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
