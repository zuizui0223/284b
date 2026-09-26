#!/usr/bin/env python3
"""Validate Paper 1 human/editor metadata and render final submission surfaces.

This script deliberately fails closed. It cannot infer authorship, affiliations,
editorial authorization, approvals or declarations from repository state. Once a
human-verified metadata JSON passes all gates, it renders final title-page,
cover-letter and declaration surfaces while preserving the frozen manuscript,
figure and archive identities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVER_TEMPLATE = ROOT / "manuscript" / "ECOLOGY_LETTERS_FULL_COVER_LETTER_V0_2.md"
DEFAULT_OUT = ROOT / "manuscript" / "final_submission"

SCIENCE_SHA = "66ad208f2a922800cb7f1d14f96b28295de13af4cdbdbec2f8b698b8fa320cc5"
SUBMISSION_SHA = "a2f45e2b91953b47f24682e95667533a923680ec65a9b0fef2c88a423b75cf84"
BUNDLE_SHA = "ebf1d848ac2eaa99f7e15b5f8a95e33262f1f76a768b1f4f8944331b177ff680"
TITLE = "Relation endpoints for ecological inference: when independent answers can support joint biological claims"

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-[\dX]{4}$")
PLACEHOLDER = "__REQUIRED"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def missing_text(value) -> bool:
    return not isinstance(value, str) or not value.strip() or PLACEHOLDER in value


def validate_metadata(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "paper1_human_metadata_v1":
        errors.append("schema must be paper1_human_metadata_v1")
    if data.get("journal") != "Ecology Letters":
        errors.append("journal must be Ecology Letters")
    if data.get("article_type") != "Method":
        errors.append("article_type must be Method")

    editorial = data.get("editorial") or {}
    if editorial.get("full_method_authorized") is not True:
        errors.append("editorial.full_method_authorized must be true")
    if missing_text(editorial.get("authorization_reference")):
        errors.append("editorial.authorization_reference is required")
    auth_date = editorial.get("authorization_date")
    if missing_text(auth_date):
        errors.append("editorial.authorization_date is required")
    else:
        try:
            date.fromisoformat(auth_date)
        except ValueError:
            errors.append("editorial.authorization_date must be YYYY-MM-DD")

    affiliations = data.get("affiliations")
    if not isinstance(affiliations, list) or not affiliations:
        errors.append("at least one affiliation is required")
        affiliations = []
    affiliation_ids: set[str] = set()
    for i, aff in enumerate(affiliations, 1):
        aid = aff.get("affiliation_id") if isinstance(aff, dict) else None
        text = aff.get("text") if isinstance(aff, dict) else None
        if missing_text(aid):
            errors.append(f"affiliation {i}: affiliation_id is required")
        elif aid in affiliation_ids:
            errors.append(f"affiliation {i}: duplicate affiliation_id {aid}")
        else:
            affiliation_ids.add(aid)
        if missing_text(text):
            errors.append(f"affiliation {i}: text is required")

    authors = data.get("authors")
    if not isinstance(authors, list) or not authors:
        errors.append("at least one author is required")
        authors = []
    author_ids: set[str] = set()
    orders: list[int] = []
    for i, author in enumerate(authors, 1):
        if not isinstance(author, dict):
            errors.append(f"author {i}: must be an object")
            continue
        aid = author.get("author_id")
        if missing_text(aid):
            errors.append(f"author {i}: author_id is required")
        elif aid in author_ids:
            errors.append(f"author {i}: duplicate author_id {aid}")
        else:
            author_ids.add(aid)
        if missing_text(author.get("name")):
            errors.append(f"author {i}: name is required")
        order = author.get("order")
        if not isinstance(order, int) or order < 1:
            errors.append(f"author {i}: order must be a positive integer")
        else:
            orders.append(order)
        refs = author.get("affiliation_ids")
        if not isinstance(refs, list) or not refs:
            errors.append(f"author {i}: at least one affiliation_id is required")
        else:
            for ref in refs:
                if ref not in affiliation_ids:
                    errors.append(f"author {i}: unknown affiliation_id {ref}")
        status = author.get("orcid_status")
        if status not in {"confirmed", "not_required"}:
            errors.append(f"author {i}: orcid_status must be confirmed or not_required")
        orcid = author.get("orcid", "")
        if status == "confirmed" and (not isinstance(orcid, str) or not ORCID_RE.fullmatch(orcid.strip())):
            errors.append(f"author {i}: confirmed ORCID must match 0000-0000-0000-0000/X")
        roles = author.get("credit_roles")
        if not isinstance(roles, list) or not roles or any(missing_text(x) for x in roles):
            errors.append(f"author {i}: at least one verified contribution/CREDIT role is required")

    if orders and sorted(orders) != list(range(1, len(authors) + 1)):
        errors.append("author orders must be unique and contiguous from 1")

    corresponding = data.get("corresponding_author") or {}
    corresponding_id = corresponding.get("author_id")
    if corresponding_id not in author_ids:
        errors.append("corresponding_author.author_id must match a listed author")
    email = corresponding.get("email")
    if missing_text(email) or not EMAIL_RE.fullmatch(str(email).strip()):
        errors.append("corresponding_author.email must be a valid verified email")

    declarations = data.get("declarations") or {}
    for key in ["author_order_confirmed", "all_authors_approved", "not_under_consideration_elsewhere"]:
        if declarations.get(key) is not True:
            errors.append(f"declarations.{key} must be true")
    for key in ["competing_interests_statement", "related_work_disclosure"]:
        if missing_text(declarations.get(key)):
            errors.append(f"declarations.{key} is required (use an explicit none statement if applicable)")

    if missing_text(data.get("funding_statement")):
        errors.append("funding_statement is required (use an explicit no-funding statement if applicable)")
    if missing_text(data.get("acknowledgements")):
        errors.append("acknowledgements is required (use an explicit none statement if applicable)")

    return errors


def ordered_authors(data: dict) -> list[dict]:
    return sorted(data["authors"], key=lambda x: x["order"])


def corresponding_author(data: dict) -> dict:
    target = data["corresponding_author"]["author_id"]
    return next(a for a in data["authors"] if a["author_id"] == target)


def render_title_page(data: dict) -> str:
    affiliations = {x["affiliation_id"]: x["text"] for x in data["affiliations"]}
    aff_order = [x["affiliation_id"] for x in data["affiliations"]]
    aff_number = {aid: i + 1 for i, aid in enumerate(aff_order)}
    author_lines = []
    for author in ordered_authors(data):
        nums = ",".join(str(aff_number[x]) for x in author["affiliation_ids"])
        orcid = f"; ORCID {author['orcid']}" if author["orcid_status"] == "confirmed" else ""
        author_lines.append(f"- {author['name']} [{nums}]{orcid}")
    corr = corresponding_author(data)
    corr_email = data["corresponding_author"]["email"]

    lines = [
        "# Ecology Letters Method — final title page",
        "",
        "**Article type:** Method",
        "",
        f"**Title:** {TITLE}",
        "",
        "**Running title:** Relation endpoints in ecology",
        "",
        "## Authors",
        "",
        *author_lines,
        "",
        "## Affiliations",
        "",
    ]
    lines.extend(f"{aff_number[aid]}. {affiliations[aid]}" for aid in aff_order)
    lines += [
        "",
        f"**Corresponding author:** {corr['name']} — {corr_email}",
        "",
        "**Keywords:** ecological inference; relation endpoint; validation; imperfect detection; identifiability; biological dependency; observation process; cross-source reproducibility; model adequacy; preregistration",
        "",
        "## Exact submission identity",
        "",
        f"- Ecology Letters manuscript SHA-256: `{SUBMISSION_SHA}`",
        f"- frozen scientific-source SHA-256: `{SCIENCE_SHA}`",
        f"- archive bundle SHA-256: `{BUNDLE_SHA}`",
        "- abstract: 146 words",
        "- main text: 3,437 words",
        "- references: 16",
        "- display items: 6",
        "",
        "## Funding",
        "",
        data["funding_statement"].strip(),
        "",
        "## Acknowledgements",
        "",
        data["acknowledgements"].strip(),
        "",
        "## Competing interests",
        "",
        data["declarations"]["competing_interests_statement"].strip(),
        "",
    ]
    return "\n".join(lines)


def render_declarations(data: dict) -> str:
    lines = [
        "# Paper 1 final declarations and author contributions",
        "",
        "## Author contributions",
        "",
    ]
    for author in ordered_authors(data):
        lines.append(f"- **{author['name']}:** " + "; ".join(author["credit_roles"]))
    lines += [
        "",
        "## Submission declarations",
        "",
        "- Author order has been confirmed by the author group.",
        "- All authors have explicitly approved the submission.",
        "- The manuscript is not under consideration elsewhere.",
        f"- Competing interests: {data['declarations']['competing_interests_statement'].strip()}",
        f"- Related work disclosure: {data['declarations']['related_work_disclosure'].strip()}",
        "",
        "## Editorial authorization",
        "",
        f"- Ecology Letters full Method authorization/invitation: {data['editorial']['authorization_reference'].strip()}",
        f"- Authorization date: {data['editorial']['authorization_date']}",
        "",
        "## Funding",
        "",
        data["funding_statement"].strip(),
        "",
        "## Acknowledgements",
        "",
        data["acknowledgements"].strip(),
        "",
    ]
    return "\n".join(lines)


def render_cover_letter(data: dict) -> str:
    text = COVER_TEMPLATE.read_text(encoding="utf-8")
    text = text.replace(
        "[Insert verified statement that the manuscript is not under consideration elsewhere and that all authors approve the submission.]",
        "The manuscript is not under consideration elsewhere, and all authors have explicitly approved this submission.",
    )
    text = text.replace(
        "[Insert the Ecology Letters Method invitation/approved-proposal reference or date.]",
        f"Ecology Letters Method authorization/invitation: {data['editorial']['authorization_reference'].strip()} ({data['editorial']['authorization_date']}).",
    )
    text = text.replace(
        "[Insert one concise sentence on any related work by the final author group and how this manuscript differs.]",
        "Related work disclosure: " + data["declarations"]["related_work_disclosure"].strip(),
    )
    corr = corresponding_author(data)
    corr_affs = {x["affiliation_id"]: x["text"] for x in data["affiliations"]}
    signature_aff = "; ".join(corr_affs[x] for x in corr["affiliation_ids"])
    old_signature = "ZHANG Ruiqi  \n[Affiliation]  \n[Corresponding email]  \n[On behalf of all authors]"
    new_signature = f"{corr['name']}  \n{signature_aff}  \n{data['corresponding_author']['email']}  \n[On behalf of all authors]"
    text = text.replace(old_signature, new_signature)
    text = text.replace(
        "An immutable repository release/archive identifier and DOI(s) will be inserted before invited full submission.",
        f"The submission content is frozen under archive bundle SHA-256 `{BUNDLE_SHA}`; the final public release/archive identifier and DOI will be inserted after the publication gate is cleared.",
    )
    text = text.replace(
        "**Status:** invited-full-submission candidate only. Do not send until an Ecology Letters Method invitation/approved proposal, final author metadata and all-author approval are verified.",
        "**Status:** rendered from human-verified metadata after all fail-closed submission gates passed.",
    )
    return text


def finalize(metadata_path: Path, out_dir: Path) -> dict:
    raw = metadata_path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    errors = validate_metadata(data)
    if errors:
        raise ValueError("human metadata gate failed:\n- " + "\n- ".join(errors))

    out_dir.mkdir(parents=True, exist_ok=True)
    title_path = out_dir / "ECOLOGY_LETTERS_TITLE_PAGE_FINAL.md"
    cover_path = out_dir / "ECOLOGY_LETTERS_COVER_LETTER_FINAL.md"
    declarations_path = out_dir / "PAPER1_DECLARATIONS_FINAL.md"
    title_path.write_text(render_title_page(data), encoding="utf-8")
    cover_path.write_text(render_cover_letter(data), encoding="utf-8")
    declarations_path.write_text(render_declarations(data), encoding="utf-8")

    receipt = {
        "schema": "paper1_human_metadata_finalization_receipt_v1",
        "metadata_sha256": sha256_bytes(raw),
        "scientific_source_sha256": SCIENCE_SHA,
        "submission_derivative_sha256": SUBMISSION_SHA,
        "archive_bundle_sha256": BUNDLE_SHA,
        "human_metadata_gate": "passed",
        "outputs": {
            title_path.name: sha256_bytes(title_path.read_bytes()),
            cover_path.name: sha256_bytes(cover_path.read_bytes()),
            declarations_path.name: sha256_bytes(declarations_path.read_bytes()),
        },
    }
    receipt_path = out_dir / "PAPER1_HUMAN_METADATA_FINALIZATION_RECEIPT_V1.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.metadata.read_text(encoding="utf-8"))
    errors = validate_metadata(data)
    if errors:
        print("Human metadata gate: BLOCKED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Human metadata gate: PASS")
    if not args.validate_only:
        receipt = finalize(args.metadata, args.out_dir)
        print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
