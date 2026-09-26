#!/usr/bin/env python3
"""Layout-only repair for reviewer-hardened pre-field Figures 2 and 5.

Scientific calculations are inherited unchanged from v0.1. This wrapper only:
- increases Figure 2 canvas height so margin diagnostics are not clipped;
- moves the Figure 5 representative-scenario parameter line above the bars so
  it does not overlap the group labels.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "scripts" / "build_prefield_main_figures_v0_1.py"
LEVEL_A = ROOT / "results" / "reviewer2_level_a_structure_audit_v0_1.json"
GENERALIZED = ROOT / "results" / "pre_field_state_dependent_invalidity_v0_2.json"

spec = importlib.util.spec_from_file_location("prefield_figures_v1", V1_PATH)
v1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v1
spec.loader.exec_module(v1)


def build_figure2(level_a: dict) -> str:
    svg = v1.build_figure2(level_a)
    svg = svg.replace(
        'width="1200" height="900" viewBox="0 0 1200 900"',
        'width="1200" height="970" viewBox="0 0 1200 970"',
        1,
    )
    svg = svg.replace(
        '<rect width="1200" height="900" fill="white"/>',
        '<rect width="1200" height="970" fill="white"/>',
        1,
    )
    return svg


def build_figure5(generalized: dict) -> str:
    svg = v1.build_figure5(generalized)
    svg = svg.replace('x="315" y="579"', 'x="315" y="371"', 1)
    return svg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=ROOT / "manuscript" / "figures")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    level_a = json.loads(LEVEL_A.read_text(encoding="utf-8"))
    generalized = json.loads(GENERALIZED.read_text(encoding="utf-8"))
    (args.out_dir / "figure2_level_a_empirical_anchor_v0_2.svg").write_text(
        build_figure2(level_a), encoding="utf-8"
    )
    (args.out_dir / "figure5_invalid_state_decomposition_v0_3.svg").write_text(
        build_figure5(generalized), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
