import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"


class SameTargetSourceModelFitContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_only_sampling_passed_taxa_may_enter(self):
        self.assertTrue(self.contract["only_source_mode_sampling_passed_taxa_may_enter"])
        self.assertTrue(self.contract["sampling_unresolved_taxa_may_not_be_replaced"])

    def test_observation_modes_are_fit_independently(self):
        self.assertEqual(
            self.contract["observation_modes"],
            ["PRESERVED_SPECIMEN", "HUMAN_OBSERVATION"],
        )
        self.assertTrue(self.contract["fits_must_be_independent_between_observation_modes"])
        self.assertTrue(self.contract["cross_mode_occurrence_leakage_forbidden"])
        self.assertTrue(self.contract["cross_mode_prediction_leakage_forbidden"])

    def test_frozen_procedure_and_M_grid_are_not_selection_targets(self):
        self.assertEqual(self.contract["M_km"], [150, 300, 500])
        self.assertTrue(self.contract["M_is_sensitivity_grid_not_selection_target"])
        library = self.contract["procedure_library"]
        self.assertEqual(library["procedure_count"], 8)
        self.assertEqual(
            library["strategies"],
            ["all", "vif", "predictive_forward", "niche_forward"],
        )
        self.assertTrue(self.contract["post_outcome_procedure_selection_forbidden"])
        self.assertTrue(self.contract["post_outcome_M_selection_forbidden"])

    def test_discordance_and_knockout_are_closed_during_fit(self):
        self.assertFalse(self.contract["paired_discordance_access_allowed_during_fit"])
        self.assertFalse(self.contract["process_knockout_access_allowed_during_fit"])
        self.assertTrue(self.contract["prediction_surfaces_must_be_sealed_before_pairing"])


if __name__ == "__main__":
    unittest.main()
