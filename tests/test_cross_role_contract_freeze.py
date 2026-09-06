import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CrossRoleContractFreezeTests(unittest.TestCase):
    def test_general_cross_role_boundary(self):
        contract = json.loads(
            (ROOT / "config/product_b_cross_role_relation_space_contract_v0_1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(contract["same_target_source_calibration_is_separate_controlled_design"])
        self.assertTrue(contract["same_target_source_calibration_may_require_same_estimator_and_same_M"])
        self.assertFalse(contract["cross_role_same_estimator_required"])
        self.assertFalse(contract["cross_role_same_accessible_area_required"])
        self.assertTrue(contract["cross_role_raw_output_scale_comparison_forbidden"])
        self.assertTrue(contract["relation_space_adapter_must_be_frozen_before_focal_relation_outcome"])
        self.assertTrue(contract["same_target_q95_transfer_to_cross_role_relations_forbidden"])
        self.assertIn(
            "prospectively_matched_non_obligate_controls",
            contract["soft_cross_role_calibration_options"],
        )
        self.assertTrue(contract["hard_cross_role_relation_uses_dedicated_invariant"])
        example = contract["plant_pollinator_example"]
        self.assertEqual(example["relation_space_example"], "plant_site_x_flowering_window")
        self.assertTrue(example["raw_adult_plant_occurrence_containment_is_not_assumed_hard"])

    def test_smil001_occurrence_only_evidence_cannot_open_hard_mutual_test(self):
        contract = json.loads(
            (ROOT / "config/product_b_smil001_role_specific_relation_contract_v0_1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(contract["pair_id"], "SMIL001")
        self.assertEqual(contract["estimator_policy"], "role_specific_estimators_allowed")
        self.assertFalse(contract["same_estimator_required"])
        self.assertFalse(contract["same_accessible_area_required"])
        self.assertTrue(contract["raw_distribution_score_comparison_forbidden"])
        self.assertFalse(contract["hard_mutual_invariant_execution_authorized"])
        self.assertFalse(contract["paired_distribution_overlap_execution_authorized_as_hard_test"])
        self.assertFalse(contract["occurrence_outcomes_opened_for_this_new_contract"])
        self.assertFalse(contract["geographic_scope_audit"]["full_range_mutual_constraint_observable"])
        self.assertFalse(contract["geographic_scope_audit"]["taiwan_partner_status_resolved"])

        directions = {row["direction_id"]: row for row in contract["relation_directions"]}
        plant = directions["plant_reproduction_requires_midge"]
        self.assertFalse(plant["adult_plant_occurrence_is_sufficient_dependent_answer"])
        self.assertFalse(plant["midge_occurrence_is_sufficient_required_answer"])
        midge = directions["midge_breeding_requires_host_male_flowers"]
        self.assertFalse(midge["adult_host_occurrence_is_sufficient_required_answer"])
        self.assertFalse(midge["midge_occurrence_is_sufficient_dependent_answer"])


if __name__ == "__main__":
    unittest.main()
