#!/usr/bin/env python3
"""Outcome-blind operating-characteristic audit for Level-C v8.1 calibration.

This audit uses only the prospectively frozen v8.1 thresholds and exact
confidence rule. It reads no field-calibration or focal Level-C data. Its
purpose is to distinguish a *minimum sample size that can pass* from a
predeclared sample size with a useful probability of passing when the true
observation-process performance exceeds the qualification floor.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from evaluate_level_c_field_calibration_v8_1 import exact_one_sided_lower_bound

ALPHA = 0.05
SENS_THRESHOLD = 0.80
SPEC_THRESHOLD = 0.95
MIN_POSITIVE_N = 30
MIN_NEGATIVE_N = 60


def binomial_upper_tail(n: int, p: float, successes: int) -> float:
    return sum(
        math.comb(n, k) * (p ** k) * ((1.0 - p) ** (n - k))
        for k in range(successes, n + 1)
    )


def critical_successes(n: int, threshold: float) -> int | None:
    """Smallest observed success count that passes rate + exact-LB threshold."""
    for successes in range(n + 1):
        rate = successes / n
        lower = exact_one_sided_lower_bound(successes, n, alpha=ALPHA)
        if rate >= threshold and lower is not None and lower >= threshold:
            return successes
    return None


def pass_probability(n: int, true_rate: float, threshold: float) -> dict:
    critical = critical_successes(n, threshold)
    if critical is None:
        probability = 0.0
    else:
        probability = binomial_upper_tail(n, true_rate, critical)
    return {
        "n": n,
        "true_rate": true_rate,
        "threshold": threshold,
        "critical_successes": critical,
        "pass_probability": probability,
    }


def first_n_for_power(
    true_rate: float,
    threshold: float,
    target_power: float = 0.80,
    n_min: int = 1,
    n_max: int = 2000,
) -> dict | None:
    for n in range(n_min, n_max + 1):
        result = pass_probability(n, true_rate, threshold)
        if result["pass_probability"] >= target_power:
            result["target_power"] = target_power
            return result
    return None


def build_summary() -> dict:
    sensitivity_true_rates = [0.80, 0.85, 0.90, 0.95, 0.98, 0.99]
    specificity_true_rates = [0.95, 0.97, 0.98, 0.99, 0.995, 0.999]

    minimum_positive = {
        str(rate): pass_probability(MIN_POSITIVE_N, rate, SENS_THRESHOLD)
        for rate in sensitivity_true_rates
    }
    minimum_negative = {
        str(rate): pass_probability(MIN_NEGATIVE_N, rate, SPEC_THRESHOLD)
        for rate in specificity_true_rates
    }

    power80_positive = {
        str(rate): first_n_for_power(
            rate,
            SENS_THRESHOLD,
            target_power=0.80,
            n_min=MIN_POSITIVE_N,
        )
        for rate in [0.85, 0.90, 0.95, 0.98, 0.99]
    }
    power80_negative = {
        str(rate): first_n_for_power(
            rate,
            SPEC_THRESHOLD,
            target_power=0.80,
            n_min=MIN_NEGATIVE_N,
        )
        for rate in [0.97, 0.98, 0.99, 0.995, 0.999]
    }

    return {
        "audit_version": "level_c_calibration_operating_characteristics_v8_1",
        "field_calibration_values_read": False,
        "focal_level_c_values_read": False,
        "confidence_method": "exact_clopper_pearson_one_sided_95_percent",
        "thresholds_unchanged": {
            "sensitivity_min": SENS_THRESHOLD,
            "specificity_min": SPEC_THRESHOLD,
            "minimum_gold_positive": MIN_POSITIVE_N,
            "minimum_gold_negative": MIN_NEGATIVE_N,
        },
        "minimum_design_critical_counts": {
            "sensitivity": {
                "n": MIN_POSITIVE_N,
                "critical_successes": critical_successes(MIN_POSITIVE_N, SENS_THRESHOLD),
            },
            "specificity": {
                "n": MIN_NEGATIVE_N,
                "critical_successes": critical_successes(MIN_NEGATIVE_N, SPEC_THRESHOLD),
            },
        },
        "pass_probability_at_minimum_design": {
            "sensitivity": minimum_positive,
            "specificity": minimum_negative,
        },
        "first_n_with_at_least_80_percent_nominal_pass_probability": {
            "sensitivity": power80_positive,
            "specificity": power80_negative,
        },
        "interpretation": (
            "These are exact nominal binomial operating characteristics under "
            "independent calibration units. They are design-planning quantities, "
            "not candidate-specific performance estimates. Any larger planned "
            "sample size must be frozen before outcome inspection; observed failure "
            "cannot justify post-hoc extension."
        ),
        "empirical_ledger_increment": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/level_c_calibration_operating_characteristics_v8_1.json"),
    )
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(build_summary(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
