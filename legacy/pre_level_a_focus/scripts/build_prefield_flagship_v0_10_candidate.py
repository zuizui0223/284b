#!/usr/bin/env python3
"""Assemble the compressed Paper-1 v0.10 full-manuscript candidate.

The v0.10 edit is presentation-only. It uses the bibliography-hardened v0.9.1
Introduction, compressed Methods/Results, unchanged v0.9 Discussion, and audited
v0.9.1 references. Abstract, numerical claim boundary, display list and empirical
ledger are inherited from v0.9 unless explicitly guarded below.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_9_CANDIDATE.md"
INTRO = ROOT / "manuscript" / "PAPER1_INTRODUCTION_V0_9_1_CANDIDATE.md"
METHODS = ROOT / "manuscript" / "PAPER1_METHODS_V0_10_CANDIDATE.md"
RESULTS = ROOT / "manuscript" / "PAPER1_RESULTS_V0_10_CANDIDATE.md"
REFS = ROOT / "manuscript" / "WORKING_REFERENCES_V0_9_1.md"
DEFAULT_OUT = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_10_CANDIDATE.md"

OLD_STATUS = "**Status:** noncanonical editorial candidate v0.9; frozen v0.7 and Stage-1 package remain authoritative until separately promoted."
NEW_STATUS = "**Status:** noncanonical editorial candidate v0.10 — main-text compressed; frozen v0.7 and Stage-1 package remain authoritative until separately promoted."


def _body(asset: str, heading: str) -> str:
    marker = f"## {heading}\n\n"
    if marker not in asset:
        raise ValueError(f"missing {heading} marker")
    return asset.split(marker, 1)[1].rstrip()


def _refs(asset: str) -> str:
    start = "- Blanchet FG, Cazelles K, Gravel D. 2020."
    if start not in asset or "\n\n## Placement notes" not in asset:
        raise ValueError("audited reference block markers missing")
    return asset[asset.index(start):].split("\n\n## Placement notes", 1)[0].rstrip()


def _replace_section(text: str, start_heading: str, next_heading: str, body: str) -> str:
    start = f"## {start_heading}"
    nxt = f"## {next_heading}"
    if text.count(start) != 1 or text.count(nxt) != 1:
        raise ValueError(f"section anchors changed: {start_heading} / {next_heading}")
    before, tail = text.split(start, 1)
    _, after = tail.split(nxt, 1)
    return before + start + "\n\n" + body + "\n\n" + nxt + after


def build_candidate(source: str, intro_asset: str, methods_asset: str, results_asset: str, refs_asset: str) -> str:
    if source.count(OLD_STATUS) != 1:
        raise ValueError("v0.9 status anchor changed")
    out = source.replace(OLD_STATUS, NEW_STATUS, 1)
    out = _replace_section(out, "1. Introduction", "2. Methods", _body(intro_asset, "Introduction"))
    out = _replace_section(out, "2. Methods", "3. Results", _body(methods_asset, "Methods"))
    out = _replace_section(out, "3. Results", "4. Discussion", _body(results_asset, "Results"))

    if out.count("## Working references") != 1 or out.count("## Proposed display items") != 1:
        raise ValueError("reference/display anchors changed")
    before, tail = out.split("## Working references", 1)
    _, after = tail.split("## Proposed display items", 1)
    out = before + "## Working references\n\n" + _refs(refs_asset) + "\n\n## Proposed display items" + after
    return out


def main() -> None:
    candidate = build_candidate(
        SOURCE.read_text(encoding="utf-8"),
        INTRO.read_text(encoding="utf-8"),
        METHODS.read_text(encoding="utf-8"),
        RESULTS.read_text(encoding="utf-8"),
        REFS.read_text(encoding="utf-8"),
    )
    DEFAULT_OUT.write_text(candidate, encoding="utf-8")
    print(DEFAULT_OUT)


if __name__ == "__main__":
    main()
