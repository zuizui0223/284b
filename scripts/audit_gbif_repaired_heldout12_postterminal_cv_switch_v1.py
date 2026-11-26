#!/usr/bin/env python3
"""Explain the four signed old/restored Level A adequacy-state transitions.

Technical retrospective diagnosis only. Folds and scientific thresholds are
read from the original 47/12 core19 model artifacts; no new model is fitted,
no source-paired prediction surface is evaluated, and the sealed 0/12 and
coverage-limited source-completeness endpoints remain unchanged.
"""
from __future__ import annotations
import argparse,csv,io,json,math,hashlib,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))
FIT_CONTRACT=ROOT/"config/product_b_same_target_source_model_fit_contract_v0_1.json"
MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
OLD_VERSION="product_b_same_target_heldout_core19_layer1_fit_taxon_v0.4"
NEW_VERSION="284b.gbif_repaired_heldout12_fixed_old_centers_fit_v1"

def require(ok,what):
    if not ok: raise RuntimeError(what)
def key(r):
    return (str(r["taxon"]),int(r["M_km"]),str(r["procedure"]))

def load_folds(path:Path):
    with path.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    keys={}
    for row in rows:
        code=(str(row["source"]),int(row["M_km"]),str(row["procedure"]))
        keys.setdefault(code,[]).append(row)
    for k,group in keys.items():
        seq=[int(r["fold"]) for r in group]
        require(len(seq)==len(set(seq)),"Duplicate outer-fold evidence for one source/method/M")
    return keys

def adequacy(rowset,settings):
    from product_b_v5.same_target_pairing import evaluate_prediction_adequacy
    values=[]
    for r in rowset:
        try:values.append(float(r["presence_rank"]))
        except (ValueError,KeyError):values.append(float("nan"))
    return evaluate_prediction_adequacy(
        values,
        expected_folds=int(settings["outer_folds"]),
        chance_auc=float(settings["chance_auc"]),
        minimum_auc_margin=float(settings["minimum_auc_margin"]),
        auc_sem_multiplier=float(settings["auc_sem_multiplier"])
    )

