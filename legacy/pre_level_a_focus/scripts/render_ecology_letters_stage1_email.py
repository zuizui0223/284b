#!/usr/bin/env python3
"""Render the canonical Ecology Letters Stage-1 proposal email from confirmed metadata.

This utility does not send mail and does not persist human metadata unless the
caller explicitly writes the rendered output to a path. It refuses to render
unless the canonical package passes the Stage-1 readiness audit and all required
human metadata fields are complete.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
AUDIT_PATH = SCRIPTS / "audit_ecology_letters_stage1_send_readiness.py"
PITCH = ROOT / "manuscript" / "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md"
ATTACHMENT = "manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg"
TITLE = "Relation endpoints for ecological inference: when independent answers can support joint biological claims"
RECIPIENTS = "ecolets@cefe.cnrs.fr; ecolets2@cefe.cnrs.fr"
SUBJECT = "Unsolicited Method proposal — Relation endpoints for ecological inference"

SPEC = importlib.util.spec_from_file_location("stage1_send_readiness", AUDIT_PATH)
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def _pitch_body() -> str:
    text = PITCH.read_text(encoding="utf-8")
    return text.split("\n\n", 1)[1].strip()


def _clean_list(values: Any, field: str) -> list[str]:
    if not isinstance(values, list):
        raise ValueError(f"{field} must be a list")
    cleaned = [value.strip() for value in values if isinstance(value, str) and value.strip()]
    if not cleaned:
        raise ValueError(f"{field} must contain at least one non-empty string")
    return cleaned


def render(metadata: dict[str, Any]) -> str:
    readiness = AUDIT.audit(metadata)
    if readiness["status"] != "metadata_complete_package_scientifically_ready":
        missing = ", ".join(readiness["missing_human_metadata"])
        raise ValueError(f"human metadata is incomplete: {missing}")

    authors = _clean_list(metadata["authors_order"], "authors_order")
    affiliations = _clean_list(metadata["affiliations"], "affiliations")
    corresponding_name = metadata["corresponding_author_name"].strip()
    corresponding_email = metadata["corresponding_email"].strip()
    qualifications = metadata["author_qualifications"].strip()

    author_line = "; ".join(authors)
    affiliation_block = "\n".join(affiliations)
    pitch_body = _pitch_body()

    return f"""# Ecology Letters Stage-1 proposal email — rendered from confirmed metadata

**Recipients:** {RECIPIENTS}  
**Subject:** {SUBJECT}

Dear Ecology Letters Method Editors,

We would like to ask whether you would consider inviting a Method submission provisionally entitled **“{TITLE}.”**

Proposed author list: {author_line}

The article introduces an executable **relation-endpoint authorization method** for deciding what biological relation independently generated ecological answers are entitled to test and when that endpoint may be opened. It is not a new occupancy estimator, JSDM, data-fusion method or observation-process typology; those methods can instead supply role-specific or joint statistical inputs to the endpoint contract.

Our 295-word proposal is reproduced below with one compact quantitative figure. The complete pre-outcome contract — including the frozen calibration or qualification reference used by its opening rule — can be canonically serialized and SHA-256 fingerprinted. A classical coupling counterexample separately shows why the relation layer is not eliminated by perfect marginal answers: exact `p_E=p_F=0.5` still permits hard-violation probability from 0 to 0.5 under different joint couplings. The empirical anchor contains 12 independently held-out taxa; its 283 evaluable procedure-by-area cells are repeated diagnostics rather than independent replication. Focal cross-role biological outcomes remain sealed.

{qualifications}

Thank you for considering the proposal. If the editors regard the quantitative contribution as better suited to another Ecology Letters article type, we would appreciate guidance before making a full submission.

Best regards,

{corresponding_name}
{affiliation_block}
{corresponding_email}

---

## Proposal text — exact canonical 295-word body

{pitch_body}

## Attachment

`{ATTACHMENT}`
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.human_metadata.read_text(encoding="utf-8"))
    rendered = render(metadata)
    if args.out is None:
        print(rendered)
    else:
        args.out.write_text(rendered, encoding="utf-8")
        print(json.dumps({
            "status": "rendered",
            "output": str(args.out),
            "does_not_send_email": True,
            "focal_level_c_values_read": False,
            "empirical_ledger_increment": 0,
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
