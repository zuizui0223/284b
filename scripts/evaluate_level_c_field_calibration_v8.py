#!/usr/bin/env python3
import argparse
import csv
import json
import math
from pathlib import Path


def wilson_lower_bound(successes, n, z=1.6448536269514722):
    if n <= 0:
        return None
    phat = successes / n
    denom = 1 + z * z / n
    center = phat + z * z / (2 * n)
    adj = z * math.sqrt((phat * (1 - phat) / n) + (z * z / (4 * n * n)))
    return (center - adj) / denom


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
        unresolved = any(parse_bool(r.get(k, "")) for k in [
            "missing", "device_failure", "observer_failure", "occlusion", "unresolved_adjudication"
        ])
        gold = r.get("gold_state", "").strip().lower()
        observed = r.get("observer_state", "").strip().lower()
        if unresolved:
            if observed in {"positive", "negative"}:
                invalid.append(f"row {i}: unresolved/failure row cannot carry biological observer_state")
            continue
        if gold not in {"positive", "negative"}:
            invalid.append(f"row {i}: gold_state must be positive or negative for resolved rows")
            continue
        if observed not in {"positive", "negative"}:
            invalid.append(f"row {i}: observer_state must be positive or negative for resolved rows")
            continue
        if gold == "positive":
            pos += 1
            if observed == "positive": tp += 1
            else: fn += 1
        else:
            neg += 1
            if observed == "negative": tn += 1
            else: fp += 1

    sensitivity = tp / pos if pos else None
    specificity = tn / neg if neg else None
    fnr = fn / pos if pos else None
    sens_lb = wilson_lower_bound(tp, pos) if pos else None
    spec_lb = wilson_lower_bound(tn, neg) if neg else None

    qc_pass = not invalid
    counts_pass = pos >= 30 and neg >= 60
    sensitivity_pass = sensitivity is not None and sensitivity >= 0.80 and sens_lb is not None and sens_lb >= 0.80
    fnr_pass = fnr is not None and fnr <= 0.20
    specificity_pass = specificity is not None and specificity >= 0.95 and spec_lb is not None and spec_lb >= 0.95
    missingness_separation_pass = qc_pass
    opening = all([counts_pass, sensitivity_pass, fnr_pass, specificity_pass, missingness_separation_pass])

    return {
        "candidate_id": candidate_id,
        "state": "calibration_pass" if opening else "calibration_not_passed",
        "resolved_gold_positive": pos,
        "resolved_gold_negative": neg,
        "tp": tp, "fn": fn, "tn": tn, "fp": fp,
        "sensitivity": sensitivity,
        "hard_fnr": fnr,
        "specificity": specificity,
        "one_sided_95_sensitivity_lower": sens_lb,
        "one_sided_95_specificity_lower": spec_lb,
        "qc_pass": qc_pass,
        "counts_pass": counts_pass,
        "sensitivity_pass": sensitivity_pass,
        "fnr_pass": fnr_pass,
        "specificity_pass": specificity_pass,
        "missingness_separation_pass": missingness_separation_pass,
        "invalid_rows": invalid,
        "opening_authorized": opening,
        "empirical_ledger_increment": 0,
        "note": "Calibration pass only authorizes later endpoint opening; it is not itself a biological conclusion."
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
