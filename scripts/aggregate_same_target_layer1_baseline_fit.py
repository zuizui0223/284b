#!/usr/bin/env python3
"""Aggregate Layer-1 fit contracts without opening paired prediction surfaces.

The aggregate preserves every frozen source × procedure × M cell. Final-fit
failures remain unresolved; they are summarized as an identifiability audit and
are never repaired, dropped, or used to select a procedure/M before pairing.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


def _strategy(procedure: object) -> str:
    text = str(procedure or "").strip()
    return text.split("|", 1)[0] if text else "unknown"


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
        expected = int(row["expected_fit_cells"])
        sealed = int(row["sealed_fit_cells"])
        unresolved = int(row["unresolved_fit_cells"])
        if sealed + unresolved != expected:
            raise RuntimeError("taxon sealed/unresolved fit inventory does not sum to frozen denominator")
        errors = list(row.get("errors", []))
        if len(errors) != unresolved:
            raise RuntimeError("taxon error audit does not match unresolved final-fit count")

    expected_cells = sum(int(row["expected_fit_cells"]) for row in rows)
    sealed_cells = sum(int(row["sealed_fit_cells"]) for row in rows)
    unresolved_cells = sum(int(row["unresolved_fit_cells"]) for row in rows)
    if sealed_cells + unresolved_cells != expected_cells:
        raise RuntimeError("aggregate sealed/unresolved count does not preserve frozen fit denominator")

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
        "result_version": "product_b_same_target_source_layer1_baseline_fit_v0.2",
        "taxa_expected": 12,
        "taxa_with_prediction_artifacts": 12,
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
            "failed_cells_dropped_from_denominator": False,
            "paired_discordance_used_to_interpret_fit_failures": False,
        },
        "taxa": sorted(rows, key=lambda x: int(x["taxon_index"])),
        "prediction_surfaces_opened_for_pairing": False,
        "paired_discordance_opened": False,
        "reference_ceiling_opened": False,
        "process_knockout_opened": False,
        "claim_strength": "final_fit_identifiability_audit_only_before_frozen_reference_heldout_pairing",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
