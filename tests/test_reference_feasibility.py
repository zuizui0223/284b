import unittest

from product_b_v5.reference_feasibility import evaluate_reference_feasibility


class ReferenceFeasibilityTests(unittest.TestCase):
    def test_below_minimum_stays_unresolved(self):
        d = evaluate_reference_feasibility(29, minimum_required_taxa=30)
        self.assertFalse(d.discordance_opening_authorized)
        self.assertEqual(d.state, "reference_calibration_unresolved_pre_discordance")

    def test_exact_minimum_authorizes_opening(self):
        d = evaluate_reference_feasibility(30, minimum_required_taxa=30)
        self.assertTrue(d.discordance_opening_authorized)
        self.assertEqual(d.state, "reference_discordance_opening_authorized")

    def test_invalid_counts_fail_closed(self):
        with self.assertRaises(ValueError):
            evaluate_reference_feasibility(-1, minimum_required_taxa=30)
        with self.assertRaises(ValueError):
            evaluate_reference_feasibility(30, minimum_required_taxa=0)


if __name__ == "__main__":
    unittest.main()
