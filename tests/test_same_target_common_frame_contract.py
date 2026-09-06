import csv
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "config/product_b_same_target_source_common_frame_contract_v0_1.json"
FIT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
TARGET = ROOT / "config/product_b_same_target_source_target_footprint_contract_v0_1.json"
PAIRING = ROOT / "config/product_b_same_target_source_pairing_contract_v0_1.json"
REGISTRY = ROOT / "registry/product_b_same_target_source_identity_pass_taxa_v0_1.csv"


class SameTargetCommonFrameContractTests(unittest.TestCase):
    def test_identity_pass_registry_is_exactly_frozen_twelve(self):
        with REGISTRY.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 12)
        self.assertEqual(len({row["scientific_name"] for row in rows}), 12)
        self.assertTrue(
            all(row["snapshot_identity_state"] == "snapshot_taxonomy_identity_passed" for row in rows)
        )
        digest = hashlib.sha256(REGISTRY.read_bytes()).hexdigest()
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        self.assertEqual(digest, target["focal_registry"]["sha256"])
        self.assertEqual(target["focal_registry"]["taxa_count"], 12)

    def test_shared_frame_is_symmetric_and_not_source_selected(self):
        frame = json.loads(FRAME.read_text(encoding="utf-8"))
        pooling = frame["shared_frame_coordinate_pooling"]
        self.assertTrue(frame["frame_is_shared_between_observation_modes"])
        self.assertTrue(pooling["allowed"])
        self.assertTrue(pooling["source_labels_removed_before_geometry_construction"])
        self.assertTrue(pooling["environmental_values_not_used_to_construct_M"])
        self.assertTrue(pooling["predictions_not_used_to_construct_M"])
        self.assertEqual(frame["M"]["km"], [150, 300, 500])
        self.assertTrue(frame["M"]["all_three_required"])
        self.assertTrue(frame["M"]["post_outcome_M_selection_forbidden"])

    def test_background_matches_frozen_product_a_geometry(self):
        frame = json.loads(FRAME.read_text(encoding="utf-8"))
        background = frame["background"]
        self.assertEqual(background["grid_cell_degrees"], 0.05)
        self.assertEqual(background["background_points_per_taxon_M"], 2000)
        self.assertTrue(background["exclude_all_12_current_focal_taxa_before_target_group_sampling"])
        self.assertTrue(background["same_background_rows_required_for_both_observation_modes_within_taxon_M"])
        self.assertEqual(frame["environment"]["active_predictors_required"], 43)

    def test_model_fit_uses_shared_frame_but_keeps_responses_independent(self):
        fit = json.loads(FIT.read_text(encoding="utf-8"))
        independence = fit["independence_semantics"]
        self.assertEqual(
            fit["input_common_frame_contract"],
            "config/product_b_same_target_source_common_frame_contract_v0_1.json",
        )
        self.assertTrue(fit["same_background_and_M_definition_required_within_taxon_procedure_M"])
        self.assertTrue(independence["cross_mode_response_occurrence_leakage_forbidden"])
        self.assertTrue(independence["cross_mode_prediction_leakage_forbidden"])
        self.assertTrue(independence["shared_source_blind_coordinate_pool_allowed_for_common_M_geometry_only"])
        self.assertEqual(fit["procedure_library"]["procedure_count"], 8)
        self.assertEqual(fit["M_km"], [150, 300, 500])
        self.assertFalse(fit["paired_discordance_access_allowed_during_fit"])
        self.assertFalse(fit["process_knockout_access_allowed_during_fit"])

    def test_target_footprint_is_pre_model_transport_only(self):
        target = json.loads(TARGET.read_text(encoding="utf-8"))
        self.assertEqual(target["snapshot_date"], "2026-08-01")
        self.assertEqual(target["grid_cell_degrees"], 0.05)
        self.assertEqual(target["parallel_chunk_count"], 16)
        self.assertEqual(target["snapshot_shard_count_expected"], 9705)
        self.assertFalse(target["environmental_values_read"])
        self.assertFalse(target["candidate_model_fitting_performed"])
        self.assertFalse(target["paired_discordance_opened"])

    def test_pairing_cannot_classify_without_calibrated_ceiling(self):
        pairing = json.loads(PAIRING.read_text(encoding="utf-8"))
        text = json.dumps(pairing, sort_keys=True)
        self.assertIn("30", text)
        self.assertIn("descriptive", text.lower())
        self.assertFalse(pairing.get("process_knockout_access_allowed_during_pairing", False))


if __name__ == "__main__":
    unittest.main()
