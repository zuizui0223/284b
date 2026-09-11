import json
from pathlib import Path
import unittest

from analysis.level_c_absence_identifiability_v4 import classify, qualification_worlds, score

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_absence_identifiability_protocol_v4.json"


class LevelCAbsenceIdentifiabilityV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    def test_protocol_is_prevalue_and_nonempirical(self):
        self.assertEqual(self.p["protocol_state"], "frozen_before_any_v4_empirical_value_opening")
        self.assertFalse(self.p["empirical_value_opening_authorized_now"])
        self.assertFalse(self.p["counts_as_empirical_evidence"])
        self.assertFalse(self.p["counts_as_empirical_conclusion"])
        self.assertEqual(self.p["empirical_ledger_increment"], 0)
        self.assertEqual(self.p["global_284b_empirical_ledger_at_protocol_freeze"], 1)

    def test_candidate_set_is_frozen_to_v3_qualified_pair(self):
        self.assertEqual(self.p["eligible_candidates"], ["CREMV3-007", "BELV3-012"])
        self.assertFalse(self.p["candidate_addition_or_replacement_authorized"])

    def test_all_absence_gates_are_frozen(self):
        self.assertEqual(set(self.p["absence_identifiability_gates"]), {f"A{i}_{name}" for i, name in [
            (0, "key_observable"),
            (1, "function_channel_directness"),
            (2, "coverage_completeness"),
            (3, "detection_adequacy"),
            (4, "missingness_separation"),
            (5, "negative_decision_rule"),
        ]})

    def test_synthetic_qualification_passes_without_false_absence(self):
        r = score(qualification_worlds())
        self.assertGreaterEqual(r["sensitivity"], 0.8)
        self.assertLessEqual(r["false_negative_rate"], 0.2)
        self.assertGreaterEqual(r["specificity"], 0.95)
        self.assertTrue(r["unavailable_not_negative"])
        self.assertTrue(r["passes"])

    def test_nonadequate_zero_is_unresolved(self):
        for world in qualification_worlds():
            if world.missing_or_failed or not world.complete_coverage or not world.detection_adequate:
                self.assertEqual(classify(world), "unresolved")

    def test_candidate_specific_shortcuts_are_forbidden(self):
        req = self.p["candidate_specific_prevalue_requirements"]
        self.assertIn("zero recorded pollinia-bearing visits alone", req["CREMV3-007"]["forbidden_negative_shortcut"])
        self.assertIn("missing budbreak record", req["BELV3-012"]["forbidden_negative_shortcut"])

    def test_level_a_q95_is_not_imported(self):
        self.assertFalse(self.p["forbidden_interpretations"]["Level_A_q95_is_cross_role_absence_tolerance"])


if __name__ == "__main__":
    unittest.main()
