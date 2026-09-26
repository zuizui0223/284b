import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
QUAL = ROOT / "config" / "product_b_level_c_functional_pool_source_qualification_v2.json"


class LevelCFunctionalPoolSourceQualificationV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q = json.loads(QUAL.read_text(encoding="utf-8"))

    def test_freeze_precedes_focal_source_values(self):
        self.assertEqual(
            self.q["qualification_state"],
            "frozen_before_any_v2_focal_source_values_are_opened",
        )
        self.assertFalse(self.q["qualification_opens_focal_outcome_values"])
        self.assertFalse(self.q["counts_as_empirical_evidence"])
        self.assertFalse(self.q["counts_as_empirical_conclusion"])
        self.assertEqual(self.q["empirical_ledger_increment"], 0)

    def test_unavailable_missing_and_zero_are_not_function_negatives(self):
        f = self.q["functional_channel"]
        self.assertFalse(f["zero_records_without_absence_adequacy_is_function_negative"])
        self.assertFalse(f["source_unavailable_is_function_negative"])
        self.assertFalse(f["missing_is_function_negative"])
        self.assertFalse(f["failed_download_or_API_is_function_negative"])
        self.assertFalse(f["empty_query_result_is_function_negative"])
        self.assertFalse(f["provider_not_in_database_is_function_negative"])

    def test_hard_violation_requires_adequate_functional_absence(self):
        v = self.q["hard_violation_license"]
        self.assertTrue(v["requires_event_positive"])
        self.assertTrue(v["requires_function_negative"])
        self.assertTrue(v["requires_function_absence_adequacy"])
        self.assertFalse(v["unavailable_can_license_violation"])
        self.assertFalse(v["missing_can_license_violation"])
        self.assertFalse(v["zero_without_detection_adequacy_can_license_violation"])

    def test_unresolved_explicitly_contains_availability_failures(self):
        unresolved = self.q["confirmatory_key_states_if_candidate_qualifies"]["unresolved"]
        for term in ["unavailable", "missing", "failed retrieval", "zero without sufficient detection adequacy"]:
            self.assertIn(term, unresolved)

    def test_relation_source_cannot_double_as_endpoint(self):
        common = self.q["common_requirements"]
        self.assertFalse(common["relation_defining_source_may_score_focal_endpoint"])
        self.assertTrue(common["same_frozen_event_key_required"])
        self.assertTrue(common["candidate_specific_relaxation_after_source_inspection_forbidden"])
        self.assertTrue(common["replacement_candidate_after_qualification_forbidden"])


if __name__ == "__main__":
    unittest.main()
