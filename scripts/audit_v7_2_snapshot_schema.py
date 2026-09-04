#!/usr/bin/env python3
"""Read only Parquet schema metadata for the frozen GBIF 2026-08-01 snapshot."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pyarrow.fs as pafs
import pyarrow.parquet as pq

from product_b_v7_2.schema_gate import schema_sha256, validate_snapshot_schema

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts/product_b_v7_2_snapshot_schema_audit.json"
BUCKET = "gbif-open-data-us-east-1"
REGION = "us-east-1"
SNAPSHOT_DATE = "2026-08-01"
OBJECT_KEY = f"occurrence/{SNAPSHOT_DATE}/occurrence.parquet/000000"


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    filesystem = pafs.S3FileSystem(anonymous=True, region=REGION)
    path = f"{BUCKET}/{OBJECT_KEY}"
    schema = pq.read_schema(path, filesystem=filesystem)
    fields = {field.name: str(field.type) for field in schema}
    reasons = validate_snapshot_schema(fields)
    outcome = {
        "status": "completed_snapshot_schema_audit" if not reasons else "unresolved_snapshot_schema",
        "snapshot_date": SNAPSHOT_DATE,
        "provider": "aws_open_data",
        "region": REGION,
        "bucket": BUCKET,
        "schema_source_object": OBJECT_KEY,
        "schema_sha256": schema_sha256(fields),
        "field_count": len(fields),
        "fields": fields,
        "validation_reasons": list(reasons),
        "parquet_schema_metadata_opened": True,
        "parquet_occurrence_rows_opened": False,
        "row_groups_read": False,
        "pair_or_taxon_selected": False,
        "occurrence_counts_opened": False,
    }
    OUTPUT.write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0 if not reasons else 1


if __name__ == "__main__":
    sys.exit(main())
