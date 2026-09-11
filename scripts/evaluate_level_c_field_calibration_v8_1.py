#!/usr/bin/env python3
"""Prospective v8.1 repair of the frozen Level-C field-calibration evaluator.

The v8 contract required a one-sided 95% exact-or-more-conservative confidence
rule, but the frozen v8 evaluator implemented a one-sided Wilson score bound.
No field-calibration data had been entered or opened when this mismatch was
identified. v8.1 preserves candidate identities, sample-count minima,
scientific thresholds, missingness rules, and endpoint-opening semantics, and
changes only the confidence-bound implementation to exact Clopper-Pearson.
"""

import argparse
import csv
import json
import math
from pathlib import Path

ONE_SIDED_ALPHA = 0.05


def _binomial_upper_tail(successes, n, p):
    if successes <= 0:
        return 1.0
    if successes > n:
        return 0.0
    return sum(
        math.comb(n, k) * (p ** k) * ((1.0 - p) ** (n - k))
        for k in range(successes, n + 1)
    )


def exact_one_sided_lower_bound(successes, n, alpha=ONE_SIDED_ALPHA):
    """Exact Clopper-Pearson one-sided lower confidence bound."""
    if n <= 0:
        return None
    if not 0 <= successes <= n:
        raise ValueError("successes must lie in [0, n]")
    if successes == 0:
        return 0.0
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")

    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if _binomial_upper_tail(successes, n, mid) < alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def parse_bool(v):
    return str(v).strip().lower() in {"1", "true", "yes", "y"}


def evaluate(path: Path, candidate_id: str):
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    rows = [r for r in rows if r.get("candidate_id") == candidate_id]
    if not rows:
        return {"candidate_id": candidate_id, "state": "no_rows", "opening_authorized": False}

    invalid = []
    pos = neg = tp = tn = fp = fn = 0
    for i, r in enumerate(rows, start=2):
        unresolved = any(
            parse_bool(r.get(k, ""))
            for k in [
                "missing",
                "device_failure",
                "observer_failure",
                "occlusion",
                "unresolved_adjudication",
            ]
        )
        gold = r.get("gold_state", "").strip().lower()
        observed = r.get("observer_state", "").strip().lower()
        if unresolved:
            if observed in {"positive", "negative"}:
                invalid.append(
                    f"row {i}: unresolved/failure row cannot carry biological observer_state"
                )
            continue
        if gold not in {"positive", "negative"}:
            invalid.append(f"row {i}: gold_state must be positive or negative for resolved rows")
            continue
        if observed not in {"positive", "negative"}:
            invalid.append(f"row {i}: observer_state must be positive or negative for resolved rows")
            continue
        if gold == "positive":
            pos += 1
            if observed == "positive":
                tp += 1
            else:
                fn += 1
        else:
            neg += 1
            if observed == "negative":
                tn += 1
            else:
                fp += 1

    sensitivity = tp / pos if pos else None
    specificity = tn / neg if neg else None
    fnr = fn / pos if pos else None
    sens_lb = exact_one_sided_lower_bound(tp, pos) if pos else None
    spec_lb = exact_one_sided_lower_bound(tn, neg) if neg else None

    qc_pass = not invalid
    counts_pass = pos >= 30 and neg >= 60
    sensitivity_pass = (
        sensitivity is not None
        and sensitivity >= 0.80
        and sens_lb is not None
        and sens_lb >= 0.80
    )
    fnr_pass = fnr is not None and fnr <= 0.20
    specificity_pass = (
        specificity is not None
        and specificity >= 0.95
        and spec_lb is not None
        and spec_lb >= 0.95
    )
    missingness_separation_pass = qc_pass
    opening = all(
        [
            counts_pass,
            sensitivity_pass,
            fnr_pass,
            specificity_pass,
            missingness_separation_pass,
        ]
    )

    return {
        "candidate_id": candidate_id,
        "evaluator_version": "level_c_field_calibration_v8_1_exact_confidence",
        "state": "calibration_pass" if opening else "calibration_not_passed",
        "resolved_gold_positive": pos,
        "resolved_gold_negative": neg,
        "tp": tp,
        "fn": fn,
        "tn": tn,
        "fp": fp,
        "sensitivity": sensitivity,
        "hard_fnr": fnr,
        "specificity": specificity,
        "one_sided_95_sensitivity_lower": sens_lb,
        "one_sided_95_specificity_lower": spec_lb,
        "confidence_method": "exact_clopper_pearson_one_sided_95_percent",
        "qc_pass": qc_pass,
        "counts_pass": counts_pass,
        "sensitivity_pass": sensitivity_pass,
        "fnr_pass": fnr_pass,
        "specificity_pass": specificity_pass,
        "missingness_separation_pass": missingness_separation_pass,
        "invalid_rows": invalid,
        "opening_authorized": opening,
        "empirical_ledger_increment": 0,
        "note": "Calibration pass only authorizes later endpoint opening; it is not itself a biological conclusion.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("candidate_id", choices=["CREMV3-007", "BELV3-012"])
    ap.add_argument("--out")
    args = ap.parse_args()
    result = evaluate(Path(args.csv), args.candidate_id)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
