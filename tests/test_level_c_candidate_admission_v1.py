import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_candidate_admission_protocol_v1.json"
REGISTRY = ROOT / "registry" / "level_c_candidate_screen_v1.csv"


class LevelCCandidateAdmissionV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        with REGISTRY.open(newline="", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_protocol_is_frozen_before_search_and_nonempirical(self):
        self.assertEqual(cls := self.p["protocol_state"], "frozen_before_new_candidate_search")
        self.assertFalse(self.p["hard_invariant_opening_authorized"])
        self.assertFalse(self.p["soft_crosscheck_opening_authorized"])
        self.assertFalse(self.p["process_knockout_authorized"])
        self.assertFalse(self.p["counts_as_empirical_evidence"])
        self.assertFalse(self.p["counts_as_empirical_conclusion"])
        self.assertEqual(self.p["empirical_ledger_increment"], 0)
        self.assertEqual(self.p["global_284b_empirical_ledger_at_protocol_freeze"], 1)

    def test_candidate_hunting_is_finite(self):
        r = self.p["candidate_registry_rule"]
        self.assertEqual(r["maximum_candidates_screened"], 12)
        self.assertEqual(r["target_fully_admitted_candidates"], 3)
        self.assertTrue(r["every_screened_candidate_must_be_logged"])
        self.assertTrue(r["failed_candidates_must_remain_in_registry"])
        self.assertTrue(r["candidate_removal_after_occurrence_or_model_inspection_forbidden"])
        self.assertTrue(r["candidate_replacement_after_occurrence_or_model_inspection_forbidden"])

    def test_all_seven_admission_gates_are_required(self):
        gates = self.p["admission_gates"]
        self.assertEqual(set(gates), {f"G{i}_{name}" for i, name in [
            (1, "event_relation"),
            (2, "operational_space"),
            (3, "operational_time"),
            (4, "role_estimands"),
            (5, "focal_evidence_independence"),
            (6, "management_and_intervention_scope"),
            (7, "fresh_endpoint_identity"),
        ]})
        self.assertTrue(all(g["required"] for g in gates.values()))

    def test_forbidden_pre_registry_information_includes_outcome_proxies(self):
        forbidden = set(self.p["forbidden_before_registry_freeze"])
        required = {
            "GBIF_or_iNaturalist_occurrence_counts",
            "focal_occurrence_coordinates",
            "plant_partner_or_host_dependent_overlap_maps",
            "fitted_role_surfaces",
            "cross_role_relation_statistics",
            "Level_A_q95_import_as_cross_role_tolerance",
            "candidate_ranking_by_expected_data_richness",
            "candidate_ranking_by_expected_result_direction",
        }
        self.assertTrue(required.issubset(forbidden))

    def test_source_feasibility_is_not_yet_authorized(self):
        f = self.p["post_registry_source_feasibility"]
        self.assertFalse(f["authorized_now"])
        self.assertTrue(f["occurrence_or_record_counts_may_be_opened_only_after_registry_freeze"])
        self.assertTrue(f["all_fully_admitted_candidates_evaluated_together"])
        self.assertTrue(f["post_feasibility_replacement_candidates_forbidden"])

    def test_registry_starts_empty(self):
        self.assertEqual(self.rows, [])


if __name__ == "__main__":
    unittest.main()
