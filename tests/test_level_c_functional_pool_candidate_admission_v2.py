import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_functional_pool_candidate_admission_protocol_v2.json"
REGISTRY = ROOT / "registry" / "level_c_functional_pool_candidate_screen_v2.csv"


class LevelCFunctionalPoolCandidateAdmissionV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        with REGISTRY.open(newline="", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_protocol_is_frozen_before_search_and_nonempirical(self):
        self.assertEqual(self.p["protocol_state"], "frozen_before_any_v2_candidate_search")
        self.assertEqual(self.p["hard_relation"], "E(k)_implies_F(k)")
        self.assertTrue(self.p["candidate_search_authorized_after_this_protocol_freeze"])
        self.assertFalse(self.p["focal_data_opening_authorized_before_registry_freeze"])
        self.assertFalse(self.p["hard_invariant_opening_authorized"])
        self.assertFalse(self.p["soft_crosscheck_opening_authorized"])
        self.assertFalse(self.p["process_knockout_authorized"])
        self.assertFalse(self.p["counts_as_empirical_evidence"])
        self.assertFalse(self.p["counts_as_empirical_conclusion"])
        self.assertEqual(self.p["empirical_ledger_increment"], 0)
        self.assertEqual(self.p["global_284b_empirical_ledger_at_protocol_freeze"], 1)

    def test_function_is_not_relabelled_occurrence(self):
        policy = self.p["external_source_policy"]
        self.assertFalse(policy["generic_occurrence_or_suitability_sufficient_as_functional_support"])
        self.assertFalse(policy["generic_occurrence_or_suitability_sufficient_as_functional_absence"])
        self.assertFalse(policy["zero_observed_service_without_detection_adequacy_is_functional_absence"])
        self.assertFalse(policy["relation_defining_observations_may_score_focal_endpoint"])

    def test_candidate_hunting_stays_finite(self):
        rule = self.p["candidate_registry_rule"]
        self.assertEqual(rule["maximum_candidates_screened"], 12)
        self.assertEqual(rule["target_fully_admitted_candidates"], 3)
        self.assertTrue(rule["every_screened_candidate_must_be_logged"])
        self.assertTrue(rule["failed_candidates_must_remain_in_registry"])
        self.assertTrue(rule["v1_screened_system_reentry_forbidden"])
        self.assertTrue(rule["candidate_replacement_after_source_or_model_inspection_forbidden"])

    def test_all_seven_admission_gates_remain_required(self):
        expected = {
            "G1_event_function_relation",
            "G2_operational_space",
            "G3_operational_time",
            "G4_role_estimands",
            "G5_focal_evidence_independence",
            "G6_management_and_intervention_scope",
            "G7_fresh_endpoint_identity",
        }
        self.assertEqual(set(self.p["admission_gates"]), expected)
        self.assertTrue(all(g["required"] for g in self.p["admission_gates"].values()))

    def test_v2_registry_was_empty_at_protocol_freeze(self):
        self.assertEqual(self.rows, [])

    def test_source_qualification_cannot_turn_unavailable_into_negative(self):
        sq = self.p["post_registry_source_qualification"]
        self.assertTrue(sq["authorized_only_after_registry_freeze"])
        self.assertTrue(sq["contract_must_be_frozen_before_opening_candidate_source_values"])
        self.assertTrue(sq["all_fully_admitted_candidates_evaluated_together"])
        self.assertTrue(sq["post_qualification_replacement_candidates_forbidden"])
        self.assertFalse(sq["unavailable_is_biological_negative"])
        self.assertFalse(sq["inadequate_is_biological_negative"])
        self.assertFalse(sq["missing_is_biological_negative"])
        self.assertFalse(sq["zero_without_prespecified_detection_adequacy_is_biological_negative"])

    def test_pre_registry_forbidden_information_includes_focal_function_values(self):
        forbidden = set(self.p["forbidden_before_registry_freeze"])
        required = {
            "GBIF_or_iNaturalist_occurrence_counts",
            "focal_occurrence_coordinates",
            "focal_visit_or_interaction_record_values",
            "focal_reproductive_or_developmental_outcome_values",
            "provider_member_or_function_overlap_maps",
            "fitted_event_or_function_surfaces",
            "cross_role_relation_statistics",
            "Level_A_q95_import_as_cross_role_tolerance",
        }
        self.assertTrue(required.issubset(forbidden))


if __name__ == "__main__":
    unittest.main()
