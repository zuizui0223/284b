import unittest

from product_b_v6.witness import (
    HostSamplingSummary,
    WitnessConstraintState,
    WitnessPreflightState,
    WitnessSamplingSummary,
    classify_witness_constraint,
    directed_witness_containment,
    empirical_nearest_rank_quantile,
    evaluate_witness_sampling_preflight,
    host_support_fraction,
    knockout_preferential_drop,
)


class WitnessSamplingPreflightTests(unittest.TestCase):
    def test_frozen_asymmetric_sampling_floor_passes(self):
        result = evaluate_witness_sampling_preflight(
            HostSamplingSummary(50, 30, 10.0),
            WitnessSamplingSummary(5, 3),
        )
        self.assertEqual(result.state, WitnessPreflightState.PASSED)

    def test_sparse_witness_is_unresolved_without_lowering_host_floor(self):
        result = evaluate_witness_sampling_preflight(
            HostSamplingSummary(500, 100, 50.0),
            WitnessSamplingSummary(4, 3),
        )
        self.assertEqual(result.state, WitnessPreflightState.UNRESOLVED)
        self.assertIn("witness_independent_record_floor_failed", result.reasons)

    def test_sparse_host_is_still_unresolved(self):
        result = evaluate_witness_sampling_preflight(
            HostSamplingSummary(49, 29, 9.9),
            WitnessSamplingSummary(20, 10),
        )
        self.assertEqual(result.state, WitnessPreflightState.UNRESOLVED)
        self.assertIn("host_independent_record_floor_failed", result.reasons)
        self.assertIn("host_unique_cell_floor_failed", result.reasons)
        self.assertIn("host_effective_cell_floor_failed", result.reasons)


class WitnessContainmentTests(unittest.TestCase):
    def test_duplicate_records_in_same_cell_count_once(self):
        support = {"a": 1, "b": 0, "c": 1}
        self.assertEqual(
            directed_witness_containment(support, ("a", "a", "b")),
            0.5,
        )

    def test_missing_witness_cell_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "absent"):
            directed_witness_containment({"a": 1}, ("a", "b"))

    def test_host_support_fraction_is_audit_space_fraction(self):
        support = {str(i): int(i < 8) for i in range(10)}
        self.assertEqual(host_support_fraction(support), 0.8)

    def test_nonbinary_support_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "binary"):
            directed_witness_containment({"a": 0.5}, ("a",))


class EmpiricalQuantileTests(unittest.TestCase):
    def test_nearest_rank_is_deterministic(self):
        values = tuple(range(1, 101))
        self.assertEqual(empirical_nearest_rank_quantile(values, 0.05), 5.0)
        self.assertEqual(empirical_nearest_rank_quantile(values, 0.95), 95.0)


class WitnessClassifierTests(unittest.TestCase):
    def test_actual_above_shuffled_q95_is_compatible(self):
        controls = (0.2,) * 95 + (0.4,) * 5
        result = classify_witness_constraint(
            preflight_passed=True,
            actual_containment=0.9,
            shuffled_control_containments=controls,
            eligible_replacement_host_count=5,
            support_fraction=0.4,
        )
        self.assertEqual(result.state, WitnessConstraintState.COMPATIBLE)
        self.assertEqual(result.control_q95, 0.2)

    def test_actual_below_shuffled_q05_is_violation(self):
        controls = (0.6,) * 5 + (0.8,) * 95
        result = classify_witness_constraint(
            preflight_passed=True,
            actual_containment=0.1,
            shuffled_control_containments=controls,
            eligible_replacement_host_count=5,
            support_fraction=0.5,
        )
        self.assertEqual(result.state, WitnessConstraintState.VIOLATION)
        self.assertEqual(result.control_q05, 0.6)

    def test_actual_inside_reference_band_is_unresolved(self):
        controls = tuple([0.2] * 10 + [0.5] * 80 + [0.8] * 10)
        result = classify_witness_constraint(
            preflight_passed=True,
            actual_containment=0.5,
            shuffled_control_containments=controls,
            eligible_replacement_host_count=6,
            support_fraction=0.3,
        )
        self.assertEqual(result.state, WitnessConstraintState.UNRESOLVED)
        self.assertIn("inside_shuffled_reference_band", result.reasons[0])

    def test_broad_host_support_cannot_pass_by_covering_everything(self):
        controls = (0.2,) * 100
        result = classify_witness_constraint(
            preflight_passed=True,
            actual_containment=1.0,
            shuffled_control_containments=controls,
            eligible_replacement_host_count=5,
            support_fraction=0.81,
        )
        self.assertEqual(result.state, WitnessConstraintState.UNRESOLVED)
        self.assertIn("host_support_breadth_guardrail_failed", result.reasons)

    def test_control_pool_and_draw_count_are_fail_closed(self):
        result = classify_witness_constraint(
            preflight_passed=True,
            actual_containment=0.9,
            shuffled_control_containments=(0.2,) * 99,
            eligible_replacement_host_count=4,
            support_fraction=0.3,
        )
        self.assertEqual(result.state, WitnessConstraintState.UNRESOLVED)
        self.assertIn("insufficient_eligible_replacement_hosts", result.reasons)
        self.assertIn("shuffled_control_draw_count_mismatch", result.reasons)


class KnockoutTests(unittest.TestCase):
    def test_preferential_drop_subtracts_shuffled_mean_drop(self):
        value = knockout_preferential_drop(
            actual_full_containment=0.9,
            actual_knockout_containment=0.5,
            shuffled_full_containments=(0.6, 0.6),
            shuffled_knockout_containments=(0.5, 0.55),
        )
        self.assertAlmostEqual(value, 0.325)


if __name__ == "__main__":
    unittest.main()
