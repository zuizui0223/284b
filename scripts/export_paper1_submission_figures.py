#!/usr/bin/env python3
"""Export Paper 1 v1 SVG figures as 173-mm-wide vector PDFs.

Production-only: no scientific values are changed. CairoSVG maps CSS px to 0.75 pt
at the default 96 dpi, so a 173-mm PDF page width corresponds to ~653.858 CSS px.
"""

from __future__ import annotations

from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "manuscript" / "figures"
OUT = ROOT / "artifacts" / "paper1_submission_figures"

WIDTH_MM = 173.0
CSS_PX_PER_IN = 96.0
OUTPUT_WIDTH_PX = WIDTH_MM / 25.4 * CSS_PX_PER_IN

FIGURES = [
    (1, FIG_DIR / "figure1_relation_endpoint_contract_v1_0.svg"),
    (2, FIG_DIR / "figure2_level_a_empirical_anchor_v1_0.svg"),
    (3, FIG_DIR / "figure3_relation_layer_and_event_function_v1_0.svg"),
    (4, FIG_DIR / "figure4_parallel_openability_audits_v1_0.svg"),
    (5, FIG_DIR / "figure5_invalid_state_decomposition_v1_0.svg"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for num, src in FIGURES:
        if not src.exists():
            raise SystemExit(f"missing v1 SVG: {src}")
        dst = OUT / f"Figure_{num}.pdf"
        cairosvg.svg2pdf(
            bytestring=src.read_bytes(),
            write_to=str(dst),
            output_width=OUTPUT_WIDTH_PX,
        )
        print(dst)


if __name__ == "__main__":
    main()
