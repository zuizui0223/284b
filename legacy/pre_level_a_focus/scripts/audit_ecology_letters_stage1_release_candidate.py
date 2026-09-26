#!/usr/bin/env python3
"""Audit current Stage-1 canonical files against the frozen byte-addressed RC.

Git blob SHA-1 is recomputed directly from local file bytes, so CI can detect
one-byte drift without a network call or a Git checkout comparison.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT = ROOT / "results" / "ecology_letters_stage1_release_candidate_v0_2.json"
EXPECTED_SCHEMA = "ecology_letters_stage1_release_candidate_v0_2"


def git_blob_sha1_bytes(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def git_blob_sha1_file(path: Path) -> str:
    return git_blob_sha1_bytes(path.read_bytes())


def identity_material(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": receipt["schema_version"],
        "source_tree_commit": receipt["source_tree_commit"],
        "canonical_blob_sha1": dict(sorted(receipt["canonical_blob_sha1"].items())),
    }


def recompute_package_identity(receipt: dict[str, Any]) -> str:
    canonical_json = json.dumps(
        identity_material(receipt),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def load_receipt(path: Path = DEFAULT_RECEIPT) -> dict[str, Any]:
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if receipt.get("schema_version") != EXPECTED_SCHEMA:
        raise ValueError(f"unexpected RC schema: {receipt.get('schema_version')}")
    expected_identity = recompute_package_identity(receipt)
    if receipt.get("package_identity_sha256") != expected_identity:
        raise ValueError("release-candidate package identity does not match receipt material")
    if receipt.get("canonical_file_count") != len(receipt.get("canonical_blob_sha1", {})):
        raise ValueError("canonical_file_count does not match blob map")
    return receipt


def audit_current_tree(
    *,
    root: Path = ROOT,
    receipt_path: Path = DEFAULT_RECEIPT,
) -> dict[str, Any]:
    receipt = load_receipt(receipt_path)
    expected = receipt["canonical_blob_sha1"]
    missing: list[str] = []
    changed: list[dict[str, str]] = []
    matched: list[str] = []

    for relpath, expected_sha in sorted(expected.items()):
        path = root / relpath
        if not path.exists():
            missing.append(relpath)
            continue
        current_sha = git_blob_sha1_file(path)
        if current_sha == expected_sha:
            matched.append(relpath)
        else:
            changed.append(
                {
                    "path": relpath,
                    "expected_git_blob_sha1": expected_sha,
                    "current_git_blob_sha1": current_sha,
                }
            )

    byte_identical = not missing and not changed and len(matched) == len(expected)
    return {
        "schema_version": "ecology_letters_stage1_release_candidate_audit_v0_1",
        "status": "matches_frozen_release_candidate" if byte_identical else "release_candidate_drift_detected",
        "release_candidate_receipt": str(receipt_path.relative_to(root)) if receipt_path.is_relative_to(root) else str(receipt_path),
        "source_tree_commit": receipt["source_tree_commit"],
        "package_identity_sha256": receipt["package_identity_sha256"],
        "canonical_file_count": len(expected),
        "matched_file_count": len(matched),
        "byte_identical_to_frozen_release_candidate": byte_identical,
        "missing_paths": missing,
        "changed_files": changed,
        "human_metadata_embedded": False,
        "email_sent": False,
        "focal_level_c_values_read": False,
        "empirical_ledger_increment": 0,
        "global_284b_empirical_ledger": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    print(json.dumps(audit_current_tree(receipt_path=args.receipt), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
