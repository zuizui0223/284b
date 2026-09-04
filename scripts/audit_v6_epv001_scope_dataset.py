#!/usr/bin/env python3
"""Audit the published EPV001 Dataset S1 workbook without occurrence access.

This step is literature-only. It downloads the PNAS supplementary XLS named by
the article's Associated Data section, hashes it, and reports workbook structure
and coordinate-column candidates. It does not construct an operational polygon.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

import xlrd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "artifacts/product_b_v6_epv001_scope_dataset_audit.json"
SOURCE_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC2947922/bin/1006225107_sd01.xls"
EXPECTED_FILENAME = "1006225107_sd01.xls"
KEYWORDS = ("lat", "latitude", "lon", "long", "longitude", "locality", "location", "site", "population")


def _normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


def _get_bytes(url: str, *, timeout_seconds: float = 90.0) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.ms-excel,application/octet-stream,*/*",
            "User-Agent": "zuizui0223-284b-product-b-v6-literature-scope/0.1",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read()
    if not payload:
        raise ValueError("published Dataset S1 download was empty")
    return payload


def _numeric_column_profile(sheet: xlrd.sheet.Sheet, col: int) -> dict[str, object]:
    values: list[float] = []
    for row in range(sheet.nrows):
        cell = sheet.cell(row, col)
        if cell.ctype == xlrd.XL_CELL_NUMBER:
            values.append(float(cell.value))
    return {
        "column_index": col,
        "numeric_count": len(values),
        "numeric_min": min(values) if values else None,
        "numeric_max": max(values) if values else None,
    }


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = _get_bytes(SOURCE_URL)
    digest = hashlib.sha256(payload).hexdigest()
    workbook = xlrd.open_workbook(file_contents=payload)

    sheet_audits: list[dict[str, object]] = []
    for sheet in workbook.sheets():
        candidate_rows: list[dict[str, object]] = []
        candidate_columns: set[int] = set()
        for row in range(min(sheet.nrows, 25)):
            values = [_normalize(sheet.cell_value(row, col)) for col in range(sheet.ncols)]
            hits = [
                col
                for col, value in enumerate(values)
                if value and any(keyword in value.lower() for keyword in KEYWORDS)
            ]
            if hits:
                candidate_columns.update(hits)
                candidate_rows.append(
                    {
                        "row_index": row,
                        "hit_columns": hits,
                        "row_values": values,
                    }
                )

        profiles = [_numeric_column_profile(sheet, col) for col in range(sheet.ncols)]
        coordinate_like_profiles = [
            profile
            for profile in profiles
            if profile["numeric_count"] >= 3
            and profile["numeric_min"] is not None
            and profile["numeric_max"] is not None
            and (
                (-90.0 <= float(profile["numeric_min"]) <= 90.0 and -90.0 <= float(profile["numeric_max"]) <= 90.0)
                or (-180.0 <= float(profile["numeric_min"]) <= 180.0 and -180.0 <= float(profile["numeric_max"]) <= 180.0)
            )
        ]
        sheet_audits.append(
            {
                "sheet_name": sheet.name,
                "nrows": sheet.nrows,
                "ncols": sheet.ncols,
                "candidate_header_rows": candidate_rows,
                "candidate_header_columns": sorted(candidate_columns),
                "coordinate_like_numeric_profiles": coordinate_like_profiles,
            }
        )

    outcome = {
        "status": "completed_literature_dataset_audit",
        "pair_id": "EPV001",
        "source_article_doi": "10.1073/pnas.1006225107",
        "source_pmcid": "PMC2947922",
        "source_url": SOURCE_URL,
        "source_filename": EXPECTED_FILENAME,
        "source_sha256": digest,
        "workbook_sheet_count": workbook.nsheets,
        "sheets": sheet_audits,
        "occurrence_reads_performed": False,
        "operational_scope_constructed": False,
    }
    OUTPUT_PATH.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
