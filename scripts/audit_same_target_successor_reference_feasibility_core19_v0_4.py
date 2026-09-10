#!/usr/bin/env python3
"""Run the reviewed pre-D successor feasibility audit on v0.4 core19 fits.

Only provenance/state labels are adapted in a temporary tree. Prediction values,
fold metrics, adequacy thresholds, the 30-taxon minimum, and the 24 procedure x M
reference-cell universe are unchanged. No paired prediction surface is read.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

from scripts import audit_same_target_successor_reference_feasibility_finite_frame_repair as base
from scripts.core19_v0_4_adapter_utils import adapt_core19_successor_root

RESULT = "product_b_same_target_successor_reference_feasibility_core19_v0.4"
CORE19_CONTRACT = "product_b_same_target_core19_requalification_v0.4"


def _arg(flag: str) -> str:
    try:
        i=sys.argv.index(flag)
    except ValueError as exc:
        raise RuntimeError(f"missing {flag}") from exc
    if i+1>=len(sys.argv): raise RuntimeError(f"missing value for {flag}")
    return sys.argv[i+1]


def main() -> int:
    source=Path(_arg("--input-root")); out=Path(_arg("--output"))
    original=list(sys.argv)
    with tempfile.TemporaryDirectory(prefix="core19_v0_4_pre_d_") as tmp:
        adapted=Path(tmp)/"adapted"
        adapt_core19_successor_root(source,adapted)
        i=sys.argv.index("--input-root"); sys.argv[i+1]=str(adapted)
        try:
            code=base.main()
        finally:
            sys.argv[:]=original
    payload=json.loads(out.read_text(encoding="utf-8"))
    if payload.get("result_version")!="product_b_same_target_successor_reference_feasibility_finite_frame_repair_v0.1":
        raise RuntimeError("reviewed pre-D body returned unexpected version")
    if payload.get("sampling_pass_taxa")!=47 or payload.get("candidate_pair_cells")!=1128 or payload.get("reference_cells_expected")!=24:
        raise RuntimeError("reviewed pre-D denominator drifted")
    for k in ("paired_prediction_surfaces_read","schoener_d_computed","reference_ceiling_computed","heldout_12_paired_discordance_read","process_knockout_opened"):
        if payload.get(k) is not False:
            raise RuntimeError(f"core19 pre-D audit crossed information boundary: {k}")
    payload["result_version"]=RESULT
    payload["core19_contract_version"]=CORE19_CONTRACT
    payload["active_predictors"]=[f"bio{i}" for i in range(1,20)]
    payload["active_predictor_count"]=19
    payload["provenance_adapter_changed_scientific_feasibility_body"]=False
    payload["counts_as_empirical_conclusion"]=False
    payload["claim_strength"]="core19_reference_pre_discordance_feasibility_only_not_empirical_evidence"
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return int(code)


if __name__=="__main__":
    raise SystemExit(main())
