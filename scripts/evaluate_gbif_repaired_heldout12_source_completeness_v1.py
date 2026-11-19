#!/usr/bin/env python3
"""One-shot, retrospective source-completeness sensitivity of historical Level A.

Only AFTER the repaired 47-reference source fits, 24 new q95 ceilings and the
12 heldout repaired-source fit audits are independently signed may the 288
original heldout source-paired cells be opened once. Uses the unchanged reviewed
heldout adequacy, Schoener D and reference classification implementation.

The 2026-08-01 GBIF object restoration is a post-freeze source repair, NOT a
new independent prospective ecological experiment. Therefore results must
never add a new empirical endpoint or replace the original signed 0/12 result.
"""
from __future__ import annotations

import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))

HELDOUT_RESULT="284b.gbif_repaired_heldout12_fixed_old_centers_fit_v1"
REFERENCE_RESULT="284b.gbif_repaired_reference47_q95_calibration.v1"
FINAL_RESULT="284b.gbif_repaired_source_completeness_heldout12_sensitivity.v1"
CORE19_CONTRACT="product_b_same_target_core19_requalification_v0.4"
ORIGINAL_ENDPOINT="same_target_cross_source_reproducibility_heldout12_core19_v0_4"
EXPECTED_MODES=["PRESERVED_SPECIMEN","HUMAN_OBSERVATION"]

def _require(ok,message):
    if not ok:raise RuntimeError(message)

def verify_preopening(reference_summary,ref_fit_audit,heldout_fit_audit,original_receipt,
                      reference_table_sha256):
    _require(reference_summary.get("result_version")==REFERENCE_RESULT
             and reference_summary.get("source_arm")=="repaired_2026-08-01_10215_parquet_files"
             and reference_summary.get("reference_cells_expected")==24
             and reference_summary.get("reference_cells_frozen")==24
             and reference_summary.get("reference_cells_unresolved")==0
             and reference_summary.get("full_reference_matrix_available") is True
             and reference_summary.get("minimum_distinct_calibration_taxa_per_reference_cell")==30
             and reference_summary.get("reference_quantile")==0.95
             and reference_summary.get("quantile_method")=="nearest_rank"
             and reference_summary.get("heldout12_repaired_source_outcomes_opened") is False
             and reference_summary.get("heldout_12_paired_discordance_read") is False
             and reference_summary.get("process_knockout_opened") is False
             and reference_summary.get("empirical_ledger_increment")==0,
             "Restored GBIF source reference q95 is not a sealed 24-cell independent reference")

    _require(ref_fit_audit.get("schema")=="284b.gbif_repaired_reference47_source_fit_audit.v1"
             and ref_fit_audit.get("status")=="ALL_47_REPAIRED_REFERENCE_SOURCE_FITS_INTEGRITY_VERIFIED_NO_Q95"
             and ref_fit_audit.get("reference_taxa_verified")==47
             and ref_fit_audit.get("fit_cells_expected")==2256
             and ref_fit_audit.get("calibration_24_q95_opened") is False
             and ref_fit_audit.get("heldout12_paired_discordance_opened") is False
             and ref_fit_audit.get("empirical_ledger_increment")==0,
             "Restored reference 47-taxon source fits are not independently verified")

    _require(heldout_fit_audit.get("schema")=="284b.gbif_repaired_heldout12_source_fit_audit.v1"
             and heldout_fit_audit.get("status")=="ALL_12_REPAIRED_HELDOUT_SOURCE_MODELS_INTEGRITY_VERIFIED_PAIRING_CLOSED"
             and heldout_fit_audit.get("heldout_taxa_verified")==12
             and heldout_fit_audit.get("source_fit_cells_expected")==576
             and heldout_fit_audit.get("source_fit_cells_sealed",-1)+heldout_fit_audit.get("source_fit_cells_unresolved",-1)==576
             and heldout_fit_audit.get("reference_q95_opened") is False
             and heldout_fit_audit.get("heldout12_paired_discordance_opened") is False
             and heldout_fit_audit.get("empirical_ledger_increment")==0,
             "Original 12 heldout repaired-source models are not all signed and closed")

    _require(original_receipt.get("endpoint_id")==ORIGINAL_ENDPOINT
             and original_receipt.get("result_version")=="product_b_same_target_heldout_final_core19_v0.4"
             and original_receipt.get("heldout",{}).get("taxa")==12
             and original_receipt["heldout"].get("cells_expected")==288
             and original_receipt["heldout"].get("paired_crosscheck_attention_required")==0
             and original_receipt["heldout"].get("paired_prediction_surfaces_opened_cells")==283
             and original_receipt.get("counts_as_empirical_conclusion") is True
             and original_receipt.get("empirical_ledger_increment")==1
             and original_receipt.get("do_not_recount_same_endpoint") is True,
             "Signed original historical Level A 0/12 receipt does not match frozen outcome")

    _require(isinstance(reference_table_sha256,str)
             and len(reference_table_sha256)==64
             and all(x in "0123456789abcdef" for x in reference_table_sha256),
             "Repaired q95 reference-table bytes must be frozen by SHA")
    return True

