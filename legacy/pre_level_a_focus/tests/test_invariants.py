import unittest

from product_b_v5.invariants import (
    InvariantState,
    ProcedureDescriptor,
    breadth_ratio_pair,
    centroid_separation_pair,
    classify_directed_invariant,
    directed_containment,
    response_blind_differentiability_precheck,
    schoener_d_pair,
    support_breadth,
)


class InvariantMetricTests(unittest.TestCase):
    def setUp(self):
        self.coordinates = ((0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0))

    def test_perfect_nesting(self):
        required = (0.4, 0.3, 0.2, 0.1)
        dependent = (0.6, 0.4, 0.0, 0.0)

        containment = directed_containment(required, dependent, 0.70)
        self.assertAlmostEqual(containment, 1.0)

        state = classify_directed_invariant(
            containment=containment,
            adequacy_required=True,
            adequacy_dependent=True,
            minimum_containment=0.90,
            required_breadth=support_breadth(required, self.coordinates),
            maximum_required_breadth=2.0,
        )
        self.assertEqual(state, InvariantState.CONSISTENT)

    def test_violated_nesting(self):
        required = (0.4, 0.3, 0.2, 0.1)
        dependent = (0.10, 0.10, 0.30, 0.50)

        containment = directed_containment(required, dependent, 0.70)
        self.assertAlmostEqual(containment, 0.20)

        state = classify_directed_invariant(
            containment=containment,
            adequacy_required=True,
            adequacy_dependent=True,
            minimum_containment=0.90,
            required_breadth=support_breadth(required, self.coordinates),
            maximum_required_breadth=2.0,
        )
        self.assertEqual(state, InvariantState.VIOLATED)

    def test_narrow_but_nested_dependent_is_not_a_violation(self):
        required = (0.4, 0.3, 0.2, 0.1)
        dependent = (1.0, 0.0, 0.0, 0.0)

        containment = directed_containment(required, dependent, 0.70)
        ratio = breadth_ratio_pair(dependent, required, self.coordinates)

        self.assertAlmostEqual(containment, 1.0)
        self.assertLess(ratio, 1.0)

        state = classify_directed_invariant(
            containment=containment,
            adequacy_required=True,
            adequacy_dependent=True,
            minimum_containment=0.90,
            required_breadth=support_breadth(required, self.coordinates),
            maximum_required_breadth=2.0,
        )
        self.assertEqual(state, InvariantState.CONSISTENT)

    def test_trivially_broad_required_partner_is_unresolved(self):
        coordinates = ((0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0))
        required = (1.0, 1.0, 1.0, 1.0)
        dependent = (1.0, 0.0, 0.0, 0.0)

        # Tied support at the quantile cutoff retains all tied cells; raw
        # containment is therefore perfect, which is exactly the triviality trap.
        containment = directed_containment(required, dependent, 0.90)
        required_breadth = support_breadth(required, coordinates)

        self.assertAlmostEqual(containment, 1.0)
        self.assertGreater(required_breadth, 5.0)

        state = classify_directed_invariant(
            containment=containment,
            adequacy_required=True,
            adequacy_dependent=True,
            minimum_containment=0.90,
            required_breadth=required_breadth,
            maximum_required_breadth=5.0,
        )
        self.assertEqual(state, InvariantState.UNRESOLVED)

    def test_pair_descriptors_remain_separate_not_composite(self):
        x = (0.5, 0.3, 0.2, 0.0)
        y = (0.4, 0.4, 0.2, 0.0)

        self.assertAlmostEqual(schoener_d_pair(x, y), 0.9)
        self.assertGreaterEqual(centroid_separation_pair(x, y, self.coordinates), 0.0)
        self.assertGreaterEqual(breadth_ratio_pair(y, x, self.coordinates), 0.0)

    def test_failed_partner_adequacy_is_unresolved(self):
        state = classify_directed_invariant(
            containment=0.1,
            adequacy_required=True,
            adequacy_dependent=False,
            minimum_containment=0.90,
            required_breadth=1.0,
            maximum_required_breadth=2.0,
        )
        self.assertEqual(state, InvariantState.UNRESOLVED)


class DifferentiabilityPreflightTests(unittest.TestCase):
    def test_degenerate_single_member_candidate_set_stops_before_opening(self):
        procedures = (
            ProcedureDescriptor("only_member", ("bio1", "bio12")),
        )
        result = response_blind_differentiability_precheck(
            procedures,
            {"temperature": True, "water": True},
        )

        self.assertFalse(result.passed)
        self.assertIn("candidate_set_degenerate", result.reasons)
        self.assertIn("predictor_signatures_not_differentiated", result.reasons)

    def test_distinct_members_and_admissible_knockouts_pass(self):
        procedures = (
            ProcedureDescriptor("member_a", ("bio1", "bio12")),
            ProcedureDescriptor("member_b", ("bio1", "vpd")),
        )
        result = response_blind_differentiability_precheck(
            procedures,
            {"temperature": True, "water": True},
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.admissible_member_count, 2)
        self.assertEqual(result.distinct_predictor_signature_count, 2)

    def test_inadmissible_process_knockout_stops_preflight(self):
        procedures = (
            ProcedureDescriptor("member_a", ("bio1", "bio12")),
            ProcedureDescriptor("member_b", ("bio1", "vpd")),
        )
        result = response_blind_differentiability_precheck(
            procedures,
            {"temperature": True, "water": False},
        )

        self.assertFalse(result.passed)
        self.assertEqual(result.inadmissible_process_knockouts, ("water",))
        self.assertIn("one_or_more_process_knockouts_inadmissible", result.reasons)


if __name__ == "__main__":
    unittest.main()
