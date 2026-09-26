import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_field_calibration_protocol_v7.json"
DESIGN = ROOT / "results" / "product_b_level_c_field_calibration_design_validation_v7.json"
CREM = ROOT / "registry" / "level_c_v7_cremastra_field_calibration_template.csv"
BEL = ROOT / "registry" / "level_c_v7_belonocnema_field_calibration_template.csv"


class LevelCFieldCalibrationV7Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.d = json.loads(DESIGN.read_text(encoding="utf-8"))

    def test_protocol_is_prospective_and_nonempirical(self):
        self.assertEqual(
            self.p["protocol_state"],
            "frozen_before_any_v7_field_calibration_or_focal_endpoint_opening",
        )
        self.assertFalse(self.p["focal_cross_role_endpoint_opening_authorized_now"])
        self.assertFalse(self.p["counts_as_empirical_evidence"])
        self.assertFalse(self.p["counts_as_empirical_conclusion"])
        self.assertEqual(self.p["empirical_ledger_increment"], 0)
        self.assertEqual(self.p["global_284b_empirical_ledger_at_v7_freeze"], 1)

    def test_candidate_set_is_fixed(self):
        self.assertEqual(set(self.p["retained_candidates"]), {"CREMV3-007", "BELV3-012"})
        self.assertFalse(self.p["new_candidate_search_authorized"])
        self.assertFalse(self.p["candidate_replacement_authorized"])
        self.assertFalse(self.p["prior_system_rescue_authorized"])

    def test_common_negative_safety_rules(self):
        c = self.p["common_rules"]
        self.assertFalse(c["missing_is_negative"])
        self.assertFalse(c["unavailable_is_negative"])
        self.assertFalse(c["zero_without_calibration_pass_is_negative"])
        self.assertFalse(c["fruit_or_emergence_outcome_may_define_gold_standard"])
        self.assertFalse(c["level_a_q95_import_authorized"])
        self.assertFalse(c["threshold_tuning_after_focal_outcome_access_authorized"])

    def test_thresholds_are_frozen(self):
        t = self.p["calibration_targets"]
        self.assertEqual(t["sensitivity_min"], 0.80)
        self.assertEqual(t["hard_false_negative_rate_max"], 0.20)
        self.assertEqual(t["specificity_min"], 0.95)
        self.assertEqual(t["minimum_gold_positive_units_if_all_detected"], 30)
        self.assertEqual(t["minimum_gold_negative_units_if_all_correctly_negative"], 60)
        self.assertFalse(t["adaptive_sample_size_rescue_after_inspecting_calibration_failures"])

    def test_clean_design_clears_frozen_floors(self):
        self.assertTrue(self.d["gold_positive_design"]["passes_floor"])
        self.assertTrue(self.d["gold_negative_design"]["passes_floor"])
        self.assertGreaterEqual(
            self.d["gold_positive_design"]["one_sided_95pct_lower_bound"],
            self.p["calibration_targets"]["sensitivity_min"],
        )
        self.assertGreaterEqual(
            self.d["gold_negative_design"]["one_sided_95pct_lower_bound"],
            self.p["calibration_targets"]["specificity_min"],
        )

    def test_candidate_specific_opening_does_not_require_joint_pass(self):
        j = self.p["joint_opening_rule"]
        self.assertFalse(j["require_both_candidates_to_pass_before_any_empirical_opening"])
        self.assertTrue(j["candidate_specific_opening_allowed"])
        self.assertTrue(j["failed_or_unavailable_candidate_remains_nonbiological_unresolved"])
        self.assertTrue(j["one_candidate_pass_does_not_rescue_or_reclassify_the_other"])

    def test_cremastra_template_separates_failures(self):
        with CREM.open(newline="", encoding="utf-8") as h:
            fields = next(csv.reader(h))
        for f in ["camera_offline", "storage_failure", "occlusion", "flower_out_of_frame", "gold_standard_gap"]:
            self.assertIn(f, fields)

    def test_belonocnema_template_separates_failures(self):
        with BEL.open(newline="", encoding="utf-8") as h:
            fields = next(csv.reader(h))
        for f in ["tree_not_found", "observer_missing", "canopy_not_visible", "date_gap", "adjudication_unresolved"]:
            self.assertIn(f, fields)


if __name__ == "__main__":
    unittest.main()
