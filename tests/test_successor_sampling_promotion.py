import unittest

from product_b_v5.sampling_promotion import promote_grouped_successor_sampling


class SuccessorSamplingPromotionTests(unittest.TestCase):
    def contract(self):
        return {
            "transport_only_promotion": True,
            "original_canonical_scientific_artifact_count_verified": 0,
            "original_canonical_sampling_jobs_completed_with_scientific_output": 0,
            "required_grouped_result_version": "product_b_same_target_successor_source_mode_sampling_grouped_v0.1",
            "required_canonical_result_version": "product_b_same_target_successor_source_mode_sampling_v0.1",
            "frozen_panel_size": 72,
            "concept_closure_passed_entering_sampling": 48,
            "minimum_complete_taxa_for_calibration": 30,
            "original_canonical_run_id": 34026548240,
            "grouped_transport_run_id": 34028547235,
        }

    def grouped(self, passed=47, unresolved=1):
        rows = []
        for i in range(72):
            if i < passed:
                state = "successor_source_mode_sampling_passed"
                reasons = []
            elif i < passed + unresolved:
                state = "successor_source_mode_sampling_unresolved"
                reasons = ["human_observation_independent_record_floor_failed"]
            else:
                state = "successor_snapshot_species_concept_closure_unresolved"
                reasons = ["snapshot_name_resolves_to_different_current_species"]
            rows.append({"requested_name": f"taxon_{i}", "state": state, "reasons": reasons})
        return {
            "result_version": "product_b_same_target_successor_source_mode_sampling_grouped_v0.1",
            "scientific_contract_equivalent_to_canonical_sampling": True,
            "canonical_result_promoted": False,
            "frozen_panel_size": 72,
            "current_taxonomy_or_snapshot_tuple_not_entering_closure": 0,
            "concept_closure_passed_entering_sampling": 48,
            "source_mode_sampling_passed": passed,
            "source_mode_sampling_unresolved": unresolved,
            "upstream_concept_closure_unresolved": 72 - passed - unresolved,
            "model_fit_would_be_authorized_if_promoted": passed >= 30,
            "results": rows,
            "raw_rows_persisted": False,
            "coordinates_persisted": False,
            "row_identifiers_persisted": False,
            "paired_discordance_opened": False,
            "model_fit_opened": False,
            "historical_key_level_sampling_selection_used": False,
            "replacement_taxa_selected": False,
            "current_layer1_paired_discordance_read": False,
            "process_intervention_outcomes_read": False,
        }

    def test_promotes_without_recomputing_sampling_states(self):
        grouped = self.grouped()
        out = promote_grouped_successor_sampling(grouped, self.contract())
        self.assertEqual(out["source_mode_sampling_passed"], 47)
        self.assertEqual(out["source_mode_sampling_unresolved"], 1)
        self.assertTrue(out["model_fit_authorized"])
        self.assertEqual(out["results"], grouped["results"])
        self.assertTrue(out["promotion_provenance"]["transport_only_promotion"])
        self.assertFalse(out["promotion_provenance"]["sampling_states_recomputed"])

    def test_rejects_nonzero_original_scientific_artifacts(self):
        contract = self.contract()
        contract["original_canonical_scientific_artifact_count_verified"] = 1
        with self.assertRaises(ValueError):
            promote_grouped_successor_sampling(self.grouped(), contract)

    def test_rejects_opened_paired_discordance(self):
        grouped = self.grouped()
        grouped["paired_discordance_opened"] = True
        with self.assertRaises(ValueError):
            promote_grouped_successor_sampling(grouped, self.contract())

    def test_rejects_state_count_mismatch(self):
        grouped = self.grouped()
        grouped["source_mode_sampling_passed"] = 46
        with self.assertRaises(ValueError):
            promote_grouped_successor_sampling(grouped, self.contract())


if __name__ == "__main__":
    unittest.main()
