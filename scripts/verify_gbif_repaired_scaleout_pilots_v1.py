#!/usr/bin/env python3
"""Fail-closed pre-scale gate: two independently completed repaired-GBIF pilots.

Reads only committed signed technical receipts. No new ecological outcomes.
"""
from pathlib import Path
import argparse,json

EXPECTED={
 "heldout_taxon":"Artemisia tridentata",
 "reference_taxon":"Abies grandis",
 "heldout_center":"b9a5db3a5e0324abfdd38626727c170911cfc8994321eb0d24e6d995cd088a15",
 "reference_center":"9eb19bf125fdd06c5e2b9ef901c869c23db6cd9aa88feb1305dffed79ff37f7e",
 "historical_manifest":"1b5b2dde8a23e78beafac1d122830e0552c2fbdac4086e9d9d8c161814a7163e",
}

def check(fit,drift,geometry,source,ref_source):
    def must(cond,message):
        if not cond:raise ValueError(message)
    must(fit.get("taxon")==EXPECTED["heldout_taxon"] and fit.get("taxon_index")==0,"wrong heldout taxon")
    must(fit.get("GBIF_source_arm")=="repaired_2026-08-01_10215_parquet_files","wrong repaired source")
    must(fit.get("original_12_block_centers_sha256")==EXPECTED["heldout_center"],"heldout center changed")
    must(fit.get("expected_fit_cells")==48 and fit.get("sealed_fit_cells")==48 and fit.get("unresolved_fit_cells")==0,"heldout fit incomplete")
    must(fit.get("source_modes")==["PRESERVED_SPECIMEN","HUMAN_OBSERVATION"],"source mode mismatch")
    must(fit.get("active_predictors")==[f"bio{i}" for i in range(1,20)] and fit.get("M_km")==[150,300,500] and fit.get("procedure_count")==8,"model design changed")
    must(fit.get("original_signed_comparison_frames_unchanged") is True and fit.get("background_rows_resampled_during_refit") is False and fit.get("posthoc_prediction_row_drop_used") is False,"comparison geometry changed")
    must(all(fit.get(k) is False for k in ("paired_discordance_computed","heldout_pairing_opened","reference_ceiling_opened_or_read","process_knockout_computed")),"heldout scientific endpoint prematurely opened")
    must(fit.get("counts_as_empirical_conclusion") is False and not fit.get("errors"),"pilot misclassified or errors")
    must(drift.get("taxon")==EXPECTED["heldout_taxon"] and drift.get("source_cells_expected")==48 and drift.get("source_cells_safely_comparable")==48 and drift.get("unresolved_source_cells")==0,"within-source drift audit incomplete")
    must(drift.get("repaired_model_prediction_SHA256")==fit.get("prediction_surface_sha256"),"prediction receipt mismatch")
    must(drift.get("historical_original_core19_frame_SHA256_by_M")==fit.get("core19_frame_sha256_by_M"),"frame digest mismatch")
    must(all(drift["source_mode_summaries"][mode]["comparable"]==24 and drift["source_mode_summaries"][mode]["unresolved"]==0 for mode in ("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")),"source mode comparison incomplete")
    must(all(drift.get(k) is False for k in ("cross_source_paired_discordance_computed","repaired_47taxon_q95_calibrated","full_repaired_12taxon_endpoint_opened")),"drift crossed outcome boundary")
    must(geometry.get("status")=="historical_Abies_grandis_reference_center_hash_reconstructed","reference geometry not qualified")
    must(geometry.get("original_source_blind_geometry_cells")==7244,"reference pooled geometry changed")
    must(geometry.get("original_signed_12block_centers_SHA256")==EXPECTED["reference_center"] and geometry.get("recomputed_centers_SHA256")==EXPECTED["reference_center"],"reference center hash mismatch")
    must(geometry.get("historical_snapshot_object_manifest_sha256")==EXPECTED["historical_manifest"],"reference source identity mismatch")
    must(geometry.get("original_historical_source_thinned_counts")=={"PRESERVED_SPECIMEN":958,"HUMAN_OBSERVATION":6566},"reference original input counts changed")
    must(geometry.get("model_training_or_refitting_performed") is False and geometry.get("ecological_prediction_scores_opened") is False,"reference geometry pilot opened scores")
    must(source.get("taxa_qualified_repaired_raw_parity")==12 and ref_source.get("completed_and_verified_shards")==8 and ref_source.get("prespecified_reference_taxa")==47,"full panel source audit not qualified")
    must(source.get("repaired_SDM_models_fit") is False and ref_source.get("original_24_calibration_q95_refitted") is False,"input-only receipts misrepresented")
    must(fit.get("counts_as_empirical_conclusion") is False and all(x.get("empirical_ledger_increment")==0 for x in (drift,geometry,source,ref_source)),"unexpected empirical endpoint")
    return {
        "schema":"284b.gbif_repaired_scaleout_technical_gate.v1",
        "status":"PILOTS_PASS_FULL_59_REFIT_NOT_YET_COMPLETE",
        "heldout_pilot":{"taxon":EXPECTED["heldout_taxon"],"sealed_cells":48,"within_source_comparable_cells":48,
                         "specimen_median_tv":drift["source_mode_summaries"]["PRESERVED_SPECIMEN"]["median_tv_when_comparable"],
                         "human_median_tv":drift["source_mode_summaries"]["HUMAN_OBSERVATION"]["median_tv_when_comparable"]},
        "reference_geometry_pilot":{"taxon":EXPECTED["reference_taxon"],"historical_keys":2,
                                     "pooled_cells":7244,"original_center_sha256":EXPECTED["reference_center"]},
        "source_inputs_audited":{"reference_taxa":47,"heldout_taxa":12},
        "authorized_next_step":"Prepare signed original-geometry reconstruction for all fixed 47 reference taxa before repaired refits; never infer full-panel success from pilots.",
        "full_reference_model_refit_complete":False,
        "q95_recalibrated":False,
        "repaired_heldout_endpoint_opened":False,
        "independent_biological_evidence":False,
        "empirical_ledger_increment":0,
        "submission_status":"HOLD",
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--root",type=Path,default=Path("."))
    a.add_argument("--out",type=Path,required=True)
    opt=a.parse_args()
    names=[
      "results/gbif_repaired_Artemisia_fixedcenters_fit_contract_v1.json",
      "results/gbif_repaired_Artemisia_single_source_drift_v1.json",
      "results/gbif_original_reference_Abies_grandis_centers_v1.json",
      "results/gbif_repaired_heldout12_thinning_v1.json",
      "results/gbif_repaired_reference47_thinning_v1.json"]
    values=[json.loads((opt.root/name).read_text(encoding="utf-8")) for name in names]
    output=check(*values)
    opt.out.parent.mkdir(parents=True,exist_ok=True)
    opt.out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(output,sort_keys=True))

if __name__=="__main__":main()
