#!/usr/bin/env python3
"""Freeze the canonical Ecology Letters Stage-1 package as a release candidate.

The release-candidate identity is SHA-256 over deterministic JSON containing
(1) the Git commit that content-addresses the source tree and (2) the exact
canonical file set. Human metadata remains a separate external layer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "ecology_letters_stage1_release_candidate_v0_1"
CANONICAL_PATHS = (
    "config/ecology_letters_stage1_human_metadata_template.json",
    "config/relation_endpoint_contract_example.json",
    "docs/relation_endpoint_quickstart.md",
    "manuscript/CLOSER_ANTECEDENT_AUDIT_V0_4.md",
    "manuscript/ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md",
    "manuscript/ECOLOGY_LETTERS_COMPLIANCE_V0_6.md",
    "manuscript/ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md",
    "manuscript/ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md",
    "manuscript/ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_6.md",
    "manuscript/ECOLOGY_LETTERS_SUBMISSION_READY_SNAPSHOT_V0_4.md",
    "manuscript/RELATION_LAYER_SEPARATION_V0_1.md",
    "manuscript/TITLE_AUDIT_V0_1.md",
    "manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg",
    "results/relation_endpoint_contract_example_freeze_v0_1.json",
    "results/relation_layer_separation_v0_1.json",
    "scripts/audit_ecology_letters_stage1_send_readiness.py",
    "scripts/freeze_relation_endpoint_contract.py",
    "scripts/relation_endpoint_contract.py",
    "scripts/relation_endpoint_quickstart.py",
    "scripts/render_ecology_letters_stage1_email.py",
)


def _validate_commit_sha(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("source_tree_commit must be a 40-character lowercase Git SHA")
    return value


def identity_material(source_tree_commit: str) -> dict:
    source_tree_commit = _validate_commit_sha(source_tree_commit)
    missing = [path for path in CANONICAL_PATHS if not (ROOT / path).exists()]
    if missing:
        raise FileNotFoundError(f"missing canonical Stage-1 files: {missing}")
    return {
        "schema_version": SCHEMA_VERSION,
        "source_tree_commit": source_tree_commit,
        "canonical_paths": sorted(CANONICAL_PATHS),
    }


def build_receipt(source_tree_commit: str) -> dict:
    material = identity_material(source_tree_commit)
    canonical_json = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    package_identity = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "package_identity_material": material,
        "package_identity_sha256": package_identity,
        "identity_semantics": "sha256(canonical_json(source_tree_commit + canonical_paths))",
        "human_metadata_embedded": False,
        "email_sent": False,
        "focal_level_c_values_read": False,
        "empirical_ledger_increment": 0,
        "global_284b_empirical_ledger": 1,
        "status": "scientific_package_frozen_human_metadata_external",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()
    receipt = build_receipt(args.source_commit)
    text = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
