import csv
import json
import unittest
from pathlib import Path


class Phase1TerminalAccountingTests(unittest.TestCase):
    def setUp(self):
        self.result = json.loads(
            Path("results/product_b_v5_phase1_feasibility_terminal_v0_1.json").read_text(
                encoding="utf-8"
            )
        )

    def test_all_seven_pairs_are_accounted_once(self):
        pairs = self.result["pairs"]
        self.assertEqual(self.result["pair_count"], 7)
        self.assertEqual(len(pairs), 7)
        ids = [row["pair_id"] for row in pairs]
        self.assertEqual(len(set(ids)), 7)

    def test_no_pair_reached_invariant_layer(self):
        self.assertEqual(self.result["pairs_reaching_invariant_evaluation"], 0)
        self.assertFalse(self.result["invariant_outcomes_opened"])
        self.assertFalse(self.result["negative_control_outcomes_opened"])
        self.assertFalse(self.result["process_knockout_outcomes_opened"])
        self.assertEqual(
            self.result["gate_counts"],
            {
                "unresolved_taxonomy": 2,
                "unresolved_operational_scope": 2,
                "unresolved_sampling": 3,
                "reached_invariant": 0,
            },
        )

    def test_consumed_sampling_pairs_have_terminal_result_files(self):
        for path in (
            "results/product_b_v5_fig001_sampling_terminal_v0_1.json",
            "results/product_b_v5_yuc001_sampling_terminal_v0_1.json",
            "results/product_b_v5_yuc002_sampling_terminal_v0_1.json",
        ):
            self.assertTrue(Path(path).is_file(), path)

    def test_glo003_and_glo004_are_taxonomy_resolved_but_scope_unresolved(self):
        taxonomy_rows = {}
        with Path("registry/obligate_pair_registry_taxonomy_v0_3.csv").open(
            "r", encoding="utf-8", newline=""
        ) as handle:
            for row in csv.DictReader(handle):
                taxonomy_rows[row["pair_id"]] = row
        scope_rows = {}
        with Path("registry/obligate_pair_registry_scope_v0_4.csv").open(
            "r", encoding="utf-8", newline=""
        ) as handle:
            for row in csv.DictReader(handle):
                scope_rows[row["pair_id"]] = row

        for pair_id in ("OPM_GLO_003", "OPM_GLO_004"):
            self.assertEqual(
                taxonomy_rows[pair_id]["pair_taxonomy_state"],
                "eligible_for_sampling_preflight",
            )
            self.assertEqual(
                scope_rows[pair_id]["operational_scope_state"],
                "unresolved_operational_scope",
            )
            self.assertEqual(scope_rows[pair_id]["filter_type"], "")
            self.assertEqual(scope_rows[pair_id]["filter_value"], "")

    def test_terminal_sampling_states_are_not_biological_violations(self):
        for row in self.result["pairs"]:
            self.assertNotEqual(row["terminal_state"], "biological_violation")


if __name__ == "__main__":
    unittest.main()
