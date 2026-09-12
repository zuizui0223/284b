#!/usr/bin/env python3
"""Audit Ecology Letters Stage-1 send readiness without reading focal Level-C values.

The gate has two layers:
1. scientific/package readiness from the frozen repository surfaces;
2. human metadata completeness supplied in a separate JSON file.

It does not send email and does not infer missing human metadata.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"

PITCH = MANUSCRIPT / "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md"
PROPOSAL = MANUSCRIPT / "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md"
EMAIL = MANUSCRIPT / "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md"
COMPLIANCE = MANUSCRIPT / "ECOLOGY_LETTERS_COMPLIANCE_V0_6.md"
MANIFEST = MANUSCRIPT / "ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_6.md"
SNAPSHOT = MANUSCRIPT / "ECOLOGY_LETTERS_SUBMISSION_READY_SNAPSHOT_V0_4.md"
ATTACHMENT = MANUSCRIPT / "figures" / "ecology_letters_method_proposal_figure_v0_5.svg"

STAGE1_TITLE = "Relation endpoints for ecological inference: when independent answers can support joint biological claims"
REQUIRED_METADATA = (
    "authors_order",
    "affiliations",
    "corresponding_author_name",
    "corresponding_email",
    "author_qualifications",
)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def _pitch_body() -> str:
    text = PITCH.read_text(encoding="utf-8")
    return text.split("\n\n", 1)[1]


def _package_checks() -> dict[str, bool]:
    manifest = MANIFEST.read_text(encoding="utf-8")
    compliance = COMPLIANCE.read_text(encoding="utf-8")
    proposal = PROPOSAL.read_text(encoding="utf-8")
    email = EMAIL.read_text(encoding="utf-8")
    snapshot = SNAPSHOT.read_text(encoding="utf-8")
    pitch_words = _word_count(_pitch_body())

    return {
        "canonical_files_exist": all(
            path.exists()
            for path in [PITCH, PROPOSAL, EMAIL, COMPLIANCE, MANIFEST, SNAPSHOT, ATTACHMENT]
        ),
        "pitch_within_300_words": pitch_words <= 300,
        "pitch_is_frozen_295_words": pitch_words == 295,
        "title_synchronized": all(
            STAGE1_TITLE in text for text in [proposal, email, compliance, manifest, snapshot]
        ),
        "manifest_routes_pitch_v08": "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md" in manifest,
        "manifest_routes_proposal_v09": "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md" in manifest,
        "manifest_routes_email_v06": "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md" in manifest,
        "manifest_routes_compliance_v06": "ECOLOGY_LETTERS_COMPLIANCE_V0_6.md" in manifest,
        "fingerprintable_contract_exposed": "opening_rule_reference" in manifest
        and "SHA-256" in compliance
        and "fingerprint" in proposal.lower(),
        "human_placeholders_not_silently_filled": "[Affiliation]" in email
        and "[Email]" in email
        and "[Insert final author-qualification sentence(s) here" in email,
        "level_c_remains_sealed": "focal hard/soft/knockout values sealed" in snapshot,
        "empirical_ledger_remains_one": "Empirical ledger: **1**" in snapshot,
    }


def _metadata_checks(metadata: dict[str, Any] | None) -> tuple[dict[str, bool], list[str]]:
    if metadata is None:
        return {key: False for key in REQUIRED_METADATA}, list(REQUIRED_METADATA)

    checks: dict[str, bool] = {}
    checks["authors_order"] = isinstance(metadata.get("authors_order"), list) and bool(
        [x for x in metadata.get("authors_order", []) if isinstance(x, str) and x.strip()]
    )
    checks["affiliations"] = isinstance(metadata.get("affiliations"), list) and bool(
        [x for x in metadata.get("affiliations", []) if isinstance(x, str) and x.strip()]
    )
    checks["corresponding_author_name"] = isinstance(metadata.get("corresponding_author_name"), str) and bool(
        metadata.get("corresponding_author_name", "").strip()
    )
    email = metadata.get("corresponding_email")
    checks["corresponding_email"] = isinstance(email, str) and bool(
        re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()) if isinstance(email, str) else False
    )
    checks["author_qualifications"] = isinstance(metadata.get("author_qualifications"), str) and bool(
        metadata.get("author_qualifications", "").strip()
    )

    missing = [key for key, ok in checks.items() if not ok]
    return checks, missing


def audit(metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    package_checks = _package_checks()
    metadata_checks, missing_metadata = _metadata_checks(metadata)
    package_ready = all(package_checks.values())
    metadata_ready = all(metadata_checks.values())

    if not package_ready:
        status = "blocked_package_integrity"
    elif not metadata_ready:
        status = "blocked_human_metadata"
    else:
        status = "metadata_complete_package_scientifically_ready"

    return {
        "schema_version": "ecology_letters_stage1_send_readiness_v0_1",
        "status": status,
        "stage1_title": STAGE1_TITLE,
        "canonical_manifest": str(MANIFEST.relative_to(ROOT)),
        "package_checks": package_checks,
        "human_metadata_checks": metadata_checks,
        "missing_human_metadata": missing_metadata,
        "does_not_send_email": True,
        "does_not_infer_human_metadata": True,
        "focal_level_c_values_read": False,
        "empirical_ledger_increment": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human-metadata", type=Path)
    args = parser.parse_args()

    metadata = None
    if args.human_metadata is not None:
        metadata = json.loads(args.human_metadata.read_text(encoding="utf-8"))
    print(json.dumps(audit(metadata), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
