import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "incubator" / "frog_chorus_synchrony"


class FrogChorusSynchronySynthesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.naamp = json.loads(
            (BASE / "NAAMP_PRIMARY_RECEIPT_V0_1.json").read_text(encoding="utf-8")
        )
        cls.frogid = json.loads(
            (BASE / "FROGID_VALIDATION_RECEIPT_V0_2.json").read_text(encoding="utf-8")
        )
        cls.synth = json.loads(
            (BASE / "FROG_CROSS_DATASET_SYNTHESIS_V0_1.json").read_text(encoding="utf-8")
        )
        cls.decision = json.loads(
            (BASE / "FROG_SYNTHESIS_CONTRACT_V0_1.json").read_text(encoding="utf-8")
        )

    def test_naamp_primary_is_small_directional_support(self):
        p = self.naamp["primary"]
        self.assertEqual(p["n_runs"], 9399)
        self.assertLess(p["beta"], 0)
        self.assertTrue(p["frozen_support_rule_pass"])
        self.assertGreater(p["p_value"], 0)
        self.assertLess(p["p_value"], 0.05)
        self.assertGreater(p["odds_ratio_per_sd_log1p_days_since_rain"], 0.94)
        self.assertLess(p["odds_ratio_per_sd_log1p_days_since_rain"], 1.0)

    def test_frogid_validation_passes_primary_and_sensitivities(self):
        p = self.frogid["primary"]
        self.assertEqual(self.frogid["frozen_sample"]["recordings"], 40754)
        self.assertEqual(
            self.frogid["frozen_sample"]["multispecies_recordings"], 18174
        )
        self.assertEqual(self.frogid["frozen_sample"]["weather_cells"], 1623)
        self.assertLess(p["beta"], 0)
        self.assertTrue(p["support_rule_pass"])
        self.assertLess(p["p_value"], 0.05)
        self.assertLess(p["ci95_beta"][1], 0)
        self.assertTrue(
            self.frogid["sensitivities"]["coordinate_uncertainty_le10km"][
                "support_rule_pass"
            ]
        )
        self.assertTrue(
            self.frogid["sensitivities"]["recorder_cluster"]["support_rule_pass"]
        )

    def test_external_validation_was_not_retuned(self):
        self.assertFalse(self.frogid["post_opening_retuning_performed"])
        self.assertFalse(self.frogid["naamp_primary_replaced"])
        self.assertFalse(self.frogid["causal_claim_authorized"])

    def test_cross_dataset_classification_follows_frozen_rule(self):
        self.assertEqual(
            self.synth["cross_dataset_classification"],
            "independent_support_robust",
        )
        self.assertTrue(self.synth["naamp"]["support"])
        self.assertTrue(self.synth["frogid"]["support"])
        self.assertFalse(self.synth["causal_claim_authorized"])
        self.assertFalse(self.synth["effect_sizes_meta_analyzed"])

    def test_negative_predictions_remain_negative(self):
        negatives = " ".join(self.synth["not_supported"]).lower()
        self.assertIn("seasonal-shoulder", negatives)
        self.assertIn("network densification", negatives)

    def test_synthesis_language_is_associational(self):
        claim = self.synth["supported_claim"].lower()
        self.assertIn("associated", claim)
        self.assertNotIn("causes", claim)
        boundary = self.synth["mechanistic_boundary"].lower()
        self.assertIn("not causal", boundary)
        self.assertIn("not", boundary)

    def test_validation_classification_was_frozen_before_result(self):
        rules = self.decision["frogid_validation_classification"]
        self.assertIn("independent_support", rules)
        self.assertIn("contradictory", rules)
        self.assertTrue(
            self.decision["sensitivity_policy"]["primary_controls_validation"]
        )


if __name__ == "__main__":
    unittest.main()
