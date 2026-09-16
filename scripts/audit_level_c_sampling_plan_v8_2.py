#!/usr/bin/env python3
"""Outcome-blind audit of the prospective Level-C v8.2 sampling plan."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V81_CONTRACT = ROOT / "config" / "product_b_level_c_operational_package_v8_1.json"
V81_EVALUATOR = ROOT / "scripts" / "evaluate_level_c_field_calibration_v8_1.py"


def _load_v81_evaluator():
    spec = importlib.util.spec_from_file_location("level_c_v8_1_eval", V81_EVALUATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_V81 = _load_v81_evaluator()
exact_one_sided_lower_bound = _V81.exact_one_sided_lower_bound


def _minimum_successes(n: int, threshold: float) -> int:
    for successes in range(n + 1):
        if exact_one_sided_lower_bound(successes, n) >= threshold:
            return successes
    raise ValueError(f"no exact lower-bound pass exists for n={n}, threshold={threshold}")


def audit_plan(path: str | Path) -> dict[str, object]:
    plan_path = Path(path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    v81 = json.loads(V81_CONTRACT.read_text(encoding="utf-8"))

    targets = plan["resolved_calibration_targets_per_candidate"]
    positive_target = int(targets["gold_positive_target"])
    negative_target = int(targets["gold_negative_target"])

    thresholds = plan["scientific_thresholds_unchanged"]
    sensitivity_min = float(thresholds["sensitivity_min"])
    specificity_min = float(thresholds["specificity_min"])

    minimum_tp = _minimum_successes(positive_target, sensitivity_min)
    minimum_tn = _minimum_successes(negative_target, specificity_min)
    maximum_fn = positive_target - minimum_tp
    maximum_fp = negative_target - minimum_tn

    scientific_thresholds_match_v8_1 = thresholds == v81["scientific_thresholds_unchanged"]
    evaluator = str(plan.get("evaluator", ""))
    evaluator_unchanged = (
        plan.get("evaluator_unchanged") is True
        and evaluator == "scripts/evaluate_level_c_field_calibration_v8_1.py"
        and V81_EVALUATOR.exists()
    )

    declared = plan["exact_count_implications"]
    exact_implications_match = (
        int(declared["sensitivity_target_n"]) == positive_target
        and int(declared["specificity_target_n"]) == negative_target
        and int(declared["sensitivity_pass_at_target_requires_tp_at_least"]) == minimum_tp
        and int(declared["specificity_pass_at_target_requires_tn_at_least"]) == minimum_tn
        and int(declared["maximum_false_negatives_at_target_while_exact_bound_passes"]) == maximum_fn
        and int(declared["maximum_false_positives_at_target_while_exact_bound_passes"]) == maximum_fp
    )

    preoutcome_frozen = (
        plan.get("state") == "prospectively_frozen_before_any_field_calibration_data_entry"
        and plan["collection_rules"].get("targets_fixed_before_outcome_inspection") is True
        and plan["collection_rules"].get("post_hoc_sample_size_extension_after_failure_forbidden") is True
    )

    receipt = {
        "purpose": "product_b_level_c_sampling_plan_v8_2_outcome_blind_audit",
        "plan": str(plan_path),
        "positive_target": positive_target,
        "negative_target": negative_target,
        "minimum_tp_for_exact_sensitivity_pass": minimum_tp,
        "maximum_fn_while_exact_sensitivity_passes": maximum_fn,
        "minimum_tn_for_exact_specificity_pass": minimum_tn,
        "maximum_fp_while_exact_specificity_passes": maximum_fp,
        "exact_sensitivity_lower_at_boundary": exact_one_sided_lower_bound(minimum_tp, positive_target),
        "exact_specificity_lower_at_boundary": exact_one_sided_lower_bound(minimum_tn, negative_target),
        "exact_specificity_lower_one_step_below": exact_one_sided_lower_bound(minimum_tn - 1, negative_target),
        "scientific_thresholds_match_v8_1": scientific_thresholds_match_v8_1,
        "evaluator": evaluator,
        "evaluator_unchanged": evaluator_unchanged,
        "preoutcome_sampling_target_frozen": preoutcome_frozen,
        "exact_count_implications_match_plan": exact_implications_match,
        "sampling_plan_exactly_verified": bool(
            scientific_thresholds_match_v8_1
            and evaluator_unchanged
            and preoutcome_frozen
            and exact_implications_match
        ),
        "counts_as_empirical_evidence": bool(plan.get("counts_as_empirical_evidence", False)),
        "counts_as_empirical_conclusion": bool(plan.get("counts_as_empirical_conclusion", False)),
        "empirical_ledger_increment": int(plan.get("empirical_ledger_increment", 0)),
    }
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "plan",
        nargs="?",
        default=str(ROOT / "config" / "product_b_level_c_sampling_plan_v8_2.json"),
    )
    parser.add_argument("--out")
    args = parser.parse_args()
    receipt = audit_plan(args.plan)
    text = json.dumps(receipt, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if not receipt["sampling_plan_exactly_verified"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
