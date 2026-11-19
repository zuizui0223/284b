#!/usr/bin/env python3
"""Metadata-first pre-D audit of restored-GBIF original 47-reference fits.

The reviewed core19 reference-feasibility method is reused without altering
scientific decisions, score vectors, fold metrics or model/procedure rules.
This step NEVER computes between-source D, opens heldout scores, or calibrates q95.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.append(str(ROOT/"legacy/pre_level_a_focus"))

SOURCE_RESULT="284b.gbif_repaired_reference47_fixed_old_centers_fit_v1"
ORIGINAL_CORE19_RESULT="product_b_same_target_successor_core19_layer1_fit_taxon_v0.4"
CORE19_CONTRACT="product_b_same_target_core19_requalification_v0.4"
AUDIT_RESULT="284b.gbif_repaired_reference47_source_fit_audit.v1"
OUTPUT_VERSION="284b.gbif_repaired_reference47_preD_feasibility.v1"

def checked_reference_fits(source_root:Path,summary:dict):
    if (summary.get("schema")!=AUDIT_RESULT
        or summary.get("status")!="ALL_47_REPAIRED_REFERENCE_SOURCE_FITS_INTEGRITY_VERIFIED_NO_Q95"
        or summary.get("reference_taxa_expected")!=47
        or summary.get("reference_taxa_verified")!=47
        or summary.get("fit_cells_expected")!=2256
        or summary.get("fit_cells_sealed",-1)+summary.get("fit_cells_unresolved",-1)!=2256
        or summary.get("source_prediction_rows_integrity_verified")!=summary["fit_cells_sealed"]*2000
        or summary.get("source_arm")!="repaired_2026-08-01_10215_parquet_files"
        or summary.get("calibration_24_q95_opened") is not False
        or summary.get("heldout12_paired_discordance_opened") is not False
        or summary.get("empirical_ledger_increment")!=0):
        raise RuntimeError("Cannot preflight unverified 47-reference fixed-geometry source fits")

    reports=summary.get("taxa",[])
    if len(reports)!=47 or [v.get("index") for v in reports]!=list(range(47)):
        raise RuntimeError("Source-fit audit changed original reference taxon order")
    contracts=list(source_root.rglob("contract.json"))
    if len(contracts)!=47:raise RuntimeError("Expected exactly 47 independent fit artifacts")
    result={}
    for p in contracts:
        c=json.loads(p.read_text(encoding="utf-8"))
        i=c.get("taxon_index")
        if type(i) is not int or not 0<=i<47 or i in result:
            raise RuntimeError("Missing, duplicate or unrecognized reference source fit")
        recorded=reports[i]
        if (c.get("result_version")!=SOURCE_RESULT
            or c.get("core19_contract_version")!=CORE19_CONTRACT
            or c.get("panel")!="successor"
            or c.get("taxon")!=recorded["taxon"]
            or c.get("sealed_fit_cells")!=recorded["sealed_fit_cells"]
            or c.get("unresolved_fit_cells")!=recorded["unresolved_fit_cells"]
            or c.get("prediction_surface_sha256")!=recorded["model_prediction_sha256"]
            or c.get("original_12_block_centers_sha256")!=recorded["original_geometry_sha256"]
            or c.get("source_modes")!=["PRESERVED_SPECIMEN","HUMAN_OBSERVATION"]
            or c.get("original_signed_comparison_frames_unchanged") is not True
            or c.get("background_rows_resampled_during_refit") is not False
            or c.get("posthoc_prediction_row_drop_used") is not False):
            raise RuntimeError("Reference source fit differs from signed 47-taxon model audit")
        for key in ("paired_discordance_computed","reference_ceiling_opened_or_read",
                    "heldout_pairing_opened","process_knockout_computed","counts_as_empirical_conclusion"):
            if c.get(key) is not False:
                raise RuntimeError("Source model fit crossed reference or heldout endpoint")
        pred=p.parent/"sealed_prediction_surfaces.parquet"
        if not pred.is_file() or hashlib.sha256(pred.read_bytes()).hexdigest()!=recorded["model_prediction_sha256"]:
            raise RuntimeError("Prediction surface bytes differ from signed source-fit audit")
        result[i]=(c,p.parent)
    if set(result)!=set(range(47)):
        raise RuntimeError("Not every original reference taxon has a signed model")
    return [result[i] for i in range(47)]

def main():
    from scripts.audit_same_target_successor_reference_feasibility_core19_v0_4 import main as reviewed_core19_preD
    from scripts.core19_v0_4_adapter_utils import adapt_core19_successor_root

    ap=argparse.ArgumentParser()
    ap.add_argument("--input-root",type=Path,required=True)
    ap.add_argument("--source-fit-audit",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    audit_bytes=args.source_fit_audit.read_bytes()
    audit=json.loads(audit_bytes)
    refs=checked_reference_fits(args.input_root,audit)

    with tempfile.TemporaryDirectory(prefix="gbif_reference47_preD_") as temp:
        temp=Path(temp);root=temp/"relabelled_source_fits"
        for contract,folder in refs:
            dst=root/f"taxon_{contract['taxon_index']:02d}"
            shutil.copytree(folder,dst)
            new=dict(contract)
            new["result_version"]=ORIGINAL_CORE19_RESULT
            new["gbif_repaired_preD_provenance_adapter_only"]=True
            new["gbif_repaired_original_result_version"]=SOURCE_RESULT
            (dst/"contract.json").write_text(json.dumps(new,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        out=temp/"preD.json"
        original_argv=sys.argv[:]
        sys.argv=["audit_same_target_successor_reference_feasibility_core19_v0_4.py",
                  "--input-root",str(root),"--output",str(out)]
        try: reviewed_core19_preD()
        finally:sys.argv[:]=original_argv
        feasibility=json.loads(out.read_text(encoding="utf-8"))
    if (feasibility.get("result_version")!="product_b_same_target_successor_reference_feasibility_core19_v0.4"
        or feasibility.get("sampling_pass_taxa")!=47
        or feasibility.get("candidate_pair_cells")!=1128
        or feasibility.get("reference_cells_expected")!=24
        or feasibility.get("minimum_eligible_taxa_per_procedure_M")!=30):
        raise RuntimeError("Reviewed 47-reference pre-D feasibility denominators changed")
    for key in ("paired_prediction_surfaces_read","schoener_d_computed",
                "reference_ceiling_computed","heldout_12_paired_discordance_read","process_knockout_opened"):
        if feasibility.get(key) is not False:
            raise RuntimeError("Reviewed pre-D implementation opened a forbidden score endpoint")
    feasibility.update({
        "result_version":OUTPUT_VERSION,
        "repaired_source_fit_audit_sha256":hashlib.sha256(audit_bytes).hexdigest(),
        "repaired_GBIF_source_arm":"repaired_2026-08-01_10215_parquet_files",
        "repaired_source_fit_taxa":47,
        "repaired_source_fit_cells":2256,
        "model_science_or_adequacy_changed":False,
        "reference_q95_recalibrated":False,
        "heldout12_repaired_sensitivity_opened":False,
        "new_independent_biological_confirmation":False,
        "empirical_ledger_increment":0,
        "submission_status":"HOLD",
    })
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(feasibility,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:feasibility[k] for k in ("result_version","reference_cells_expected",
                "reference_cells_authorized_to_open_discordance","reference_cells_unresolved_pre_discordance",
                "empirical_ledger_increment")},sort_keys=True))

if __name__=="__main__":main()
