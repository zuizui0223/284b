import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"incubator"/"frog_chorus_synchrony"

class FrogChorusSynchronyV1Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.claim=json.loads((BASE/"CLAIM_BOUNDARY_V1.json").read_text())
        cls.naamp=json.loads((BASE/"NAAMP_PRIMARY_RECEIPT_V0_1.json").read_text())
        cls.frogid=json.loads((BASE/"FROGID_VALIDATION_RECEIPT_V0_2.json").read_text())
        cls.network=json.loads((BASE/"NAAMP_NETWORK_RECEIPT_V0_1.json").read_text())

    def test_cross_dataset_rain_direction_is_preserved(self):
        self.assertLess(self.naamp["primary"]["beta"],0)
        self.assertTrue(self.naamp["primary"]["frozen_support_rule_pass"])
        self.assertLess(self.frogid["primary"]["beta"],0)
        self.assertTrue(self.frogid["primary"]["support_rule_pass"])

    def test_validation_is_conditional_active_recording(self):
        text=self.frogid["interpretation"].lower()
        self.assertIn("at least one calling", text)
        self.assertIn("species", text)

    def test_pairwise_network_is_negative(self):
        self.assertFalse(self.network["primary"]["support_rule_pass"])
        self.assertGreater(self.network["primary"]["p_value"],0.05)

    def test_causal_overclaim_is_forbidden(self):
        forbidden=" ".join(self.claim["prohibited"]).lower()
        self.assertIn("causal",forbidden)
        self.assertIn("facilitation",forbidden)
        self.assertIn("network rewiring",forbidden)

if __name__=="__main__":
    unittest.main()
