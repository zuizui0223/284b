#!/usr/bin/env python3
"""After-terminal old-vs-repaired source-score and q95 threshold drift audit.

This is a descriptive, SHA-attested comparison of two ALREADY UNSEALED,
non-independent sensitivity endpoints. No new model selection, paired-score
opening, reference cutoff fitting or biological evidence is permitted.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,math,statistics
from pathlib import Path

OLD_ENDPOINT="same_target_cross_source_reproducibility_heldout12_core19_v0_4"
NEW_RESULT="284b.gbif_repaired_source_completeness_heldout12_sensitivity.v1"
REFERENCE_KEY="one_minus_schoener_d_reference_ceiling"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def read_csv(data:bytes):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))

def cell_key(r):
    return (str(r["taxon"]),int(r["M_km"]),str(r["procedure"]))

def ref_key(r):
    return (int(r["M_km"]),str(r["procedure"]))

def keyed(rows,key_fn):
    out={}
    for row in rows:
        key=key_fn(row)
        require(key not in out,"CSV contains duplicate taxon/procedure/M or reference key")
        out[key]=row
    return out

def opened(row):
    val=str(row["paired_prediction_surface_opened"]).strip().lower()
    require(val in ("true","false"),"Missing or malformed signed opened-cell Boolean")
    return val=="true"

def summary_delta(values):
    require(len(values)>0 and all(math.isfinite(x) for x in values),"Nonfinite or empty signed metric shift")
    sorted_values=sorted(values)
    return {
      "n":len(values),
      "median":statistics.median(sorted_values),
      "minimum":sorted_values[0],
      "maximum":sorted_values[-1],
      "positive_count":sum(x>1e-12 for x in sorted_values),
      "negative_count":sum(x< -1e-12 for x in sorted_values),
      "zero_with_tolerance_1e_12_count":sum(abs(x)<=1e-12 for x in sorted_values),
    }

def audit(old:dict,new:dict,old_csv:bytes,new_csv:bytes,
          old_reference_csv:bytes,new_reference_csv:bytes)->dict:
    sha=lambda b:hashlib.sha256(b).hexdigest()
    require(old.get("endpoint_id")==OLD_ENDPOINT
            and old.get("heldout",{}).get("paired_prediction_surfaces_opened_cells")==283
            and old.get("heldout",{}).get("paired_crosscheck_attention_required")==0
            and old.get("do_not_recount_same_endpoint") is True,
            "Historical original endpoint is not exact signed Level A 0/12")
    require(new.get("result_version")==NEW_RESULT
            and new.get("terminal_class")=="postfreeze_source_completeness_sensitivity"
            and new.get("historical_endpoint_fingerprint")==old.get("final_endpoint_fingerprint")
            and new.get("historical_signed_288_cells_sha256")==old.get("cells_sha256")
            and new.get("historical_original_opened_cells_lost")==1
            and new.get("newly_evaluable_repaired_cells")==3
            and new.get("historical_original_opened_cells_retained")==282
            and new.get("paired_prediction_surfaces_opened_cells")==285
            and new.get("paired_crosscheck_attention_required")==0
            and new.get("reference_cells_frozen")==24
            and new.get("empirical_ledger_increment")==0
            and new.get("counts_as_empirical_evidence") is False
            and new.get("status")=="repaired_source_no_attention_but_original_283_cell_coverage_decreased",
            "Repaired one-shot source-completeness result is not the expected signed coverage-limited conclusion")
    require(sha(old_csv)==old["cells_sha256"]
            and sha(new_csv)==new["cells_sha256"]
            and sha(old_reference_csv)==old["reference_table_sha256"]
            and sha(new_reference_csv)==new["reference_table_sha256"],
            "Original or repaired independent terminal/threshold CSV SHA-256 changed")
    old_cells=keyed(read_csv(old_csv),cell_key)
    new_cells=keyed(read_csv(new_csv),cell_key)
    require(len(old_cells)==len(new_cells)==288
            and set(old_cells)==set(new_cells)
            and len({k[0] for k in old_cells})==12,
            "288 fixed taxon × method × M original/repaired pairing keys not identical")

    old_ref=keyed(read_csv(old_reference_csv),ref_key)
    new_ref=keyed(read_csv(new_reference_csv),ref_key)
    require(len(old_ref)==len(new_ref)==24 and set(old_ref)==set(new_ref),
            "24 original and repaired reference cells not keyed identically")
    require(set(k[1] for k in old_ref)==set(k[1] for k in new_ref)
            and {k[0] for k in old_ref}=={150,300,500},
            "Original three-M q95 reference universe changed")
    ref_delta=[]
    for key in sorted(old_ref):
        a=old_ref[key];b=new_ref[key]
        require(a["reference_state"]==b["reference_state"]=="reference_ceiling_frozen",
                "An original or repaired q95 is no longer frozen")
        x=float(a[REFERENCE_KEY]);y=float(b[REFERENCE_KEY])
        require(math.isfinite(x) and math.isfinite(y) and 0<=x<=1 and 0<=y<=1,
                "Original or restored reference threshold invalid")
        ref_delta.append(y-x)

    old_open={k for k,v in old_cells.items() if opened(v)}
    new_open={k for k,v in new_cells.items() if opened(v)}
    require(len(old_open)==283 and len(new_open)==285 and len(old_open&new_open)==282
            and len(old_open-new_open)==1 and len(new_open-old_open)==3,
            "Historical source-opened cell coverage transition differs from signed endpoint")
    paired_drifts=[]
    paired_margin_drifts=[]
    near=[]
    per_taxon={}
    for key in sorted(old_open&new_open):
        a=old_cells[key];b=new_cells[key]
        d_old=float(a["one_minus_schoener_d"])
        d_new=float(b["one_minus_schoener_d"])
        margin_old=float(a["discordance_minus_reference"])
        margin_new=float(b["discordance_minus_reference"])
        require(all(math.isfinite(x) for x in (d_old,d_new,margin_old,margin_new))
                and 0<=d_old<=1 and 0<=d_new<=1,
                "Original/repaired opened source-paired score nonfinite")
        require(a["paired_state"]==b["paired_state"]=="paired_crosscheck_consistent"
                and margin_old<0 and margin_new<0,
                "Common original/repaired cell is no longer q95-consistent")
        paired_drifts.append(d_new-d_old)
        paired_margin_drifts.append(margin_new-margin_old)
        per_taxon.setdefault(key[0],[]).append(d_new-d_old)
    all_new_margins=[]
    for key in sorted(new_open):
        row=new_cells[key]
        margin=float(row["discordance_minus_reference"])
        require(math.isfinite(margin) and margin<0
                and row["paired_state"]=="paired_crosscheck_consistent",
                "A repaired eligible paired cell exceeds q95 or lacks finite margin")
        all_new_margins.append((margin,key))
    closest=max(all_new_margins,key=lambda x:x[0])
    for taxon in sorted(per_taxon):
        require(len(per_taxon[taxon])>0,"Original paired taxon unexpectedly not represented")
    return {
      "schema":"284b.gbif_repaired_heldout12_postterminal_model_score_threshold_drift.v1",
      "status":"SHA_VERIFIED_PAIRED_DISCORDANCE_AND_Q95_SOURCE_VERSION_DRIFT_DESCRIPTIVE_ONLY",
      "historical_opened_cells":283,
      "restored_opened_cells":285,
      "common_opened_cells":282,
      "original_opened_lost":1,
      "restored_newly_evaluable":3,
      "restored_q95_exceedances":0,
      "original_reference_q95_thresholds":24,
      "repaired_reference_q95_thresholds":24,
      "reference_q95_restored_minus_original":summary_delta(ref_delta),
      "common_cell_discordance_restored_minus_original":summary_delta(paired_drifts),
      "common_cell_q95_margin_restored_minus_original":summary_delta(paired_margin_drifts),
      "per_taxon_common_cell_discordance_delta_median":[
           {"taxon":taxon,"n_common_cells":len(vals),
            "median_restored_minus_original":statistics.median(vals)}
           for taxon,vals in sorted(per_taxon.items())
      ],
      "nearest_restored_q95_margin":{
          "taxon":closest[1][0],"M_km":closest[1][1],
          "procedure":closest[1][2],"discordance_minus_q95":closest[0]
      },
      "historical_signed_288_cell_sha256":sha(old_csv),
      "restored_signed_288_cell_sha256":sha(new_csv),
      "historical_signed_24_q95_sha256":sha(old_reference_csv),
      "restored_signed_24_q95_sha256":sha(new_reference_csv),
      "robustness_does_not_pass_full_283_cell_coverage_rule":True,
      "scientific_model_or_q95_recalculated_in_this_audit":False,
      "postfreeze_source_repair_is_independent_replication":False,
      "empirical_ledger_increment":0,
      "submission_status":"HOLD_FOR_SENSITIVITY_REVIEW",
      "historical_endpoint_fingerprint":old["final_endpoint_fingerprint"],
      "restored_endpoint_fingerprint":new["final_endpoint_fingerprint"],
    }

def main():
    p=argparse.ArgumentParser()
    for flag in ("--old-receipt","--new-receipt","--old-cells","--new-cells",
                 "--old-reference","--new-reference","--out"):
        p.add_argument(flag,type=Path,required=True)
    a=p.parse_args()
    r=audit(json.loads(a.old_receipt.read_text(encoding="utf-8")),
            json.loads(a.new_receipt.read_text(encoding="utf-8")),
            a.old_cells.read_bytes(),a.new_cells.read_bytes(),
            a.old_reference.read_bytes(),a.new_reference.read_bytes())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:r[k] for k in ("status","common_opened_cells",
                                      "reference_q95_restored_minus_original",
                                      "common_cell_discordance_restored_minus_original",
                                      "restored_q95_exceedances")},sort_keys=True))
if __name__=="__main__":main()
