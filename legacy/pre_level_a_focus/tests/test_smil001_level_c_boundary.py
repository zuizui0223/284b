import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "product_b_level_c_smil001_operational_relation_v0_2.json"
MODULE = ROOT / "product_b_v7_3" / "event_relation.py"


class Smil001LevelCBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.module_text = MODULE.read_text(encoding="utf-8")

    def test_candidate_remains_pre_outcome_and_non_empirical(self):
        c = self.contract
        self.assertEqual(
            c["contract_state"],
            "response_blind_operationalization_blocked_before_focal_outcome",
        )
        self.assertFalse(c["focal_occurrence_relation_opening_authorized"])
        self.assertFalse(c["hard_invariant_opening_authorized"])
        self.assertFalse(c["soft_crosscheck_opening_authorized"])
        self.assertFalse(c["process_knockout_authorized"])
        self.assertFalse(c["counts_as_empirical_evidence"])
        self.assertFalse(c["counts_as_empirical_conclusion"])
        self.assertEqual(c["empirical_ledger_increment"], 0)

    def test_only_plant_requires_midge_direction_is_admitted(self):
        c = self.contract
        self.assertEqual(c["constraint_class"], "directional_dependency")
        self.assertEqual(c["authorized_direction"], "X_requires_Y")
        self.assertFalse(c["mutual_obligacy_authorized"])

    def test_exact_2026_site_is_not_borrowed_from_2025_anchor(self):
        d = self.contract["spatial_provenance_decision"]
        self.assertFalse(d["borrow_2025_Higashinakama_coordinate_for_2026_dependency_experiment"])
        self.assertFalse(d["island_level_hard_relation_fallback_authorized"])
        self.assertFalse(d["exact_relation_site_key_frozen"])
        self.assertEqual(d["current_state"], "unresolved_exact_dependency_experiment_site")

    def test_temporal_sources_are_not_collapsed(self):
        d = self.contract["temporal_provenance_decision"]
        self.assertEqual(d["2025_species_flowering_period"], "March_to_August")
        self.assertEqual(d["2026_species_flowering_period"], "May_to_October")
        self.assertFalse(d["single_interchangeable_flowering_window_assumed"])
        self.assertFalse(d["event_specific_relation_window_frozen"])

    def test_raw_occurrence_surfaces_are_not_relabelled_as_event_answers(self):
        c = self.contract
        self.assertFalse(c["role_x_answer_contract"]["generic_adult_occurrence_SDM_sufficient"])
        self.assertFalse(c["role_y_answer_contract"]["generic_midge_occurrence_SDM_sufficient"])
        self.assertFalse(c["relation_space"]["raw_range_overlap_is_hard_invariant"])
        self.assertFalse(c["relation_space"]["raw_suitability_equality_is_required"])
        self.assertFalse(c["level_a_same_target_q95_imported_as_cross_role_tolerance"])

    def test_relation_evidence_cannot_double_as_confirmatory_focal_answer(self):
        g = self.contract["evidence_independence_gate"]
        self.assertFalse(g["external_relation_evidence_may_define_focal_role_answer"])
        self.assertFalse(
            g["2026_pollinator_observations_from_dependency_paper_eligible_as_confirmatory_focal_role_y_answer"]
        )
        self.assertFalse(
            g["2025_interaction_observations_used_to_admit_candidate_eligible_as_confirmatory_focal_role_y_answer"]
        )
        self.assertFalse(
            g["same_published_dataset_may_both_define_hard_relation_and_score_confirmatory_endpoint"]
        )
        self.assertTrue(g["confirmatory_role_x_requires_fresh_or_independent_answer_source"])
        self.assertTrue(g["confirmatory_role_y_requires_fresh_or_independent_answer_source"])
        self.assertEqual(g["current_state"], "unresolved_independent_focal_role_answers")

    def test_event_relation_module_is_pure_and_surface_free(self):
        forbidden = (
            "requests",
            "urllib",
            "subprocess",
            "github",
            "gbif",
            "inat",
            "pandas",
            "numpy",
            "directed_containment(",
            "schoener_d_pair(",
        )
        lowered = self.module_text.lower()
        for token in forbidden:
            self.assertNotIn(token.lower(), lowered)


if __name__ == "__main__":
    unittest.main()
