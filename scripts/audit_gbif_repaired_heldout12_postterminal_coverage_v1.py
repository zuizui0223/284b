#!/usr/bin/env python3
"""Independent post-terminal audit of restored-GBIF Level A heldout coverage.

Cross-check the original signed 283/288 heldout-cell receipt against the
distinct source-restoration sensitivity terminal result and signed 288-row CSV.
This is a descriptive integrity audit of an ALREADY OPENED retrospective
sensitivity result. It cannot reopen or reclassify the one-shot endpoint.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
from collections import Counter

SOURCE_RESULT="284b.gbif_repaired_source_completeness_heldout12_sensitivity.v1"
SOURCE_STATUS="repaired_source_no_attention_but_original_283_cell_coverage_decreased"
OLD_ENDPOINT="same_target_cross_source_reproducibility_heldout12_core19_v0_4"
REPAIRED_ARM="repaired_2026-08-01_10215_parquet_files"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
MS=(150,300,500)
def require(flag,message):
    if not flag: raise RuntimeError(message)

def key_of(row):
    return str(row["taxon"]),int(row["M_km"]),str(row["procedure"])
def as_key_dict(k):
    return {"taxon":k[0],"M_km":k[1],"procedure":k[2]}

def audit(old:dict,new:dict,model_rows:list[dict],csv_bytes:bytes,reference:dict)->dict:
    require(old.get("endpoint_id")==OLD_ENDPOINT
            and old.get("result_version")=="product_b_same_target_heldout_final_core19_v0.4"
            and old.get("heldout",{}).get("taxa")==12
            and old["heldout"].get("cells_expected")==288
            and old["heldout"].get("paired_prediction_surfaces_opened_cells")==283
            and old["heldout"].get("paired_crosscheck_attention_required")==0
            and old.get("do_not_recount_same_endpoint") is True,
            "Historical signed 283/288 heldout endpoint changed")
    require(new.get("result_version")==SOURCE_RESULT
            and new.get("terminal_class")=="postfreeze_source_completeness_sensitivity"
            and new.get("source_arm")==REPAIRED_ARM
            and new.get("historical_endpoint_id")==OLD_ENDPOINT
            and new.get("historical_endpoint_fingerprint")==old.get("final_endpoint_fingerprint")
            and new.get("historical_signed_288_cells_sha256")==old.get("cells_sha256")
            and new.get("historical_heldout_opened_cells")==283
            and new.get("heldout_cells_expected")==288
            and new.get("heldout_cells_audited")==288
            and new.get("reference_cells_frozen")==24
            and new.get("reference_cells_unresolved")==0
            and new.get("historical_result_replaced") is False
            and new.get("counts_as_empirical_evidence") is False
            and new.get("counts_as_empirical_conclusion") is False
            and new.get("empirical_ledger_increment")==0,
            "Retrospective repaired-source terminal result invalid or double-counted")
    require(hashlib.sha256(csv_bytes).hexdigest()==new["cells_sha256"],
            "Signed 288-cell terminal CSV SHA-256 mismatch")
    require(new.get("reference_summary_sha256")==new.get("postfreeze_reference_summary_sha256")
            and new.get("reference_table_sha256")==new.get("postfreeze_reference_table_sha256"),
            "Final q95 reference SHA-256 provenance changed")
    require(reference.get("result_version")=="284b.gbif_repaired_reference47_q95_calibration.v1"
            and reference.get("reference_cells_frozen")==24
            and reference.get("reference_cells_unresolved")==0
            and reference.get("paired_cells_expected")==1128
            and reference.get("sampling_pass_taxa_in_audit")==47
            and reference.get("heldout12_repaired_source_outcomes_opened") is False
            and reference.get("empirical_ledger_increment")==0,
            "The separately calibrated repaired reference does not remain frozen")

    required={"taxon","M_km","procedure","both_final_fits_sealed",
              "preserved_specimen_adequate","human_observation_adequate",
              "reference_state","paired_prediction_surface_opened",
              "one_minus_schoener_d","frozen_reference_ceiling",
              "discordance_minus_reference","paired_state","reasons"}
    require(len(model_rows)==288 and all(required.issubset(row) for row in model_rows),
            "Repaired terminal 288-row schema/denominator invalid")
    observed={}
    proc_by_m={}
    for row in model_rows:
        key=key_of(row)
        require(key not in observed and key[1] in MS,"Duplicate/non-original heldout pairing cell key")
        require(row["both_final_fits_sealed"]=="True"
                and row["reference_state"]=="reference_ceiling_frozen",
                "Repaired final cell model or reference threshold became unresolved")
        observed[key]=row
        proc_by_m.setdefault(key[1],set()).add(key[2])
    require(len({x[0] for x in observed})==12 and all(len([k for k in observed if k[0]==t])==24 for t in {x[0] for x in observed}),
            "The original heldout 12 taxa must each retain 24 procedure/M cells")
    require(all(len(v)==8 for v in proc_by_m.values()) and len(proc_by_m)==3,
            "Heldout procedure × M model universe changed")

    old_unresolved=old["heldout"].get("unresolved_cells",[])
    require(len(old_unresolved)==5,"Historical original 5 unresolved cells not signed")
    old_closed={key_of(row) for row in old_unresolved}
    require(len(old_closed)==5 and old_closed.issubset(observed),
            "Original unresolved cell identifiers differ from prespecified 288 cells")
    original_opened=set(observed)-old_closed
    require(len(original_opened)==283,"Historical 283 original opened-cell identity proof failed")
    repaired_opened=set()
    repaired_closed=set()
    attention=set()
    margins=[]
    for key,row in observed.items():
        status=row["paired_prediction_surface_opened"]
        require(status in ("True","False"),"Repaired opening flag must be signed explicit Boolean")
        if status=="True":
            repaired_opened.add(key)
            require(row["paired_state"] in ("paired_crosscheck_consistent","paired_crosscheck_attention_required"),
                    "Opened repaired paired surface has invalid state")
            margin=float(row["discordance_minus_reference"])
            discordance=float(row["one_minus_schoener_d"])
            threshold=float(row["frozen_reference_ceiling"])
            require(all(map(math.isfinite,(margin,discordance,threshold)))
                    and 0<=discordance<=1 and 0<=threshold<=1
                    and math.isclose(margin,discordance-threshold,abs_tol=1e-10,rel_tol=0),
                    "Repaired opened source-paired D and q95 margin inconsistent")
            margins.append((margin,key,discordance,threshold))
            if row["paired_state"]=="paired_crosscheck_attention_required":
                attention.add(key)
        else:
            repaired_closed.add(key)
            require(row["paired_state"]=="paired_crosscheck_unresolved"
                    and not row["one_minus_schoener_d"].strip()
                    and not row["discordance_minus_reference"].strip(),
                    "Closed repaired source cell must not carry paired D or exceedance")
            require(row["preserved_specimen_adequate"]=="False"
                    or row["human_observation_adequate"]=="False",
                    "An otherwise adequate cell should not silently become unresolved")
    require(len(repaired_opened)==new["paired_prediction_surfaces_opened_cells"]
            and len(repaired_closed)==new["paired_prediction_surfaces_kept_closed_cells"],
            "Signed repaired pairing opening/closure totals differ from CSV")
    require(len(attention)==new["paired_crosscheck_attention_required"],
            "Repaired attention count differs from signed endpoint")
    lost=sorted(original_opened-repaired_opened)
    gained=sorted(repaired_opened-original_opened)
    common=original_opened&repaired_opened
    require(len(common)==new["historical_original_opened_cells_retained"]
            and len(lost)==new["historical_original_opened_cells_lost"]
            and len(gained)==new["newly_evaluable_repaired_cells"],
            "Historical vs restored source 288-key coverage transition mismatch")
    require([as_key_dict(x) for x in lost]==new["historical_original_opened_cells_lost_keys"],
            "Historical source-opened cell loss list changed")
    require(not attention and new["repaired_heldout_taxa_with_attention"]==0,
            "This report summarizes only the observed zero-exceedance terminal; use another version for changed results")
    require(new.get("status")==SOURCE_STATUS
            and new.get("source_completeness_0_of_12_robust") is False
            and len(lost)==1 and len(gained)==3,
            "One-shot terminal robust/coverage-limited classification mismatch")
    ranked=sorted(margins,key=lambda x:x[0],reverse=True)
    require(ranked and ranked[0][0]<0,
            "No q95 exceedance claim contradicts opened-cell score margins")

    changes=[]
    for label,keys in (("original_open_lost",lost),("restored_newly_open",gained)):
        for key in keys:
            r=observed[key]
            changes.append({
                "transition":label,
                **as_key_dict(key),
                "preserved_specimen_adequate":r["preserved_specimen_adequate"]=="True",
                "human_observation_adequate":r["human_observation_adequate"]=="True",
                "restored_pair_state":r["paired_state"],
                "restored_reasons":r["reasons"],
            })
    return {
       "schema":"284b.gbif_repaired_heldout12_postterminal_coverage_audit.v1",
       "status":"POSTTERMINAL_EXACT_288_CELL_COVERAGE_AUDITED_NO_INDEPENDENT_REPLICATION",
       "historical_opened_cells":283,
       "restored_opened_cells":len(repaired_opened),
       "original_opened_retained":len(common),
       "original_opened_lost":len(lost),
       "newly_opened_restored_cells":len(gained),
       "originally_unresolved_cells":5,
       "still_unresolved_restored_cells":len(repaired_closed),
       "q95_exceeding_restored_opened_cells":len(attention),
       "q95_recalibrated_reference_cells":24,
       "closest_signed_restored_cell":{
            **as_key_dict(ranked[0][1]),
            "discordance_minus_q95":ranked[0][0],
            "discordance":ranked[0][2],
            "q95":ranked[0][3],
       },
       "transition_cells":changes,
       "full_original_cell_coverage_preserved":False,
       "historical_0_of_12_source_completeness_fully_robust":False,
       "postfreeze_source_repair_is_not_independent_new_biological_evidence":True,
       "empirical_ledger_increment":0,
       "submission_status":"HOLD_FOR_SENSITIVITY_REVIEW",
       "historical_endpoint_fingerprint":old["final_endpoint_fingerprint"],
       "restored_endpoint_fingerprint":new["final_endpoint_fingerprint"],
       "restored_terminal_cells_sha256":new["cells_sha256"],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--historical",required=True,type=Path)
    p.add_argument("--restored",required=True,type=Path)
    p.add_argument("--restored-cells",required=True,type=Path)
    p.add_argument("--reference",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    b=args.restored_cells.read_bytes()
    raw=list(csv.DictReader(b.decode("utf-8").splitlines()))
    obj=audit(json.loads(args.historical.read_text(encoding="utf-8")),
              json.loads(args.restored.read_text(encoding="utf-8")),raw,b,
              json.loads(args.reference.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:obj[k] for k in ("status","historical_opened_cells","restored_opened_cells","original_opened_lost","newly_opened_restored_cells","q95_exceeding_restored_opened_cells","submission_status")},sort_keys=True))
if __name__=="__main__":main()
