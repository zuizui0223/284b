import math
import unittest

from product_b_v5.reference_calibration import freeze_reference_ceiling, nearest_rank_quantile


class ReferenceCalibrationTests(unittest.TestCase):
    def test_nearest_rank_q95_at_n30_is_29th_value(self):
        value, rank = nearest_rank_quantile(range(1, 31), 0.95)
        self.assertEqual(rank, 29)
        self.assertEqual(value, 29.0)

    def test_reference_ceiling_freezes_at_frozen_minimum(self):
        decision = freeze_reference_ceiling(range(1, 31), minimum_n=30, quantile=0.95)
        self.assertEqual(decision.state, "reference_ceiling_frozen")
        self.assertEqual(decision.n, 30)
        self.assertEqual(decision.nearest_rank_index_1_based, 29)
        self.assertEqual(decision.ceiling, 29.0)

    def test_reference_ceiling_stays_unresolved_below_minimum(self):
        decision = freeze_reference_ceiling(range(1, 30), minimum_n=30, quantile=0.95)
        self.assertEqual(decision.state, "reference_ceiling_unresolved")
        self.assertEqual(decision.n, 29)
        self.assertIsNone(decision.nearest_rank_index_1_based)
        self.assertIsNone(decision.ceiling)

    def test_nonfinite_authorized_value_is_not_silently_dropped(self):
        with self.assertRaises(ValueError):
            freeze_reference_ceiling([0.1] * 29 + [math.nan], minimum_n=30, quantile=0.95)

    def test_invalid_quantile_rejected(self):
        with self.assertRaises(ValueError):
            nearest_rank_quantile([0.1, 0.2], 0.0)


if __name__ == "__main__":
    unittest.main()
