import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_source_architecture_protocol_v3.json"
REGISTRY = ROOT / "registry" / "level_c_source_architecture_candidate_screen_v3.csv"


class LevelCSourceArchitectureV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        with REGISTRY.open(newline="", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_protocol_is_prospective_and_nonempirical(self):
        self.assertEqual(
            self.p["protocol_state"],
            "frozen_before_any_v3_candidate_search_or_focal_value_access",
        )
        self.assertEqual(self.p["hard_relation"], "E(k)_implies_F(k)")
        self.assertTrue(self.p["candidate_search_authorized_after_this_freeze"])
        self.assertFalse(self.p["focal_value_opening_authorized_before_registry_freeze"])
        self.assertFalse(self.p["counts_as_empirical_evidence"])
        self.assertFalse(self.p["counts_as_empirical_conclusion"])
        self.assertEqual(self.p["empirical_ledger_increment"], 0)
        self.assertEqual(self.p["global_284b_empirical_ledger_at_protocol_freeze"], 1)

    def test_candidate_identity_requires_three_preseparated_channels(self):
        a = self.p["three_channel_architecture"]
        self.assertFalse(a["R_may_equal_X"])
        self.assertFalse(a["R_may_equal_Y"])
        self.assertFalse(a["X_may_equal_Y"])
        self.assertFalse(a["relation_defining_observations_may_score_confirmatory_endpoint"])

    def test_independence_is_about_observation_stream_not_citation_label(self):
        s = self.p["source_identity_rule"]
        self.assertTrue(s["independence_requires_distinct_observation_generation_or_sampling_stream"])
        self.assertFalse(s["different_publication_of_same_underlying_observations_is_independent"])
        self.assertFalse(s["different_model_fit_to_same_underlying_observations_is_independent"])
        self.assertFalse(s["author_overlap_alone_invalidates_independence"])

    def test_finite_hard_stop_is_preserved(self):
        r = self.p["candidate_registry_rule"]
        self.assertEqual(r["maximum_candidates_screened"], 12)
        self.assertEqual(r["target_architecture_qualified_candidates"], 3)
        self.assertTrue(r["every_screened_candidate_must_be_logged"])
        self.assertTrue(r["failed_candidates_must_remain_in_registry"])
        self.assertTrue(r["v1_or_v2_screened_system_reentry_forbidden"])
        self.assertTrue(r["replacement_after_value_or_availability_inspection_forbidden"])

    def test_all_nine_prevalue_gates_are_frozen(self):
        self.assertEqual(
            set(self.p["prevalue_architecture_gates"]),
            {
                "A1_hard_relation_source",
                "A2_event_answer_source_identity",
                "A3_function_answer_source_identity",
                "A4_three_way_independence",
                "A5_common_operational_space",
                "A6_common_operational_time",
                "A7_estimand_alignment",
                "A8_management_scope",
                "A9_fresh_endpoint_identity",
            },
        )

    def test_v3_registry_is_empty_at_protocol_freeze(self):
        self.assertEqual(self.rows, [])

    def test_unavailable_cannot_become_biological_negative(self):
        q = self.p["post_registry_source_qualification"]
        for key in [
            "unavailable_is_biological_negative",
            "missing_is_biological_negative",
            "retrieval_failure_is_biological_negative",
            "inadequate_detection_is_biological_negative",
            "zero_without_prespecified_detection_adequacy_is_biological_negative",
        ]:
            self.assertFalse(q[key])
        self.assertIn("unavailable", q["terminal_nonbiological_states"])
        self.assertIn("insufficient_detection_adequacy", q["terminal_nonbiological_states"])

    def test_pre_registry_forbids_focal_values_and_level_a_tolerance_import(self):
        forbidden = set(self.p["forbidden_before_registry_freeze"])
        self.assertTrue({
            "focal_record_counts",
            "focal_coordinates",
            "focal_visit_or_interaction_values",
            "focal_reproductive_or_developmental_values",
            "fitted_event_or_function_surfaces",
            "cross_role_statistics",
            "Level_A_q95_import_as_cross_role_tolerance",
        }.issubset(forbidden))


if __name__ == "__main__":
    unittest.main()
