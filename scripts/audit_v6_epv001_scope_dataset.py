#!/usr/bin/env python3
"""Audit the published EPV001 Dataset S1 delivery path without occurrence access.

If PMC returns its public 'Preparing to download' bridge, this literature-only
step records script/challenge metadata rather than executing browser code. It
constructs no geographic scope and never accesses biodiversity occurrence data.
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
EXPECTED_FILENAME = "1006225107_sd01.xls"
KEYWORDS = ("lat", "latitude", "lon", "long", "longitude", "locality", "location", "site", "population")
OLE2_MAGIC = bytes.fromhex("D0CF11E0A1B11AE1")
CHALLENGE_TERMS = ("pow", "proof", "cookie", "cloudpmc", "challenge", "download", "worker", "wasm")


def _normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


def _request_bytes(url: str, *, accept: str, timeout_seconds: float = 90.0) -> tuple[bytes, str, str]:
    request = Request(url, headers={"Accept": accept, "Referer": ARTICLE_URL, "User-Agent": "zuizui0223-284b-product-b-v6-literature-scope/0.4"}, method="GET")
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read()
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
    if not payload:
        raise ValueError(f"published resource download was empty: {url}")
    return payload, final_url, content_type


def _resolve_dataset_asset_url() -> tuple[str, str]:
    article_bytes, final_article_url, _ = _request_bytes(ARTICLE_URL, accept="text/html,application/xhtml+xml")
    article_text = html.unescape(article_bytes.decode("utf-8", errors="replace"))
    pattern = re.compile(r'''href=["']([^"']*''' + re.escape(EXPECTED_FILENAME) + r'''[^"']*)["']''', re.I)
    unique = list(dict.fromkeys(match.group(1) for match in pattern.finditer(article_text)))
    if len(unique) != 1:
        raise ValueError(f"expected exactly one PMC href for {EXPECTED_FILENAME}; found {len(unique)}")
    return urljoin(final_article_url, unique[0]), final_article_url


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
    interesting = [url for url in link_urls + script_urls if EXPECTED_FILENAME.lower() in url.lower() or any(term in url.lower() for term in CHALLENGE_TERMS)]
    cookie_tokens = sorted(set(re.findall(r'''[A-Za-z0-9_-]*cookie[A-Za-z0-9_-]*|cloudpmc[A-Za-z0-9_-]*''', text, flags=re.I)))
    return {
        "status": "bridge_unresolved",
        "bridge_final_url": final_url,
        "bridge_content_type": content_type,
        "bridge_sha256": hashlib.sha256(payload).hexdigest(),
        "bridge_title": (re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S).group(1).strip() if re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S) else ""),
        "bridge_href_count": len(hrefs),
        "bridge_form_action_count": len(actions),
        "bridge_script_srcs": script_urls,
        "bridge_inline_script_count": len(inline_scripts),
        "bridge_challenge_script_snippets": challenge_snippets,
        "bridge_cookie_or_challenge_tokens": cookie_tokens,
        "interesting_resolved_links": interesting,
    }


def _numeric_column_profile(sheet: xlrd.sheet.Sheet, col: int) -> dict[str, object]:
    values = [float(sheet.cell(row, col).value) for row in range(sheet.nrows) if sheet.cell(row, col).ctype == xlrd.XL_CELL_NUMBER]
    return {"column_index": col, "numeric_count": len(values), "numeric_min": min(values) if values else None, "numeric_max": max(values) if values else None}


def _workbook_audit(payload: bytes) -> tuple[str, list[dict[str, object]]]:
    digest = hashlib.sha256(payload).hexdigest()
    workbook = xlrd.open_workbook(file_contents=payload)
    audits: list[dict[str, object]] = []
    for sheet in workbook.sheets():
        candidate_rows = []
        for row in range(min(sheet.nrows, 25)):
            values = [_normalize(sheet.cell_value(row, col)) for col in range(sheet.ncols)]
            hits = [col for col, value in enumerate(values) if value and any(k in value.lower() for k in KEYWORDS)]
            if hits:
                candidate_rows.append({"row_index": row, "hit_columns": hits, "row_values": values})
        profiles = [_numeric_column_profile(sheet, col) for col in range(sheet.ncols)]
        audits.append({"sheet_name": sheet.name, "nrows": sheet.nrows, "ncols": sheet.ncols, "candidate_header_rows": candidate_rows, "coordinate_like_numeric_profiles": [p for p in profiles if p["numeric_count"] >= 3 and p["numeric_min"] is not None and -180 <= float(p["numeric_min"]) <= 180 and -180 <= float(p["numeric_max"]) <= 180]})
    return digest, audits


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    asset_url, article_url = _resolve_dataset_asset_url()
    payload, final_asset_url, content_type = _request_bytes(asset_url, accept="application/vnd.ms-excel,application/octet-stream,text/html,*/*")
    common = {"pair_id": "EPV001", "source_article_doi": "10.1073/pnas.1006225107", "source_pmcid": "PMC2947922", "article_url_resolved": article_url, "source_href_resolved_from_article": asset_url, "source_filename": EXPECTED_FILENAME, "occurrence_reads_performed": False, "operational_scope_constructed": False}
    if payload.startswith(OLE2_MAGIC):
        digest, sheets = _workbook_audit(payload)
        outcome = {**common, "status": "completed_literature_dataset_audit", "source_asset_url_resolved": final_asset_url, "source_content_type": content_type, "source_sha256": digest, "sheets": sheets}
    else:
        outcome = {**common, **_bridge_audit(payload, final_asset_url, content_type)}
    OUTPUT_PATH.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