def audit(coverage:dict,historical:dict,repaired:dict,source_audit:dict,manifest:dict,
          original_fit_root:Path,repaired_fit_root:Path):
    require(coverage.get("status")=="POSTTERMINAL_EXACT_288_CELL_COVERAGE_AUDITED_NO_INDEPENDENT_REPLICATION"
            and coverage.get("historical_opened_cells")==283
            and coverage.get("restored_opened_cells")==285
            and coverage.get("original_opened_lost")==1
            and coverage.get("newly_opened_restored_cells")==3
            and coverage.get("empirical_ledger_increment")==0,
            "Four fixed signed source-adequacy switch cells have not been independently audited")
    require(repaired.get("result_version")=="284b.gbif_repaired_source_completeness_heldout12_sensitivity.v1"
            and repaired.get("final_endpoint_fingerprint")==coverage.get("restored_endpoint_fingerprint")
            and historical.get("final_endpoint_fingerprint")==coverage.get("historical_endpoint_fingerprint"),
            "Original/repaired one-shot sensitivity fingerprint changed")
    require(manifest.get("frozen_taxon_count")==12 and len(manifest.get("entries",[]))==12
            and source_audit.get("taxa_qualified_repaired_raw_parity")==12,
            "Original 12 taxon and source input populations differ")
    original_geometry=json.loads(
        (ROOT/"results/gbif_original_heldout12_geometry_complete_v1.json").read_text(encoding="utf-8")
    )
    require(original_geometry.get("status")=="ALL_12_ORIGINAL_SIGNED_HELDOUT_GEOMETRIES_VERIFIED_NO_REPAIRED_MODELS"
            and original_geometry.get("original_heldout_geometry_exactly_reproduced")==12
            and len(original_geometry.get("taxa",[]))==12,
            "Signed original 12-taxon center geometry receipt not verified")
    settings=json.loads(FIT_CONTRACT.read_text(encoding="utf-8"))["prediction_adequacy"]
    require(settings["outer_folds"]==4 and settings["chance_auc"]==0.5
            and settings["minimum_auc_margin"]==0.01
            and settings["auc_sem_multiplier"]==1,
            "Original outer CV adequacy science changed")
    transition=coverage["transition_cells"]
    require(len(transition)==4
            and {r["transition"] for r in transition}=={"original_open_lost","restored_newly_open"},
            "Original source-flip diagnostic scope changed")
    switches={key(r):r for r in transition}
    require(len(switches)==4
            and sum(r["transition"]=="original_open_lost" for r in switches.values())==1,
            "Original/restored matched adequately diagnosed keys not exactly four")
    historical_unresolved={key(r):r for r in historical["heldout"]["unresolved_cells"]}
    seen_index={r["taxon"]:r["index"] for r in manifest["entries"]}
    require(len(seen_index)==12,"Original fixed taxon inventory changed")

    allrows=[]
    for taxon in sorted({r["taxon"] for r in transition}):
        idx=seen_index[taxon];entry=manifest["entries"][idx]
        require(entry["taxon"]==taxon and source_audit["per_taxon_source_mode_result"][idx]["taxon"]==taxon,
                "Original/repaired historical taxonomic concept changed")
        old_dir=original_fit_root/str(idx)
        new_dir=repaired_fit_root/str(idx)
        oc=json.loads((old_dir/"contract.json").read_text(encoding="utf-8"))
        nc=json.loads((new_dir/"contract.json").read_text(encoding="utf-8"))
        require(oc["result_version"]==OLD_VERSION and nc["result_version"]==NEW_VERSION
                and oc["taxon"]==nc["taxon"]==taxon
                and oc["taxon_index"]==nc["taxon_index"]==idx
                and oc["specieskey"]==nc["specieskey"]==entry["historical_specieskey"]
                and oc["core19_frame_sha256_by_M"]==nc["core19_frame_sha256_by_M"]
                and oc["core19_preflight_receipt_sha256"]==nc["core19_preflight_receipt_sha256"]
                and original_geometry["taxa"][idx]["taxon"]==taxon
                and nc["original_12_block_centers_sha256"]==original_geometry["taxa"][idx]["original_center_sha256"],
                "Historical/restored fit ZIPs did not hold the same source, taxon, spatial centers and frozen M rows")
        originals=load_folds(old_dir/"outer_cv_fold_metrics.csv")
        restorations=load_folds(new_dir/"outer_cv_fold_metrics.csv")
        expected=source_audit["per_taxon_source_mode_result"][idx]
        old_n=expected["original_signed_source_thinned_model_presence"]
        new_n=expected["repaired_source_thinned_presence"]
        require(nc["repaired_source_thinned_presence_count"]==new_n,
                "Original/restored thinned source input counts changed")
        for t in [r for r in transition if r["taxon"]==taxon]:
            k=key(t)
            original_invalid=historical_unresolved.get(k)
            should_old_open=t["transition"]=="original_open_lost"
            require((original_invalid is None)==should_old_open,
                    "Historical opened/closed cell does not agree with original endpoint")
            for mode in MODES:
                cell=(mode,k[1],k[2])
                old=adequacy(originals.get(cell,[]),settings)
                new=adequacy(restorations.get(cell,[]),settings)
                require(new.adequate==bool(t["preserved_specimen_adequate"] if mode==MODES[0] else t["human_observation_adequate"]),
                        "Recomputed repaired source answer adequacy disagrees with signed paired state")
                if should_old_open:
                    require(old.adequate,"Original source model should have qualified for this lost opened cell")
                if original_invalid is not None and mode==MODES[0] and "preserved_specimen" in original_invalid["reason"]:
                    require(not old.adequate,"Original specimen inadequacy diagnosis disagrees")
                if original_invalid is not None and mode==MODES[1] and "human_observation" in original_invalid["reason"]:
                    require(not old.adequate,"Original human inadequate diagnosis disagrees")
                allrows.append({
                    "taxon":taxon,"taxon_index":idx,"M_km":k[1],"procedure":k[2],
                    "transition":t["transition"],"source_mode":mode,
                    "old_admitted_thinned_n":old_n[mode],
                    "repaired_admitted_thinned_n":new_n[mode],
                    "old_adequate":bool(old.adequate),
                    "repaired_adequate":bool(new.adequate),
                    "old_n_folds":int(old.n_folds),
                    "repaired_n_folds":int(new.n_folds),
                    "old_mean_presence_rank":old.mean_presence_rank,
                    "repaired_mean_presence_rank":new.mean_presence_rank,
                    "old_sem_presence_rank":old.sem_presence_rank,
                    "repaired_sem_presence_rank":new.sem_presence_rank,
                    "old_lower_evidence_bound":old.lower_evidence_bound,
                    "repaired_lower_evidence_bound":new.lower_evidence_bound,
                    "frozen_mean_floor":old.mean_floor,
                    "frozen_chance_floor":old.chance_floor,
                    "old_failure_reasons":list(old.reasons),
                    "repaired_failure_reasons":list(new.reasons),
                })
    require(len(allrows)==8,"All four changed paired cells require both original and repaired source-fold evidence")
    flipped=[r for r in allrows if r["old_adequate"]!=r["repaired_adequate"]]
    require(len(flipped)==4,"Exactly four original/repaired source adequacy transitions should explain changed paired opening")
    for t in transition:
        rows=[r for r in allrows if key(r)==key(t)]
        require(len(rows)==2 and sum(r["old_adequate"]!=r["repaired_adequate"] for r in rows)==1,
                "Each original-to-repaired cell transition must be explained by exactly one source flip")
    return {
        "schema":"284b.gbif_repaired_heldout12_postterminal_cv_adequacy_switches.v1",
        "status":"SIGNED_4_CELL_SOURCE_ADEQUACY_TRANSITIONS_EXPLAINED_NO_SCIENCE_CHANGED",
        "model_source_flip_taxa":len({r["taxon"] for r in transition}),
        "paired_cells_with_changed_evaluability":4,
        "source_specific_adequacy_state_flips":len(flipped),
        "original_opened_lost":1,
        "newly_restored_opened":3,
        "frozen_adequacy_science":{"outer_folds":4,"chance_auc":0.5,"minimum_auc_margin":0.01,"auc_sem_multiplier":1},
        "source_cv_evidence":allrows,
        "terminal_result_changed_or_reopened":False,
        "model_retrained_or_procedure_reselected":False,
        "repaired_0_of_12_coverage_fully_robust":False,
        "independent_biological_evidence":False,
        "empirical_ledger_increment":0,
        "submission_status":"HOLD_FOR_SENSITIVITY_REVIEW",
        "historical_endpoint_fingerprint":historical["final_endpoint_fingerprint"],
        "repaired_endpoint_fingerprint":repaired["final_endpoint_fingerprint"]
    }

def main():
    p=argparse.ArgumentParser()
    for flag in ("--coverage","--historical","--repaired","--source-audit","--manifest",
                 "--old-fit-root","--new-fit-root","--out"):
        p.add_argument(flag,type=Path,required=True)
    a=p.parse_args()
    read=lambda path:json.loads(path.read_text(encoding="utf-8"))
    result=audit(read(a.coverage),read(a.historical),read(a.repaired),read(a.source_audit),
                 read(a.manifest),a.old_fit_root,a.new_fit_root)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","paired_cells_with_changed_evaluability",
                                           "source_specific_adequacy_state_flips","repaired_0_of_12_coverage_fully_robust")}))
if __name__=="__main__":main()
