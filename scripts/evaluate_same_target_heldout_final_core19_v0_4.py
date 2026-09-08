#!/usr/bin/env python3
"""Core19 v0.4 provenance adapter for the reviewed one-shot held-out final body.

The held-out adequacy gate, authorized prediction materialization, Schoener-D
calculation, frozen-reference comparison, and terminal classification are reused
unchanged. This adapter only accepts the distinct prospectively qualified
core19 provenance and assigns a distinct endpoint identity/fingerprint.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

from scripts import evaluate_same_target_heldout_final_finite_frame_repair as base

HELDOUT_RESULT = "product_b_same_target_heldout_core19_layer1_fit_taxon_v0.4"
CORE19_CONTRACT = "product_b_same_target_core19_requalification_v0.4"
REFERENCE_RESULT = "product_b_same_target_successor_pairing_calibration_core19_v0.4"
FINAL_RESULT = "product_b_same_target_heldout_final_core19_v0.4"
ENDPOINT_ID = "same_target_cross_source_reproducibility_heldout12_core19_v0_4"
SEALED_STATE = "core19_layer1_model_fit_sealed"


def _arg_value(name: str) -> str:
    try:
        i=sys.argv.index(name)
    except ValueError as exc:
        raise RuntimeError(f"missing required CLI argument: {name}") from exc
    if i+1>=len(sys.argv): raise RuntimeError(f"missing value for CLI argument: {name}")
    return sys.argv[i+1]


def _load_core19_heldout(root: Path):
    rows=[]
    for p in sorted(root.rglob("contract.json")):
        c=json.loads(p.read_text(encoding="utf-8"))
        if c.get("result_version")==HELDOUT_RESULT:
            rows.append((c,p.parent))
    if len(rows)!=12 or sorted(int(c["taxon_index"]) for c,_ in rows)!=list(range(12)) or len({str(c["taxon"]) for c,_ in rows})!=12:
        raise RuntimeError("core19 held-out root must contain exactly frozen 12 taxa")
    for c,_ in rows:
        if c.get("core19_contract_version")!=CORE19_CONTRACT or c.get("panel")!="heldout":
            raise RuntimeError("held-out final received wrong core19 provenance")
        if c.get("active_predictors")!=[f"bio{i}" for i in range(1,20)] or c.get("active_predictor_count")!=19:
            raise RuntimeError("held-out core19 predictor identity drifted")
        if c.get("prediction_surfaces_sealed") is not True or c.get("all_prediction_scores_finite_for_sealed_cells") is not True:
            raise RuntimeError("held-out core19 prediction surface is not sealed finite")
        if c.get("same_frozen_core19_background_rows_used_for_both_sources") is not True:
            raise RuntimeError("held-out core19 final received asymmetric comparison frame")
        if c.get("background_rows_resampled_during_refit") is not False or c.get("posthoc_prediction_row_drop_used") is not False:
            raise RuntimeError("held-out core19 fit changed frozen comparison rows")
        for key in ("paired_discordance_computed","reference_ceiling_opened_or_read","heldout_pairing_opened","process_knockout_computed"):
            if c.get(key) is not False:
                raise RuntimeError(f"held-out core19 fit crossed boundary before final: {key}")
        if c.get("counts_as_empirical_conclusion") is not False:
            raise RuntimeError("held-out core19 refit incorrectly marked empirical")
    return rows


def main() -> int:
    base.REFERENCE_RESULT=REFERENCE_RESULT
    base.HELDOUT_RESULT=HELDOUT_RESULT
    base.SEALED_STATE=SEALED_STATE
    base._load_heldout=_load_core19_heldout
    rc=base.main()
    if rc not in (None,0): return int(rc)

    out=Path(_arg_value("--output-final"))
    result=json.loads(out.read_text(encoding="utf-8"))
    if result.get("terminal_class")!="empirical_result" or result.get("counts_as_empirical_conclusion") is not True or result.get("counts_as_empirical_evidence") is not True:
        raise RuntimeError("reviewed held-out body did not emit empirical terminal")
    if int(result.get("paired_prediction_surfaces_opened_cells",0))<1:
        raise RuntimeError("reviewed held-out body opened no paired cell")
    if result.get("process_knockout_opened") is not False:
        raise RuntimeError("process knockout crossed core19 baseline final")

    payload={
        "endpoint":FINAL_RESULT,
        "cells_sha256":result["cells_sha256"],
        "reference_summary_sha256":result["reference_summary_sha256"],
        "reference_table_sha256":result["reference_table_sha256"],
        "source_manifest":result["source_manifest"],
        "opened_cells":int(result["paired_prediction_surfaces_opened_cells"]),
        "consistent":int(result["paired_crosscheck_consistent"]),
        "attention_required":int(result["paired_crosscheck_attention_required"]),
    }
    result["result_version"]=FINAL_RESULT
    result["endpoint_id"]=ENDPOINT_ID
    result["reference_result_version"]=REFERENCE_RESULT
    result["core19_contract_version"]=CORE19_CONTRACT
    result["active_predictors"]=[f"bio{i}" for i in range(1,20)]
    result["active_predictor_count"]=19
    result["provenance_adapter_changed_scientific_evaluation_body"]=False
    result["final_endpoint_fingerprint"]=sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
