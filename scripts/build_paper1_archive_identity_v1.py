#!/usr/bin/env python3
"""Build a content-addressed archive identity receipt for Paper 1.

This script is packaging-only. It hashes the exact submission derivative, frozen
scientific source, supplement, claim/display assets, and executable Method object.
It does not create a DOI, release, or alter any scientific endpoint.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "manuscript/PAPER1_ECOLOGY_LETTERS_SUBMISSION_V1.md",
    "manuscript/PAPER1_ECOLOGY_LETTERS_SUBMISSION_V1.sha256",
    "manuscript/PAPER1_ECOLOGY_LETTERS_SUBMISSION_V1_IDENTITY.txt",
    "manuscript/PREFIELD_FLAGSHIP_V0_10_CANDIDATE.md",
    "manuscript/PREFIELD_FLAGSHIP_V0_10_CANDIDATE.sha256",
    "manuscript/PAPER1_SUPPLEMENT_V0_1.md",
    "manuscript/PAPER1_SUPPLEMENT_MANIFEST_V0_1.md",
    "manuscript/CLAIM_EVIDENCE_LEDGER_V0_5.md",
    "manuscript/FULL_SUBMISSION_DISPLAY_MANIFEST_V0_3.md",
    "manuscript/FULL_SUBMISSION_FIGURE_CAPTIONS_V0_3.md",
    "manuscript/figures/figure1_relation_endpoint_contract_v1_0.svg",
    "manuscript/figures/figure2_level_a_empirical_anchor_v1_0.svg",
    "manuscript/figures/figure3_relation_layer_and_event_function_v1_0.svg",
    "manuscript/figures/figure4_parallel_openability_audits_v1_0.svg",
    "manuscript/figures/figure5_invalid_state_decomposition_v1_0.svg",
    "manuscript/TABLE1_CLAIM_EVIDENCE_MATRIX_V0_2.md",
    "scripts/relation_endpoint_contract.py",
    "scripts/freeze_relation_endpoint_contract.py",
    "scripts/relation_endpoint_quickstart.py",
    "scripts/build_prefield_flagship_v0_10_candidate.py",
    "scripts/build_paper1_ecology_letters_submission_v1.py",
    "scripts/build_paper1_submission_figures_v1.py",
    "scripts/render_paper1_submission_figures.py",
    "scripts/export_paper1_submission_figures.py",
    "scripts/build_paper1_archive_identity_v1.py",
]

EXPECTED_SCIENCE_SHA256 = "66ad208f2a922800cb7f1d14f96b28295de13af4cdbdbec2f8b698b8fa320cc5"
EXPECTED_SUBMISSION_SHA256 = "a2f45e2b91953b47f24682e95667533a923680ec65a9b0fef2c88a423b75cf84"

JSON_OUT = ROOT / "manuscript" / "PAPER1_ARCHIVE_IDENTITY_V1.json"
MD_OUT = ROOT / "manuscript" / "PAPER1_ARCHIVE_IDENTITY_V1.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> None:
    missing = [p for p in FILES if not (ROOT / p).exists()]
    if missing:
        raise FileNotFoundError("missing archive files: " + ", ".join(missing))

    science_sha = sha256(ROOT / "manuscript/PREFIELD_FLAGSHIP_V0_10_CANDIDATE.md")
    submission_sha = sha256(ROOT / "manuscript/PAPER1_ECOLOGY_LETTERS_SUBMISSION_V1.md")
    if science_sha != EXPECTED_SCIENCE_SHA256:
        raise ValueError(f"scientific source SHA drift: {science_sha}")
    if submission_sha != EXPECTED_SUBMISSION_SHA256:
        raise ValueError(f"submission derivative SHA drift: {submission_sha}")

    entries = [
        {"path": rel, "sha256": sha256(ROOT / rel), "bytes": (ROOT / rel).stat().st_size}
        for rel in sorted(FILES)
    ]
    payload = {
        "schema": "paper1_archive_identity_v1",
        "status": "archive_candidate_not_doi_release",
        "source_commit": git_head(),
        "scientific_source_sha256": science_sha,
        "submission_derivative_sha256": submission_sha,
        "scientific_boundary": {
            "level_a": "sole_completed_empirical_endpoint",
            "level_b": "unopened",
            "level_c": "focal_outcomes_sealed",
            "empirical_ledger": 1,
        },
        "doi": None,
        "release_tag": None,
        "files": entries,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload["bundle_identity_sha256"] = hashlib.sha256(canonical).hexdigest()

    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Paper 1 archive identity v1",
        "",
        "**Status:** archive candidate; no DOI or public release is asserted by this receipt.",
        "",
        f"- source commit used to build receipt: `{payload['source_commit']}`",
        f"- scientific source SHA-256: `{science_sha}`",
        f"- Ecology Letters submission derivative SHA-256: `{submission_sha}`",
        f"- bundle identity SHA-256: `{payload['bundle_identity_sha256']}`",
        "- scientific boundary: Level A sole empirical closure; Level B unopened; focal Level-C outcomes sealed; empirical ledger = 1.",
        "",
        "## Included files",
        "",
    ]
    lines.extend(f"- `{e['path']}` — `{e['sha256']}` — {e['bytes']} bytes" for e in entries)
    lines += [
        "",
        "## Publication gate",
        "",
        "A GitHub release/tag and archive DOI must be added only after the final human/editor fields are resolved. Publishing an archive must not open Level B or Level C or change the empirical ledger.",
        "",
    ]
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(JSON_OUT)
    print(MD_OUT)
    print(payload["bundle_identity_sha256"])


if __name__ == "__main__":
    main()
