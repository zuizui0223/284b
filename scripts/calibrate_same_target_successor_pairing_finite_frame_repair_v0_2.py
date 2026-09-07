#!/usr/bin/env python3
"""v0.2 provenance gate around the unchanged strict repaired calibration body."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

from scripts import calibrate_same_target_successor_pairing_finite_frame_repair as base

FIT_RESULT = "product_b_same_target_successor_layer1_fit_taxon_finite_frame_repair_v0.1"
FRAME_RESULT = "product_b_same_target_successor_finite_frame_preflight_taxon_v0.2"
REPAIR_CONTRACT = "product_b_same_target_reference_finite_frame_repair_v0.2"
FEASIBILITY_V2 = "product_b_same_target_successor_reference_feasibility_finite_frame_repair_v0.2"
FEASIBILITY_V1 = "product_b_same_target_successor_reference_feasibility_finite_frame_repair_v0.1"
SUMMARY_V2 = "product_b_same_target_successor_pairing_calibration_finite_frame_repair_v0.2"


def _arg(flag: str) -> str:
    try:
        i = sys.argv.index(flag)
    except ValueError as exc:
        raise RuntimeError(f"missing {flag}") from exc
    return sys.argv[i + 1]


def main() -> int:
    root = Path(_arg("--input-root"))
    feasibility_path = Path(_arg("--feasibility"))
    output_summary = Path(_arg("--output-summary"))
    contracts=[]
    for p in sorted(root.rglob("contract.json")):
        c=json.loads(p.read_text(encoding="utf-8"))
        if c.get("result_version")==FIT_RESULT:
            contracts.append(c)
    if len(contracts)!=47:
        raise RuntimeError(f"v0.2 calibration requires 47 repaired contracts, found {len(contracts)}")
    for c in contracts:
        if c.get("finite_frame_preflight_result_version")!=FRAME_RESULT or c.get("finite_frame_repair_contract_version")!=REPAIR_CONTRACT:
            raise RuntimeError("v0.2 calibration rejects non-v0.2 repaired fit")
        if c.get("v0_2_adapter_changed_frame_bytes") is not False or c.get("v0_2_adapter_changed_model_fit_body") is not False:
            raise RuntimeError("v0.2 calibration rejects adapted content drift")
    f=json.loads(feasibility_path.read_text(encoding="utf-8"))
    if f.get("result_version")!=FEASIBILITY_V2 or f.get("finite_frame_repair_contract_version")!=REPAIR_CONTRACT:
        raise RuntimeError("v0.2 calibration requires sealed v0.2 pre-D feasibility")
    for k in ("paired_prediction_surfaces_read","schoener_d_computed","reference_ceiling_computed","heldout_12_paired_discordance_read","process_knockout_opened"):
        if f.get(k) is not False:
            raise RuntimeError(f"v0.2 feasibility crossed boundary: {k}")

    original_argv=list(sys.argv)
    with tempfile.TemporaryDirectory(prefix="reference_feasibility_v0_2_adapter_") as tmp:
        adapted=Path(tmp)/"feasibility.json"
        payload=dict(f); payload["result_version"]=FEASIBILITY_V1
        adapted.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        i=sys.argv.index("--feasibility"); sys.argv[i+1]=str(adapted)
        try:
            code=base.main()
        finally:
            sys.argv[:]=original_argv
    summary=json.loads(output_summary.read_text(encoding="utf-8"))
    summary["result_version"]=SUMMARY_V2
    summary["finite_frame_repair_contract_version"]=REPAIR_CONTRACT
    summary["input_finite_frame_preflight_result_version"]=FRAME_RESULT
    summary["input_reference_feasibility_result_version"]=FEASIBILITY_V2
    summary["v0_2_adapter_changed_prediction_bytes"]=False
    summary["v0_2_adapter_changed_calibration_rule"]=False
    summary["counts_as_empirical_conclusion"]=False
    output_summary.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return int(code)


if __name__ == "__main__":
    raise SystemExit(main())
