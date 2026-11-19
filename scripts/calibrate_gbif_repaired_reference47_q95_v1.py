#!/usr/bin/env python3
"""Recalibrate exact 24 q95 reference ceilings after 47 repaired-GBIF refits.

The historical core19 Schoener-D and nearest-rank q95 implementation is reused
unchanged. Only after 47 signed fits and all 24 pre-D eligibility cells pass
n>=30 does this script open source-paired scores. It never opens heldout labels.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))

from scripts.audit_gbif_repaired_reference47_preD_v1 import (
    checked_reference_fits, ORIGINAL_CORE19_RESULT, CORE19_CONTRACT, OUTPUT_VERSION
)

RESULT_VERSION="284b.gbif_repaired_reference47_q95_calibration.v1"
REVIEWED_PRED_VERSION="product_b_same_target_successor_pairing_calibration_core19_v0.4"
REVIEWED_PRE_D_VERSION="product_b_same_target_successor_reference_feasibility_core19_v0.4"

def check_calibration_gate(feas:dict,feas_raw:bytes,fit:dict,fit_raw:bytes):
    if (feas.get("result_version")!=OUTPUT_VERSION
        or feas.get("core19_contract_version")!=CORE19_CONTRACT
        or feas.get("repaired_GBIF_source_arm")!="repaired_2026-08-01_10215_parquet_files"
        or feas.get("repaired_source_fit_audit_sha256")!=hashlib.sha256(fit_raw).hexdigest()
        or feas.get("repaired_source_fit_taxa")!=47
        or feas.get("repaired_source_fit_cells")!=2256
        or feas.get("sampling_pass_taxa")!=47
        or feas.get("candidate_pair_cells")!=1128
        or feas.get("reference_cells_expected")!=24
        or feas.get("minimum_eligible_taxa_per_procedure_M")!=30
        or feas.get("reference_cells_authorized_to_open_discordance")!=24
        or feas.get("reference_cells_unresolved_pre_discordance")!=0):
        raise RuntimeError("Not all 24 predeclared reference q95 cells reached n>=30 before D")
    for flag in ("paired_prediction_surfaces_read","schoener_d_computed",
                 "reference_ceiling_computed","reference_q95_recalibrated",
                 "heldout_12_paired_discordance_read","heldout12_repaired_sensitivity_opened"):
        if feas.get(flag) is not False:
            raise RuntimeError("Pre-D reference feasibility already opened outcome: "+flag)
    if feas.get("empirical_ledger_increment")!=0:
        raise RuntimeError("Pre-D eligibility was misclassified as biological evidence")
    if (fit.get("schema")!="284b.gbif_repaired_reference47_source_fit_audit.v1"
        or fit.get("status")!="ALL_47_REPAIRED_REFERENCE_SOURCE_FITS_INTEGRITY_VERIFIED_NO_Q95"
        or fit.get("reference_taxa_verified")!=47
        or fit.get("fit_cells_expected")!=2256
        or fit.get("calibration_24_q95_opened") is not False
        or fit.get("heldout12_paired_discordance_opened") is not False):
        raise RuntimeError("Unverified signed reference source fits cannot recalibrate q95")
    if (len(feas.get("reference_cells",[]))!=24
        or len({(r["M_km"],r["procedure"]) for r in feas["reference_cells"]})!=24
        or any(r.get("discordance_opening_authorized") is not True
               or r.get("eligible_distinct_taxa_pre_discordance",0)<30 for r in feas["reference_cells"])):
        raise RuntimeError("Pre-D approved reference cell universe is incomplete")
    return hashlib.sha256(feas_raw).hexdigest()

def main():
    import numpy as np,pandas as pd
    from scripts.calibrate_same_target_successor_pairing_core19_v0_4 import main as reviewed_calibrate

    ap=argparse.ArgumentParser()
    ap.add_argument("--fit-root",type=Path,required=True)
    ap.add_argument("--fit-audit",type=Path,required=True)
    ap.add_argument("--preD",type=Path,required=True)
    ap.add_argument("--out-cells",type=Path,required=True)
    ap.add_argument("--out-reference",type=Path,required=True)
    ap.add_argument("--out-summary",type=Path,required=True)
    args=ap.parse_args()
    fit_raw=args.fit_audit.read_bytes()
    fit=json.loads(fit_raw)
    feas_raw=args.preD.read_bytes()
    feas=json.loads(feas_raw)
    preD_sha=check_calibration_gate(feas,feas_raw,fit,fit_raw)
    refs=checked_reference_fits(args.fit_root,fit)

    args.out_summary.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gbif_repaired_reference47_q95_") as work:
        temp=Path(work)
        root=temp/"original_core19_contract_view"
        for contract,source in refs:
            dest=root/f"taxon_{contract['taxon_index']:02d}"
            shutil.copytree(source,dest)
            adapted=dict(contract)
            adapted["result_version"]=ORIGINAL_CORE19_RESULT
            adapted["gbif_repaired_q95_provenance_adapter_only"]=True
            adapted["gbif_original_repaired_fit_result"]=contract["result_version"]
            (dest/"contract.json").write_text(json.dumps(adapted,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        original_feas=dict(feas)
        original_feas["result_version"]=REVIEWED_PRE_D_VERSION
        feas_path=temp/"reviewed_core19_preD.json"
        feas_path.write_text(json.dumps(original_feas,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        orig_argv=sys.argv[:]
        sys.argv=["calibrate_same_target_successor_pairing_core19_v0_4.py",
             "--input-root",str(root),"--feasibility",str(feas_path),
             "--output-cells",str(args.out_cells),
             "--output-reference",str(args.out_reference),
             "--output-summary",str(args.out_summary)]
        try:reviewed_calibrate()
        finally:sys.argv[:]=orig_argv

    summary=json.loads(args.out_summary.read_text(encoding="utf-8"))
    if (summary.get("result_version")!=REVIEWED_PRED_VERSION
        or summary.get("sampling_pass_taxa_in_audit")!=47
        or summary.get("paired_cells_expected")!=1128
        or summary.get("reference_cells_expected")!=24
        or summary.get("minimum_distinct_calibration_taxa_per_reference_cell")!=30
        or summary.get("reference_quantile")!=0.95
        or summary.get("quantile_method")!="nearest_rank"
        or summary.get("reference_cells_frozen")!=24
        or summary.get("reference_cells_unresolved")!=0
        or summary.get("full_reference_matrix_available") is not True
        or summary.get("heldout_12_paired_discordance_read") is not False
        or summary.get("process_knockout_opened") is not False
        or summary.get("counts_as_empirical_conclusion") is not False):
        raise RuntimeError("Restored GBIF failed reviewed fixed 24-q95 reference calibration rule")
    cells=pd.read_csv(args.out_cells);ceilings=pd.read_csv(args.out_reference)
    if len(cells)!=1128 or len(ceilings)!=24:
        raise RuntimeError("Repaired calibration row denominators differ from original")
    if (not ceilings["reference_state"].eq("reference_ceiling_frozen").all()
        or not ceilings["minimum_required_taxa"].eq(30).all()
        or not ceilings["quantile"].eq(.95).all()
        or not ceilings["quantile_method"].eq("nearest_rank").all()
        or not ceilings["authorized_distinct_calibration_taxa"].ge(30).all()):
        raise RuntimeError("Repaired q95 reference thresholds not all independently qualified")
    q=pd.to_numeric(ceilings["one_minus_schoener_d_reference_ceiling"],errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(q).all() or (q<0).any() or (q>1).any():
        raise RuntimeError("Invalid restored-GBIF reference ceiling")
    summary.update({
        "result_version":RESULT_VERSION,
        "source_arm":"repaired_2026-08-01_10215_parquet_files",
        "original_historical_source_manifest_sha256":"1b5b2dde8a23e78beafac1d122830e0552c2fbdac4086e9d9d8c161814a7163e",
        "repaired_source_fit_audit_sha256":hashlib.sha256(fit_raw).hexdigest(),
        "repaired_preD_sha256":preD_sha,
        "original_scientific_quantile_and_adequacy_implementation_unchanged":True,
        "new_independent_biological_confirmation":False,
        "heldout12_repaired_source_outcomes_opened":False,
        "empirical_ledger_increment":0,
        "submission_status":"HOLD",
    })
    args.out_summary.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:summary[k] for k in ("result_version","reference_cells_frozen",
                  "reference_cells_unresolved","heldout12_repaired_source_outcomes_opened",
                  "empirical_ledger_increment")}))

if __name__=="__main__":main()
