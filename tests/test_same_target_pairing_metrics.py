import unittest

from product_b_v5.same_target_pairing import (
    evaluate_prediction_adequacy,
    schoener_d_from_sealed_vectors,
    schoener_d_if_both_answers_adequate,
)


class SameTargetPredictionAdequacyTests(unittest.TestCase):
    def test_complete_above_chance_profile_passes(self):
        result = evaluate_prediction_adequacy([0.60, 0.61, 0.59, 0.60], expected_folds=4)
        self.assertTrue(result.adequate)
        self.assertTrue(result.evidence_complete)
        self.assertEqual(result.n_folds, 4)
        self.assertEqual(result.reasons, ())

    def test_incomplete_outer_fold_profile_is_unresolved(self):
        result = evaluate_prediction_adequacy([0.70, 0.70, 0.70], expected_folds=4)
        self.assertFalse(result.adequate)
        self.assertFalse(result.evidence_complete)
        self.assertIn("outer_fold_evidence_incomplete", result.reasons)

    def test_mean_floor_and_chance_bound_are_both_required(self):
        result = evaluate_prediction_adequacy([0.53, 0.53, 0.49, 0.49], expected_folds=4)
        self.assertFalse(result.adequate)
        self.assertTrue(result.evidence_complete)
        self.assertTrue(
            "mean_presence_rank_below_frozen_floor" in result.reasons
            or "presence_rank_lower_bound_below_chance" in result.reasons
        )


class SameTargetSchoenerDTests(unittest.TestCase):
    def test_identical_vectors_have_d_one(self):
        ids = ["a", "b", "c"]
        self.assertAlmostEqual(
            schoener_d_from_sealed_vectors(ids, [1, 2, 3], ids, [1, 2, 3]),
            1.0,
        )

    def test_disjoint_mass_has_d_zero(self):
        ids = ["a", "b"]
        self.assertAlmostEqual(
            schoener_d_from_sealed_vectors(ids, [1, 0], ids, [0, 1]),
            0.0,
        )

    def test_row_order_does_not_matter_but_row_set_does(self):
        self.assertAlmostEqual(
            schoener_d_from_sealed_vectors(["a", "b"], [1, 3], ["b", "a"], [3, 1]),
            1.0,
        )
        with self.assertRaises(ValueError):
            schoener_d_from_sealed_vectors(["a", "b"], [1, 3], ["a", "c"], [1, 3])

    def test_nonfinite_or_duplicate_rows_fail_closed(self):
        with self.assertRaises(ValueError):
            schoener_d_from_sealed_vectors(["a", "a"], [1, 2], ["a", "b"], [1, 2])
        with self.assertRaises(ValueError):
            schoener_d_from_sealed_vectors(["a", "b"], [1, float("nan")], ["a", "b"], [1, 2])

    def test_pair_discordance_is_not_opened_when_either_answer_is_inadequate(self):
        adequate = evaluate_prediction_adequacy([0.60, 0.61, 0.59, 0.60], expected_folds=4)
        inadequate = evaluate_prediction_adequacy([0.40, 0.41, 0.39, 0.40], expected_folds=4)
        # Deliberately invalid/mismatched sealed vectors prove the helper returns
        # before inspecting paired outcomes when the answer-check is inadmissible.
        self.assertIsNone(
            schoener_d_if_both_answers_adequate(
                adequacy_a=adequate,
                adequacy_b=inadequate,
                row_ids_a=["a"],
                scores_a=[float("nan")],
                row_ids_b=["different"],
                scores_b=[-1.0],
            )
        )

    def test_pair_discordance_opens_only_after_both_answers_are_adequate(self):
        adequate_a = evaluate_prediction_adequacy([0.60, 0.61, 0.59, 0.60], expected_folds=4)
        adequate_b = evaluate_prediction_adequacy([0.62, 0.61, 0.60, 0.59], expected_folds=4)
        self.assertAlmostEqual(
            schoener_d_if_both_answers_adequate(
                adequacy_a=adequate_a,
                adequacy_b=adequate_b,
                row_ids_a=["a", "b"],
                scores_a=[1.0, 3.0],
                row_ids_b=["b", "a"],
                scores_b=[3.0, 1.0],
            ),
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
