#!/usr/bin/env python3
"""Independent metadata-only replay of exact GBIF 2026-08-01 frozen S3 listing.

The scanner that attempted to reconstruct Artemisia model inputs found a
+135 PRESERVED_SPECIMEN 0.05-degree-cell discrepancy. This audit checks
whether the original public *object set* changed, before attributing a
difference to taxon filters or source-model behavior.

No occurrence rows, taxon records, coordinates, or NEON plot records opened.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import argparse
import hashlib
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"legacy/pre_level_a_focus"))
from product_b_v7_2.snapshot_transport import (
  SnapshotObject, EXPECTED_BUCKET, EXPECTED_CITATION_KEY, EXPECTED_SNAPSHOT_DATE,
  EXPECTED_OBJECT_COUNT, EXPECTED_PARQUET_OBJECT_COUNT,
  EXPECTED_OBJECT_MANIFEST_SHA256, object_manifest_sha256
)
OLD_RECEIPT=ROOT/"legacy/pre_level_a_focus/results/product_b_v7_2_snapshot_metadata_freeze_v0_1.json"


def _name(parent,local):
    return (parent.tag.split("}",1)[0]+"}" if parent.tag.startswith("{") else "")+local


def _field(parent,local):
    child=parent.find(_name(parent,local))
    return (child.text or "").strip() if child is not None else ""


def _read(url):
    req=Request(url,headers={"User-Agent":"284b-GBIF-frozen-manifest-integrity/1.0"})
    with urlopen(req,timeout=60) as f:return f.read()


def list_objects(prefix:str):
    objects=[]
    continuation=None
    for page in range(20):
        query={"list-type":"2","prefix":prefix,"max-keys":"1000"}
        if continuation:query["continuation-token"]=continuation
        payload=_read(f"https://{EXPECTED_BUCKET}.s3.amazonaws.com/?"+urlencode(query))
        root=ET.fromstring(payload)
        for item in root.findall(_name(root,"Contents")):
            objects.append(SnapshotObject(
              key=_field(item,"Key"),
              size=int(_field(item,"Size")),
              etag=_field(item,"ETag"),
              last_modified=_field(item,"LastModified"),
            ))
        if _field(root,"IsTruncated").lower()!="true":return objects
        continuation=_field(root,"NextContinuationToken")
        if not continuation:raise RuntimeError("truncated object manifest without continuation")
    raise RuntimeError("GBIF snapshot object listing exceeds 20 pages")


def run():
    prior=json.loads(OLD_RECEIPT.read_text(encoding="utf-8"))
    prefix=f"occurrence/{EXPECTED_SNAPSHOT_DATE}/"
    objects=list_objects(prefix)
    digest=object_manifest_sha256(objects)
    citations=_read(f"https://{EXPECTED_BUCKET}.s3.amazonaws.com/{EXPECTED_CITATION_KEY}")
    citation=hashlib.sha256(citations).hexdigest()
    parquet=sum(o.key.startswith(prefix+"occurrence.parquet/") for o in objects)
    matches={
      "object_count":len(objects)==EXPECTED_OBJECT_COUNT==prior["object_count"],
      "parquet_count":parquet==EXPECTED_PARQUET_OBJECT_COUNT==prior["parquet_object_count"],
      "object_manifest_sha256":digest==EXPECTED_OBJECT_MANIFEST_SHA256==prior["object_manifest_sha256"],
      "citation_sha256":citation==prior["citation_sha256"],
    }
    return {
      "schema":"284b.original_gbif_snapshot_object_integrity_v1",
      "status":"source_objects_match_frozen_metadata" if all(matches.values()) else "SOURCE_SNAPSHOT_OBJECT_DRIFT_STOP",
      "source_original_audit":"legacy/pre_level_a_focus/results/product_b_v7_2_snapshot_metadata_freeze_v0_1.json",
      "source_GBIF_monthly_snapshot":"2026-08-01",
      "current_object_count":len(objects),
      "current_parquet_object_count":parquet,
      "current_object_manifest_sha256":digest,
      "original_object_manifest_sha256":prior["object_manifest_sha256"],
      "current_citation_sha256":citation,
      "match_checks":matches,
      "PRESERVED_SPECIMEN_model_reconstruction_mismatch_recorded":True,
      "reconstruction_original_thinned_count":3285,
      "reconstruction_nov15_thinned_count":3420,
      "difference":135,
      "cause_of_different_thinned_counts_established":False,
      "NEON_voucher_source_model_overlap_checked":False,
      "occurrence_rows_read":False,
      "species_outcomes_read":False,
      "external_validation_authorized":False,
      "empirical_ledger_increment":0,
      "interpretation":"Matching S3 object metadata only constrains transport drift; it does not prove identical bytes or identical admitted training records. A mismatch means the historical source must be treated as drifted.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"object_count":result["current_object_count"],
                      "manifest_sha":result["current_object_manifest_sha256"],
                      "checks":result["match_checks"]}))
    if result["status"]!="source_objects_match_frozen_metadata":
        raise SystemExit("original GBIF snapshot object manifest drift: provenance STOP")


if __name__=="__main__":
    main()
