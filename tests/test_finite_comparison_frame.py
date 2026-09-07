import unittest

import numpy as np
import pandas as pd

from product_b_v5.finite_comparison_frame import freeze_finite_comparison_frame


class FiniteComparisonFrameTests(unittest.TestCase):
    def test_freezes_exact_size_from_all_predictor_complete_rows(self):
        frame = pd.DataFrame({
            "row": list(range(8)),
            "p1": [1, 2, 3, 4, 5, 6, 7, 8],
            "p2": [1, np.nan, 3, 4, 5, np.nan, 7, 8],
        })
        selected, audit = freeze_finite_comparison_frame(
            frame, ("p1", "p2"), required_rows=4, random_state=17
        )
        self.assertEqual(audit.state, "finite_comparison_frame_frozen")
        self.assertEqual(audit.candidate_rows, 8)
        self.assertEqual(audit.all_predictor_finite_rows, 6)
        self.assertEqual(audit.selected_rows, 4)
        self.assertEqual(len(selected), 4)
        self.assertTrue(np.isfinite(selected[["p1", "p2"]].to_numpy(float)).all())

    def test_fails_closed_without_partial_frame(self):
        frame = pd.DataFrame({"p1": [1.0, np.nan, 2.0], "p2": [1.0, 2.0, np.nan]})
        selected, audit = freeze_finite_comparison_frame(
            frame, ("p1", "p2"), required_rows=2, random_state=9
        )
        self.assertEqual(audit.state, "finite_comparison_frame_unresolved")
        self.assertEqual(audit.all_predictor_finite_rows, 1)
        self.assertEqual(audit.selected_rows, 0)
        self.assertTrue(selected.empty)

    def test_deterministic_under_fixed_seed(self):
        frame = pd.DataFrame({"row": range(20), "p1": range(20), "p2": range(20)})
        a, _ = freeze_finite_comparison_frame(frame, ("p1", "p2"), required_rows=7, random_state=123)
        b, _ = freeze_finite_comparison_frame(frame, ("p1", "p2"), required_rows=7, random_state=123)
        self.assertEqual(a["row"].tolist(), b["row"].tolist())

    def test_rejects_missing_predictor(self):
        with self.assertRaises(ValueError):
            freeze_finite_comparison_frame(
                pd.DataFrame({"p1": [1.0]}), ("p1", "p2"), required_rows=1, random_state=1
            )


if __name__ == "__main__":
    unittest.main()
