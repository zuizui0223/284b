"""Small correctness checks; full frozen receipts are checked by the workflow."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_level_a_discriminability_v1 import nearest_rank


class QuantileTests(unittest.TestCase):
    def test_nearest_rank_matches_reference_rule(self):
        self.assertEqual(nearest_rank(list(range(1, 35))), 33)
        self.assertEqual(nearest_rank(list(range(1, 41))), 38)
        self.assertEqual(nearest_rank(list(range(1, 47))), 44)

    def test_nearest_rank_rejects_empty_and_bad_quantiles(self):
        with self.assertRaises(ValueError):
            nearest_rank([])
        with self.assertRaises(ValueError):
            nearest_rank([1.0, 2.0], 0.0)

    def test_nearest_rank_preserves_sorted_rank(self):
        self.assertEqual(nearest_rank([9, 2, 6, 3, 1], 0.8), 6)


if __name__ == "__main__":
    unittest.main()
