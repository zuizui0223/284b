#!/usr/bin/env python3
"""Aggregate successor Layer-1 fit contracts without opening paired surfaces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLING = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"


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

    expected_cells = sum(int(row["expected_fit_cells"]) for row in rows)
    sealed_cells = sum(int(row["sealed_fit_cells"]) for row in rows)
    unresolved_cells = sum(int(row["unresolved_fit_cells"]) for row in rows)
    outcome = {
        "result_version": "product_b_same_target_successor_layer1_fit_v0.1",
        "taxa_expected_from_sampling_pass": expected_taxa,
        "taxa_with_sealed_prediction_artifacts": len(rows),
        "expected_fit_cells": expected_cells,
        "sealed_fit_cells": sealed_cells,
        "unresolved_fit_cells": unresolved_cells,
        "all_fit_cells_sealed": sealed_cells == expected_cells and unresolved_cells == 0,
        "taxa": sorted(rows, key=lambda x: int(x["taxon_index"])),
        "prediction_surfaces_opened_for_pairing": False,
        "paired_discordance_opened": False,
        "reference_ceiling_opened": False,
        "process_knockout_opened": False,
        "sampling_or_taxonomy_reopened": False,
        "claim_strength": "engineering_only_until_successor_pairing_and_reference_ceiling_are_frozen"
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
