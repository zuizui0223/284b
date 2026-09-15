#!/usr/bin/env python3
"""Build the Ecology Letters submission-format derivative of frozen Paper 1 v0.10.

Allowed changes relative to the exact scientific v0.10 snapshot:
- Introduction citation coverage/order (v0.9.2 production pass);
- reference-list typography/style;
- submission-status metadata and the reference heading.

Methods, Results, Discussion, abstract, scientific numbers and endpoint states are
inherited unchanged from v0.10.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_10_CANDIDATE.md"
INTRO = ROOT / "manuscript" / "PAPER1_INTRODUCTION_V0_9_2_CANDIDATE.md"
REFS = ROOT / "manuscript" / "ECOLOGY_LETTERS_REFERENCES_V1.md"
DEFAULT_OUT = ROOT / "manuscript" / "PAPER1_ECOLOGY_LETTERS_SUBMISSION_V1.md"

SOURCE_SHA256 = "66ad208f2a922800cb7f1d14f96b28295de13af4cdbdbec2f8b698b8fa320cc5"
OLD_STATUS = "**Status:** noncanonical editorial candidate v0.10 — main-text compressed; frozen v0.7 and Stage-1 package remain authoritative until separately promoted."
NEW_STATUS = (
    "**Status:** Ecology Letters submission-format derivative v1; scientific content "
    "frozen to exact v0.10."
)


def _intro_body(asset: str) -> str:
    marker = "## Introduction\n\n"
    if marker not in asset:
        raise ValueError("Introduction marker missing")
    return asset.split(marker, 1)[1].rstrip()


def _reference_body(asset: str) -> str:
    start = "## Reference list\n\n"
    end = "\n\n## Audit notes"
    if start not in asset or end not in asset:
        raise ValueError("Reference block markers missing")
    return asset.split(start, 1)[1].split(end, 1)[0].rstrip()


def build_submission(source: str, intro_asset: str, refs_asset: str) -> str:
    if source.count(OLD_STATUS) != 1:
        raise ValueError("v0.10 status anchor changed")
    out = source.replace(OLD_STATUS, NEW_STATUS, 1)

    intro_start = "## 1. Introduction"
    methods_start = "## 2. Methods"
    if out.count(intro_start) != 1 or out.count(methods_start) != 1:
        raise ValueError("Introduction/Methods anchors changed")
    before, tail = out.split(intro_start, 1)
    _, after = tail.split(methods_start, 1)
    out = before + intro_start + "\n\n" + _intro_body(intro_asset) + "\n\n" + methods_start + after

    old_ref = "## Working references"
    displays = "## Proposed display items"
    if out.count(old_ref) != 1 or out.count(displays) != 1:
        raise ValueError("Reference/display anchors changed")
    before, tail = out.split(old_ref, 1)
    _, after = tail.split(displays, 1)
    out = before + "## References\n\n" + _reference_body(refs_asset) + "\n\n" + displays + after
    return out


def main() -> None:
    output = build_submission(
        SOURCE.read_text(encoding="utf-8"),
        INTRO.read_text(encoding="utf-8"),
        REFS.read_text(encoding="utf-8"),
    )
    DEFAULT_OUT.write_text(output, encoding="utf-8")
    print(DEFAULT_OUT)


if __name__ == "__main__":
    main()
