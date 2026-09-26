#!/usr/bin/env python3
"""Prepare minimal proposal-stage metadata for the frozen Ecology Letters Stage-1 renderer.

This helper is administrative only. It does not send email and does not modify any
frozen Stage-1 scientific asset. It converts a proposal-stage provisional author
set into the legacy metadata schema already consumed by the frozen readiness audit
and email renderer.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_SINGLE_AUTHOR_QUALIFICATION = (
    "The lead author works across empirical pollination ecology, "
    "species-distribution modelling and reproducible computational inference."
)


def _clean_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    cleaned = [x.strip() for x in value if isinstance(x, str) and x.strip()]
    if not cleaned:
        raise ValueError(f"{field} must contain at least one non-empty string")
    return cleaned


def prepare(metadata: dict[str, Any]) -> dict[str, Any]:
    authors = _clean_list(metadata.get("provisional_authors"), "provisional_authors")
    affiliations = _clean_list(metadata.get("affiliations"), "affiliations")

    sender_name = metadata.get("sender_name", "")
    if not isinstance(sender_name, str):
        raise ValueError("sender_name must be a string")
    sender_name = sender_name.strip() or authors[0]

    sender_email = metadata.get("sender_email", "")
    if not isinstance(sender_email, str) or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", sender_email.strip()):
        raise ValueError("sender_email must be a valid email address")
    sender_email = sender_email.strip()

    qualifications = metadata.get("author_qualifications", "")
    if not isinstance(qualifications, str):
        raise ValueError("author_qualifications must be a string")
    qualifications = qualifications.strip()

    if not qualifications:
        if len(authors) == 1:
            qualifications = DEFAULT_SINGLE_AUTHOR_QUALIFICATION
        else:
            raise ValueError(
                "author_qualifications is required for a multi-author proposal; "
                "the frozen lead-author sentence must not be silently generalized"
            )

    return {
        "authors_order": authors,
        "affiliations": affiliations,
        "corresponding_author_name": sender_name,
        "corresponding_email": sender_email,
        "author_qualifications": qualifications,
        "stage1_authorship_status": "provisional_for_unsolicited_proposal_only",
        "does_not_freeze_full_submission_author_order": True,
        "does_not_send_email": True,
        "focal_level_c_values_read": False,
        "empirical_ledger_increment": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposal-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.proposal_metadata.read_text(encoding="utf-8"))
    prepared = prepare(metadata)
    rendered = json.dumps(prepared, indent=2, ensure_ascii=False) + "\n"
    if args.out is None:
        print(rendered, end="")
    else:
        args.out.write_text(rendered, encoding="utf-8")
        print(json.dumps({"status": "prepared", "output": str(args.out), "does_not_send_email": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
