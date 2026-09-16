import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "config" / "product_b_level_c_sampling_plan_v8_2.json"
SCRIPT = ROOT / "scripts" / "audit_level_c_sampling_plan_v8_2.py"

FIELDS = [
    "candidate_id","calibration_unit_id","date_time","site_or_tree_id","gold_state","observer_state",
    "missing","device_failure","observer_failure","occlusion","unresolved_adjudication","notes"
]


def load_audit_module():
    if not SCRIPT.exists():
        raise AssertionError("v8.2 sampling-plan audit script is missing")
    spec = importlib.util.spec_from_file_location("level_c_v8_2_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_rows(rows):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8")
    with f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return Path(f.name)


def row(cid, gold, observed, unit_id="u", **flags):
    result = {k: "false" for k in FIELDS}
    result.update({
        "candidate_id": cid,
        "calibration_unit_id": unit_id,
        "date_time": "2026-01-01T00:00:00",
        "site_or_tree_id": "s",
        "gold_state": gold,
        "observer_state": observed,
        "notes": "",
    })
    for key, value in flags.items():
        result[key] = "true" if value else "false"
    return result


class LevelCSamplingPlanV82Tests(unittest.TestCase):
    def test_plan_freezes_30_positive_and_93_negative_targets_before_outcomes(self):
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        self.assertEqual(plan["state"], "prospectively_frozen_before_any_field_calibration_data_entry")
        self.assertEqual(plan["resolved_calibration_targets_per_candidate"]["gold_positive_target"], 30)
        self.assertEqual(plan["resolved_calibration_targets_per_candidate"]["gold_negative_target"], 93)
        self.assertTrue(plan["collection_rules"]["targets_fixed_before_outcome_inspection"])
        self.assertTrue(plan["collection_rules"]["post_hoc_sample_size_extension_after_failure_forbidden"])
        self.assertEqual(plan["empirical_ledger_increment"], 0)

    def test_audit_reproduces_exact_count_boundaries(self):
        mod = load_audit_module()
        receipt = mod.audit_plan(PLAN)
        self.assertEqual(receipt["positive_target"], 30)
        self.assertEqual(receipt["negative_target"], 93)
        self.assertEqual(receipt["minimum_tp_for_exact_sensitivity_pass"], 28)
        self.assertEqual(receipt["maximum_fn_while_exact_sensitivity_passes"], 2)
        self.assertEqual(receipt["minimum_tn_for_exact_specificity_pass"], 92)
        self.assertEqual(receipt["maximum_fp_while_exact_specificity_passes"], 1)
        self.assertTrue(receipt["sampling_plan_exactly_verified"])

    def test_one_false_positive_passes_at_93_but_two_fail(self):
        mod = load_audit_module()
        self.assertGreaterEqual(mod.exact_one_sided_lower_bound(92, 93), 0.95)
        self.assertLess(mod.exact_one_sided_lower_bound(91, 93), 0.95)

    def test_28_of_30_passes_but_27_of_30_fails(self):
        mod = load_audit_module()
        self.assertGreaterEqual(mod.exact_one_sided_lower_bound(28, 30), 0.80)
        self.assertLess(mod.exact_one_sided_lower_bound(27, 30), 0.80)

    def test_v8_2_changes_sampling_target_not_scientific_thresholds_or_evaluator(self):
        mod = load_audit_module()
        receipt = mod.audit_plan(PLAN)
        self.assertTrue(receipt["scientific_thresholds_match_v8_1"])
        self.assertTrue(receipt["evaluator_unchanged"])
        self.assertEqual(receipt["evaluator"], "scripts/evaluate_level_c_field_calibration_v8_1.py")
        self.assertFalse(receipt["counts_as_empirical_evidence"])
        self.assertFalse(receipt["counts_as_empirical_conclusion"])

    def test_v8_2_gate_requires_93_resolved_negatives_even_if_v8_1_minimum_passes(self):
        mod = load_audit_module()
        cid = "CREMV3-007"
        rows = [row(cid, "positive", "positive", f"p{i}") for i in range(30)]
        rows += [row(cid, "negative", "negative", f"n{i}") for i in range(60)]
        result = mod.evaluate_candidate_against_plan(write_rows(rows), cid, PLAN)
        self.assertTrue(result["v8_1_opening_authorized"])
        self.assertFalse(result["resolved_sampling_targets_met"])
        self.assertFalse(result["opening_authorized"])
        self.assertEqual(result["state"], "sampling_target_not_reached")

    def test_v8_2_gate_allows_one_false_positive_at_frozen_target(self):
        mod = load_audit_module()
        cid = "BELV3-012"
        rows = [row(cid, "positive", "positive", f"p{i}") for i in range(30)]
        rows += [row(cid, "negative", "negative", f"n{i}") for i in range(92)]
        rows += [row(cid, "negative", "positive", "n92")]
        result = mod.evaluate_candidate_against_plan(write_rows(rows), cid, PLAN)
        self.assertTrue(result["resolved_sampling_targets_met"])
        self.assertTrue(result["v8_1_opening_authorized"])
        self.assertTrue(result["opening_authorized"])
        self.assertEqual(result["state"], "calibration_pass_at_frozen_sampling_target")

    def test_v8_2_gate_rejects_two_false_positives_at_frozen_target(self):
        mod = load_audit_module()
        cid = "BELV3-012"
        rows = [row(cid, "positive", "positive", f"p{i}") for i in range(30)]
        rows += [row(cid, "negative", "negative", f"n{i}") for i in range(91)]
        rows += [row(cid, "negative", "positive", "n91"), row(cid, "negative", "positive", "n92")]
        result = mod.evaluate_candidate_against_plan(write_rows(rows), cid, PLAN)
        self.assertTrue(result["resolved_sampling_targets_met"])
        self.assertFalse(result["v8_1_opening_authorized"])
        self.assertFalse(result["opening_authorized"])
        self.assertEqual(result["state"], "calibration_not_passed_at_frozen_sampling_target")

    def test_unresolved_rows_do_not_satisfy_the_resolved_negative_target(self):
        mod = load_audit_module()
        cid = "CREMV3-007"
        rows = [row(cid, "positive", "positive", f"p{i}") for i in range(30)]
        rows += [row(cid, "negative", "negative", f"n{i}") for i in range(92)]
        rows += [row(cid, "negative", "", "n92", device_failure=True)]
        result = mod.evaluate_candidate_against_plan(write_rows(rows), cid, PLAN)
        self.assertEqual(result["resolved_gold_negative"], 92)
        self.assertFalse(result["resolved_sampling_targets_met"])
        self.assertFalse(result["opening_authorized"])


if __name__ == "__main__":
    unittest.main()
