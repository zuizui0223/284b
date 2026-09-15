#!/usr/bin/env python3
"""Build full-width Paper 1 submission figures with legible final-size typography.

The scientific content and numerical values are inherited from the current v0.x SVGs.
This builder only changes presentation: typography, a few line breaks/short labels,
and limited box/canvas geometry needed to keep text legible at 173 mm width.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "manuscript" / "figures"

SOURCES = {
    1: FIG_DIR / "figure1_relation_endpoint_contract_v0_2.svg",
    2: FIG_DIR / "figure2_level_a_empirical_anchor_v0_2.svg",
    3: FIG_DIR / "figure3_relation_layer_and_event_function_v0_2.svg",
    4: FIG_DIR / "figure4_parallel_openability_audits_v0_1.svg",
    5: FIG_DIR / "figure5_invalid_state_decomposition_v0_3.svg",
}
OUTPUTS = {
    1: FIG_DIR / "figure1_relation_endpoint_contract_v1_0.svg",
    2: FIG_DIR / "figure2_level_a_empirical_anchor_v1_0.svg",
    3: FIG_DIR / "figure3_relation_layer_and_event_function_v1_0.svg",
    4: FIG_DIR / "figure4_parallel_openability_audits_v1_0.svg",
    5: FIG_DIR / "figure5_invalid_state_decomposition_v1_0.svg",
}


def upgrade_style(svg: str) -> str:
    svg = svg.replace(
        "text{font-family:Arial,sans-serif;fill:#111}",
        "text{font-family:'Liberation Sans',Arial,sans-serif;fill:#111}",
    )
    replacements = {
        ".h{font-size:24px;font-weight:bold}": ".h{font-size:27px;font-weight:bold}",
        ".sh{font-size:18px;font-weight:bold}": ".sh{font-size:20px;font-weight:bold}",
        ".b{font-size:14px}": ".b{font-size:17px}",
        ".s{font-size:12px}": ".s{font-size:16px}",
        ".xs{font-size:10.5px}": ".xs{font-size:15px}",
        ".n{font-size:26px;font-weight:bold}": ".n{font-size:29px;font-weight:bold}",
        ".n{font-size:27px;font-weight:bold}": ".n{font-size:29px;font-weight:bold}",
    }
    for old, new in replacements.items():
        if old in svg:
            svg = svg.replace(old, new)
    return svg


def figure1(svg: str) -> str:
    svg = upgrade_style(svg)
    svg = svg.replace("coherence / dependency /", "coherence / dependency")
    svg = svg.replace("other declared biology", "declared biology")
    svg = svg.replace(
        '<text x="1043" y="763" class="xs" text-anchor="middle">hard violation authorized</text>',
        '<text x="1043" y="763" class="xs" text-anchor="middle">hard violation</text>',
    )
    svg = svg.replace(
        "One layer above model fitting: answer construction first, biological relation authorization second.",
        "Answer construction first; biological relation authorization second.",
    )
    return svg


def figure2(svg: str) -> str:
    svg = upgrade_style(svg)
    svg = svg.replace(
        '<text x="890" y="210" class="b" text-anchor="middle">held-out values read during calibration</text><text x="890" y="230" class="s" text-anchor="middle">relation threshold fixed prospectively</text>',
        '<text x="890" y="208" class="b" text-anchor="middle">held-out values read</text><text x="890" y="232" class="s" text-anchor="middle">none; threshold frozen prospectively</text>',
    )
    svg = svg.replace(
        "Interpretation: conditional cross-source reproducibility relative to predeclared empirical envelopes—not 283 independent successes.",
        "Conditional cross-source reproducibility relative to frozen envelopes—not 283 independent successes.",
    )
    return svg


def figure3(svg: str) -> str:
    svg = upgrade_style(svg)
    svg = svg.replace(
        "Figure 3. Accurate answers do not determine the biological relation they may jointly test",
        "Figure 3. Exact marginals do not determine a biological relation",
    )
    svg = svg.replace("Route 1: externally complete provider set", "Route 1: complete provider set")
    svg = svg.replace(
        "Established probability theory used as a separation argument, not claimed as a new theorem.",
        "Established probability theory used as a separation argument; not a new theorem.",
    )
    return svg


def figure4(svg: str) -> str:
    svg = upgrade_style(svg)
    short = {
        "external relation evidence": "relation evidence",
        "dependent-event answer": "event answer",
        "required-function answer": "function answer",
        "R / X / Y separated": "R / X / Y separate",
        "required before F=false": "required for F=false",
        "external experimental evidence": "external experiment",
        "separate from monitoring stream": "separate channel",
        "same monitored inflorescences": "same inflorescences",
        "direct dependent-event estimand": "direct event estimand",
        "flower contact on camera": "camera flower contact",
        "direct positive function observation": "positive function observation",
        "independent relation evidence": "independent evidence",
        "separate from phenology files": "separate channel",
        "natural emergence stream": "emergence stream",
        "natural budbreak stream": "budbreak stream",
        "direct required-resource signal": "required-resource signal",
        "camera non-detection ≠ effective-pollination absence": "camera non-detection ≠ function absence",
        "no gold-standard detection comparison": "no reference detection comparison",
        "new data: same-flower reference observation": "new: same-flower reference observation",
        "plus explicit failure / out-of-frame accounting": "+ failure / out-of-frame accounting",
        "unrecorded budbreak ≠ confirmed resource absence": "unrecorded budbreak ≠ resource absence",
        "no repeated / cross-observer validation": "no repeated/cross-observer validation",
        "new data: repeated within-tree scoring": "new: repeated within-tree scoring",
        "plus explicit missing-versus-absence coding": "+ missing-versus-absence coding",
    }
    for old, new in short.items():
        svg = svg.replace(old, new)

    # The original two-line 10.5 px footers had only 12 user units of leading.
    # Give the 15 px v1 footers real leading and a slightly taller STOP box.
    svg = svg.replace('x="795" y="332" width="305" height="116"', 'x="795" y="332" width="305" height="136"')
    svg = svg.replace('x="947" y="434" class="xs"', 'x="947" y="439" class="xs"')
    svg = svg.replace('x="947" y="446" class="xs"', 'x="947" y="459" class="xs"')
    svg = svg.replace('x="600" y="483" class="s"', 'x="600" y="497" class="s"')

    svg = svg.replace('x="795" y="610" width="305" height="116"', 'x="795" y="610" width="305" height="136"')
    svg = svg.replace('x="947" y="712" class="xs"', 'x="947" y="717" class="xs"')
    svg = svg.replace('x="947" y="724" class="xs"', 'x="947" y="737" class="xs"')
    svg = svg.replace('x="600" y="761" class="s"', 'x="600" y="775" class="s"')
    return svg


def figure5(svg: str) -> str:
    svg = upgrade_style(svg)
    svg = svg.replace(
        "Zero collapsing is an ablation of the unresolved-state guard, not a competitor to detection-aware observation models.",
        "Zero collapsing ablates the unresolved-state guard; it is not a competitor to detection-aware models.",
    )
    svg = svg.replace(
        "The decomposition quantifies removing the unresolved-state guard; it does not replace occupancy, LIES, or other detection-aware models.",
        "This quantifies removing the unresolved-state guard; it does not replace detection-aware models.",
    )
    return svg


TRANSFORMS = {1: figure1, 2: figure2, 3: figure3, 4: figure4, 5: figure5}


def build_all() -> None:
    for num in range(1, 6):
        source = SOURCES[num].read_text(encoding="utf-8")
        out = TRANSFORMS[num](source)
        OUTPUTS[num].write_text(out, encoding="utf-8")
        print(OUTPUTS[num])


if __name__ == "__main__":
    build_all()
