#!/usr/bin/env python3
"""Strict metadata-only aggregation of 47 SHA-verified historical reference geometries.

No q95/pairing/model predictions are opened. All 47 original source-blind
centers must reproduce the signed original preflight hash, with no substitutions.
"""
from pathlib import Path
import argparse,json,hashlib

def aggregate(manifest,receipts):
    entries=manifest.get("entries",[])
    if (manifest.get("status")!="PREDECLARED_REFERENCE47_ORIGINAL_GEOMETRY_ONLY"
        or len(entries)!=47 or [x.get("index") for x in entries]!=list(range(47))):
        raise RuntimeError("Source reference47 manifest population is not fixed")
    if len(receipts)!=47:raise RuntimeError("Reference geometry requires exactly 47 receipts")
    by={}
    for r in receipts:
        idx=r.get("taxon_index")
        if not isinstance(idx,int) or idx in by or idx not in range(47):
            raise RuntimeError("Reference index missing, duplicate or outside frozen set")
        by[idx]=r
    rows=[]
    for e in entries:
        r=by[e["index"]]
        if (r.get("schema")!="284b.gbif_original_reference47_center_reconstruction.v1"
            or r.get("status")!="ORIGINAL_SIGNED_REFERENCE_GEOMETRY_EXACTLY_REPRODUCED"
            or r.get("taxon")!=e["taxon"]
            or r.get("historical_specieskeys")!=e["historical_specieskeys"]
            or r.get("original_qualification_artifact_id")!=e["original_qualification_artifact_id"]
            or r.get("original_fit_artifact_id")!=e["original_fit_artifact_id"]
            or r.get("historical_source_manifest_sha256")!=manifest["original_source_manifest_sha256"]
            or r.get("historical_source_parquet_count")!=9705
            or r.get("original_center_sha256")!=r.get("reconstructed_center_sha256")
            or not isinstance(r.get("original_common_pooled_geometry_cells"),int)
            or r["original_common_pooled_geometry_cells"]<12):
            raise RuntimeError("Original reference geometry receipt changed: "+str(e["index"]))
        if set(r.get("original_comparison_frame_sha256_by_M",{}))!={"150","300","500"}:
            raise RuntimeError("Reference original frame SHA count changed")
        for x in [r.get("original_center_sha256"),r.get("center_npy_sha256"),
                  *r["original_comparison_frame_sha256_by_M"].values()]:
            if not isinstance(x,str) or len(x)!=64 or any(c not in "0123456789abcdef" for c in x):
                raise RuntimeError("Reference source SHA fingerprint invalid")
        for k in ("source_rows_or_coordinates_exported","model_refit_performed",
                  "paired_discordance_computed","reference_q95_computed",
                  "heldout12_opened","neon_field_outcomes_read"):
            if r.get(k) is not False:raise RuntimeError("Reference geometry opened forbidden outcome")
        if r.get("empirical_ledger_increment")!=0:
            raise RuntimeError("Reference geometry incorrectly claimed independent biological evidence")
        rows.append({
           "index":e["index"],"taxon":e["taxon"],
           "original_center_sha256":r["original_center_sha256"],
           "original_comparison_frame_sha256_by_M":r["original_comparison_frame_sha256_by_M"],
           "original_geometry_cells":r["original_common_pooled_geometry_cells"],
           "center_npy_sha256":r["center_npy_sha256"],
           "original_comparison_frame_sha256_by_M":r["original_comparison_frame_sha256_by_M"],
           "original_source_thinned_counts":r["original_source_thinned_counts"],
           "original_qualification_artifact_id":e["original_qualification_artifact_id"],
        })
    return {
      "schema":"284b.gbif_original_reference47_geometry_complete_v1",
      "status":"ALL_47_ORIGINAL_SIGNED_REFERENCE_GEOMETRIES_VERIFIED_NO_MODELS",
      "reference_taxa_expected":47,
      "reference_taxa_original_geometry_exactly_reproduced":47,
      "historical_source_manifest_sha256":manifest["original_source_manifest_sha256"],
      "reference_taxa":rows,
      "repaired_source_reference_model_refits_completed":0,
      "calibration_reference_q95_opened":False,
      "heldout12_endpoint_opened":False,
      "independent_empirical_biological_evidence":False,
      "empirical_ledger_increment":0,
      "submission_status":"HOLD",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--receipts-root",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    o=p.parse_args()
    manifest=json.loads(o.manifest.read_text(encoding="utf-8"))
    paths=list(o.receipts_root.rglob("geometry_ref_*.json"))
    receipts=[json.loads(path.read_text(encoding="utf-8")) for path in paths]
    obj=aggregate(manifest,receipts)
    o.out_json.parent.mkdir(parents=True,exist_ok=True)
    o.out_json.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:obj[k] for k in ("status","reference_taxa_original_geometry_exactly_reproduced",
                                      "repaired_source_reference_model_refits_completed")}))

if __name__=="__main__":main()
