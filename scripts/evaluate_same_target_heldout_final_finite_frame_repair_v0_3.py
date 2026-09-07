#!/usr/bin/env python3
"""v0.3 provenance adapter for the one-shot repaired held-out final endpoint.

The scientific held-out evaluation body, prediction-opening rule, adequacy gate,
Schoener-D computation and classification logic are reused unchanged from the
reviewed finite-frame final implementation.  This adapter only accepts v0.3
composite-frame provenance and assigns a distinct v0.3 endpoint identity.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

from scripts import evaluate_same_target_heldout_final_finite_frame_repair as base

HELDOUT_RESULT = "product_b_same_target_source_layer1_baseline_fit_taxon_finite_frame_repair_v0.1"
FRAME_RESULT_V3 = "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.3"
FRAME_RESULT_V2 = "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.2"
HELDOUT_CONTRACT_V3 = "product_b_same_target_heldout_finite_frame_repair_v0.3"
REFERENCE_RESULT_V3 = "product_b_same_target_successor_pairing_calibration_finite_frame_repair_v0.3"
FINAL_RESULT_V3 = "product_b_same_target_heldout_final_finite_frame_repair_v0.3"
ENDPOINT_ID_V3 = "same_target_cross_source_reproducibility_heldout12_finite_frame_v0_3"


def _arg_value(name: str) -> str:
    try:
        i = sys.argv.index(name)
    except ValueError as exc:
        raise RuntimeError(f"missing required CLI argument: {name}") from exc
    if i + 1 >= len(sys.argv):
        raise RuntimeError(f"missing value for CLI argument: {name}")
    return sys.argv[i + 1]


def _load_heldout_v3(root: Path):
    rows = []
    for p in sorted(root.rglob("contract.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        if c.get("result_version") == HELDOUT_RESULT:
            rows.append((c, p.parent))
    indices = sorted(int(c["taxon_index"]) for c, _ in rows)
    names = [str(c["taxon"]) for c, _ in rows]
    if len(rows) != 12 or indices != list(range(12)) or len(set(names)) != 12:
        raise RuntimeError("v0.3 repaired held-out root must contain exactly the frozen 12 taxa")
    for c, _ in rows:
        if c.get("finite_frame_preflight_result_version") != FRAME_RESULT_V3:
            raise RuntimeError("held-out final requires v0.3 finite-frame fits")
        if c.get("finite_frame_parent_preflight_result_version") != FRAME_RESULT_V2:
            raise RuntimeError("held-out final requires exact v0.2 parent provenance")
        if c.get("finite_frame_repair_contract_version") != HELDOUT_CONTRACT_V3:
            raise RuntimeError("held-out final v0.3 repair-contract identity mismatch")
        if c.get("v0_3_adapter_changed_frame_bytes") is not False:
            raise RuntimeError("held-out final rejects changed v0.3 frame bytes")
        if c.get("v0_3_adapter_changed_model_fit_body") is not False:
            raise RuntimeError("held-out final rejects changed v0.3 model-fit body")
        if c.get("prediction_surfaces_sealed") is not True or c.get("all_prediction_scores_finite_by_contract") is not True:
            raise RuntimeError("held-out v0.3 repaired prediction surface is not sealed all-finite")
        if c.get("same_frozen_finite_background_rows_used_for_both_sources") is not True:
            raise RuntimeError("held-out final received asymmetric comparison frame")
        if c.get("background_rows_resampled_during_refit") is not False or c.get("posthoc_prediction_row_drop_used") is not False:
            raise RuntimeError("held-out v0.3 repaired fit changed frozen comparison rows")
        for key in (
            "paired_discordance_computed",
            "reference_ceiling_read",
            "heldout_pairing_opened",
            "process_knockout_computed",
        ):
            if c.get(key) is not False:
                raise RuntimeError(f"held-out v0.3 repaired fit crossed boundary before final: {key}")
    return rows


def main() -> int:
    # Patch provenance acceptance only. All scientific evaluation functions used
    # by base.main() remain the reviewed implementation.
    base.REFERENCE_RESULT = REFERENCE_RESULT_V3
    base._load_heldout = _load_heldout_v3
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
        "endpoint": FINAL_RESULT_V3,
        "cells_sha256": result["cells_sha256"],
        "reference_summary_sha256": result["reference_summary_sha256"],
        "reference_table_sha256": result["reference_table_sha256"],
        "source_manifest": result["source_manifest"],
        "opened_cells": int(result["paired_prediction_surfaces_opened_cells"]),
        "consistent": int(result["paired_crosscheck_consistent"]),
        "attention_required": int(result["paired_crosscheck_attention_required"]),
    }
    result["result_version"] = FINAL_RESULT_V3
    result["endpoint_id"] = ENDPOINT_ID_V3
    result["reference_result_version"] = REFERENCE_RESULT_V3
    result["heldout_finite_frame_repair_contract_version"] = HELDOUT_CONTRACT_V3
    result["heldout_finite_frame_preflight_result_version"] = FRAME_RESULT_V3
    result["v0_3_adapter_changed_scientific_evaluation_body"] = False
    result["final_endpoint_fingerprint"] = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
