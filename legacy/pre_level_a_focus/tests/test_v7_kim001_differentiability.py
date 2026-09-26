import csv
import json
from pathlib import Path
import unittest

from product_b_v7.differentiability import (
    FORBIDDEN_VALUE_COLUMNS,
    SAFE_STRUCTURE_COLUMNS,
    evaluate_structural_differentiability,
    parse_sanitized_structure_rows,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config/product_b_v7_kim001_model_structure_source_v0_1.json"
RESULT = ROOT / "results/product_b_v7_kim001_structural_differentiability_v0_1.json"
OVERLAY = ROOT / "config/product_b_v7_differentiability_overlay_v0_1.json"
PROCESS = ROOT / "config/product_b_v7_product_a_process_registry_snapshot_v0_1.csv"


class KIM001StructuralDifferentiabilityTests(unittest.TestCase):
    def test_source_is_exact_presealed_artifact_and_occurrence_blind(self):
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(source["source_run_id"], 33155971954)
        self.assertEqual(source["source_artifact_id"], 9686651663)
        self.assertEqual(
            source["source_artifact_sha256"],
            "747ccdb6d100df22e993e14acf551e3208a0616584f699c6877ee22662f80519",
        )
        self.assertEqual(tuple(source["allowed_structural_columns"]), SAFE_STRUCTURE_COLUMNS)
        self.assertTrue(set(source["forbidden_value_columns"]).issubset(FORBIDDEN_VALUE_COLUMNS))
        self.assertFalse(source["kim001_occurrence_reads_performed"])
        self.assertFalse(source["kim001_invariant_reads_performed"])
        self.assertFalse(source["source_boundary"]["sealed_occurrence_environments_read_by_source"])

    def test_committed_structural_result_passes_without_value_reads(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(result["state"], "structural_differentiability_preflight_passed")
        self.assertEqual(result["structure"]["candidate_fold_member_count"], 32)
        self.assertEqual(result["structure"]["unique_procedure_count"], 8)
        self.assertEqual(result["structure"]["distinct_selected_predictor_signature_count"], 20)
        self.assertEqual(result["sanitizer"]["forbidden_value_columns_emitted"], [])
        self.assertFalse(result["sanitizer"]["product_a_score_or_recovery_values_emitted"])
        self.assertFalse(result["candidate_scores_read_for_this_preflight"])
        self.assertFalse(result["ecological_recovery_values_read_for_this_preflight"])
        self.assertFalse(result["kim001_occurrence_reads_performed"])
        self.assertFalse(result["kim001_invariant_reads_performed"])
        statuses = result["process_knockout_structure"]
        self.assertEqual(
            {row["process"] for row in statuses},
            {"thermal", "water", "seasonality_phenology", "energy_productivity", "snow", "wind"},
        )
        self.assertTrue(all(row["admissible"] for row in statuses))
        self.assertTrue(all(row["admissible_member_count"] > 0 for row in statuses))

    def test_two_stage_overlay_keeps_post_fit_gate_closed_before_invariant(self):
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertTrue(overlay["frozen_before_any_v7_occurrence_or_invariant_read"])
        stage1 = overlay["stage_1_pre_occurrence"]
        stage2 = overlay["stage_2_post_host_fit_pre_invariant"]
        self.assertEqual(stage1["minimum_structural_members"], 2)
        self.assertEqual(stage1["minimum_distinct_selected_predictor_signatures"], 2)
        self.assertFalse(stage1["candidate_scores_may_be_read"])
        self.assertEqual(stage2["minimum_adequate_members"], 2)
        self.assertEqual(stage2["minimum_distinct_selected_predictor_signatures_among_adequate_members"], 2)
        self.assertFalse(stage2["invariant_reads_allowed_if_failed"])

    def test_synthetic_sanitized_members_pass_and_metric_column_fails(self):
        base = {
            "fold": "0",
            "candidate": "a",
            "procedure": "a",
            "strategy": "all",
            "model": "m",
            "selected_predictors": "bio1,bio12",
            "selected_ecological_predictors": "bio1,bio12",
            "n_predictors": "2",
            "n_ecological_predictors": "2",
            "taxon": "T",
            "M": "buffer_300km",
            "group": "base",
            "excluded_process_domain": "",
        }
        other = dict(base)
        other.update(
            fold="1",
            candidate="b",
            procedure="b",
            selected_predictors="bio3,bio12",
            selected_ecological_predictors="bio3,bio12",
        )
        members = parse_sanitized_structure_rows(
            (base, other), expected_taxon="T", expected_M="buffer_300km"
        )
        result = evaluate_structural_differentiability(
            members,
            {"bio1": "thermal", "bio3": "seasonality_phenology", "bio12": "water"},
            ("thermal", "water", "seasonality_phenology"),
        )
        self.assertTrue(result.passed)
        bad = dict(base)
        bad["presence_rank"] = "0.9"
        with self.assertRaisesRegex(ValueError, "schema changed"):
            parse_sanitized_structure_rows(
                (bad,), expected_taxon="T", expected_M="buffer_300km"
            )

    def test_process_snapshot_is_six_domain_fixed_registry(self):
        with PROCESS.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        domains = {row["empirical_process_domain"] for row in rows}
        self.assertEqual(
            domains,
            {"thermal", "water", "seasonality_phenology", "energy_productivity", "snow", "wind"},
        )
        self.assertEqual(len({row["predictor"] for row in rows}), len(rows))


if __name__ == "__main__":
    unittest.main()
