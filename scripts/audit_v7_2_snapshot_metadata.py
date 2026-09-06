#!/usr/bin/env python3
"""Freeze GBIF 2026-08-01 public snapshot metadata without occurrence-row access."""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from product_b_v7_2.snapshot_transport import (
    EXPECTED_BUCKET,
    EXPECTED_CITATION_KEY,
    EXPECTED_SNAPSHOT_DATE,
    SnapshotObject,
    build_metadata_audit,
    validate_completed_metadata_audit,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts/product_b_v7_2_snapshot_metadata_audit.json"
S3_ENDPOINT = f"https://{EXPECTED_BUCKET}.s3.amazonaws.com/"
DATE_PREFIX = f"occurrence/{EXPECTED_SNAPSHOT_DATE}/"


def _read_bytes(url: str, *, timeout: float = 60.0) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": "zuizui0223-284b-product-b-v7-2-snapshot-metadata/0.1"},
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


def _list_objects() -> tuple[SnapshotObject, ...]:
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
            size_text = _text(content, "Size")
            etag = _text(content, "ETag")
            last_modified = _text(content, "LastModified")
            if not key:
                raise ValueError(f"S3 listing page {page} contains blank key")
            objects.append(
                SnapshotObject(
                    key=key,
                    size=int(size_text),
                    etag=etag,
                    last_modified=last_modified,
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
    objects = _list_objects()
    citation_bytes = _read_bytes(S3_ENDPOINT + EXPECTED_CITATION_KEY)
    audit = build_metadata_audit(objects=objects, citation_bytes=citation_bytes)
    reasons = validate_completed_metadata_audit(asdict(audit))
    outcome = {
        "status": "completed_snapshot_metadata_audit" if not reasons else "invalid_snapshot_metadata_audit",
        **asdict(audit),
        "provider": "aws_open_data",
        "region": "us-east-1",
        "bucket": EXPECTED_BUCKET,
        "occurrence_prefix": f"occurrence/{EXPECTED_SNAPSHOT_DATE}/occurrence.parquet/",
        "citation_key": EXPECTED_CITATION_KEY,
        "validation_reasons": list(reasons),
        "parquet_occurrence_rows_opened": False,
        "pair_or_taxon_selected": False,
        "occurrence_counts_opened": False,
        "live_occurrence_search_used": False,
    }
    OUTPUT.write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0 if not reasons else 1


if __name__ == "__main__":
    sys.exit(main())
