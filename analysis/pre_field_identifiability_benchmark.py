#!/usr/bin/env python3
"""Exact pre-field benchmark for hard ecological dependency inference.

This benchmark is synthetic and analytic. It never reads focal Level-C values.

Latent relation:
    E(k) -> F(k)

Condition on an adequately positive dependent event E(k). Let:
    v  = P(F=false | E=true), the true violation prevalence
    s  = P(positive function detection | F=true, valid observation)
    sp = P(negative function observation | F=false, valid observation)
    a  = P(valid observation key)

where a is the product of complete-window coverage, non-missingness, and
non-failure probabilities.

Two rules are compared:
1. naive-zero: any non-positive/invalid function observation is collapsed to F=false.
2. identifiability-gated: a hard violation is emitted only when the observation
   process is prospectively qualified and the key itself is valid; invalid keys
   are unresolved.

For a qualified observation process:
    naive false-violation rate | F=true = 1 - a*s
    gated false-violation rate | F=true = a*(1-s)
    naive true-violation sensitivity | F=false = 1 - a*(1-sp)
    gated true-violation sensitivity | F=false = a*sp

Therefore both the apparent sensitivity gain and the false-violation inflation
created by collapsing invalid states equal exactly 1-a.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

SENSITIVITY_MIN = 0.80
SPECIFICITY_MIN = 0.95
HARD_FNR_MAX = 0.20

SCENARIOS = [
    dict(name="high_quality_dense", violation_prevalence=0.10, event_probability=0.50,
         event_detection_sensitivity=0.95, opportunities=20, complete_window_fraction=1.00,
         missingness=0.00, failure_rate=0.00, specificity=0.99),
    dict(name="threshold_sensitivity", violation_prevalence=0.10, event_probability=0.20,
         event_detection_sensitivity=0.80, opportunities=1, complete_window_fraction=1.00,
         missingness=0.00, failure_rate=0.00, specificity=0.99),
    dict(name="subthreshold_sensitivity", violation_prevalence=0.10, event_probability=0.20,
         event_detection_sensitivity=0.50, opportunities=1, complete_window_fraction=1.00,
         missingness=0.00, failure_rate=0.00, specificity=0.99),
    dict(name="sparse_event", violation_prevalence=0.10, event_probability=0.05,
         event_detection_sensitivity=0.80, opportunities=5, complete_window_fraction=1.00,
         missingness=0.00, failure_rate=0.00, specificity=0.99),
    dict(name="high_missingness", violation_prevalence=0.10, event_probability=0.50,
         event_detection_sensitivity=0.95, opportunities=20, complete_window_fraction=1.00,
         missingness=0.30, failure_rate=0.00, specificity=0.99),
    dict(name="device_failure", violation_prevalence=0.10, event_probability=0.50,
         event_detection_sensitivity=0.95, opportunities=20, complete_window_fraction=1.00,
         missingness=0.00, failure_rate=0.20, specificity=0.99),
    dict(name="incomplete_window", violation_prevalence=0.10, event_probability=0.50,
         event_detection_sensitivity=0.95, opportunities=20, complete_window_fraction=0.50,
         missingness=0.00, failure_rate=0.00, specificity=0.99),
    dict(name="mixed_qualified", violation_prevalence=0.10, event_probability=0.20,
         event_detection_sensitivity=0.80, opportunities=5, complete_window_fraction=0.80,
         missingness=0.10, failure_rate=0.05, specificity=0.95),
    dict(name="subthreshold_specificity", violation_prevalence=0.10, event_probability=0.50,
         event_detection_sensitivity=0.95, opportunities=20, complete_window_fraction=1.00,
         missingness=0.00, failure_rate=0.00, specificity=0.80),
]


def effective_key_sensitivity(event_probability: float, event_detection_sensitivity: float,
                              opportunities: int) -> float:
    """P(at least one detected event | at least one true event) over a window."""
    if not (0.0 < event_probability <= 1.0):
        raise ValueError("event_probability must be in (0, 1]")
    if not (0.0 <= event_detection_sensitivity <= 1.0):
        raise ValueError("event_detection_sensitivity must be in [0, 1]")
    if opportunities < 1:
        raise ValueError("opportunities must be >= 1")
    p_true_any = 1.0 - (1.0 - event_probability) ** opportunities
    p_detect_any = 1.0 - (1.0 - event_probability * event_detection_sensitivity) ** opportunities
    return p_detect_any / p_true_any


def benchmark_metrics(*, violation_prevalence: float, key_sensitivity: float,
                      valid_key_fraction: float, specificity: float) -> dict[str, float | bool | None]:
    for name, value in {
        "violation_prevalence": violation_prevalence,
        "key_sensitivity": key_sensitivity,
        "valid_key_fraction": valid_key_fraction,
        "specificity": specificity,
    }.items():
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"{name} must be in [0, 1]")

    v = violation_prevalence
    q = 1.0 - v
    s = key_sensitivity
    a = valid_key_fraction
    sp = specificity

    calibration_pass = (
        s >= SENSITIVITY_MIN
        and (1.0 - s) <= HARD_FNR_MAX + 1e-12
        and sp >= SPECIFICITY_MIN
    )

    naive_false_violation_rate = 1.0 - a * s
    naive_true_violation_sensitivity = 1.0 - a * (1.0 - sp)

    if calibration_pass:
        gated_false_violation_rate = a * (1.0 - s)
        gated_true_violation_sensitivity = a * sp
        gated_unresolved_fraction = 1.0 - a
    else:
        gated_false_violation_rate = 0.0
        gated_true_violation_sensitivity = 0.0
        # Positive observations remain compatible; all non-positive states are unresolved.
        gated_unresolved_fraction = (
            q * (1.0 - a * s)
            + v * (1.0 - a * (1.0 - sp))
        )

    naive_called_violation = (
        q * naive_false_violation_rate
        + v * naive_true_violation_sensitivity
    )
    naive_false_discovery_fraction = (
        q * naive_false_violation_rate / naive_called_violation
        if naive_called_violation > 0 else None
    )

    gated_called_violation = (
        q * gated_false_violation_rate
        + v * gated_true_violation_sensitivity
    )
    gated_false_discovery_fraction = (
        q * gated_false_violation_rate / gated_called_violation
        if gated_called_violation > 0 else None
    )

    return {
        "calibration_pass": calibration_pass,
        "naive_false_violation_rate": naive_false_violation_rate,
        "gated_false_violation_rate": gated_false_violation_rate,
        "naive_true_violation_sensitivity": naive_true_violation_sensitivity,
        "gated_true_violation_sensitivity": gated_true_violation_sensitivity,
        "gated_unresolved_fraction": gated_unresolved_fraction,
        "naive_false_discovery_fraction": naive_false_discovery_fraction,
        "gated_false_discovery_fraction": gated_false_discovery_fraction,
        "invalid_state_mass": 1.0 - a,
        "false_violation_inflation_from_invalid_states": (
            naive_false_violation_rate - gated_false_violation_rate
            if calibration_pass else None
        ),
        "apparent_sensitivity_gain_from_invalid_states": (
            naive_true_violation_sensitivity - gated_true_violation_sensitivity
            if calibration_pass else None
        ),
    }


def scenario_row(scenario: dict) -> dict:
    s = effective_key_sensitivity(
        scenario["event_probability"],
        scenario["event_detection_sensitivity"],
        scenario["opportunities"],
    )
    a = (
        scenario["complete_window_fraction"]
        * (1.0 - scenario["missingness"])
        * (1.0 - scenario["failure_rate"])
    )
    metrics = benchmark_metrics(
        violation_prevalence=scenario["violation_prevalence"],
        key_sensitivity=s,
        valid_key_fraction=a,
        specificity=scenario["specificity"],
    )
    return {
        "scenario": scenario["name"],
        **{k: v for k, v in scenario.items() if k != "name"},
        "key_sensitivity": s,
        "valid_key_fraction": a,
        **metrics,
    }


def build_surface() -> list[dict]:
    rows = []
    for v in (0.01, 0.05, 0.10, 0.25, 0.50):
        for s in (0.50, 0.80, 0.90, 0.95, 0.99):
            for a_i in range(1, 11):
                a = a_i / 10.0
                m = benchmark_metrics(
                    violation_prevalence=v,
                    key_sensitivity=s,
                    valid_key_fraction=a,
                    specificity=0.99,
                )
                rows.append({
                    "violation_prevalence": v,
                    "key_sensitivity": s,
                    "valid_key_fraction": a,
                    "specificity": 0.99,
                    **m,
                })
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("rows must be non-empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_svg(path: Path) -> None:
    """Dependency-free two-panel SVG from exact formulas."""
    width, height = 1000, 440
    margin = 60
    panel_w = 400
    panel_h = 300
    gap = 80

    def xA(a): return margin + a * panel_w
    def yA(p): return 40 + panel_h * (1.0 - p)
    def xB(v): return margin + panel_w + gap + (v / 0.5) * panel_w
    def yB(p): return 40 + panel_h * (1.0 - p)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;font-size:14px}.lab{font-size:16px;font-weight:bold}.small{font-size:12px}</style>',
    ]

    for x0 in (margin, margin + panel_w + gap):
        lines += [
            f'<line x1="{x0}" y1="40" x2="{x0}" y2="{40+panel_h}" stroke="black"/>',
            f'<line x1="{x0}" y1="{40+panel_h}" x2="{x0+panel_w}" y2="{40+panel_h}" stroke="black"/>',
        ]
    lines += [
        f'<text x="{margin}" y="24" class="lab">A  Invalid-state inflation of false hard violations</text>',
        f'<text x="{margin+panel_w+gap}" y="24" class="lab">B  False-discovery fraction depends on violation prevalence</text>',
    ]

    curves = [
        ("naive s=0.80", 0.80, True, "4 2"),
        ("gated s=0.80", 0.80, False, None),
        ("naive s=0.95", 0.95, True, "4 2"),
        ("gated s=0.95", 0.95, False, None),
    ]
    for idx, (label, s, naive, dash) in enumerate(curves):
        pts = []
        for i in range(0, 101):
            a = i / 100
            p = 1 - a*s if naive else a*(1-s)
            pts.append(f"{xA(a):.1f},{yA(p):.1f}")
        attr = f' stroke-dasharray="{dash}"' if dash else ""
        shade = "black" if s == 0.80 else "gray"
        lines.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{shade}" stroke-width="2"{attr}/>')
        lines.append(f'<text x="{margin+15}" y="{365+idx*15}" class="small">{label}</text>')

    for t in (0, .25, .5, .75, 1):
        lines.append(f'<line x1="{xA(t)}" y1="340" x2="{xA(t)}" y2="346" stroke="black"/>')
        lines.append(f'<text x="{xA(t)-8}" y="362" class="small">{t:g}</text>')
        lines.append(f'<line x1="{margin-6}" y1="{yA(t)}" x2="{margin}" y2="{yA(t)}" stroke="black"/>')
        lines.append(f'<text x="{margin-42}" y="{yA(t)+4}" class="small">{t:g}</text>')
    lines.append(f'<text x="{margin+130}" y="395">valid-key fraction a</text>')
    lines.append('<text transform="translate(18,250) rotate(-90)">false violation rate | F=true</text>')

    for idx, s in enumerate((0.80, 0.95, 0.99)):
        pts = []
        for i in range(1, 501):
            v = i / 1000
            q = 1-v
            fdf = q*(1-s)/(q*(1-s)+v*0.99)
            pts.append(f"{xB(v):.1f},{yB(fdf):.1f}")
        dash = None if idx == 0 else ("5 3" if idx == 1 else "2 3")
        attr = f' stroke-dasharray="{dash}"' if dash else ""
        lines.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="black" stroke-width="2"{attr}/>')
        lines.append(f'<text x="{margin+panel_w+gap+15}" y="{365+idx*15}" class="small">gated s={s:.2f}, specificity=0.99</text>')

    for t in (0, .1, .2, .3, .4, .5):
        lines.append(f'<line x1="{xB(t)}" y1="340" x2="{xB(t)}" y2="346" stroke="black"/>')
        lines.append(f'<text x="{xB(t)-8}" y="362" class="small">{t:g}</text>')
    for t in (0, .25, .5, .75, 1):
        x0=margin+panel_w+gap
        lines.append(f'<line x1="{x0-6}" y1="{yB(t)}" x2="{x0}" y2="{yB(t)}" stroke="black"/>')
        lines.append(f'<text x="{x0-42}" y="{yB(t)+4}" class="small">{t:g}</text>')
    lines.append(f'<text x="{margin+panel_w+gap+120}" y="395">true violation prevalence v</text>')
    lines.append(f'<text transform="translate({margin+panel_w+gap-42},260) rotate(-90)">false-discovery fraction</text>')
    lines.append('</svg>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    scenario_rows = [scenario_row(x) for x in SCENARIOS]
    surface_rows = build_surface()

    scenario_path = root / "results" / "pre_field_identifiability_benchmark_scenarios_v0_1.csv"
    surface_path = root / "results" / "pre_field_identifiability_benchmark_surface_v0_1.csv"
    summary_path = root / "results" / "pre_field_identifiability_benchmark_summary_v0_1.json"
    svg_path = root / "manuscript" / "figures" / "pre_field_identifiability_benchmark_v0_1.svg"

    _write_csv(scenario_path, scenario_rows)
    _write_csv(surface_path, surface_rows)
    write_svg(svg_path)

    qualified = [r for r in scenario_rows if r["calibration_pass"]]
    max_identity_error = max(
        abs(r["false_violation_inflation_from_invalid_states"] - r["invalid_state_mass"])
        + abs(r["apparent_sensitivity_gain_from_invalid_states"] - r["invalid_state_mass"])
        for r in qualified
    )

    threshold_example = benchmark_metrics(
        violation_prevalence=0.10,
        key_sensitivity=0.80,
        valid_key_fraction=1.0,
        specificity=0.99,
    )

    summary = {
        "version": "pre_field_identifiability_benchmark_v0_1",
        "data_source": "synthetic_exact_analytic_only_no_focal_Level_C_values",
        "scenario_count": len(scenario_rows),
        "surface_row_count": len(surface_rows),
        "qualification_thresholds": {
            "sensitivity_min": SENSITIVITY_MIN,
            "hard_fnr_max": HARD_FNR_MAX,
            "specificity_min": SPECIFICITY_MIN,
        },
        "exact_result_for_qualified_process": {
            "naive_false_violation_minus_gated_false_violation": "1 - valid_key_fraction",
            "naive_true_violation_sensitivity_minus_gated_true_violation_sensitivity": "1 - valid_key_fraction",
            "interpretation": (
                "Collapsing invalid observation states into biological negatives adds exactly the "
                "same probability mass to apparent true-violation sensitivity and to false hard violations."
            ),
            "max_numeric_identity_error_across_qualified_named_scenarios": max_identity_error,
        },
        "base_rate_result": {
            "example_violation_prevalence": 0.10,
            "example_sensitivity": 0.80,
            "example_specificity": 0.99,
            "gated_false_discovery_fraction": threshold_example["gated_false_discovery_fraction"],
            "interpretation": (
                "Passing an observation-process qualification threshold is necessary for opening a hard test "
                "but does not itself control the posterior false-discovery fraction of called violations."
            ),
        },
        "scenario_highlights": {
            r["scenario"]: {
                "calibration_pass": r["calibration_pass"],
                "valid_key_fraction": r["valid_key_fraction"],
                "naive_false_violation_rate": r["naive_false_violation_rate"],
                "gated_false_violation_rate": r["gated_false_violation_rate"],
                "gated_unresolved_fraction": r["gated_unresolved_fraction"],
            }
            for r in scenario_rows
            if r["scenario"] in {
                "high_quality_dense", "high_missingness", "device_failure",
                "incomplete_window", "mixed_qualified",
                "subthreshold_sensitivity", "subthreshold_specificity"
            }
        },
        "boundary": {
            "counts_as_empirical_biological_evidence": False,
            "authorizes_Level_C_endpoint_opening": False,
            "changes_candidate_specific_thresholds": False,
            "global_284b_empirical_ledger_increment": 0,
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
