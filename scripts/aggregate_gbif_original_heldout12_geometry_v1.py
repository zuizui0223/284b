#!/usr/bin/env python3
"""Fail-closed 12-heldout historical geometry aggregator, source-only.

All 12 predeclared original taxa and comparison-frame SHA identifiers must
be present. This stage neither trains restored GBIF models nor opens the
post-freeze paired-source D, q95 reference or external NEON plot labels.
"""
import argparse,json
from pathlib import Path

MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
MS=("150","300","500")

def aggregate(manifest,records):
    entries=manifest.get("entries",[])
    if (manifest.get("status")!="PREDECLARED_HELDOUT12_ORIGINAL_GEOMETRY_ONLY"
        or manifest.get("frozen_taxon_count")!=12
        or len(entries)!=12
        or [x.get("index") for x in entries]!=list(range(12))
        or manifest.get("full_repaired_model_refit") is not False
        or manifest.get("q95_computed") is not False
        or manifest.get("heldout_scores_opened") is not False
        or manifest.get("empirical_ledger_increment")!=0):
        raise RuntimeError("Original heldout12 manifest or boundary invalid")
    if len(records)!=12:
        raise RuntimeError("Exactly 12 source-only original heldout geometry receipts required")
    by={}
    for r in records:
        i=r.get("taxon_index")
        if not isinstance(i,int) or i not in range(12) or i in by:
            raise RuntimeError("Duplicate/missing/nonoriginal heldout taxon index")
        by[i]=r
    if set(by)!=set(range(12)):
        raise RuntimeError("Original 12 heldout taxon universe incomplete")
    rows=[]
    for e in entries:
        r=by[e["index"]]
        if (r.get("schema")!="284b.gbif_original_heldout12_center_reconstruction.v1"
            or r.get("status")!="ORIGINAL_SIGNED_HELDOUT_GEOMETRY_EXACTLY_REPRODUCED"
            or r.get("taxon")!=e["taxon"]
            or r.get("historical_specieskey")!=e["historical_specieskey"]
            or r.get("original_qualification_artifact_id")!=e["original_qualification_artifact_id"]
            or r.get("original_fit_artifact_id")!=e["original_fit_artifact_id"]
            or r.get("historical_source_manifest_sha256")!=manifest["original_source_manifest_sha256"]
            or r.get("historical_source_parquet_count")!=9705
            or r.get("original_center_sha256")!=r.get("reconstructed_center_sha256")
            or r.get("original_source_thinned_counts")!=e["original_source_thinned_counts"]
            or not isinstance(r.get("original_pooled_geometry_cells"),int)
            or r["original_pooled_geometry_cells"]<12):
            raise RuntimeError("Heldout original spatial geometry failed signed identity: "+str(e["index"]))
        if set(r.get("original_comparison_frame_sha256_by_M",{}))!=set(MS):
            raise RuntimeError("Original heldout 3-M frame hash set changed")
        for v in (r["original_center_sha256"],r["center_npy_sha256"],
                  *r["original_comparison_frame_sha256_by_M"].values()):
            if not isinstance(v,str) or len(v)!=64 or any(c not in "0123456789abcdef" for c in v):
                raise RuntimeError("Original heldout SHA-256 metadata invalid")
        for flag in ("source_rows_or_coordinates_exported","repaired_model_fit_performed",
                     "paired_discordance_computed","reference_q95_opened",
                     "repaired_heldout_endpoint_opened","neon_field_outcomes_read"):
            if r.get(flag) is not False:
                raise RuntimeError("Original heldout geometry opened a forbidden outcome: "+flag)
        if r.get("empirical_ledger_increment")!=0:
            raise RuntimeError("Heldout geometry falsely recorded biological evidence")
        rows.append({
            "index":e["index"],"taxon":e["taxon"],"historical_specieskey":e["historical_specieskey"],
            "original_center_sha256":r["original_center_sha256"],
            "original_comparison_frame_sha256_by_M":r["original_comparison_frame_sha256_by_M"],
            "original_source_thinned_counts":r["original_source_thinned_counts"],
            "original_pooled_geometry_cells":r["original_pooled_geometry_cells"],
            "center_npy_sha256":r["center_npy_sha256"],
            "original_qualification_artifact_id":e["original_qualification_artifact_id"],
            "original_fit_artifact_id":e["original_fit_artifact_id"],
        })
    return {
        "schema":"284b.gbif_original_heldout12_geometry_complete.v1",
        "status":"ALL_12_ORIGINAL_SIGNED_HELDOUT_GEOMETRIES_VERIFIED_NO_REPAIRED_MODELS",
        "original_heldout_taxa_expected":12,
        "original_heldout_geometry_exactly_reproduced":12,
        "historical_source_manifest_sha256":manifest["original_source_manifest_sha256"],
        "taxa":rows,
        "repaired_source_heldout_model_refits_completed":0,
        "repaired_47_reference_q95_calibrated":False,
        "repaired_12_heldout_paired_outcomes_opened":False,
        "NEON_field_plot_labels_read":False,
        "new_independent_biological_evidence":False,
        "empirical_ledger_increment":0,
        "submission_status":"HOLD",
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--manifest",required=True,type=Path)
    a.add_argument("--receipts-root",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    p=a.parse_args()
    manifest=json.loads(p.manifest.read_text(encoding="utf-8"))
    files=list(p.receipts_root.rglob("heldout_geometry_ref_*.json"))
    receipts=[json.loads(f.read_text(encoding="utf-8")) for f in files]
    result=aggregate(manifest,receipts)
    p.out.parent.mkdir(parents=True,exist_ok=True)
    p.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","original_heldout_geometry_exactly_reproduced",
                                           "repaired_source_heldout_model_refits_completed")}))
if __name__=="__main__":main()
