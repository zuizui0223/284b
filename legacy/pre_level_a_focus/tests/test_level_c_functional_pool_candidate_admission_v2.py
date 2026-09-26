import csv
import json
from collections import Counter
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_functional_pool_candidate_admission_protocol_v2.json"
REGISTRY = ROOT / "registry" / "level_c_functional_pool_candidate_screen_v2.csv"
HARD_STOP = ROOT / "results" / "product_b_level_c_functional_pool_candidate_hard_stop_v2.json"


class LevelCFunctionalPoolCandidateAdmissionV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.h = json.loads(HARD_STOP.read_text(encoding="utf-8"))
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

    def test_registry_closes_exactly_at_twelve_in_discovery_order(self):
        self.assertEqual(len(self.rows), 12)
        self.assertEqual(
            [int(row["discovery_index"]) for row in self.rows],
            list(range(1, 13)),
        )
        ids = [row["candidate_id"] for row in self.rows]
        self.assertEqual(ids, self.h["candidate_ids_in_frozen_discovery_order"])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(self.h["hard_stop_reached"])
        self.assertTrue(self.h["candidate_hunting_closed_for_v2"])
        self.assertEqual(
            self.h["hard_stop_reason"],
            "maximum_candidates_screened_reached_before_three_admissions",
        )

    def test_zero_candidates_are_fully_admitted(self):
        admitted = [
            row for row in self.rows
            if row["screen_state"] == "fully_admitted_for_later_source_qualification"
        ]
        self.assertEqual(admitted, [])
        self.assertEqual(self.h["fully_admitted_candidates"], 0)
        self.assertFalse(self.h["source_qualification"]["authorized_for_execution_now"])
        self.assertFalse(self.h["source_qualification"]["candidate_source_values_opened"])

    def test_failure_distribution_is_frozen(self):
        counts = Counter(row["screen_state"] for row in self.rows)
        self.assertEqual(counts["blocked_event_function_relation"], 7)
        self.assertEqual(counts["blocked_focal_evidence_independence"], 3)
        self.assertEqual(counts["blocked_operational_space"], 1)
        self.assertEqual(counts["excluded_previously_consumed_or_v1_screened_system"], 1)
        self.assertEqual(dict(counts), {
            key: value
            for key, value in self.h["screen_state_counts"].items()
            if value
        })

    def test_functional_pool_improves_relation_closure_but_not_admission(self):
        g1_pass = [row["candidate_id"] for row in self.rows if row["G1_event_function_relation"] == "pass"]
        self.assertEqual(g1_pass, self.h["functional_pool_diagnostic"]["candidate_ids_passing_G1"])
        self.assertEqual(g1_pass, ["YUFIV2-003", "ORCHV2-006", "CYMDV2-010", "PELTV2-012"])
        g5_blocked = [
            row["candidate_id"] for row in self.rows
            if row["screen_state"] == "blocked_focal_evidence_independence"
        ]
        self.assertEqual(g5_blocked, ["YUFIV2-003", "ORCHV2-006", "CYMDV2-010"])

    def test_v1_system_is_logged_but_cannot_reenter(self):
        first = self.rows[0]
        self.assertEqual(first["candidate_id"], "SMILV2-001")
        self.assertEqual(first["previously_consumed_or_v1_screened"], "true")
        self.assertEqual(first["G7_fresh_endpoint_identity"], "fail")
        self.assertEqual(
            first["screen_state"],
            "excluded_previously_consumed_or_v1_screened_system",
        )

    def test_later_frozen_queries_are_not_opened_after_cap(self):
        self.assertEqual(len(self.h["queries_reached_in_order"]), 2)
        self.assertEqual(len(self.h["queries_not_reached_due_to_hard_stop"]), 2)
        self.assertFalse(self.h["post_cap_policy"]["query_3_or_query_4_candidate_screening_authorized"])
        self.assertFalse(self.h["post_cap_policy"]["replacement_candidates_authorized"])

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
        self.assertFalse(self.h["source_qualification"]["unavailable_interpreted_as_biological_negative"])
        self.assertFalse(self.h["source_qualification"]["missing_interpreted_as_biological_negative"])
        self.assertFalse(self.h["source_qualification"]["zero_without_detection_adequacy_interpreted_as_biological_negative"])

    def test_no_focal_or_cross_role_values_were_opened(self):
        q = self.h["source_qualification"]
        self.assertFalse(q["focal_occurrence_or_interaction_counts_opened"])
        self.assertFalse(q["focal_reproductive_or_developmental_values_opened"])
        self.assertFalse(q["fitted_event_or_function_surfaces_opened"])
        self.assertFalse(q["cross_role_relation_statistics_opened"])
        self.assertFalse(q["level_a_q95_imported"])

    def test_hard_stop_is_nonempirical_and_preserves_ledger(self):
        self.assertFalse(self.h["hard_invariant_opening_authorized"])
        self.assertFalse(self.h["soft_crosscheck_opening_authorized"])
        self.assertFalse(self.h["process_knockout_authorized"])
        self.assertFalse(self.h["counts_as_empirical_evidence"])
        self.assertFalse(self.h["counts_as_empirical_conclusion"])
        self.assertEqual(self.h["empirical_ledger_increment"], 0)
        self.assertEqual(self.h["global_284b_empirical_ledger_after_v2_hard_stop"], 1)

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
