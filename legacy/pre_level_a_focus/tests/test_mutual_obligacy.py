import unittest

from product_b_v5.invariants import InvariantState, support_breadth
from product_b_v5.mutual import (
    ConstraintClass,
    classify_mutual_obligacy,
    mutual_obligacy_containment,
    rank_profile_discordance_pair,
)


class MutualObligacyTests(unittest.TestCase):
    def setUp(self):
        self.coordinates = ((0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0))

    def test_constraint_class_is_explicit(self):
        self.assertEqual(ConstraintClass.MUTUAL_OBLIGACY.value, "mutual_obligacy")
        self.assertEqual(ConstraintClass.DIRECTED_DEPENDENCY.value, "directed_dependency")

    def test_bidirectional_containment_passes_when_supports_are_compatible(self):
        x = (0.45, 0.35, 0.15, 0.05)
        y = (0.50, 0.30, 0.15, 0.05)
        containment = mutual_obligacy_containment(x, y, 0.90)

        decision = classify_mutual_obligacy(
            containment_y_in_x=containment.y_in_x,
            containment_x_in_y=containment.x_in_y,
            adequacy_x=True,
            adequacy_y=True,
            minimum_containment=0.90,
            breadth_x=support_breadth(x, self.coordinates),
            breadth_y=support_breadth(y, self.coordinates),
            maximum_partner_breadth=2.0,
        )

        self.assertEqual(decision.state, InvariantState.CONSISTENT)
        self.assertEqual(decision.y_requires_x_state, InvariantState.CONSISTENT)
        self.assertEqual(decision.x_requires_y_state, InvariantState.CONSISTENT)

    def test_one_complete_directional_failure_falsifies_mutual_obligacy(self):
        x = (0.60, 0.30, 0.10, 0.00)
        y = (0.00, 0.10, 0.30, 0.60)
        containment = mutual_obligacy_containment(x, y, 0.80)

        decision = classify_mutual_obligacy(
            containment_y_in_x=containment.y_in_x,
            containment_x_in_y=containment.x_in_y,
            adequacy_x=True,
            adequacy_y=True,
            minimum_containment=0.90,
            breadth_x=support_breadth(x, self.coordinates),
            breadth_y=support_breadth(y, self.coordinates),
            maximum_partner_breadth=2.0,
        )

        self.assertEqual(decision.state, InvariantState.VIOLATED)
        self.assertIn(
            InvariantState.VIOLATED,
            (decision.y_requires_x_state, decision.x_requires_y_state),
        )

    def test_unresolved_direction_prevents_mutual_consistency(self):
        decision = classify_mutual_obligacy(
            containment_y_in_x=0.98,
            containment_x_in_y=0.98,
            adequacy_x=True,
            adequacy_y=False,
            minimum_containment=0.90,
            breadth_x=1.0,
            breadth_y=1.0,
            maximum_partner_breadth=2.0,
        )
        self.assertEqual(decision.state, InvariantState.UNRESOLVED)

    def test_rank_discordance_is_scale_free(self):
        x = (0.4, 0.3, 0.2, 0.1)
        same_rank_scaled = (4.0, 3.0, 2.0, 1.0)
        reversed_rank = (0.1, 0.2, 0.3, 0.4)

        self.assertAlmostEqual(rank_profile_discordance_pair(x, same_rank_scaled), 0.0)
        self.assertGreater(rank_profile_discordance_pair(x, reversed_rank), 0.0)

    def test_rank_discordance_requires_common_audit_cells(self):
        with self.assertRaisesRegex(ValueError, "same audit cells"):
            rank_profile_discordance_pair((1.0, 2.0), (1.0, 2.0, 3.0))


if __name__ == "__main__":
    unittest.main()
