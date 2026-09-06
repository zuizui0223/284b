import unittest

from product_b_v5.heldout_crosscheck import classify_heldout_crosscheck


class HeldoutCrosscheckTests(unittest.TestCase):
    def test_inadequate_answer_keeps_discordance_closed(self):
        decision = classify_heldout_crosscheck(
            both_answers_adequate=False,
            discordance=None,
            reference_state="reference_ceiling_frozen",
            reference_ceiling=0.20,
        )
        self.assertEqual(decision.state, "paired_crosscheck_unresolved")
        self.assertIsNone(decision.discordance)

    def test_inadequate_answer_rejects_opened_discordance(self):
        with self.assertRaises(ValueError):
            classify_heldout_crosscheck(
                both_answers_adequate=False,
                discordance=0.10,
                reference_state="reference_ceiling_frozen",
                reference_ceiling=0.20,
            )

    def test_missing_reference_keeps_discordance_closed(self):
        decision = classify_heldout_crosscheck(
            both_answers_adequate=True,
            discordance=None,
            reference_state="reference_ceiling_unresolved",
            reference_ceiling=None,
        )
        self.assertEqual(decision.state, "paired_crosscheck_calibration_unresolved")
        self.assertIsNone(decision.discordance)
        self.assertIsNone(decision.exceedance)

    def test_missing_reference_rejects_opened_discordance(self):
        with self.assertRaises(ValueError):
            classify_heldout_crosscheck(
                both_answers_adequate=True,
                discordance=0.10,
                reference_state="reference_ceiling_unresolved",
                reference_ceiling=None,
            )

    def test_equal_to_ceiling_is_consistent(self):
        decision = classify_heldout_crosscheck(
            both_answers_adequate=True,
            discordance=0.20,
            reference_state="reference_ceiling_frozen",
            reference_ceiling=0.20,
        )
        self.assertEqual(decision.state, "paired_crosscheck_consistent")

    def test_strict_exceedance_requires_attention(self):
        decision = classify_heldout_crosscheck(
            both_answers_adequate=True,
            discordance=0.2001,
            reference_state="reference_ceiling_frozen",
            reference_ceiling=0.20,
        )
        self.assertEqual(decision.state, "paired_crosscheck_attention_required")
        self.assertGreater(decision.exceedance, 0.0)


if __name__ == "__main__":
    unittest.main()
