"""Strict provenance adapters for reusing reviewed repaired-reference logic on core19 fits.

These helpers never alter prediction values, fold metrics, comparison-row IDs,
or scientific decisions. They only translate the v0.4 result/state labels into
the already-reviewed finite-frame reference code's input schema inside a
temporary directory.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import pandas as pd

CORE19_RESULT = "product_b_same_target_successor_core19_layer1_fit_taxon_v0.4"
CORE19_CONTRACT = "product_b_same_target_core19_requalification_v0.4"
BASE_RESULT = "product_b_same_target_successor_layer1_fit_taxon_finite_frame_repair_v0.1"
CORE19_SEALED = "core19_layer1_model_fit_sealed"
CORE19_UNRESOLVED = "core19_layer1_model_fit_unresolved"
BASE_SEALED = "successor_layer1_model_fit_sealed_finite_frame_repair"
BASE_UNRESOLVED = "successor_layer1_model_fit_unresolved_finite_frame_repair"


def verified_core19_successor_contracts(root: Path) -> list[tuple[dict[str, object], Path]]:
    found=[]
    for p in sorted(root.rglob("contract.json")):
        c=json.loads(p.read_text(encoding="utf-8"))
        if c.get("result_version") != CORE19_RESULT:
            continue
        if c.get("core19_contract_version") != CORE19_CONTRACT:
            raise RuntimeError("core19 successor fit has wrong contract version")
        if c.get("panel") != "successor":
            raise RuntimeError("core19 reference adapter received non-successor fit")
        if c.get("active_predictors") != [f"bio{i}" for i in range(1,20)] or c.get("active_predictor_count") != 19:
            raise RuntimeError("core19 successor fit predictor identity drifted")
        if c.get("prediction_surfaces_sealed") is not True or c.get("all_prediction_scores_finite_for_sealed_cells") is not True:
            raise RuntimeError("core19 successor fit lacks sealed finite-score contract")
        if c.get("same_frozen_core19_background_rows_used_for_both_sources") is not True:
            raise RuntimeError("core19 successor fit did not use source-symmetric frozen frame")
        if c.get("background_rows_resampled_during_refit") is not False or c.get("posthoc_prediction_row_drop_used") is not False:
            raise RuntimeError("core19 successor fit changed frozen comparison rows")
        for k in ("paired_discordance_computed","reference_ceiling_opened_or_read","heldout_pairing_opened","process_knockout_computed"):
            if c.get(k) is not False:
                raise RuntimeError(f"core19 successor fit crossed information boundary: {k}")
        if c.get("counts_as_empirical_conclusion") is not False:
            raise RuntimeError("core19 successor fit incorrectly marked empirical")
        found.append((c,p.parent))
    if len(found)!=47 or sorted(int(c["taxon_index"]) for c,_ in found)!=list(range(47)):
        raise RuntimeError(f"core19 successor adapter requires exact 47 fit artifacts, found {len(found)}")
    return found


def adapt_core19_successor_root(source_root: Path, destination_root: Path) -> None:
    destination_root.mkdir(parents=True,exist_ok=True)
    found=verified_core19_successor_contracts(source_root)
    for c,src in found:
        dst=destination_root/f"taxon_{int(c['taxon_index']):02d}"
        if dst.exists():
            raise RuntimeError("duplicate core19 adapter destination")
        shutil.copytree(src,dst)
        adapted=dict(c)
        adapted["result_version"]=BASE_RESULT
        adapted["all_prediction_scores_finite_by_contract"]=True
        adapted["same_frozen_finite_background_rows_used_for_both_sources"]=True
        adapted["reference_ceiling_read"]=False
        adapted["heldout_12_paired_discordance_read"]=False
        adapted["core19_v0_4_provenance_adapter_only"]=True
        adapted["core19_original_result_version"]=CORE19_RESULT
        adapted["core19_original_contract_version"]=CORE19_CONTRACT
        (dst/"contract.json").write_text(json.dumps(adapted,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        inv=pd.read_csv(dst/"fit_inventory.csv")
        mapping={CORE19_SEALED:BASE_SEALED,CORE19_UNRESOLVED:BASE_UNRESOLVED}
        unknown=set(inv["state"].astype(str))-set(mapping)
        if unknown:
            raise RuntimeError(f"unexpected core19 fit states: {sorted(unknown)}")
        inv["state"]=inv["state"].astype(str).map(mapping)
        inv.to_csv(dst/"fit_inventory.csv",index=False)
