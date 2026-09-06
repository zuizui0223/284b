#!/usr/bin/env python3
"""Aggregate Layer-1 fit contracts without opening paired prediction surfaces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.input_root)
    contracts = sorted(root.rglob("contract.json"))
    if len(contracts) != 12:
        raise RuntimeError(f"expected 12 taxon fit contracts, found {len(contracts)}")
    rows = [json.loads(path.read_text(encoding="utf-8")) for path in contracts]
    names = [str(row["taxon"]) for row in rows]
    if len(set(names)) != 12:
        raise RuntimeError("taxon fit aggregate contains duplicate/missing taxa")
    for row in rows:
        if row.get("prediction_surfaces_sealed") is not True:
            raise RuntimeError("prediction surfaces are not sealed")
        if row.get("paired_discordance_computed") is not False:
            raise RuntimeError("paired discordance was opened during model fitting")
        if row.get("process_knockout_computed") is not False:
            raise RuntimeError("process knockout was opened during baseline fitting")
        if row.get("raw_occurrence_rows_persisted") is not False:
            raise RuntimeError("raw occurrence persistence boundary violated")
        if row.get("occurrence_coordinates_persisted") is not False:
            raise RuntimeError("occurrence coordinate persistence boundary violated")
        if row.get("shared_source_blind_M_and_block_geometry") is not True:
            raise RuntimeError("source-symmetric geometry contract violated")
        if row.get("same_background_rows_used_for_both_sources") is not True:
            raise RuntimeError("source answers did not share comparison background")

    expected_cells = sum(int(row["expected_fit_cells"]) for row in rows)
    sealed_cells = sum(int(row["sealed_fit_cells"]) for row in rows)
    unresolved_cells = sum(int(row["unresolved_fit_cells"]) for row in rows)
    outcome = {
        "result_version": "product_b_same_target_source_layer1_baseline_fit_v0.1",
        "taxa_expected": 12,
        "taxa_with_sealed_prediction_artifacts": 12,
        "expected_fit_cells": expected_cells,
        "sealed_fit_cells": sealed_cells,
        "unresolved_fit_cells": unresolved_cells,
        "all_fit_cells_sealed": sealed_cells == expected_cells and unresolved_cells == 0,
        "taxa": sorted(rows, key=lambda x: int(x["taxon_index"])),
        "prediction_surfaces_opened_for_pairing": False,
        "paired_discordance_opened": False,
        "reference_ceiling_opened": False,
        "process_knockout_opened": False,
        "claim_strength": "engineering_descriptive_only_until_pairing_and_no_calibrated_soft_ceiling_with_12_taxa",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