def load_qualified_heldout(root,fit_audit):
    found=list(root.rglob("contract.json"))
    _require(len(found)==12,"Exactly 12 repaired heldout source-model contract files required")
    reports=fit_audit.get("taxa",[])
    _require(len(reports)==12 and [r.get("index") for r in reports]==list(range(12)),
             "Repaired original 12 heldout model indexes must be complete and ordered")
    output={}
    for f in found:
        c=json.loads(f.read_text(encoding="utf-8"))
        i=c.get("taxon_index")
        _require(type(i) is int and i in range(12) and i not in output,
                 "Wrong, duplicate or replacement repaired heldout taxon")
        expected=reports[i]
        _require(c.get("result_version")==HELDOUT_RESULT
                 and c.get("core19_contract_version")==CORE19_CONTRACT
                 and c.get("panel")=="heldout"
                 and c.get("taxon")==expected["taxon"]
                 and c.get("original_12_block_centers_sha256")==expected["original_center_sha256"]
                 and c.get("prediction_surface_sha256")==expected["repaired_prediction_sha256"]
                 and c.get("sealed_fit_cells")==expected["sealed_source_cells"]
                 and c.get("unresolved_fit_cells")==expected["unresolved_source_cells"]
                 and c.get("source_modes")==EXPECTED_MODES
                 and c.get("GBIF_source_arm")=="repaired_2026-08-01_10215_parquet_files"
                 and c.get("original_signed_comparison_frames_unchanged") is True
                 and c.get("background_rows_resampled_during_refit") is False
                 and c.get("posthoc_prediction_row_drop_used") is False,
                 "Original 12 heldout taxon/model/center/prediction provenance changed")
        for k in ("paired_discordance_computed","reference_ceiling_opened_or_read",
                  "heldout_pairing_opened","process_knockout_computed","counts_as_empirical_conclusion"):
            _require(c.get(k) is False,"Heldout source model opened forbidden outcome: "+k)
        output[i]=(c,f.parent)
    return [output[i] for i in range(12)]

