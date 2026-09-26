import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "config" / "product_b_level_c_source_architecture_protocol_v3.json"
REGISTRY = ROOT / "registry" / "level_c_source_architecture_candidate_screen_v3.csv"
FREEZE = ROOT / "results" / "product_b_level_c_source_architecture_protocol_freeze_v3.json"
HARD_STOP = ROOT / "results" / "product_b_level_c_source_architecture_hard_stop_v3.json"
QUAL = ROOT / "results" / "product_b_level_c_source_qualification_v3.json"
DEVIATION = ROOT / "results" / "product_b_level_c_v3_postcap_query_deviation.json"


class LevelCSourceArchitectureV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.f = json.loads(FREEZE.read_text(encoding="utf-8"))
        cls.h = json.loads(HARD_STOP.read_text(encoding="utf-8"))
        cls.q = json.loads(QUAL.read_text(encoding="utf-8"))
        cls.d = json.loads(DEVIATION.read_text(encoding="utf-8"))
        with REGISTRY.open(newline="", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_protocol_was_frozen_prospectively(self):
        self.assertEqual(self.p["protocol_state"], "frozen_before_any_v3_candidate_search_or_focal_value_access")
        self.assertEqual(self.f["protocol_commit"], "0ff549db6d856f184262f5f0325368a0db064b9e")
        self.assertEqual(self.f["empty_registry_commit"], "3b108228e6efe6f3aba3f8f8ac5f9d0dbaa0e8a8")
        self.assertTrue(self.f["protocol_frozen_before_candidate_search"])
        self.assertTrue(self.f["registry_empty_at_freeze"])
        self.assertFalse(self.f["focal_values_opened_before_freeze"])

    def test_three_channel_source_identity_remains_strict(self):
        a = self.p["three_channel_architecture"]
        self.assertFalse(a["R_may_equal_X"])
        self.assertFalse(a["R_may_equal_Y"])
        self.assertFalse(a["X_may_equal_Y"])
        s = self.p["source_identity_rule"]
        self.assertTrue(s["independence_requires_distinct_observation_generation_or_sampling_stream"])
        self.assertFalse(s["different_publication_of_same_underlying_observations_is_independent"])
        self.assertFalse(s["different_model_fit_to_same_underlying_observations_is_independent"])

    def test_finite_screen_closed_at_exact_cap(self):
        rule = self.p["candidate_registry_rule"]
        self.assertEqual(rule["maximum_candidates_screened"], 12)
        self.assertEqual(rule["target_architecture_qualified_candidates"], 3)
        self.assertEqual(len(self.rows), 12)
        self.assertEqual([int(r["discovery_index"]) for r in self.rows], list(range(1, 13)))
        self.assertTrue(self.h["hard_stop_reached"])
        self.assertTrue(self.h["candidate_hunting_closed_for_v3"])
        self.assertEqual(self.h["architecture_qualified_candidates"], 2)
        self.assertEqual(self.h["qualified_candidate_ids"], ["CREMV3-007", "BELV3-012"])

    def test_qualified_rows_pass_all_architecture_gates(self):
        gates = [
            "A1_hard_relation_source", "A2_event_answer_source_identity",
            "A3_function_answer_source_identity", "A4_three_way_independence",
            "A5_common_operational_space", "A6_common_operational_time",
            "A7_estimand_alignment", "A8_management_scope", "A9_fresh_endpoint_identity",
        ]
        qualified = [r for r in self.rows if r["screen_state"] == "architecture_qualified_for_source_qualification"]
        self.assertEqual([r["candidate_id"] for r in qualified], ["CREMV3-007", "BELV3-012"])
        for row in qualified:
            self.assertTrue(all(row[g] == "pass" for g in gates))

    def test_postcap_query4_deviation_is_quarantined(self):
        self.assertTrue(self.d["hard_stop_already_reached"])
        self.assertFalse(self.d["query4_candidate_admission_performed"])
        self.assertFalse(self.d["query4_candidate_gate_scoring_performed"])
        self.assertFalse(self.d["query4_source_qualification_performed"])
        self.assertFalse(self.d["query4_focal_values_opened"])
        self.assertFalse(self.d["query4_candidate_replacement_performed"])
        self.assertTrue(self.d["query4_results_quarantined_from_v3"])
        self.assertFalse(self.h["query4_candidate_admission_performed"])
        self.assertTrue(self.h["postcap_query4_metadata_search_deviation_logged"])

    def test_source_qualification_does_not_convert_unresolved_to_negative(self):
        self.assertEqual(self.q["qualified_for_frozen_endpoint_opening"], [])
        for cid in ["CREMV3-007", "BELV3-012"]:
            r = self.q["candidate_results"][cid]
            self.assertEqual(r["terminal_state"], "unresolved_absence_adequacy")
            self.assertFalse(r["hard_endpoint_opening_authorized"])
            self.assertFalse(r["biological_negative"])
        self.assertFalse(self.q["unavailable_or_unresolved_interpreted_as_biological_negative"])
        self.assertFalse(self.q["candidate_replacement_authorized"])
        self.assertFalse(self.q["new_candidate_search_authorized"])

    def test_empirical_ledger_remains_one_everywhere(self):
        self.assertEqual(self.p["global_284b_empirical_ledger_at_protocol_freeze"], 1)
        self.assertEqual(self.f["global_284b_empirical_ledger_at_freeze"], 1)
        self.assertEqual(self.h["global_284b_empirical_ledger_after_architecture_screen"], 1)
        self.assertEqual(self.q["global_284b_empirical_ledger_after_source_qualification"], 1)
        self.assertEqual(self.d["global_284b_empirical_ledger_after_receipt"], 1)
        self.assertFalse(self.q["counts_as_empirical_conclusion"])
        self.assertFalse(self.h["counts_as_empirical_conclusion"])


if __name__ == "__main__":
    unittest.main()
