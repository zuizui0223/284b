import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_candidate_admission_protocol_v1.json"
REGISTRY = ROOT / "registry" / "level_c_candidate_screen_v1.csv"
HARD_STOP = ROOT / "results" / "product_b_level_c_candidate_admission_v1_hard_stop.json"


class LevelCCandidateAdmissionV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.h = json.loads(HARD_STOP.read_text(encoding="utf-8"))
        with REGISTRY.open(newline="", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_protocol_is_frozen_before_search_and_nonempirical(self):
        self.assertEqual(self.p["protocol_state"], "frozen_before_new_candidate_search")
        self.assertFalse(self.p["hard_invariant_opening_authorized"])
        self.assertFalse(self.p["soft_crosscheck_opening_authorized"])
        self.assertFalse(self.p["process_knockout_authorized"])
        self.assertFalse(self.p["counts_as_empirical_evidence"])
        self.assertFalse(self.p["counts_as_empirical_conclusion"])
        self.assertEqual(self.p["empirical_ledger_increment"], 0)
        self.assertEqual(self.p["global_284b_empirical_ledger_at_protocol_freeze"], 1)

    def test_candidate_hunting_contract_is_finite(self):
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

    def test_registry_is_exactly_frozen_at_the_twelve_candidate_cap(self):
        limit = self.p["candidate_registry_rule"]["maximum_candidates_screened"]
        self.assertEqual(limit, 12)
        self.assertEqual(len(self.rows), limit)
        self.assertEqual(
            [int(row["discovery_index"]) for row in self.rows],
            list(range(1, limit + 1)),
        )
        ids = [row["candidate_id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, self.h["candidate_ids_in_frozen_discovery_order"])

    def test_registry_uses_only_declared_screen_states_and_gate_values(self):
        allowed_states = set(self.p["screen_states"])
        allowed_gate_values = {"pass", "fail", "not_evaluated"}
        gate_columns = [
            "G1_event_relation",
            "G2_operational_space",
            "G3_operational_time",
            "G4_role_estimands",
            "G5_focal_evidence_independence",
            "G6_management_scope",
            "G7_fresh_endpoint_identity",
        ]
        for row in self.rows:
            self.assertIn(row["screen_state"], allowed_states)
            for column in gate_columns:
                self.assertIn(row[column], allowed_gate_values)

    def test_hard_stop_is_triggered_with_zero_fully_admitted_candidates(self):
        admitted = [
            row for row in self.rows
            if row["screen_state"] == "fully_admitted_for_later_source_feasibility"
        ]
        self.assertEqual(admitted, [])
        self.assertEqual(self.h["screened_candidates"], 12)
        self.assertEqual(self.h["fully_admitted_candidates"], 0)
        self.assertTrue(self.h["hard_stop_reached"])
        self.assertEqual(
            self.h["hard_stop_reason"],
            "maximum_candidates_screened_reached_before_three_admissions",
        )
        self.assertTrue(self.h["candidate_hunting_closed_for_v1"])
        self.assertFalse(self.h["post_registry_source_feasibility_authorized"])

    def test_screening_boundary_is_relation_not_occurrence_availability(self):
        self.assertEqual(
            sum(row["screen_state"] == "blocked_event_relation" for row in self.rows),
            11,
        )
        self.assertEqual(
            sum(row["screen_state"] == "blocked_operational_space" for row in self.rows),
            1,
        )
        self.assertEqual(sum(row["G1_event_relation"] == "pass" for row in self.rows), 1)
        self.assertFalse(self.h["occurrence_or_record_counts_inspected_for_candidate_admission"])
        self.assertFalse(self.h["focal_occurrence_coordinates_inspected_for_candidate_admission"])
        self.assertFalse(self.h["overlap_maps_inspected_for_candidate_admission"])
        self.assertFalse(self.h["fitted_role_surfaces_inspected_for_candidate_admission"])
        self.assertFalse(self.h["cross_role_relation_statistics_opened"])
        self.assertFalse(self.h["level_a_q95_imported"])

    def test_post_cap_promising_candidate_cannot_enter_v1(self):
        ids = {row["candidate_id"] for row in self.rows}
        taxa = " ".join(row["dependent_taxon"] + " " + row["required_taxon"] for row in self.rows)
        self.assertNotIn("GANASPIS", ids)
        self.assertNotIn("Ganaspis kimorum", taxa)
        post = self.h["post_cap_observation"]
        self.assertTrue(post["discovered_after_candidate_index_12"])
        self.assertFalse(post["eligible_for_v1_registry"])
        self.assertFalse(post["v1_gate_scoring_performed"])
        self.assertFalse(post["v1_source_feasibility_performed"])

    def test_hard_stop_receipt_is_nonempirical_and_preserves_ledger(self):
        self.assertFalse(self.h["hard_invariant_opening_authorized"])
        self.assertFalse(self.h["soft_crosscheck_opening_authorized"])
        self.assertFalse(self.h["process_knockout_authorized"])
        self.assertFalse(self.h["counts_as_empirical_evidence"])
        self.assertFalse(self.h["counts_as_empirical_conclusion"])
        self.assertEqual(self.h["empirical_ledger_increment"], 0)
        self.assertEqual(self.h["global_284b_empirical_ledger_after_hard_stop"], 1)


if __name__ == "__main__":
    unittest.main()
