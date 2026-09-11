import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_raw_calibration_reconstruction_protocol_v6.json"
RESULT = ROOT / "results" / "product_b_level_c_raw_calibration_reconstruction_v6.json"


class LevelCRawCalibrationReconstructionV6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.r = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_candidate_set_is_frozen_and_no_hunting_reopens(self):
        self.assertEqual(self.p["candidate_set"], ["CREMV3-007", "BELV3-012"])
        self.assertTrue(self.p["candidate_set_frozen"])
        self.assertFalse(self.p["new_candidate_search_authorized"])
        self.assertFalse(self.p["candidate_replacement_authorized"])
        self.assertFalse(self.p["prior_level_c_system_rescue_authorized"])
        self.assertFalse(self.r["new_candidate_search_authorized"])

    def test_six_reconstruction_gates_are_frozen(self):
        self.assertEqual(set(self.p["reconstruction_gates"]), {
            "R1_calibration_stream_exists",
            "R2_same_unit_same_window_alignment",
            "R3_reference_not_defined_by_focal_outcome",
            "R4_failure_missingness_separable",
            "R5_performance_estimable",
            "R6_v5_thresholds_met",
        })

    def test_no_candidate_passes_existing_data_reconstruction(self):
        self.assertEqual(self.r["candidate_count"], 2)
        self.assertEqual(self.r["candidates_passing_reconstruction"], 0)
        for candidate in self.r["candidate_results"].values():
            self.assertEqual(candidate["R1_calibration_stream_exists"], "fail")
            self.assertEqual(candidate["R5_performance_estimable"], "fail")
            self.assertEqual(candidate["terminal_state"], "calibration_stream_absent")
            self.assertFalse(candidate["empirical_opening_authorized"])

    def test_unavailable_never_becomes_biological_negative(self):
        self.assertFalse(self.p["unavailable_is_biological_negative"])
        self.assertFalse(self.p["missing_is_biological_negative"])
        self.assertFalse(self.p["retrieval_failure_is_biological_negative"])
        self.assertFalse(self.p["zero_without_reconstruction_pass_is_biological_negative"])

    def test_no_focal_endpoint_is_opened(self):
        self.assertFalse(self.r["focal_cross_role_values_opened"])
        self.assertFalse(self.r["hard_invariant_opening_authorized"])
        self.assertFalse(self.r["soft_crosscheck_opening_authorized"])
        self.assertFalse(self.r["process_knockout_authorized"])

    def test_ledger_remains_unchanged(self):
        self.assertFalse(self.r["counts_as_empirical_evidence"])
        self.assertFalse(self.r["counts_as_empirical_conclusion"])
        self.assertEqual(self.r["empirical_ledger_increment"], 0)
        self.assertEqual(self.r["global_284b_empirical_ledger_after_v6"], 1)


if __name__ == "__main__":
    unittest.main()
