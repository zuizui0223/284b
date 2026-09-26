import unittest

from product_b_v5.paired_relations import (
    PairedRelationContract,
    PairedRelationKind,
    RelationStrength,
    bidirectional_containment_discordance,
    containment_discordance,
    overlap_discordance,
    validate_paired_relation_contract,
)


class PairedRelationContractTests(unittest.TestCase):
    def test_same_target_independent_source_soft_contract_passes(self):
        contract = PairedRelationContract(
            relation_id="SELF001",
            relation_kind=PairedRelationKind.SAME_TARGET_INDEPENDENT_SOURCE,
            strength=RelationStrength.SOFT_CROSSCHECK,
            answer_a_role="herbarium_occurrence_model",
            answer_b_role="independent_observation_model",
            declared_scale="same_taxon_same_decadal_range_frame",
            external_relation_basis="same biological target under independently sampled observation systems",
            discordance_metric="one_minus_schoener_d",
            reference_ceiling=0.20,
            relation_frozen_before_focal_outcome=True,
            threshold_frozen_before_focal_outcome=True,
            answers_fit_independently=True,
        )
        self.assertEqual(validate_paired_relation_contract(contract), ())

    def test_soft_contract_cannot_set_threshold_after_outcome(self):
        contract = PairedRelationContract(
            relation_id="SELF002",
            relation_kind=PairedRelationKind.SAME_TARGET_INDEPENDENT_SOURCE,
            strength=RelationStrength.SOFT_CROSSCHECK,
            answer_a_role="source_a",
            answer_b_role="source_b",
            declared_scale="same frame",
            external_relation_basis="same target",
            discordance_metric="rank_profile_discordance",
            reference_ceiling=0.25,
            relation_frozen_before_focal_outcome=True,
            threshold_frozen_before_focal_outcome=False,
            answers_fit_independently=True,
        )
        self.assertIn(
            "soft_crosscheck_threshold_not_frozen",
            validate_paired_relation_contract(contract),
        )

    def test_answers_must_be_independent(self):
        contract = PairedRelationContract(
            relation_id="BAD001",
            relation_kind=PairedRelationKind.EXPECTED_SYMMETRIC_CONCORDANCE,
            strength=RelationStrength.SOFT_CROSSCHECK,
            answer_a_role="answer_a",
            answer_b_role="answer_b",
            declared_scale="same frame",
            external_relation_basis="external biology",
            discordance_metric="one_minus_overlap",
            reference_ceiling=0.25,
            relation_frozen_before_focal_outcome=True,
            threshold_frozen_before_focal_outcome=True,
            answers_fit_independently=False,
        )
        self.assertIn(
            "answers_not_independently_fit",
            validate_paired_relation_contract(contract),
        )

    def test_hard_relation_cannot_be_replaced_by_soft_ceiling(self):
        contract = PairedRelationContract(
            relation_id="HARD001",
            relation_kind=PairedRelationKind.MUTUAL_DEPENDENCY,
            strength=RelationStrength.HARD_INVARIANT,
            answer_a_role="partner_x",
            answer_b_role="partner_y",
            declared_scale="reproductive persistence",
            external_relation_basis="bidirectional dependency literature",
            discordance_metric="dedicated_mutual_classifier",
            reference_ceiling=0.20,
            relation_frozen_before_focal_outcome=True,
            threshold_frozen_before_focal_outcome=True,
            answers_fit_independently=True,
        )
        self.assertIn(
            "hard_invariant_must_use_dedicated_classifier",
            validate_paired_relation_contract(contract),
        )


class DiscordanceConversionTests(unittest.TestCase):
    def test_directional_containment_to_discordance(self):
        self.assertAlmostEqual(containment_discordance(0.95), 0.05)
        self.assertAlmostEqual(containment_discordance(0.20), 0.80)

    def test_bidirectional_uses_weaker_direction(self):
        self.assertAlmostEqual(bidirectional_containment_discordance(0.95, 0.90), 0.10)
        self.assertAlmostEqual(bidirectional_containment_discordance(0.95, 0.20), 0.80)

    def test_overlap_to_discordance(self):
        self.assertAlmostEqual(overlap_discordance(0.92), 0.08)


if __name__ == "__main__":
    unittest.main()
