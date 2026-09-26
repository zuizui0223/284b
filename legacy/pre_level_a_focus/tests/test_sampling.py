import unittest

from product_b_v5.sampling import (
    PRIMARY_THRESHOLDS,
    STRICT_SENSITIVITY_THRESHOLDS,
    RecordIdentity,
    SamplingState,
    SamplingSummary,
    cross_partner_collision_reasons,
    evaluate_sampling_pair,
    inverse_simpson_effective_cells,
)


class EffectiveCellTests(unittest.TestCase):
    def test_uniform_four_cells_have_four_effective_cells(self):
        self.assertAlmostEqual(inverse_simpson_effective_cells((5, 5, 5, 5)), 4.0)

    def test_concentration_reduces_effective_cells(self):
        value = inverse_simpson_effective_cells((17, 1, 1, 1))
        self.assertLess(value, 2.0)
        self.assertGreater(value, 1.0)


class CollisionRuleTests(unittest.TestCase):
    def test_shared_occurrence_lineage_is_collision(self):
        x = RecordIdentity(occurrence_id_lineage="shared")
        y = RecordIdentity(occurrence_id_lineage="shared")
        self.assertIn("occurrence_id_lineage", cross_partner_collision_reasons(x, y))

    def test_shared_dataset_date_coordinate_is_collision(self):
        x = RecordIdentity(dataset_key="d", event_date="2020-01-01", coordinate_key="1,2")
        y = RecordIdentity(dataset_key="d", event_date="2020-01-01", coordinate_key="1,2")
        self.assertIn(
            "dataset_key_plus_event_date_plus_coordinate",
            cross_partner_collision_reasons(x, y),
        )

    def test_same_coordinate_alone_is_not_collision(self):
        x = RecordIdentity(coordinate_key="1,2")
        y = RecordIdentity(coordinate_key="1,2")
        self.assertEqual(cross_partner_collision_reasons(x, y), ())

    def test_shared_recorder_date_coordinate_is_collision(self):
        x = RecordIdentity(recorder="A", event_date="2020-01-01", coordinate_key="1,2")
        y = RecordIdentity(recorder="A", event_date="2020-01-01", coordinate_key="1,2")
        self.assertIn(
            "recorder_plus_date_plus_coordinate",
            cross_partner_collision_reasons(x, y),
        )


class SamplingPreflightTests(unittest.TestCase):
    def test_primary_preflight_passes_admissible_pair(self):
        x = SamplingSummary(100, 60, 40.0, raw_records=110, collision_excluded_records=10)
        y = SamplingSummary(80, 50, 30.0, raw_records=85, collision_excluded_records=5)
        result = evaluate_sampling_pair(
            x, y, taxonomy_eligible=True, thresholds=PRIMARY_THRESHOLDS
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.state, SamplingState.PASSED)

    def test_record_floor_failure_is_unresolved(self):
        x = SamplingSummary(49, 40, 20.0)
        y = SamplingSummary(80, 50, 30.0)
        result = evaluate_sampling_pair(x, y, taxonomy_eligible=True)
        self.assertFalse(result.passed)
        self.assertIn("x_independent_record_floor_failed", result.reasons)

    def test_asymmetry_ceiling_failure_is_unresolved(self):
        x = SamplingSummary(600, 100, 50.0)
        y = SamplingSummary(50, 30, 10.0)
        result = evaluate_sampling_pair(x, y, taxonomy_eligible=True)
        self.assertFalse(result.passed)
        self.assertIn("record_asymmetry_ceiling_failed", result.reasons)

    def test_taxonomy_gate_failure_cannot_be_rescued_by_abundant_sampling(self):
        x = SamplingSummary(1000, 500, 300.0)
        y = SamplingSummary(1000, 500, 300.0)
        result = evaluate_sampling_pair(x, y, taxonomy_eligible=False)
        self.assertFalse(result.passed)
        self.assertIn("taxonomy_gate_not_passed", result.reasons)

    def test_strict_sensitivity_is_predeclared_and_stricter(self):
        x = SamplingSummary(80, 40, 15.0)
        y = SamplingSummary(80, 40, 15.0)
        primary = evaluate_sampling_pair(
            x, y, taxonomy_eligible=True, thresholds=PRIMARY_THRESHOLDS
        )
        strict = evaluate_sampling_pair(
            x, y, taxonomy_eligible=True, thresholds=STRICT_SENSITIVITY_THRESHOLDS
        )
        self.assertTrue(primary.passed)
        self.assertFalse(strict.passed)

    def test_zero_denominator_is_unresolved_not_infinite_success(self):
        x = SamplingSummary(0, 0, 0.0)
        y = SamplingSummary(100, 50, 20.0)
        result = evaluate_sampling_pair(x, y, taxonomy_eligible=True)
        self.assertFalse(result.passed)
        self.assertIn("record_asymmetry_unresolved_zero_denominator", result.reasons)


if __name__ == "__main__":
    unittest.main()
