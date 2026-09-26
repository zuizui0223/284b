#!/usr/bin/env python3
"""Sanitize one frozen Product-A presealed artifact to structure-only CSV.

The raw Product-A CSV contains both fitted-structure metadata and forbidden score /
recovery values.  This boundary verifies the exact pinned ZIP digest and emits only
the allowlisted columns declared in the v7 source contract.  Downstream v7 code
must consume the sanitized CSV, never the raw metric-bearing member.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

from product_b_v7.differentiability import SAFE_STRUCTURE_COLUMNS


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sanitize(source_zip: Path, contract_path: Path, output_csv: Path) -> dict[str, object]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    observed_digest = sha256_file(source_zip)
    expected_digest = str(contract["source_artifact_sha256"])
    if observed_digest != expected_digest:
        raise ValueError("Product-A source artifact digest changed")

    allowed = tuple(str(x) for x in contract["allowed_structural_columns"])
    if allowed != SAFE_STRUCTURE_COLUMNS:
        raise ValueError("v7 structural allowlist changed")
    forbidden = set(str(x) for x in contract["forbidden_value_columns"])
    if set(allowed) & forbidden:
        raise ValueError("structural allowlist overlaps forbidden Product-A values")

    member = str(contract["source_member"])
    with zipfile.ZipFile(source_zip) as archive:
        names = set(archive.namelist())
        if member not in names:
            raise ValueError("pinned Product-A member missing from artifact")
        raw = archive.read(member).decode("utf-8")

    reader = csv.DictReader(io.StringIO(raw))
    header = tuple(reader.fieldnames or ())
    missing = [column for column in allowed if column not in header]
    if missing:
        raise ValueError(f"Product-A structural columns missing: {missing}")
    missing_forbidden = [column for column in forbidden if column not in header]
    if missing_forbidden:
        raise ValueError(
            "raw source no longer has the expected metric-bearing schema; refuse silent source substitution"
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    row_count = 0
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(allowed))
        writer.writeheader()
        for raw_row in reader:
            writer.writerow({column: raw_row[column] for column in allowed})
            row_count += 1

    return {
        "status": "sanitized_structure_only",
        "source_artifact_sha256": observed_digest,
        "source_member": member,
        "output_columns": list(allowed),
        "forbidden_columns_emitted": [],
        "row_count": row_count,
        "product_a_score_or_recovery_values_emitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-zip", required=True)
    parser.add_argument(
        "--contract",
        default="config/product_b_v7_kim001_model_structure_source_v0_1.json",
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit-json", required=False)
    args = parser.parse_args()
    audit = sanitize(Path(args.source_zip), Path(args.contract), Path(args.output))
    if args.audit_json:
        target = Path(args.audit_json)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
