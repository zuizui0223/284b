#!/usr/bin/env python3
"""Exact synthetic benchmark for pre-field negative-state identifiability.

This module does not read any focal Level-C biological values. It evaluates
two decision rules on synthetic event keys with known latent truth:

1. naive-zero: any non-detection/invalid observation at E=true is treated as
   F=false and therefore as a hard dependency violation;
2. identifiability-gated: a hard violation is allowed only when the
   observation process passes the frozen sensitivity/specificity thresholds
   and the event key has complete, nonmissing, nonfailed observation.

The benchmark is deliberately analytic rather than Monte Carlo so every
reported value is exactly reproducible from the declared parameter grid.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
from typing import Iterable

SENSITIVITY_MIN = 0.80
SPECIFICITY_MIN = 0.95

GRID = {
    "violation_prevalence": (0.05, 0.10, 0.20, 0.50),
    "event_probability": (0.05, 0.20, 0.50),
    "event_detection_sensitivity": (0.50, 0.80, 0.95),
    "opportunities": (1, 5, 20),
    "complete_window_fraction": (0.50, 0.80, 1.00),
    "missingness": (0.00, 0.10, 0.30),
    "failure_rate": (0.00, 0.05, 0.20),
    "specificity": (0.80, 0.95, 0.99),
}

REPRESENTATIVE_SCENARIOS = {
    "high_quality_dense": {
        "violation_prevalence": 0.10,
        "event_probability": 0.50,
        "event_detection_sensitivity": 0.95,
        "opportunities": 20,
        "complete_window_fraction": 1.00,
        "missingness": 0.00,
        "failure_rate": 0.00,
        "specificity": 0.99,
    },
    "threshold_sensitivity": {
        "violation_prevalence": 0.10,
        "event_probability": 0.20,
        "event_detection_sensitivity": 0.80,
        "opportunities": 1,
        "complete_window_fraction": 1.00,
        "missingness": 0.00,
        "failure_rate": 0.00,
        "specificity": 0.99,
    },
    "subthreshold_sensitivity": {
        "violation_prevalence": 0.10,
        "event_probability": 0.20,
        "event_detection_sensitivity": 0.50,
        "opportunities": 1,
        "complete_window_fraction": 1.00,
        "missingness": 0.00,
        "failure_rate": 0.00,
        "specificity": 0.99,
    },
    "sparse_event": {
        "violation_prevalence": 0.10,
        "event_probability": 0.05,
        "event_detection_sensitivity": 0.80,
        "opportunities": 5,
        "complete_window_fraction": 1.00,
        "missingness": 0.00,
        "failure_rate": 0.00,
        "specificity": 0.99,
    },
    "high_missingness": {
        "violation_prevalence": 0.10,
        "event_probability": 0.50,
        "event_detection_sensitivity": 0.95,
        "opportunities": 20,
        "complete_window_fraction": 1.00,
        "missingness": 0.30,
        "failure_rate": 0.00,
        "specificity": 0.99,
    },
    "device_failure": {
        "violation_prevalence": 0.10,
        "event_probability": 0.50,
        "event_detection_sensitivity": 0.95,
        "opportunities": 20,
        "complete_window_fraction": 1.00,
        "missingness": 0.00,
        "failure_rate": 0.20,
        "specificity": 0.99,
    },
    "incomplete_window": {
        "violation_prevalence": 0.10,
        "event_probability": 0.50,
        "event_detection_sensitivity": 0.95,
        "opportunities": 20,
        "complete_window_fraction": 0.50,
        "missingness": 0.00,
        "failure_rate": 0.00,
        "specificity": 0.99,
    },
    "mixed_qualified": {
        "violation_prevalence": 0.10,
        "event_probability": 0.20,
        "event_detection_sensitivity": 0.80,
        "opportunities": 5,
        "complete_window_fraction": 0.80,
        "missingness": 0.10,
        "failure_rate": 0.05,
        "specificity": 0.95,
    },
    "subthreshold_specificity": {
        "violation_prevalence": 0.10,
        "event_probability": 0.50,
        "event_detection_sensitivity": 0.95,
        "opportunities": 20,
        "complete_window_fraction": 1.00,
        "missingness": 0.00,
        "failure_rate": 0.00,
        "specificity": 0.80,
    },
}


@dataclass(frozen=True)
class ScenarioResult:
    violation_prevalence: float
    event_probability: float
    event_detection_sensitivity: float
    opportunities: int
    complete_window_fraction: float
    missingness: float
    failure_rate: float
    specificity: float
    key_sensitivity: float
    valid_key_fraction: float
    calibration_pass: bool
    naive_false_violation_rate: float
    gated_false_violation_rate: float
    naive_true_violation_sensitivity: float
    gated_true_violation_sensitivity: float
    gated_unresolved_fraction: float
    naive_false_discovery_fraction: float | None
    gated_false_discovery_fraction: float | None


def conditional_key_sensitivity(
    event_probability: float,
    event_detection_sensitivity: float,
    opportunities: int,
) -> float:
    """P(at least one detection | at least one true event in the key)."""
    if not (0.0 < event_probability <= 1.0):
        raise ValueError("event_probability must be in (0, 1]")
    if not (0.0 <= event_detection_sensitivity <= 1.0):
        raise ValueError("event_detection_sensitivity must be in [0, 1]")
    if opportunities < 1:
        raise ValueError("opportunities must be >= 1")

    p_true = 1.0 - (1.0 - event_probability) ** opportunities
    p_detected = 1.0 - (
        1.0 - event_probability * event_detection_sensitivity
    ) ** opportunities
    return p_detected / p_true


def _fdr(false_rate: float, true_rate: float) -> float | None:
    denominator = false_rate + true_rate
    if denominator == 0.0:
        return None
    return false_rate / denominator


def evaluate_scenario(
    *,
    violation_prevalence: float,
    event_probability: float,
    event_detection_sensitivity: float,
    opportunities: int,
    complete_window_fraction: float,
    missingness: float,
    failure_rate: float,
    specificity: float,
) -> ScenarioResult:
    for name, value in (
        ("violation_prevalence", violation_prevalence),
        ("complete_window_fraction", complete_window_fraction),
        ("missingness", missingness),
        ("failure_rate", failure_rate),
        ("specificity", specificity),
    ):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0, 1]")

    key_sensitivity = conditional_key_sensitivity(
        event_probability,
        event_detection_sensitivity,
        opportunities,
    )
    valid = complete_window_fraction * (1.0 - missingness) * (1.0 - failure_rate)
    calibration_pass = (
        key_sensitivity >= SENSITIVITY_MIN and specificity >= SPECIFICITY_MIN
    )

    naive_fpr = 1.0 - valid * key_sensitivity
    gated_fpr = valid * (1.0 - key_sensitivity) if calibration_pass else 0.0

    naive_tpr = 1.0 - valid * (1.0 - specificity)
    gated_tpr = valid * specificity if calibration_pass else 0.0

    if calibration_pass:
        unresolved_if_function_true = 1.0 - valid
        unresolved_if_function_false = 1.0 - valid
    else:
        unresolved_if_function_true = 1.0 - valid * key_sensitivity
        unresolved_if_function_false = 1.0 - valid * (1.0 - specificity)

    unresolved = (
        (1.0 - violation_prevalence) * unresolved_if_function_true
        + violation_prevalence * unresolved_if_function_false
    )

    naive_false = (1.0 - violation_prevalence) * naive_fpr
    naive_true = violation_prevalence * naive_tpr
    gated_false = (1.0 - violation_prevalence) * gated_fpr
    gated_true = violation_prevalence * gated_tpr

    return ScenarioResult(
        violation_prevalence=violation_prevalence,
        event_probability=event_probability,
        event_detection_sensitivity=event_detection_sensitivity,
        opportunities=opportunities,
        complete_window_fraction=complete_window_fraction,
        missingness=missingness,
        failure_rate=failure_rate,
        specificity=specificity,
        key_sensitivity=key_sensitivity,
        valid_key_fraction=valid,
        calibration_pass=calibration_pass,
        naive_false_violation_rate=naive_fpr,
        gated_false_violation_rate=gated_fpr,
        naive_true_violation_sensitivity=naive_tpr,
        gated_true_violation_sensitivity=gated_tpr,
        gated_unresolved_fraction=unresolved,
        naive_false_discovery_fraction=_fdr(naive_false, naive_true),
        gated_false_discovery_fraction=_fdr(gated_false, gated_true),
    )


def iter_grid() -> Iterable[ScenarioResult]:
    keys = tuple(GRID)
    for values in itertools.product(*(GRID[key] for key in keys)):
        yield evaluate_scenario(**dict(zip(keys, values)))


def build_summary(rows: list[ScenarioResult]) -> dict:
    passing = [row for row in rows if row.calibration_pass]
    failing = [row for row in rows if not row.calibration_pass]

    fpr_identity_error = max(
        abs(
            (row.naive_false_violation_rate - row.gated_false_violation_rate)
            - (1.0 - row.valid_key_fraction)
        )
        for row in passing
    )
    tpr_identity_error = max(
        abs(
            (
                row.naive_true_violation_sensitivity
                - row.gated_true_violation_sensitivity
            )
            - (1.0 - row.valid_key_fraction)
        )
        for row in passing
    )

    representative = {
        name: asdict(evaluate_scenario(**params))
        for name, params in REPRESENTATIVE_SCENARIOS.items()
    }

    return {
        "benchmark_version": "pre_field_identifiability_benchmark_v0_1",
        "focal_level_c_values_read": False,
        "analytic_not_monte_carlo": True,
        "thresholds": {
            "key_sensitivity_min": SENSITIVITY_MIN,
            "specificity_min": SPECIFICITY_MIN,
        },
        "grid": {key: list(values) for key, values in GRID.items()},
        "scenario_count": len(rows),
        "calibration_pass_count": len(passing),
        "calibration_fail_count": len(failing),
        "equal_weight_grid_descriptives": {
            "naive_false_violation_rate_median": median(
                row.naive_false_violation_rate for row in rows
            ),
            "gated_false_violation_rate_median": median(
                row.gated_false_violation_rate for row in rows
            ),
        },
        "structural_results": {
            "max_gated_false_violation_rate_among_passing_scenarios": max(
                row.gated_false_violation_rate for row in passing
            ),
            "max_naive_false_violation_rate_among_passing_scenarios": max(
                row.naive_false_violation_rate for row in passing
            ),
            "max_abs_error_fpr_identity_naive_minus_gated_equals_invalid_mass": (
                fpr_identity_error
            ),
            "max_abs_error_tpr_identity_naive_minus_gated_equals_invalid_mass": (
                tpr_identity_error
            ),
            "gated_hard_calls_in_failing_scenarios": sum(
                row.gated_false_violation_rate
                + row.gated_true_violation_sensitivity
                for row in failing
            ),
        },
        "representative_scenarios": representative,
        "interpretation_boundary": (
            "Synthetic inferential benchmark only. Results do not estimate "
            "Cremastra or Belonocnema detection performance, do not authorize "
            "Level-C endpoint opening, and do not increment the empirical ledger."
        ),
    }


def write_outputs(output_dir: Path, *, write_full_grid: bool) -> None:
    rows = list(iter_grid())
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "pre_field_identifiability_benchmark_summary_v0_1.json"
    summary_path.write_text(
        json.dumps(build_summary(rows), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    scenario_path = output_dir / "pre_field_identifiability_benchmark_scenarios_v0_1.csv"
    scenario_rows = [
        {"scenario": name, **asdict(evaluate_scenario(**params))}
        for name, params in REPRESENTATIVE_SCENARIOS.items()
    ]
    with scenario_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=scenario_rows[0].keys())
        writer.writeheader()
        writer.writerows(scenario_rows)

    if write_full_grid:
        full_path = output_dir / "pre_field_identifiability_benchmark_full_grid_v0_1.csv"
        dict_rows = [asdict(row) for row in rows]
        with full_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=dict_rows[0].keys())
            writer.writeheader()
            writer.writerows(dict_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
        help="Directory for deterministic benchmark outputs.",
    )
    parser.add_argument(
        "--write-full-grid",
        action="store_true",
        help="Also write the complete 8,748-scenario grid CSV.",
    )
    args = parser.parse_args()
    write_outputs(args.output_dir, write_full_grid=args.write_full_grid)


if __name__ == "__main__":
    main()
