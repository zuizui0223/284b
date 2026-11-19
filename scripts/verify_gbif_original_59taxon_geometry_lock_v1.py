#!/usr/bin/env python3
"""Prove exact disjoint 47-reference / 12-heldout original geometry populations.

This metadata-only lock combines two independently signed, complete
historical 9705-object geometry receipts. No restored-source fitted model,
paired prediction, recalibrated q95, or NEON field observation is read.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

OLD_MANIFEST_SHA="1b5b2dde8a23e78beafac1d122830e0552c2fbdac4086e9d9d8c161814a7163e"
REFERENCE_RECEIPT_SHA="bb4f221884af9f4b4800adb1f0267c91d1e2b5f05b5e4f867ecc35f4824b554a"
HELDOUT_RECEIPT_SHA="aeddef8cc43568416a0224ea623ba6329b6e3038a267de4b960cc3af2ef8424e"
EXPECTED_MS={"150","300","500"}


def lock(reference:dict,heldout:dict,reference_sha:str,heldout_sha:str)->dict:
    def require(ok,message):
        if not ok:raise RuntimeError(message)

    require(reference_sha==REFERENCE_RECEIPT_SHA
            and heldout_sha==HELDOUT_RECEIPT_SHA,
            "Original reference or heldout 59-taxon geometry source receipt bytes changed")
    require(reference.get("schema")=="284b.gbif_original_reference47_geometry_complete_v1"
            and reference.get("status")=="ALL_47_ORIGINAL_SIGNED_REFERENCE_GEOMETRIES_VERIFIED_NO_MODELS"
            and reference.get("reference_taxa_expected")==47
            and reference.get("reference_taxa_original_geometry_exactly_reproduced")==47,
            "Original frozen reference47 spatial partition reconstruction not complete")
    require(heldout.get("schema")=="284b.gbif_original_heldout12_geometry_complete.v1"
            and heldout.get("status")=="ALL_12_ORIGINAL_SIGNED_HELDOUT_GEOMETRIES_VERIFIED_NO_REPAIRED_MODELS"
            and heldout.get("original_heldout_taxa_expected")==12
            and heldout.get("original_heldout_geometry_exactly_reproduced")==12,
            "Original frozen heldout12 spatial partition reconstruction not complete")
    require(reference.get("historical_source_manifest_sha256")==OLD_MANIFEST_SHA
            and heldout.get("historical_source_manifest_sha256")==OLD_MANIFEST_SHA,
            "Reference and heldout geometry have different historical 9705-object GBIF sources")
    require(reference.get("repaired_source_reference_model_refits_completed")==0
            and reference.get("calibration_reference_q95_opened") is False
            and reference.get("heldout12_endpoint_opened") is False
            and reference.get("empirical_ledger_increment")==0,
            "Reference historical geometry receipt crossed source-fit/q95 endpoint")
    require(heldout.get("repaired_source_heldout_model_refits_completed")==0
            and heldout.get("repaired_47_reference_q95_calibrated") is False
            and heldout.get("repaired_12_heldout_paired_outcomes_opened") is False
            and heldout.get("empirical_ledger_increment")==0,
            "Heldout historical geometry receipt crossed repaired source-paired endpoint")
    a=reference.get("reference_taxa",[]);b=heldout.get("taxa",[])
    require(len(a)==47 and len(b)==12,"Original reference/heldout panel source count missing")
    seen_names=set();seen_centers=set();seen_keys=set()
    rows=[]
    for panel,taxa,n in (("reference",a,47),("heldout",b,12)):
        require([r.get("index") for r in taxa]==list(range(n)),
                "Original 47/12 index order changed")
        for r in taxa:
            taxon=r.get("taxon")
            require(isinstance(taxon,str) and taxon and taxon not in seen_names,
                    "Original reference and heldout taxa collide or have invalid names")
            seen_names.add(taxon)
            center=r.get("original_center_sha256")
            require(isinstance(center,str) and len(center)==64 and
                    all(c in "0123456789abcdef" for c in center) and center not in seen_centers,
                    "Original reference/heldout spatial block center SHA invalid or reused")
            seen_centers.add(center)
            frames=r.get("original_comparison_frame_sha256_by_M",{})
            require(set(frames)==EXPECTED_MS and
                    all(isinstance(v,str) and len(v)==64 and
                        all(c in "0123456789abcdef" for c in v) for v in frames.values()),
                    "Not all three historical 2000-row M frame hashes certified")
            require(isinstance(r.get("original_source_thinned_counts"),dict) and
                    set(r["original_source_thinned_counts"])=={"PRESERVED_SPECIMEN","HUMAN_OBSERVATION"}
                    and all(isinstance(v,int) and v>0 for v in r["original_source_thinned_counts"].values()),
                    "Original source-specific thinned presences missing")
            require(isinstance(r.get("original_qualification_artifact_id"),int) and
                    r["original_qualification_artifact_id"]>0,
                    "Original signed qualification artifact ID missing")
            key=(panel,r["index"])
            require(key not in seen_keys,"Duplicate frozen taxon index")
            seen_keys.add(key)
            rows.append({"panel":panel,"index":r["index"],"taxon":taxon,
                         "original_center_sha256":center})
    require(len(seen_names)==len(seen_centers)==len(rows)==59,
            "Full original reference47 and heldout12 spatial geometry provenance not unique")
    return {
        "schema":"284b.gbif_original_59taxon_geometry_provenance_lock.v1",
        "status":"59_ORIGINAL_HISTORICAL_GEOMETRIES_SIGNED_DISJOINT_NO_REPAIRED_OUTCOMES",
        "reference_taxa_original_spatial_geometry_complete":47,
        "heldout_taxa_original_spatial_geometry_complete":12,
        "taxa_total":59,
        "original_signed_historical_parquet_count":9705,
        "original_historical_manifest_sha256":OLD_MANIFEST_SHA,
        "original_reference47_receipt_sha256":reference_sha,
        "original_heldout12_receipt_sha256":heldout_sha,
        "unique_taxon_names":59,
        "unique_spatial_center_hashes":59,
        "all_taxa_three_original_frame_hashes_verified":True,
        "all_taxa_signed_original_fit_and_qualification_provenance":True,
        "original_reference_and_heldout_no_taxon_overlap":True,
        "repaired_reference_source_model_refits_verified":False,
        "repaired_heldout_source_model_refits_verified":False,
        "repaired_reference_q95_recalibrated":False,
        "repaired_heldout_paired_D_opened":False,
        "independent_biological_replication":False,
        "empirical_ledger_increment":0,
        "submission_status":"HOLD",
        "taxa":rows,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--reference",type=Path,required=True)
    p.add_argument("--heldout",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    raw_ref=args.reference.read_bytes();raw_held=args.heldout.read_bytes()
    result=lock(json.loads(raw_ref),json.loads(raw_held),
                hashlib.sha256(raw_ref).hexdigest(),hashlib.sha256(raw_held).hexdigest())
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","taxa_total","unique_taxon_names",
                                            "unique_spatial_center_hashes","empirical_ledger_increment")}))


if __name__=="__main__":
    main()