def main():
    import pandas as pd
    from scripts import evaluate_same_target_heldout_final_finite_frame_repair as reviewed

    p=argparse.ArgumentParser()
    p.add_argument("--input-root",type=Path,required=True)
    p.add_argument("--ref-summary",type=Path,required=True)
    p.add_argument("--ref-table",type=Path,required=True)
    p.add_argument("--ref-fit-audit",type=Path,required=True)
    p.add_argument("--heldout-fit-audit",type=Path,required=True)
    p.add_argument("--original-receipt",type=Path,required=True)
    p.add_argument("--original-cells",type=Path,required=True)
    p.add_argument("--source-manifest",type=Path,required=True)
    p.add_argument("--out-cells",type=Path,required=True)
    p.add_argument("--out-final",type=Path,required=True)
    a=p.parse_args()

    ref_raw=a.ref_summary.read_bytes();ref=json.loads(ref_raw)
    table_raw=a.ref_table.read_bytes()
    historical=json.loads(a.original_receipt.read_text(encoding="utf-8"))
    historical_cells_raw=a.original_cells.read_bytes()
    _require(hashlib.sha256(historical_cells_raw).hexdigest()==historical["cells_sha256"],
             "Original signed historical 288-cell outcome CSV SHA-256 changed")
    ref_fit_raw=a.ref_fit_audit.read_bytes();ref_fit=json.loads(ref_fit_raw)
    heldout_fit_raw=a.heldout_fit_audit.read_bytes();heldout_fit=json.loads(heldout_fit_raw)
    verify_preopening(ref,ref_fit,heldout_fit,historical,hashlib.sha256(table_raw).hexdigest())

    table=pd.read_csv(a.ref_table)
    _require(len(table)==24 and set(table["reference_state"])=={"reference_ceiling_frozen"}
             and (table["authorized_distinct_calibration_taxa"]>=30).all(),
             "Repaired reference table is not fully frozen with n>=30")
    index={(int(v["M_km"]),str(v["procedure"])) for _,v in table.iterrows()}
    _require(len(index)==24,"Reference procedure × M universe cannot contain duplicate thresholds")
    _require(set(m for m,_ in index)=={150,300,500},"Original M universe changed")

    models=load_qualified_heldout(a.input_root,heldout_fit)
    # Use the original reviewed adequacy, Schoener D, threshold-comparison and
    # terminal-classification body. Only source/result labels are adapted.
    reviewed.HELDOUT_RESULT=HELDOUT_RESULT
    reviewed.REFERENCE_RESULT=REFERENCE_RESULT
    reviewed.SEALED_STATE="core19_layer1_model_fit_sealed"
    reviewed._load_heldout=lambda unused:models

    old_argv=sys.argv[:]
    sys.argv=["evaluate_same_target_heldout_final_finite_frame_repair.py",
        "--input-root",str(a.input_root),
        "--reference-summary",str(a.ref_summary),
        "--reference-table",str(a.ref_table),
        "--source-manifest",str(a.source_manifest),
        "--output-cells",str(a.out_cells),
        "--output-final",str(a.out_final)]
    try:rc=reviewed.main()
    finally:sys.argv[:]=old_argv
    if rc not in (None,0):raise RuntimeError("Original heldout one-shot body did not terminate cleanly")

    base=json.loads(a.out_final.read_text(encoding="utf-8"))
    scores=pd.read_csv(a.out_cells)
    historical_scores=pd.read_csv(a.original_cells)
    key_columns=["taxon","M_km","procedure"]
    _require(len(historical_scores)==288 and historical_scores[key_columns].duplicated().sum()==0
             and scores[key_columns].duplicated().sum()==0,
             "Original/repaired heldout 288-cell key uniqueness violated")
    historical_scores["M_km"]=historical_scores["M_km"].astype(int)
    scores["M_km"]=scores["M_km"].astype(int)
    original_keys=set(tuple(r) for r in historical_scores[key_columns].itertuples(index=False,name=None))
    repaired_keys=set(tuple(r) for r in scores[key_columns].itertuples(index=False,name=None))
    _require(len(original_keys)==288 and original_keys==repaired_keys,
             "Original heldout taxon × procedure × M universe cannot change")
    original_open={
        tuple(r) for r in historical_scores.loc[
            historical_scores["paired_prediction_surface_opened"].astype(bool),key_columns
        ].itertuples(index=False,name=None)
    }
    repaired_open={
        tuple(r) for r in scores.loc[
            scores["paired_prediction_surface_opened"].astype(bool),key_columns
        ].itertuples(index=False,name=None)
    }
    _require(len(original_open)==283 and len(repaired_open)==int(base["paired_prediction_surfaces_opened_cells"]),
             "Historical original open-cell cardinality or repaired opened count changed")
    lost_original_open=original_open-repaired_open
    added_repaired_open=repaired_open-original_open
    _require(len(scores)==288 and base["heldout_taxa"]==12
             and base["heldout_cells_expected"]==288
             and base["heldout_cells_audited"]==288
             and base["reference_cells_frozen"]==24
             and base["reference_cells_unresolved"]==0
             and base.get("process_knockout_opened") is False
             and base.get("procedure_selected_from_heldout_outcome") is False
             and base.get("M_selected_from_heldout_outcome") is False
             and base.get("heldout_taxa_replaced") is False,
             "Repaired-source one-shot sensitivity denominator/selection drift")
    counts=scores["paired_state"].value_counts().to_dict()
    _require(base["paired_crosscheck_attention_required"]==counts.get("paired_crosscheck_attention_required",0),
             "Heldout paired-state attention count differs")
    _require(base["paired_prediction_surfaces_opened_cells"]+
             base["paired_prediction_surfaces_kept_closed_cells"]==288,
             "Repaired heldout 288-cell denominator incomplete")

    alerts=sorted(scores.loc[
        scores["paired_state"].astype(str)=="paired_crosscheck_attention_required","taxon"
    ].unique().tolist())
    _require(set(alerts).issubset({c["taxon"] for c,_ in models}),"Attention taxa outside frozen 12")

    full_comparability=(len(lost_original_open)==0)
    robust_to_source_completeness=(len(alerts)==0 and full_comparability)
    base.update({
      "result_version":FINAL_RESULT,
      "terminal_class":"postfreeze_source_completeness_sensitivity",
      "source_arm":"repaired_2026-08-01_10215_parquet_files",
      "historical_source_arm":"original_2026-08-01_9705_parquet_files",
      "historical_endpoint_id":ORIGINAL_ENDPOINT,
      "historical_endpoint_fingerprint":historical["final_endpoint_fingerprint"],
      "historical_heldout_taxa_with_attention":0,
      "repaired_heldout_taxa_with_attention":len(alerts),
      "repaired_heldout_taxa_with_attention_names":alerts,
      "historical_heldout_opened_cells":283,
      "source_completeness_0_of_12_robust":robust_to_source_completeness,
      "historical_original_opened_cells_retained":283-len(lost_original_open),
      "historical_original_opened_cells_lost":len(lost_original_open),
      "historical_original_opened_cells_lost_keys":[
          {"taxon":taxon,"M_km":m,"procedure":procedure}
          for taxon,m,procedure in sorted(lost_original_open)
      ],
      "newly_evaluable_repaired_cells":len(added_repaired_open),
      "full_original_283_cell_evaluability_preserved":full_comparability,
      "historical_signed_288_cells_sha256":hashlib.sha256(historical_cells_raw).hexdigest(),
      "historical_result_replaced":False,
      "source_completeness_is_new_independent_replication":False,
      "counts_as_empirical_conclusion":False,
      "counts_as_empirical_evidence":False,
      "empirical_ledger_increment":0,
      "do_not_recount_same_endpoint":True,
      "postfreeze_reference_fit_audit_sha256":hashlib.sha256(ref_fit_raw).hexdigest(),
      "postfreeze_heldout_fit_audit_sha256":hashlib.sha256(heldout_fit_raw).hexdigest(),
      "postfreeze_reference_summary_sha256":hashlib.sha256(ref_raw).hexdigest(),
      "postfreeze_reference_table_sha256":hashlib.sha256(table_raw).hexdigest(),
      "comparison_to_historical_original": "original original-source 0/12 vs repaired source-retrospective sensitivity",
      "submission_status":"HOLD_FOR_SENSITIVITY_REVIEW",
      "claim_strength":"retrospective_upstream_source_completeness_robustness_not_new_independent_biological_confirmation",
    })
    base["status"]=(
        "historical_0of12_not_robust_to_repaired_source"
        if alerts else (
            "historical_0of12_robust_to_repaired_source"
            if full_comparability else "repaired_source_no_attention_but_original_283_cell_coverage_decreased"
        )
    )
    base["final_endpoint_fingerprint"]=hashlib.sha256(
        (base["cells_sha256"]+base["reference_summary_sha256"]+
         base["reference_table_sha256"]+historical["final_endpoint_fingerprint"]).encode("utf-8")
    ).hexdigest()
    a.out_final.write_text(json.dumps(base,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:base[k] for k in ("result_version","terminal_class","status",
       "repaired_heldout_taxa_with_attention","paired_prediction_surfaces_opened_cells",
       "paired_prediction_surfaces_kept_closed_cells","empirical_ledger_increment")},sort_keys=True))

if __name__=="__main__":main()
