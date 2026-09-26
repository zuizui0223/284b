import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_candidate_specific_calibration_protocol_v5.json"
AUDIT = ROOT / "results" / "product_b_level_c_candidate_specific_calibration_audit_v5.json"


class LevelCCandidateSpecificCalibrationV5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.a = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_protocol_is_frozen_before_candidate_specific_calibration(self):
        self.assertEqual(
            self.p["protocol_state"],
            "frozen_before_candidate_specific_detection_calibration_or_focal_outcome_opening",
        )
        self.assertEqual(self.p["retained_candidates"], ["CREMV3-007", "BELV3-012"])
        self.assertFalse(self.p["new_candidate_search_authorized"])
        self.assertFalse(self.p["candidate_replacement_authorized"])
        self.assertFalse(self.p["hard_invariant_opening_authorized"])

    def test_candidate_specific_thresholds_are_fixed_and_symmetric(self):
        for cid in self.p["retained_candidates"]:
            c = self.p["candidate_specific_calibration"][cid]
            self.assertEqual(c["minimum_detection_sensitivity"], 0.80)
            self.assertEqual(c["maximum_hard_false_negative_rate"], 0.20)
            self.assertEqual(c["minimum_specificity"], 0.95)
            self.assertTrue(c["coverage_must_span_declared_focal_window"])

    def test_no_zero_or_missing_shortcut_to_negative(self):
        crem = self.p["candidate_specific_calibration"]["CREMV3-007"]
        bel = self.p["candidate_specific_calibration"]["BELV3-012"]
        self.assertFalse(crem["zero_camera_detections_without_validation_is_F_false"])
        self.assertFalse(bel["missing_or_unobserved_budbreak_without_validation_is_F_false"])

    def test_all_candidate_calibration_gates_are_frozen(self):
        self.assertEqual(
            set(self.p["calibration_gates"]),
            {
                "C1_independent_calibration_stream",
                "C2_known_state_support",
                "C3_detection_performance",
                "C4_window_coverage",
                "C5_failure_state_separation",
                "C6_no_outcome_tuning",
            },
        )

    def test_both_candidates_are_stopped_as_nonbiological_unavailable(self):
        for cid in self.p["retained_candidates"]:
            a = self.a["candidate_audits"][cid]
            self.assertEqual(a["terminal_state"], "calibration_unavailable")
            self.assertFalse(a["hard_negative_authorized"])
            self.assertFalse(a["focal_value_opening_authorized"])
            self.assertEqual(a["C1_independent_calibration_stream"], "fail")
            self.assertEqual(a["C2_known_state_support"], "fail")
            self.assertEqual(a["C3_detection_performance"], "not_evaluable")

    def test_v4_synthetic_pass_cannot_substitute_for_candidate_calibration(self):
        d = self.a["joint_decision"]
        self.assertEqual(d["candidates_passing_all_C1_C6"], 0)
        self.assertFalse(d["reuse_synthetic_v4_pass_as_candidate_specific_calibration_authorized"])
        self.assertFalse(d["threshold_relaxation_authorized"])
        self.assertFalse(d["new_candidate_search_authorized"])
        self.assertFalse(d["candidate_replacement_authorized"])

    def test_empirical_ledger_remains_closed(self):
        self.assertFalse(self.a["counts_as_empirical_evidence"])
        self.assertFalse(self.a["counts_as_empirical_conclusion"])
        self.assertEqual(self.a["empirical_ledger_increment"], 0)
        self.assertEqual(self.a["global_284b_empirical_ledger_after_v5_audit"], 1)


if __name__ == "__main__":
    unittest.main()
