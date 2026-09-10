#!/usr/bin/env python3
"""v0.2 provenance adapter for the one-shot repaired held-out final endpoint.

The underlying held-out evaluation logic is intentionally reused unchanged from
``evaluate_same_target_heldout_final_finite_frame_repair``.  This adapter only
updates the accepted successor-reference result version and the terminal
endpoint identity/fingerprint so a v0.2 reference can never be confused with
the superseded v0.1 repair path.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

from scripts import evaluate_same_target_heldout_final_finite_frame_repair as base

REFERENCE_RESULT_V0_2 = "product_b_same_target_successor_pairing_calibration_finite_frame_repair_v0.2"
FINAL_RESULT_V0_2 = "product_b_same_target_heldout_final_finite_frame_repair_v0.2"
ENDPOINT_ID_V0_2 = "same_target_cross_source_reproducibility_heldout12_finite_frame_v0_2"


def _arg_value(name: str) -> str:
    try:
        i = sys.argv.index(name)
    except ValueError as exc:
        raise RuntimeError(f"missing required CLI argument after delegated evaluation: {name}") from exc
    if i + 1 >= len(sys.argv):
        raise RuntimeError(f"missing value for CLI argument: {name}")
    return sys.argv[i + 1]


def main() -> int:
    # The scientific evaluation body, opening rules, adequacy gate and
    # classification logic remain exactly the reviewed implementation.
    base.REFERENCE_RESULT = REFERENCE_RESULT_V0_2
    rc = base.main()
    if rc not in (None, 0):
        return int(rc)

    out_path = Path(_arg_value("--output-final"))
    result = json.loads(out_path.read_text(encoding="utf-8"))
    if result.get("terminal_class") != "empirical_result":
        raise RuntimeError("delegated final did not emit an empirical terminal")
    if result.get("counts_as_empirical_conclusion") is not True:
        raise RuntimeError("delegated final did not count as empirical conclusion")
    if int(result.get("paired_prediction_surfaces_opened_cells", 0)) < 1:
        raise RuntimeError("delegated final opened no held-out paired cell")
    if result.get("process_knockout_opened") is not False:
        raise RuntimeError("process knockout crossed the final baseline boundary")

    payload = {
        "endpoint": FINAL_RESULT_V0_2,
        "cells_sha256": result["cells_sha256"],
        "reference_summary_sha256": result["reference_summary_sha256"],
        "reference_table_sha256": result["reference_table_sha256"],
        "source_manifest": result["source_manifest"],
        "opened_cells": int(result["paired_prediction_surfaces_opened_cells"]),
        "consistent": int(result["paired_crosscheck_consistent"]),
        "attention_required": int(result["paired_crosscheck_attention_required"]),
    }
    result["result_version"] = FINAL_RESULT_V0_2
    result["endpoint_id"] = ENDPOINT_ID_V0_2
    result["reference_result_version"] = REFERENCE_RESULT_V0_2
    result["heldout_finite_frame_repair_contract_version"] = "product_b_same_target_heldout_finite_frame_repair_v0.2"
    result["final_endpoint_fingerprint"] = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
