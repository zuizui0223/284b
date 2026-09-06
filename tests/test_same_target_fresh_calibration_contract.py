import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_same_target_fresh_calibration_contract_v0_1.json"
REGISTRY = ROOT / "registry/product_b_same_target_fresh_calibration_candidates_v0_1.csv"
OPENED_IDENTITY = ROOT / "results/product_b_same_target_source_snapshot_identity_v0_1.json"


class FreshSameTargetCalibrationContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        with REGISTRY.open(newline="", encoding="utf-8") as handle:
            self.registry = list(csv.DictReader(handle))
        self.opened = json.loads(OPENED_IDENTITY.read_text(encoding="utf-8"))

    def test_all_36_predeclared_fresh_candidates_are_retained(self):
        self.assertEqual(len(self.registry), 36)
        self.assertEqual(len({row["scientific_name"] for row in self.registry}), 36)
        strata = {}
        for row in self.registry:
            strata.setdefault(row["validation_stratum"], []).append(int(row["candidate_rank"]))
        self.assertEqual(len(strata), 12)
        for ranks in strata.values():
            self.assertEqual(sorted(ranks), [1, 2, 3])
        panel = self.contract["panel_rule"]
        self.assertTrue(panel["use_all_36_predeclared_candidates"])
        self.assertFalse(panel["select_one_per_stratum"])
        self.assertTrue(panel["candidate_rank_may_not_select_or_reorder_taxa"])
        self.assertEqual(panel["minimum_complete_taxa_for_calibration"], 30)

    def test_fresh_panel_is_disjoint_from_the_opened_36_taxa(self):
        fresh = {row["scientific_name"] for row in self.registry}
        opened = {str(row["requested_name"]) for row in self.opened["identity_results"]}
        self.assertEqual(len(opened), 36)
        self.assertTrue(fresh.isdisjoint(opened))

    def test_snapshot_identity_is_species_concept_closure_not_single_key(self):
        closure = self.contract["taxonomy_concept_closure"]
        self.assertFalse(closure["single_snapshot_specieskey_required"])
        self.assertTrue(closure["current_taxonomy_exact_accepted_species_required_before_snapshot_access"])
        self.assertTrue(closure["all_distinct_specieskeys_under_exact_species_name_form_candidate_historical_key_set"])
        self.assertTrue(closure["current_taxonomy_review_attempt_required_for_every_distinct_snapshot_scientific_name"])
        self.assertTrue(closure["completed_current_no_match_for_historical_name_is_audited_not_a_concept_conflict"])
        self.assertTrue(closure["taxonomy_transport_or_parse_failure_makes_review_incomplete_and_fails_closed"])
        self.assertTrue(closure["historical_key_set_frozen_only_after_complete_review_without_explicit_species_conflict"])
        self.assertTrue(closure["current_24_single_key_failures_may_not_be_retroactively_rescued_by_this_rule"])
        self.assertEqual(
            closure["snapshot_taxonomy_fields_allowed"],
            ["species", "specieskey", "taxonkey", "scientificname", "taxonrank"],
        )
        self.assertIn("occurrence_counts", closure["occurrence_counts_coordinates_dates_dataset_ids_and_model_outcomes_forbidden_during_closure"])

    def test_sampling_and_reference_ceiling_cannot_be_relaxed(self):
        sampling = self.contract["source_mode_sampling"]
        self.assertEqual(sampling["minimum_independent_records_per_mode"], 50)
        self.assertEqual(sampling["minimum_unique_10km_cells_per_mode"], 30)
        self.assertEqual(sampling["minimum_effective_cells_per_mode"], 10.0)
        self.assertTrue(sampling["both_modes_must_pass"])
        pairing = self.contract["model_and_pairing"]
        self.assertEqual(pairing["minimum_complete_taxa_per_procedure_M"], 30)
        self.assertEqual(pairing["calibration_quantile"], 0.95)
        self.assertEqual(pairing["quantile_method"], "nearest_rank")
        self.assertTrue(pairing["high_discordance_complete_taxa_may_not_be_dropped"])

    def test_current_layer1_outcomes_cannot_select_the_fresh_panel(self):
        barrier = self.contract["information_barrier"]
        self.assertTrue(barrier["current_12_taxon_layer1_paired_D_may_not_select_taxa"])
        self.assertTrue(barrier["current_12_taxon_layer1_paired_D_may_not_set_fresh_reference_ceiling"])
        self.assertTrue(barrier["process_intervention_outcomes_may_not_select_taxa_or_thresholds"])


if __name__ == "__main__":
    unittest.main()
