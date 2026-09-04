#!/usr/bin/env python3
"""Read only Parquet footer schema metadata for the frozen GBIF 2026-08-01 snapshot.

The script first re-lists the already-frozen S3 date prefix, proves that the
object-set digest is identical to the completed metadata audit, and only then
selects one real Parquet object for a schema/footer read.  No occurrence rows,
row groups, taxon counts, or pair-specific values are read.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import pyarrow.fs as pafs
import pyarrow.parquet as pq

from product_b_v7_2.schema_gate import schema_sha256, validate_snapshot_schema
from product_b_v7_2.snapshot_transport import (
    EXPECTED_BUCKET,
    EXPECTED_REGION,
    EXPECTED_SNAPSHOT_DATE,
    SnapshotObject,
    select_frozen_schema_probe_object,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts/product_b_v7_2_snapshot_schema_audit.json"
S3_ENDPOINT = f"https://{EXPECTED_BUCKET}.s3.amazonaws.com/"
DATE_PREFIX = f"occurrence/{EXPECTED_SNAPSHOT_DATE}/"


def _read_bytes(url: str, *, timeout: float = 60.0) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": "zuizui0223-284b-product-b-v7-2-schema/0.2"},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def _tag(element: ET.Element, local_name: str) -> str:
    if element.tag.startswith("{"):
        namespace = element.tag.split("}", 1)[0] + "}"
        return namespace + local_name
    return local_name


def _text(parent: ET.Element, local_name: str) -> str:
    child = parent.find(_tag(parent, local_name))
    return "" if child is None or child.text is None else child.text.strip()


def _list_frozen_objects() -> tuple[SnapshotObject, ...]:
    objects: list[SnapshotObject] = []
    continuation: str | None = None
    page = 0
    while True:
        params = {"list-type": "2", "prefix": DATE_PREFIX, "max-keys": "1000"}
        if continuation:
            params["continuation-token"] = continuation
        payload = _read_bytes(S3_ENDPOINT + "?" + urlencode(params))
        root = ET.fromstring(payload)
        page += 1
        for content in root.findall(_tag(root, "Contents")):
            key = _text(content, "Key")
            if not key:
                raise ValueError(f"S3 listing page {page} contains blank key")
            objects.append(
                SnapshotObject(
                    key=key,
                    size=int(_text(content, "Size")),
                    etag=_text(content, "ETag"),
                    last_modified=_text(content, "LastModified"),
                )
            )
        truncated = _text(root, "IsTruncated").lower() == "true"
        if not truncated:
            break
        continuation = _text(root, "NextContinuationToken")
        if not continuation:
            raise ValueError("S3 listing is truncated but has no continuation token")
        if page > 1000:
            raise ValueError("S3 listing exceeded 1000 pages")
    return tuple(objects)


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # Metadata-only revalidation: this must match the previously frozen listing
    # before the script is allowed to inspect even a Parquet footer.
    objects = _list_frozen_objects()
    probe = select_frozen_schema_probe_object(objects)

    filesystem = pafs.S3FileSystem(anonymous=True, region=EXPECTED_REGION)
    path = f"{EXPECTED_BUCKET}/{probe.key}"
    schema = pq.read_schema(path, filesystem=filesystem)
    fields = {field.name: str(field.type) for field in schema}
    reasons = validate_snapshot_schema(fields)
    outcome = {
        "status": "completed_snapshot_schema_audit" if not reasons else "unresolved_snapshot_schema",
        "snapshot_date": EXPECTED_SNAPSHOT_DATE,
        "provider": "aws_open_data",
        "region": EXPECTED_REGION,
        "bucket": EXPECTED_BUCKET,
        "schema_source_object": probe.key,
        "schema_source_object_size": probe.size,
        "schema_source_object_etag": probe.etag,
        "schema_source_object_last_modified": probe.last_modified,
        "schema_sha256": schema_sha256(fields),
        "field_count": len(fields),
        "fields": fields,
        "validation_reasons": list(reasons),
        "frozen_object_manifest_revalidated": True,
        "s3_listing_metadata_opened": True,
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
