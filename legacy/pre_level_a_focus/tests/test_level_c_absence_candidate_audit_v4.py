import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "results" / "product_b_level_c_absence_synthetic_qualification_v4.json"
AUDIT = ROOT / "results" / "product_b_level_c_absence_candidate_audit_v4.json"


class LevelCAbsenceCandidateAuditV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = json.loads(SYNTH.read_text(encoding="utf-8"))
        cls.a = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_synthetic_pass_does_not_authorize_empirical_opening(self):
        self.assertEqual(cls_s := self.s["qualification_state"], "synthetic_absence_classifier_passed")
        self.assertFalse(self.s["hard_endpoint_opening_authorized_by_this_result_alone"])
        self.assertFalse(self.s["candidate_empirical_values_opened"])

    def test_both_candidates_remain_nonbiological_unresolved(self):
        self.assertEqual(set(self.a["candidate_results"]), {"CREMV3-007", "BELV3-012"})
        for result in self.a["candidate_results"].values():
            self.assertEqual(result["A3_detection_adequacy"], "fail_not_prospectively_validated")
            self.assertEqual(result["terminal_state"], "insufficient_detection_adequacy")
            self.assertFalse(result["biological_negative"])
            self.assertFalse(result["empirical_value_opening_authorized"])

    def test_no_candidate_rescue_or_threshold_tuning(self):
        self.assertFalse(self.a["candidate_replacement_authorized"])
        self.assertFalse(self.a["candidate_specific_threshold_tuning_authorized"])

    def test_no_empirical_ledger_increment(self):
        self.assertFalse(self.a["counts_as_empirical_evidence"])
        self.assertFalse(self.a["counts_as_empirical_conclusion"])
        self.assertEqual(self.a["empirical_ledger_increment"], 0)
        self.assertEqual(self.a["global_284b_empirical_ledger_after_candidate_audit"], 1)


if __name__ == "__main__":
    unittest.main()
