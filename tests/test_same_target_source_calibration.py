import csv
import json
from pathlib import Path
import unittest

from product_b_v5.observation_modes import (
    SameTargetObservationSplit,
    validate_same_target_observation_split,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_same_target_source_calibration_contract_v0_1.json"
PANEL = ROOT / "registry/product_b_same_target_source_calibration_taxa_v0_1.csv"


class SameTargetObservationSplitTests(unittest.TestCase):
    def test_frozen_modes_are_disjoint_and_independent(self):
        split = SameTargetObservationSplit(
            taxon_name="Capsella bursa-pastoris",
            partition_field="basisofrecord",
            mode_a="PRESERVED_SPECIMEN",
            mode_b="HUMAN_OBSERVATION",
            same_snapshot=True,
            same_spatial_temporal_frame=True,
            answers_fit_independently=True,
        )
        self.assertEqual(validate_same_target_observation_split(split), ())

    def test_prediction_leakage_invalidates_split(self):
        split = SameTargetObservationSplit(
            taxon_name="Capsella bursa-pastoris",
            partition_field="basisofrecord",
            mode_a="PRESERVED_SPECIMEN",
            mode_b="HUMAN_OBSERVATION",
            same_snapshot=True,
            same_spatial_temporal_frame=True,
            answers_fit_independently=True,
            cross_mode_prediction_leakage=True,
        )
        self.assertIn(
            "cross_mode_prediction_leakage",
            validate_same_target_observation_split(split),
        )


class CalibrationFreezeTests(unittest.TestCase):
    def test_contract_keeps_calibration_nonconfirmatory(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertFalse(contract["confirmatory_claims_allowed_for_calibration_panel"])
        self.assertEqual(contract["observation_mode_a"], "PRESERVED_SPECIMEN")
        self.assertEqual(contract["observation_mode_b"], "HUMAN_OBSERVATION")
        self.assertEqual(contract["reference_ceiling_rule"]["quantile"], 0.95)
        self.assertEqual(contract["reference_ceiling_rule"]["quantile_method"], "nearest_rank")
        self.assertEqual(
            contract["reference_ceiling_rule"]["minimum_complete_calibration_taxa_per_procedure_M"],
            30,
        )
        self.assertTrue(
            contract["reference_ceiling_rule"]["calibrate_separate_ceiling_for_each_procedure_and_M"]
        )
        procedure = contract["procedure_library_source"]
        self.assertEqual(procedure["procedure_count"], 8)
        self.assertEqual(procedure["strategies"], ["all", "vif", "predictive_forward", "niche_forward"])
        self.assertEqual(contract["shared_frame_source"]["M_km"], [150, 300, 500])
        floors = contract["source_specific_sampling_floors"]
        self.assertEqual(
            (
                floors["minimum_independent_records"],
                floors["minimum_unique_10km_cells"],
                floors["minimum_effective_10km_cells"],
            ),
            (50, 30, 10.0),
        )
        source = contract["calibration_panel_source"]
        self.assertEqual(source["candidate_count"], 36)
        self.assertEqual(source["validation_strata"], 12)
        self.assertTrue(source["selection_predates_product_b_cross_source_discordance"])
        self.assertTrue(source["all_36_candidates_enter_preflight"])

    def test_frozen_registry_has_36_unopened_candidates(self):
        with PANEL.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 36)
        self.assertEqual(len({row["validation_stratum"] for row in rows}), 12)
        for stratum in {row["validation_stratum"] for row in rows}:
            ranks = sorted(
                int(row["candidate_rank"])
                for row in rows
                if row["validation_stratum"] == stratum
            )
            self.assertEqual(ranks, [1, 2, 3])
        self.assertTrue(all(row["snapshot_taxonomy_state"] == "unopened" for row in rows))
        self.assertTrue(all(row["mode_sampling_state"] == "unopened" for row in rows))
        self.assertTrue(all(row["paired_discordance_state"] == "unopened" for row in rows))


if __name__ == "__main__":
    unittest.main()
