#!/usr/bin/env python3
"""Build reviewer-hardened pre-field main Figures 2 and 5 as SVG.

Only frozen/outcome-blind repository summaries are read. No focal Level-C
biological values are accessed.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVEL_A = ROOT / "results" / "reviewer2_level_a_structure_audit_v0_1.json"
GENERALIZED = ROOT / "results" / "pre_field_state_dependent_invalidity_v0_2.json"


def esc(text: object) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def text(x, y, value, cls="b", anchor="start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def rect(x, y, w, h, cls="box", rx=7) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>'


def line(x1, y1, x2, y2, cls="axis") -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"/>'


def svg_header(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111}.h{font-size:24px;font-weight:bold}.sh{font-size:18px;font-weight:bold}.b{font-size:14px}.s{font-size:12px}.xs{font-size:10.5px}.n{font-size:27px;font-weight:bold}.box{fill:white;stroke:#333;stroke-width:1.4}.soft{fill:#f7f7f7;stroke:#777;stroke-width:1.1}.axis{stroke:#333;stroke-width:1.2}.grid{stroke:#ddd;stroke-width:1}.heavy{stroke:#111;stroke-width:2;fill:none}.thin{stroke:#555;stroke-width:1.5;fill:none}.dash{stroke:#777;stroke-width:1.2;stroke-dasharray:5 4;fill:none}</style>',
    ]


def close_svg(parts: list[str]) -> str:
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_figure2(level_a: dict) -> str:
    d = level_a["heldout_design"]
    ref = level_a["reference_calibration"]
    ratios = level_a["taxon_level_max_observed_to_ceiling_ratio"]
    margins = level_a["cell_level_margin_diagnostics"]

    parts = svg_header(1200, 900)
    parts += [
        text(45, 40, "Figure 2. Controlled Level-A cross-source empirical anchor", "h"),
        text(45, 68, "Independent replication is by held-out taxon; procedure × area cells are repeated diagnostics.", "b"),
        text(45, 112, "A  Reference envelopes frozen before held-out opening", "sh"),
        rect(50, 132, 1100, 135, "soft", 10),
    ]

    cards = [
        (85, "24 / 24", "reference cells frozen", f"{ref['distinct_successor_taxa_per_cell_min']}–{ref['distinct_successor_taxa_per_cell_max']} adequate successor taxa / cell"),
        (415, "q95", "nearest-rank empirical envelope", "not a nominal 95% predictive interval"),
        (745, "0", "held-out values read during calibration", "relation threshold fixed prospectively"),
    ]
    for x, big, mid, small in cards:
        parts += [rect(x, 158, 290, 82), text(x+145, 187, big, "n", "middle"), text(x+145, 210, mid, "b", "middle"), text(x+145, 230, small, "s", "middle")]

    parts += [
        text(45, 315, "B  Held-out structure and outcome", "sh"),
        rect(50, 335, 1100, 145, "soft", 10),
    ]
    cards2 = [
        (82, str(d["independent_heldout_taxa"]), "fresh held-out taxa", "independent biological units"),
        (340, str(d["prespecified_cells"]), "prespecified diagnostics", "3 areas × 8 procedures / taxon"),
        (598, str(d["evaluable_cells"]), "evaluable cell diagnostics", f"{d['unresolved_cells']} unresolved"),
        (856, "0 / 12", "taxa with any exceedance", "among evaluable cells"),
    ]
    for x, big, mid, small in cards2:
        parts += [rect(x, 360, 220, 92), text(x+110, 390, big, "n", "middle"), text(x+110, 416, mid, "b", "middle"), text(x+110, 439, small, "s", "middle")]

    parts += [
        text(45, 525, "C  Taxon-level maximum observed discordance / frozen envelope", "sh"),
        text(45, 548, "Values near 1 approach the prospectively frozen cell-specific envelope; none exceed 1.", "s"),
    ]

    sorted_items = sorted(ratios.items(), key=lambda kv: kv[1], reverse=True)
    plot_x0, plot_y0, plot_w, row_h = 335, 570, 780, 21
    parts += [line(plot_x0, plot_y0-4, plot_x0+plot_w, plot_y0-4, "grid")]
    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        x = plot_x0 + plot_w * tick
        parts += [line(x, plot_y0-4, x, plot_y0 + row_h*len(sorted_items)+5, "grid"), text(x, plot_y0-10, f"{tick:.2f}", "xs", "middle")]
    for i, (taxon, ratio) in enumerate(sorted_items):
        y = plot_y0 + i*row_h + 14
        parts += [text(320, y, taxon, "s", "end")]
        x2 = plot_x0 + plot_w * ratio
        parts += [line(plot_x0, y-4, x2, y-4, "heavy"), text(min(x2+7, 1135), y, f"{ratio:.3f}", "xs")]
    y_end = plot_y0 + row_h*len(sorted_items) + 35
    parts += [
        text(45, y_end, "D  Margin diagnostics", "sh"),
        text(45, y_end+26, f"Closest margin to envelope: {margins['closest_margin']:.4f} ({margins['closest_taxon']}).", "b"),
        text(45, y_end+48, f"Cells within 0.025 of envelope: {margins['cells_with_margin_le_0_025']} / {d['evaluable_cells']}; within 0.05: {margins['cells_with_margin_le_0_05']} / {d['evaluable_cells']}.", "b"),
        text(45, y_end+70, "Interpretation: conditional cross-source reproducibility relative to predeclared empirical envelopes—not 283 independent successes.", "s"),
    ]
    return close_svg(parts)


def fdf(pi: float, q: float, sp: float) -> float:
    den = (1-pi)*(1-q) + pi*sp
    return ((1-pi)*(1-q))/den if den else 0.0


def build_figure5(generalized: dict) -> str:
    rep = generalized["representative_state_dependent_scenario"]
    p = rep["parameters"]
    r = rep["result"]

    parts = svg_header(1200, 900)
    parts += [
        text(45, 40, "Figure 5. Exact cost of coercing invalid observation into a biological negative", "h"),
        text(45, 68, "Zero collapsing is an ablation of the unresolved-state guard, not a competitor to detection-aware observation models.", "b"),
        text(45, 112, "A  General class-conditional decomposition", "sh"),
        rect(50, 132, 1100, 145, "soft", 10),
        text(92, 162, "Compatible keys (F=true)", "sh"),
        text(92, 190, "a₁ = P(valid | F=true)", "b"),
        text(92, 218, "FPRzero − FPRgated = 1 − a₁", "sh"),
        text(650, 162, "True violations (F=false)", "sh"),
        text(650, 190, "a₀ = P(valid | F=false)", "b"),
        text(650, 218, "TPRzero − TPRgated = 1 − a₀", "sh"),
        text(600, 258, "Equal-validity corollary: if a₁ = a₀ = a, both increments equal 1 − a.", "b", "middle"),
    ]

    parts += [text(45, 325, "B  State-dependent validity example", "sh"), rect(50, 345, 530, 250, "soft", 10)]
    # axes for paired bars
    x0, y0, w, h = 115, 390, 420, 150
    parts += [line(x0, y0+h, x0+w, y0+h), line(x0, y0, x0, y0+h)]
    for tick in [0, .25, .5, .75, 1.0]:
        y = y0+h - tick*h
        parts += [line(x0, y, x0+w, y, "grid"), text(x0-8, y+4, f"{tick:.2f}", "xs", "end")]
    groups = [
        ("False violation", r["gated_false_violation_rate"], r["zero_false_violation_rate"]),
        ("True-violation sensitivity", r["gated_true_violation_sensitivity"], r["zero_true_violation_sensitivity"]),
    ]
    for gi, (label, gated, zero) in enumerate(groups):
        gx = x0 + 70 + gi*210
        for j, (name, val) in enumerate([("gated", gated), ("zero", zero)]):
            bx = gx + j*55
            by = y0+h - val*h
            parts += [rect(bx, by, 38, val*h, "box", 2), text(bx+19, by-6, f"{val:.3f}", "xs", "middle"), text(bx+19, y0+h+18, name, "xs", "middle")]
        parts += [text(gx+47, y0+h+39, label, "s", "middle")]
    parts += [text(315, 579, f"a₁={p['a1']:.2f}, a₀={p['a0']:.2f}, q={p['q']:.2f}, sp={p['sp']:.2f}", "s", "middle")]

    parts += [text(620, 325, "C  Qualification is not false-discovery control", "sh"), rect(620, 345, 530, 250, "soft", 10)]
    px, py, pw, ph = 690, 385, 405, 160
    parts += [line(px, py+ph, px+pw, py+ph), line(px, py, px, py+ph)]
    for tick in [0, .25, .5, .75, 1.0]:
        y = py+ph - tick*ph
        parts += [line(px, y, px+pw, y, "grid"), text(px-8, y+4, f"{tick:.2f}", "xs", "end")]
    for tick in [0.05, .25, .5, .75, 1.0]:
        x = px + pw*((tick-.01)/.99)
        parts += [line(x, py, x, py+ph, "grid"), text(x, py+ph+18, f"{tick:.2f}", "xs", "middle")]
    for q, cls in [(0.80, "heavy"), (0.90, "thin"), (0.95, "dash")]:
        pts=[]
        for i in range(100):
            pi=.01+.99*i/99
            x=px+pw*((pi-.01)/.99)
            y=py+ph-fdf(pi,q,.99)*ph
            pts.append((x,y))
        path="M"+" L".join(f"{x:.1f},{y:.1f}" for x,y in pts)
        parts.append(f'<path d="{path}" class="{cls}"/>')
    parts += [
        text(895, 574, "true violation prevalence π", "s", "middle"),
        text(637, 470, "FDF", "s", "middle"),
        text(1080, 390, "q=0.80", "xs"),
        text(1080, 408, "q=0.90", "xs"),
        text(1080, 426, "q=0.95", "xs"),
    ]
    # marker example pi=.10 q=.80 sp=.99
    ex_pi=.10; ex=fdf(ex_pi,.80,.99); exx=px+pw*((ex_pi-.01)/.99); exy=py+ph-ex*ph
    parts += [f'<circle cx="{exx}" cy="{exy}" r="4" fill="#111"/>', text(exx+8, exy-7, f"π=0.10 → FDF≈{ex:.3f}", "xs")]

    parts += [
        text(45, 645, "D  Endpoint-state interpretation", "sh"),
        rect(50, 665, 1100, 170, "soft", 10),
        rect(100, 704, 220, 76, "box"), text(210, 731, "Qualified observation", "b", "middle"), text(210, 754, "+ valid focal key", "b", "middle"),
        line(320, 742, 410, 742, "heavy"),
        rect(420, 704, 250, 76, "box"), text(545, 731, "negative can enter", "b", "middle"), text(545, 754, "hard endpoint", "b", "middle"),
        rect(780, 695, 300, 92, "box"), text(930, 720, "Invalid / missing / failed key", "b", "middle"), text(930, 745, "must remain unresolved", "sh", "middle"), text(930, 768, "zero collapsing deletes this state", "s", "middle"),
        text(600, 822, "The decomposition quantifies the cost of removing the unresolved-state guard; it does not replace occupancy, LIES, or other detection-aware models.", "s", "middle"),
    ]
    return close_svg(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=ROOT / "manuscript" / "figures")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    level_a = json.loads(LEVEL_A.read_text(encoding="utf-8"))
    generalized = json.loads(GENERALIZED.read_text(encoding="utf-8"))
    (args.out_dir / "figure2_level_a_empirical_anchor_v0_1.svg").write_text(build_figure2(level_a), encoding="utf-8")
    (args.out_dir / "figure5_invalid_state_decomposition_v0_2.svg").write_text(build_figure5(generalized), encoding="utf-8")


if __name__ == "__main__":
    main()
