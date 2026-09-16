import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "config" / "product_b_level_c_sampling_plan_v8_2.json"
SCRIPT = ROOT / "scripts" / "audit_level_c_sampling_plan_v8_2.py"


def load_audit_module():
    if not SCRIPT.exists():
        raise AssertionError("v8.2 sampling-plan audit script is missing")
    spec = importlib.util.spec_from_file_location("level_c_v8_2_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


if __name__ == "__main__":
    unittest.main()
