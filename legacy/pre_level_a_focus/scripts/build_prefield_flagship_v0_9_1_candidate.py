#!/usr/bin/env python3
"""Assemble the bibliography-hardened Paper-1 v0.9.1 candidate.

The builder is editorial only. It starts from the guarded v0.9 candidate, replaces
only the Introduction and working-reference block with audited v0.9.1 assets, and
updates the candidate status line. Methods, Results, Discussion, numerical results,
endpoint states and the empirical ledger are preserved byte-for-byte from v0.9.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_9_CANDIDATE.md"
INTRO = ROOT / "manuscript" / "PAPER1_INTRODUCTION_V0_9_1_CANDIDATE.md"
REFS = ROOT / "manuscript" / "WORKING_REFERENCES_V0_9_1.md"
DEFAULT_OUT = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_9_1_CANDIDATE.md"

OLD_STATUS = "**Status:** noncanonical editorial candidate v0.9; frozen v0.7 and Stage-1 package remain authoritative until separately promoted."
NEW_STATUS = "**Status:** noncanonical editorial candidate v0.9.1; frozen v0.7 and Stage-1 package remain authoritative until separately promoted."


def _extract_intro(text: str) -> str:
    marker = "## Introduction\n\n"
    if marker not in text:
        raise ValueError("v0.9.1 introduction marker missing")
    return text.split(marker, 1)[1].rstrip()


def _extract_refs(text: str) -> str:
    start = "- Blanchet FG, Cazelles K, Gravel D. 2020."
    if start not in text:
        raise ValueError("audited reference block start missing")
    body = text[text.index(start):]
    if "\n\n## Placement notes" not in body:
        raise ValueError("audited reference block end missing")
    return body.split("\n\n## Placement notes", 1)[0].rstrip()


def build_candidate(source: str, intro_asset: str, refs_asset: str) -> str:
    if source.count(OLD_STATUS) != 1:
        raise ValueError("v0.9 status anchor changed")
    if source.count("## 1. Introduction") != 1 or source.count("## 2. Methods") != 1:
        raise ValueError("v0.9 Introduction/Methods anchors changed")
    if source.count("## Working references") != 1 or source.count("## Proposed display items") != 1:
        raise ValueError("v0.9 reference/display anchors changed")

    intro = _extract_intro(intro_asset)
    refs = _extract_refs(refs_asset)

    out = source.replace(OLD_STATUS, NEW_STATUS, 1)

    before_intro, after_intro_marker = out.split("## 1. Introduction", 1)
    _, after_intro = after_intro_marker.split("## 2. Methods", 1)
    out = before_intro + "## 1. Introduction\n\n" + intro + "\n\n## 2. Methods" + after_intro

    before_refs, after_refs_marker = out.split("## Working references", 1)
    _, after_refs = after_refs_marker.split("## Proposed display items", 1)
    out = before_refs + "## Working references\n\n" + refs + "\n\n## Proposed display items" + after_refs

    return out


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    intro = INTRO.read_text(encoding="utf-8")
    refs = REFS.read_text(encoding="utf-8")
    candidate = build_candidate(source, intro, refs)
    DEFAULT_OUT.write_text(candidate, encoding="utf-8")
    print(DEFAULT_OUT)


if __name__ == "__main__":
    main()
