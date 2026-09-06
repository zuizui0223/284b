#!/usr/bin/env python3
"""Audit official NCBI/PMC S3 delivery for EPV001 supporting material.

This is literature-distribution metadata only. It queries the world-readable
`pmc-oa-opendata` bucket exactly as documented by PMC for article-version
objects. It does not access biodiversity occurrence data and does not construct
an operational geographic scope unless a published supplementary object is
actually discoverable.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "artifacts/product_b_v6_epv001_ncbi_s3_delivery.json"
BUCKET_BASE = "https://pmc-oa-opendata.s3.amazonaws.com/"
PMCID = "PMC2947922"
EXPECTED_FILENAME = "1006225107_sd01.xls"


def _get_bytes(url: str, *, accept: str, timeout_seconds: float = 90.0) -> tuple[bytes, str]:
    request = Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "zuizui0223-284b-product-b-v6-ncbi-s3-audit/0.1",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read()
        content_type = response.headers.get("Content-Type", "")
    if not payload:
        raise ValueError(f"empty response from official PMC S3 resource: {url}")
    return payload, content_type


def _list_article_version_prefixes() -> tuple[str, ...]:
    params = urlencode({"list-type": "2", "prefix": PMCID + ".", "delimiter": "/"})
    payload, _ = _get_bytes(BUCKET_BASE + "?" + params, accept="application/xml,text/xml")
    root = ET.fromstring(payload)
    prefixes: list[str] = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] == "Prefix" and element.text:
            value = element.text.strip()
            if value.startswith(PMCID + ".") and value.endswith("/"):
                prefixes.append(value)
    return tuple(dict.fromkeys(prefixes))


def _metadata_url_for_prefix(prefix: str) -> str:
    stem = prefix.rstrip("/")
    return BUCKET_BASE + prefix + stem + ".json"


def _get_json(url: str) -> Mapping[str, object]:
    payload, _ = _get_bytes(url, accept="application/json")
    parsed = json.loads(payload.decode("utf-8"))
    if not isinstance(parsed, Mapping):
        raise ValueError("PMC S3 metadata response must be a JSON object")
    return parsed


def _media_filename(url: str) -> str:
    no_query = url.split("?", 1)[0]
    return no_query.rsplit("/", 1)[-1]


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    prefixes = _list_article_version_prefixes()
    versions: list[dict[str, object]] = []
    exact_matches: list[dict[str, object]] = []

    for prefix in prefixes:
        metadata_url = _metadata_url_for_prefix(prefix)
        metadata = _get_json(metadata_url)
        media_urls_raw = metadata.get("media_urls", [])
        media_urls = [str(value) for value in media_urls_raw] if isinstance(media_urls_raw, list) else []
        filenames = [_media_filename(value) for value in media_urls]
        matches = [value for value in media_urls if _media_filename(value) == EXPECTED_FILENAME]
        versions.append(
            {
                "prefix": prefix,
                "metadata_url": metadata_url,
                "pmcid": metadata.get("pmcid"),
                "version": metadata.get("version"),
                "is_pmc_openaccess": metadata.get("is_pmc_openaccess"),
                "is_manuscript": metadata.get("is_manuscript"),
                "license_code": metadata.get("license_code"),
                "media_url_count": len(media_urls),
                "media_filenames": filenames,
                "exact_expected_filename_matches": matches,
            }
        )
        for value in matches:
            exact_matches.append(
                {
                    "prefix": prefix,
                    "metadata_url": metadata_url,
                    "media_url": value,
                }
            )

    if exact_matches:
        state = "official_s3_supplement_discoverable"
    elif prefixes:
        state = "article_version_available_but_expected_supplement_not_listed"
    else:
        state = "pmcid_not_available_in_current_pmc_article_dataset_s3"

    outcome = {
        "status": "completed_official_ncbi_s3_delivery_audit",
        "pair_id": "EPV001",
        "pmcid": PMCID,
        "bucket": "pmc-oa-opendata",
        "official_distribution_state": state,
        "expected_filename": EXPECTED_FILENAME,
        "article_version_prefixes": list(prefixes),
        "versions": versions,
        "exact_expected_filename_matches": exact_matches,
        "occurrence_reads_performed": False,
        "operational_scope_constructed": False,
        "challenge_bypass_attempted": False,
    }
    OUTPUT_PATH.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
