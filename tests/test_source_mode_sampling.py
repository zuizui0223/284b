import unittest

from product_b_v5.sampling import SamplingSummary
from product_b_v5.source_mode_sampling import (
    evaluate_paired_source_mode_adequacy,
    evaluate_source_mode_adequacy,
)


class SourceModeSamplingTests(unittest.TestCase):
    def test_each_mode_must_clear_50_30_10(self):
        summary = SamplingSummary(50, 30, 10.0, raw_records=60)
        decision = evaluate_source_mode_adequacy(summary, label="preserved_specimen")
        self.assertTrue(decision.passed)
        self.assertEqual(decision.reasons, ())

    def test_mode_failure_is_explicit(self):
        summary = SamplingSummary(49, 29, 9.9, raw_records=49)
        decision = evaluate_source_mode_adequacy(summary, label="human_observation")
        self.assertFalse(decision.passed)
        self.assertEqual(
            decision.reasons,
            (
                "human_observation_independent_record_floor_failed",
                "human_observation_unique_cell_floor_failed",
                "human_observation_effective_cell_floor_failed",
            ),
        )

    def test_cross_mode_asymmetry_is_not_a_failure(self):
        specimen = SamplingSummary(50, 30, 10.0, raw_records=50)
        observation = SamplingSummary(50000, 3000, 1000.0, raw_records=50000)
        decision = evaluate_paired_source_mode_adequacy(specimen, observation)
        self.assertTrue(decision.passed)

    def test_one_inadequate_mode_makes_pair_unresolved(self):
        specimen = SamplingSummary(50, 30, 10.0, raw_records=50)
        observation = SamplingSummary(20, 15, 8.0, raw_records=20)
        decision = evaluate_paired_source_mode_adequacy(specimen, observation)
        self.assertFalse(decision.passed)
        self.assertIn("human_observation_independent_record_floor_failed", decision.reasons)


if __name__ == "__main__":
    unittest.main()
