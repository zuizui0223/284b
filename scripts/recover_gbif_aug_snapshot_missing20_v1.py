#!/usr/bin/env python3
"""Test whether repaired GBIF 2026-08-01 S3 objects reproduce frozen Sept-04 file set.

Known upstream incident: gbif/occurrence issue #609; each filename divisible
by 20 was missing from the public AWS monthly snapshots. This audit recovers
a *candidate* historical object set by excluding exactly those numeric files,
and accepts it only if the original full-list metadata SHA256 is recovered.
No occurrence rows or species data read.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from check_original_gbif_object_manifest_v1 import (
    list_objects,
    ROOT,
    EXPECTED_CITATION_KEY,
    EXPECTED_OBJECT_MANIFEST_SHA256,
    EXPECTED_OBJECT_COUNT,
    EXPECTED_PARQUET_OBJECT_COUNT,
    object_manifest_sha256,
    EXPECTED_SNAPSHOT_DATE,
)


def partition_historical(objects):
    prefix=f"occurrence/{EXPECTED_SNAPSHOT_DATE}/occurrence.parquet/"
    preserved=[]
    repaired=[]
    unexpected=[]
    for obj in objects:
        if obj.key==EXPECTED_CITATION_KEY:
            preserved.append(obj)
            continue
        if not obj.key.startswith(prefix):
            unexpected.append(obj.key)
            continue
        name=obj.key[len(prefix):]
        if not name.isdecimal() or len(name)!=6:
            unexpected.append(obj.key)
            continue
        if int(name)%20==0:
            repaired.append(obj)
        else:
            preserved.append(obj)
    return preserved,repaired,unexpected


def run():
    objects=list_objects(f"occurrence/{EXPECTED_SNAPSHOT_DATE}/")
    before=object_manifest_sha256(objects)
    historical, repaired, unknown=partition_historical(objects)
    legacy_fingerprint=object_manifest_sha256(historical)
    recovered=(not unknown and
               len(historical)==EXPECTED_OBJECT_COUNT and
               len(repaired)==510 and
               legacy_fingerprint==EXPECTED_OBJECT_MANIFEST_SHA256)
    filenames=sorted(i.key for i in repaired)
    origparquet=[x for x in historical if x.key!=EXPECTED_CITATION_KEY]
    assert len(origparquet)==len(historical)-1
    def time_field(seq):
        vals=[x.last_modified for x in seq]
        return {"min":min(vals) if vals else None,"max":max(vals) if vals else None}
    return {
       "schema":"284b.gbif_2026_08_snapshot_recovered_missing20.v1",
       "status":"historical_9705_parquet_manifest_exactly_recovered"
              if recovered else "historical_manifest_not_recovered_STOP",
       "current_object_count":len(objects),
       "current_manifest_sha256":before,
       "candidate_historical_object_count":len(historical),
       "candidate_historical_parquet_count":len(origparquet),
       "candidate_historical_manifest_sha256":legacy_fingerprint,
       "expected_historical_manifest_sha256":EXPECTED_OBJECT_MANIFEST_SHA256,
       "candidate_added_divisible_by_20_count":len(repaired),
       "added_file_first_5":filenames[:5],
       "added_file_last_5":filenames[-5:],
       "added_file_last_modified_range":time_field(repaired),
       "historical_file_last_modified_range":time_field(historical),
       "unknown_object_keys":unknown[:8],
       "restored_file_counts_by_modulo20":
            {"mod0":len(repaired),"other":len(origparquet)},
       "filename_divisible_by_20_matches_gbif_issue609":recovered,
       "upstream_incident_url":"https://github.com/gbif/occurrence/issues/609",
       "original_metadata_audit_run_id":33869400385,
       "original_metadata_audit_date":"2026-09-04",
       "NEON_datasetkey_training_overlap_still_unresolved":True,
       "original_thinned_presence_reconstruction_still_unresolved":True,
       "source_reproducibility_issue_is_external_public_S3_snapshot_change":recovered,
       "direct_NEON_plant_observations_read":False,
       "GBIF_occurrence_rows_read":False,
       "external_validation_authorized":False,
       "empirical_ledger_increment":0,
       "interpretation":"Only if the frozen full-object ETag/size/LastModified manifest SHA256 matches can we identify an exact original object set. The newer files cannot be assumed to have been in the original study. A full model input reconstruction is still necessary before training-overlap claims.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    obj=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":obj["status"],
                      "candidate_historical_object_count":obj["candidate_historical_object_count"],
                      "removed_mod20":obj["candidate_added_divisible_by_20_count"],
                      "sha":obj["candidate_historical_manifest_sha256"]}))
    if obj["status"]!="historical_9705_parquet_manifest_exactly_recovered":
        raise SystemExit("historical file set not recoverable using reported GBIF missing20 pattern")


if __name__=="__main__":
    main()
