#!/usr/bin/env python3
"""Audit the frozen public EPV001 Dataset S1 delivery path without occurrence access.

The official PMC asset URL was already resolved from article HTML in successful
bridge-audit run 33851758152. This step therefore never re-reads article HTML.
It either audits XLS bytes directly or records public bridge/challenge metadata.
No geographic scope is constructed here.
"""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import xlrd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "artifacts/product_b_v6_epv001_scope_dataset_audit.json"
ARTICLE_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC2947922/"
FROZEN_PUBLIC_ASSET_URL = "https://pmc.ncbi.nlm.nih.gov/articles/instance/2947922/bin/1006225107_sd01.xls"
EXPECTED_FILENAME = "1006225107_sd01.xls"
BRIDGE_PROVENANCE = {
    "workflow_run_id": 33851758152,
    "artifact_id": 9928597009,
    "artifact_digest": "sha256:3ae439375023cd8494f9c88a852db9ab38defe7545eddd5364064ca7e2d18046",
    "bridge_sha256": "739a3ac22c4d24d20b01ebe84281779c739fd517c58e0fff544c2517cbb50184"
}
KEYWORDS = ("lat", "latitude", "lon", "long", "longitude", "locality", "location", "site", "population")
OLE2_MAGIC = bytes.fromhex("D0CF11E0A1B11AE1")
CHALLENGE_TERMS = ("pow", "proof", "cookie", "cloudpmc", "challenge", "download", "worker", "wasm")


def _normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


def _request_bytes(url: str, *, accept: str, timeout_seconds: float = 90.0) -> tuple[bytes, str, str]:
    request = Request(
        url,
        headers={
            "Accept": accept,
            "Referer": ARTICLE_URL,
            "User-Agent": "zuizui0223-284b-product-b-v6-literature-scope/0.5",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read()
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
    if not payload:
        raise ValueError(f"published resource download was empty: {url}")
    return payload, final_url, content_type


def _bridge_audit(payload: bytes, final_url: str, content_type: str) -> dict[str, object]:
    text = html.unescape(payload.decode("utf-8", errors="replace"))
    hrefs = re.findall(r'''href=["']([^"']+)["']''', text, flags=re.I)
    actions = re.findall(r'''action=["']([^"']+)["']''', text, flags=re.I)
    script_srcs = re.findall(r'''<script[^>]+src=["']([^"']+)["'][^>]*>''', text, flags=re.I)
    inline_scripts = re.findall(r'''<script(?![^>]+src=)[^>]*>(.*?)</script>''', text, flags=re.I | re.S)
    link_urls = list(dict.fromkeys(urljoin(final_url, raw) for raw in hrefs + actions))
    script_urls = list(dict.fromkeys(urljoin(final_url, raw) for raw in script_srcs))
    challenge_snippets: list[str] = []
    for script in inline_scripts:
        compact = re.sub(r"\s+", " ", script).strip()
        if any(term in compact.lower() for term in CHALLENGE_TERMS):
            challenge_snippets.append(compact[:4000])
    interesting = [
        url for url in link_urls + script_urls
        if EXPECTED_FILENAME.lower() in url.lower()
        or any(term in url.lower() for term in CHALLENGE_TERMS)
    ]
    cookie_tokens = sorted(set(re.findall(
        r'''[A-Za-z0-9_-]*cookie[A-Za-z0-9_-]*|cloudpmc[A-Za-z0-9_-]*|[A-Za-z0-9_-]*pow[A-Za-z0-9_-]*''',
        text,
        flags=re.I,
    )))
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    return {
        "status": "bridge_unresolved",
        "bridge_final_url": final_url,
        "bridge_content_type": content_type,
        "bridge_sha256": hashlib.sha256(payload).hexdigest(),
        "bridge_title": title_match.group(1).strip() if title_match else "",
        "bridge_href_count": len(hrefs),
        "bridge_form_action_count": len(actions),
        "bridge_script_srcs": script_urls,
        "bridge_inline_script_count": len(inline_scripts),
        "bridge_challenge_script_snippets": challenge_snippets,
        "bridge_cookie_or_challenge_tokens": cookie_tokens,
        "interesting_resolved_links": interesting,
    }


def _numeric_column_profile(sheet: xlrd.sheet.Sheet, col: int) -> dict[str, object]:
    values = [
        float(sheet.cell(row, col).value)
        for row in range(sheet.nrows)
        if sheet.cell(row, col).ctype == xlrd.XL_CELL_NUMBER
    ]
    return {
        "column_index": col,
        "numeric_count": len(values),
        "numeric_min": min(values) if values else None,
        "numeric_max": max(values) if values else None,
    }


def _workbook_audit(payload: bytes) -> tuple[str, list[dict[str, object]]]:
    digest = hashlib.sha256(payload).hexdigest()
    workbook = xlrd.open_workbook(file_contents=payload)
    audits: list[dict[str, object]] = []
    for sheet in workbook.sheets():
        candidate_rows: list[dict[str, object]] = []
        for row in range(min(sheet.nrows, 25)):
            values = [_normalize(sheet.cell_value(row, col)) for col in range(sheet.ncols)]
            hits = [
                col for col, value in enumerate(values)
                if value and any(keyword in value.lower() for keyword in KEYWORDS)
            ]
            if hits:
                candidate_rows.append({"row_index": row, "hit_columns": hits, "row_values": values})
        profiles = [_numeric_column_profile(sheet, col) for col in range(sheet.ncols)]
        audits.append({
            "sheet_name": sheet.name,
            "nrows": sheet.nrows,
            "ncols": sheet.ncols,
            "candidate_header_rows": candidate_rows,
            "coordinate_like_numeric_profiles": [
                profile for profile in profiles
                if profile["numeric_count"] >= 3
                and profile["numeric_min"] is not None
                and -180 <= float(profile["numeric_min"]) <= 180
                and -180 <= float(profile["numeric_max"]) <= 180
            ],
        })
    return digest, audits


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload, final_asset_url, content_type = _request_bytes(
        FROZEN_PUBLIC_ASSET_URL,
        accept="application/vnd.ms-excel,application/octet-stream,text/html,*/*",
    )
    common = {
        "pair_id": "EPV001",
        "source_article_doi": "10.1073/pnas.1006225107",
        "source_pmcid": "PMC2947922",
        "frozen_public_asset_url": FROZEN_PUBLIC_ASSET_URL,
        "asset_url_provenance": BRIDGE_PROVENANCE,
        "source_filename": EXPECTED_FILENAME,
        "occurrence_reads_performed": False,
        "operational_scope_constructed": False,
    }
    if payload.startswith(OLE2_MAGIC):
        digest, sheets = _workbook_audit(payload)
        outcome = {
            **common,
            "status": "completed_literature_dataset_audit",
            "source_asset_url_resolved": final_asset_url,
            "source_content_type": content_type,
            "source_sha256": digest,
            "sheets": sheets,
        }
    else:
        outcome = {**common, **_bridge_audit(payload, final_asset_url, content_type)}
    OUTPUT_PATH.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
