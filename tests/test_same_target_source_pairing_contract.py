import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_same_target_source_pairing_contract_v0_1.json"


class SameTargetSourcePairingContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_pairing_requires_sealed_predictions(self):
        self.assertTrue(self.contract["prediction_surfaces_must_be_sealed_before_pairing"])
        self.assertEqual(self.contract["pairing_key"], ["taxon", "procedure", "M_km"])

    def test_no_classification_without_reference_ceiling(self):
        rule = self.contract["reference_ceiling_rule"]
        self.assertEqual(rule["minimum_complete_calibration_taxa_per_procedure_M"], 30)
        self.assertTrue(rule["classification_allowed_only_if_reference_ceiling_exists"])
        unresolved = self.contract["when_reference_ceiling_unavailable"]
        self.assertEqual(unresolved["state"], "paired_crosscheck_calibration_unresolved")
        self.assertTrue(unresolved["descriptive_discordance_may_be_reported"])
        self.assertTrue(unresolved["paired_crosscheck_consistent_may_not_be_emitted"])
        self.assertTrue(unresolved["paired_crosscheck_attention_required_may_not_be_emitted"])

    def test_knockout_waits_for_baseline_pairing_freeze(self):
        self.assertTrue(self.contract["process_knockout_allowed_only_after_baseline_pairing_state_is_frozen"])


if __name__ == "__main__":
    unittest.main()
