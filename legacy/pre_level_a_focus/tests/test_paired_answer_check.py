import unittest

from product_b_v5.crosscheck import (
    PairedCheckState,
    classify_paired_answer_check,
    reciprocal_containment_discordance,
)


class PairedAnswerCheckTests(unittest.TestCase):
    def test_within_predeclared_tolerance_is_consistent(self):
        decision = classify_paired_answer_check(
            discordance=0.12,
            reference_ceiling=0.20,
            adequacy_a=True,
            adequacy_b=True,
        )
        self.assertEqual(decision.state, PairedCheckState.CONSISTENT)
        self.assertAlmostEqual(decision.excess_discordance, -0.08)

    def test_excess_discordance_is_attention_not_hard_violation(self):
        decision = classify_paired_answer_check(
            discordance=0.35,
            reference_ceiling=0.20,
            adequacy_a=True,
            adequacy_b=True,
        )
        self.assertEqual(decision.state, PairedCheckState.ATTENTION_REQUIRED)
        self.assertAlmostEqual(decision.excess_discordance, 0.15)

    def test_inadequate_answer_is_unresolved_not_attention(self):
        decision = classify_paired_answer_check(
            discordance=0.80,
            reference_ceiling=0.20,
            adequacy_a=True,
            adequacy_b=False,
        )
        self.assertEqual(decision.state, PairedCheckState.UNRESOLVED)
        self.assertIn("answer_b_inadequate", decision.reasons)

    def test_reciprocal_containment_discordance(self):
        self.assertAlmostEqual(reciprocal_containment_discordance(0.90, 0.85), 0.05)
        self.assertAlmostEqual(reciprocal_containment_discordance(0.95, 0.20), 0.75)

    def test_reference_ceiling_must_be_finite(self):
        with self.assertRaises(ValueError):
            classify_paired_answer_check(
                discordance=0.2,
                reference_ceiling=float("nan"),
                adequacy_a=True,
                adequacy_b=True,
            )


if __name__ == "__main__":
    unittest.main()
