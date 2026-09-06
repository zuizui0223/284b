import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_same_target_source_process_intervention_contract_v0_1.json"


class SameTargetProcessInterventionContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_all_six_frozen_domains_are_mandatory(self):
        self.assertEqual(
            self.contract["process_domains"],
            ["thermal", "water", "seasonality_phenology", "energy_productivity", "snow", "wind"],
        )
        self.assertTrue(self.contract["all_six_domains_must_be_evaluated_for_every_structurally_evaluable_baseline_cell"])
        self.assertEqual(self.contract["process_registry"]["predictor_count"], 43)

    def test_intervention_is_on_fixed_surface_without_refit(self):
        intervention = self.contract["intervention_implementation"]
        self.assertEqual(intervention["function"], "score_with_joint_reference_marginalization")
        self.assertFalse(intervention["model_refit_after_intervention"])
        self.assertFalse(intervention["predictor_reselection_after_intervention"])
        self.assertFalse(intervention["regularization_retuning_after_intervention"])
        self.assertFalse(intervention["M_or_background_change_after_intervention"])

    def test_current_panel_cannot_emit_process_necessity(self):
        boundary = self.contract["current_panel_claim_boundary"]
        self.assertEqual(boundary["taxa"], 12)
        self.assertFalse(boundary["calibrated_reference_ceiling_available"])
        self.assertFalse(boundary["process_necessity_label_allowed"])
        self.assertTrue(boundary["descriptive_delta_discordance_allowed"])

    def test_execution_waits_for_frozen_baseline_pairing(self):
        self.assertTrue(self.contract["frozen_before_baseline_paired_discordance_opened"])
        self.assertTrue(self.contract["execution_allowed_only_after_baseline_pairing_is_frozen"])


if __name__ == "__main__":
    unittest.main()
