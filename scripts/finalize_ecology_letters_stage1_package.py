#!/usr/bin/env python3
"""Finalize the Ecology Letters Stage-1 proposal package after human metadata is confirmed.

The finalizer composes existing gates rather than weakening them:
1. verify the frozen Stage-1 RC is byte-identical;
2. verify all required human metadata are complete;
3. render the canonical proposal email;
4. write the rendered email plus a non-sensitive receipt outside the repository.

It never sends email, never infers missing human metadata, never opens focal Level-C
outcomes, and refuses to write human-metadata-bearing output inside the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
AUDIT_PATH = SCRIPTS / "audit_ecology_letters_stage1_send_readiness.py"
RENDER_PATH = SCRIPTS / "render_ecology_letters_stage1_email.py"

EMAIL_FILENAME = "ecology_letters_stage1_proposal_email.md"
RECEIPT_FILENAME = "ecology_letters_stage1_finalization_receipt.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _load_module("stage1_send_readiness_for_finalizer", AUDIT_PATH)
RENDER = _load_module("stage1_email_renderer_for_finalizer", RENDER_PATH)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_within_repo(path: Path) -> bool:
    resolved = path.resolve()
    return resolved == ROOT.resolve() or resolved.is_relative_to(ROOT.resolve())


def build_finalization(
    metadata: dict[str, Any],
    *,
    out_dir: Path | None = None,
    write_outputs: bool = False,
) -> tuple[str, dict[str, Any]]:
    """Return rendered email and a non-sensitive finalization receipt.

    When ``write_outputs`` is true, ``out_dir`` is required and must be outside
    the repository. The receipt deliberately stores no raw human metadata.
    """
    readiness = AUDIT.audit(metadata)
    if readiness["status"] != "metadata_complete_package_scientifically_ready":
        missing = readiness.get("missing_human_metadata", [])
        details = f"; missing={','.join(missing)}" if missing else ""
        raise ValueError(f"Stage-1 finalization blocked: {readiness['status']}{details}")

    rendered = RENDER.render(metadata)
    rc = readiness["release_candidate_audit"]
    receipt: dict[str, Any] = {
        "schema_version": "ecology_letters_stage1_finalization_receipt_v0_1",
        "status": "finalized_not_sent",
        "stage1_title": readiness["stage1_title"],
        "canonical_manifest": readiness["canonical_manifest"],
        "release_candidate_package_identity_sha256": rc["package_identity_sha256"],
        "release_candidate_source_tree_commit": rc["source_tree_commit"],
        "release_candidate_byte_identical": rc["byte_identical"],
        "rendered_email_sha256": _sha256_text(rendered),
        "rendered_email_filename": EMAIL_FILENAME,
        "attachment": RENDER.ATTACHMENT,
        "required_human_metadata_complete": all(readiness["human_metadata_checks"].values()),
        "raw_human_metadata_embedded_in_receipt": False,
        "output_written_inside_repository": False,
        "does_not_send_email": True,
        "does_not_infer_human_metadata": True,
        "focal_level_c_values_read": False,
        "empirical_ledger_increment": 0,
        "global_284b_empirical_ledger": 1,
    }

    if write_outputs:
        if out_dir is None:
            raise ValueError("out_dir is required when write_outputs=True")
        if _is_within_repo(out_dir):
            raise ValueError("refusing to write rendered human metadata inside the repository")
        out_dir.mkdir(parents=True, exist_ok=True)
        email_path = out_dir / EMAIL_FILENAME
        receipt_path = out_dir / RECEIPT_FILENAME
        email_path.write_text(rendered, encoding="utf-8")
        receipt_path.write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return rendered, receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human-metadata", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and print the non-sensitive receipt without writing the rendered email",
    )
    args = parser.parse_args()

    metadata = json.loads(args.human_metadata.read_text(encoding="utf-8"))
    if not args.dry_run and args.out_dir is None:
        parser.error("--out-dir is required unless --dry-run is used")

    _, receipt = build_finalization(
        metadata,
        out_dir=args.out_dir,
        write_outputs=not args.dry_run,
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
