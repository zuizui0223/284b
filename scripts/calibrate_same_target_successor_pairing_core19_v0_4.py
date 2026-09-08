#!/usr/bin/env python3
"""Reuse the reviewed repaired reference-calibration body for core19 v0.4.

The v0.4 fit provenance and feasibility result are translated only inside a
temporary workspace. The prediction rows, adequacy rule, Schoener-D formula,
minimum n=30, q=.95, and nearest-rank quantile implementation are unchanged.
Held-out paired outcomes and process knockouts remain closed.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

import pandas as pd

from scripts import calibrate_same_target_successor_pairing_finite_frame_repair as base
from scripts.core19_v0_4_adapter_utils import adapt_core19_successor_root

CORE19_FEASIBILITY = "product_b_same_target_successor_reference_feasibility_core19_v0.4"
BASE_FEASIBILITY = "product_b_same_target_successor_reference_feasibility_finite_frame_repair_v0.1"
BASE_RESULT = "product_b_same_target_successor_pairing_calibration_finite_frame_repair_v0.1"
RESULT = "product_b_same_target_successor_pairing_calibration_core19_v0.4"
CORE19_CONTRACT = "product_b_same_target_core19_requalification_v0.4"


def _arg(flag: str) -> str:
    try:
        i=sys.argv.index(flag)
    except ValueError as exc:
        raise RuntimeError(f"missing {flag}") from exc
    if i+1>=len(sys.argv): raise RuntimeError(f"missing value for {flag}")
    return sys.argv[i+1]


def main() -> int:
    source=Path(_arg("--input-root")); feasibility_path=Path(_arg("--feasibility"))
    cells_path=Path(_arg("--output-cells")); reference_path=Path(_arg("--output-reference")); summary_path=Path(_arg("--output-summary"))
    f=json.loads(feasibility_path.read_text(encoding="utf-8"))
    if f.get("result_version")!=CORE19_FEASIBILITY or f.get("core19_contract_version")!=CORE19_CONTRACT:
        raise RuntimeError("core19 calibration received wrong pre-D feasibility artifact")
    for k in ("paired_prediction_surfaces_read","schoener_d_computed","reference_ceiling_computed","heldout_12_paired_discordance_read","process_knockout_opened"):
        if f.get(k) is not False:
            raise RuntimeError(f"core19 feasibility already crossed boundary: {k}")
    if f.get("counts_as_empirical_conclusion") is not False:
        raise RuntimeError("core19 feasibility incorrectly marked empirical")

    original=list(sys.argv)
    with tempfile.TemporaryDirectory(prefix="core19_v0_4_reference_") as tmp:
        tmpdir=Path(tmp); adapted=tmpdir/"adapted_fits"
        adapt_core19_successor_root(source,adapted)
        adapted_feas=dict(f); adapted_feas["result_version"]=BASE_FEASIBILITY
        feas_tmp=tmpdir/"feasibility.json"; feas_tmp.write_text(json.dumps(adapted_feas,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        i=sys.argv.index("--input-root"); sys.argv[i+1]=str(adapted)
        j=sys.argv.index("--feasibility"); sys.argv[j+1]=str(feas_tmp)
        try:
            code=base.main()
        finally:
            sys.argv[:]=original

    summary=json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("result_version")!=BASE_RESULT:
        raise RuntimeError("reviewed reference calibration returned unexpected version")
    if summary.get("sampling_pass_taxa_in_audit")!=47 or summary.get("paired_cells_expected")!=1128 or summary.get("reference_cells_expected")!=24:
        raise RuntimeError("core19 reference calibration denominator drifted")
    if summary.get("minimum_distinct_calibration_taxa_per_reference_cell")!=30 or summary.get("reference_quantile")!=0.95 or summary.get("quantile_method")!="nearest_rank":
        raise RuntimeError("core19 strict reference rule drifted")
    if summary.get("heldout_12_paired_discordance_read") is not False or summary.get("process_knockout_opened") is not False:
        raise RuntimeError("core19 reference calibration crossed heldout/process boundary")
    summary["result_version"]=RESULT
    summary["core19_contract_version"]=CORE19_CONTRACT
    summary["active_predictors"]=[f"bio{i}" for i in range(1,20)]
    summary["active_predictor_count"]=19
    summary["provenance_adapter_changed_scientific_calibration_body"]=False
    summary["counts_as_empirical_conclusion"]=False
    summary["claim_strength"]="core19_successor_reference_calibration_only_not_heldout_empirical_conclusion"
    summary_path.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    cells=pd.read_csv(cells_path); refs=pd.read_csv(reference_path)
    if len(cells)!=1128 or len(refs)!=24:
        raise RuntimeError("core19 calibrated table denominator drifted")
    cells["core19_contract_version"]=CORE19_CONTRACT; cells["active_predictor_count"]=19
    refs["core19_contract_version"]=CORE19_CONTRACT; refs["active_predictor_count"]=19
    cells.to_csv(cells_path,index=False); refs.to_csv(reference_path,index=False)
    return int(code)


if __name__=="__main__":
    raise SystemExit(main())
