import unittest

from product_b_v5.paired_relations import (
    PairedRelationContract,
    PairedRelationKind,
    RelationStrength,
)
from product_b_v5.relation_space import (
    AdaptedAnswer,
    AnswerEstimand,
    EcologicalAnswerContract,
    EstimatorPolicy,
    RelationSpaceContract,
    RelationSpaceKind,
    align_adapted_answers,
    directional_containment_on_relation_space,
    validate_paired_relation_with_space,
    validate_relation_space_contract,
)


def answer(
    *,
    answer_id: str,
    role: str,
    target: str,
    estimator_id: str,
    estimator_family: str,
    estimand: AnswerEstimand,
    m: str,
) -> EcologicalAnswerContract:
    return EcologicalAnswerContract(
        answer_id=answer_id,
        role=role,
        biological_target=target,
        estimator_id=estimator_id,
        estimator_family=estimator_family,
        estimand=estimand,
        spatial_unit="10-km cells",
        temporal_unit="season",
        accessible_area_semantics=m,
        observation_process="independent occurrence evidence",
        estimator_frozen_before_outcome=True,
    )


class RelationSpaceContractTests(unittest.TestCase):
    def test_same_target_source_calibration_requires_common_estimator_and_M(self):
        a = answer(
            answer_id="plant_specimen",
            role="preserved_specimen",
            target="Plant species A",
            estimator_id="all|logit_l2_C1_degree2",
            estimator_family="sdmr_product_a_v2_7_1",
            estimand=AnswerEstimand.REALIZED_ENVIRONMENTAL_SUPPORT,
            m="shared M=150 km",
        )
        b = answer(
            answer_id="plant_observation",
            role="human_observation",
            target="Plant species A",
            estimator_id="all|logit_l2_C1_degree2",
            estimator_family="sdmr_product_a_v2_7_1",
            estimand=AnswerEstimand.REALIZED_ENVIRONMENTAL_SUPPORT,
            m="shared M=150 km",
        )
        contract = RelationSpaceContract(
            relation_id="SELF",
            relation_kind=PairedRelationKind.SAME_TARGET_INDEPENDENT_SOURCE,
            estimator_policy=EstimatorPolicy.SAME_TARGET_COMMON_ESTIMATOR,
            answer_a=a,
            answer_b=b,
            relation_space_kind=RelationSpaceKind.SAME_TARGET_SUPPORT,
            relation_keys_semantics="same frozen background rows",
            relation_event_semantics="same taxon realized environmental support",
            answer_a_projection="normalize specimen prediction on shared rows",
            answer_b_projection="normalize observation prediction on shared rows",
            same_accessible_area_required=True,
            raw_output_scale_comparison_allowed=False,
            adapter_frozen_before_focal_outcome=True,
        )
        self.assertEqual(validate_relation_space_contract(contract), ())

    def test_cross_species_dependency_allows_different_estimators_and_M(self):
        plant = answer(
            answer_id="plant_reproduction",
            role="plant",
            target="obligately pollinated plant",
            estimator_id="plant_reproductive_support_v1",
            estimator_family="sdmr_or_demographic_model",
            estimand=AnswerEstimand.REPRODUCTIVE_SUPPORT,
            m="plant establishment/reproductive domain",
        )
        pollinator = answer(
            answer_id="pollinator_visitation",
            role="pollinator",
            target="obligate pollinator",
            estimator_id="pollinator_reachability_v1",
            estimator_family="eog_or_dynamic_movement_model",
            estimand=AnswerEstimand.VISITATION_SUPPORT,
            m="pollinator movement-accessible domain",
        )
        contract = RelationSpaceContract(
            relation_id="PLANT_POLLINATOR",
            relation_kind=PairedRelationKind.DIRECTIONAL_DEPENDENCY,
            estimator_policy=EstimatorPolicy.ROLE_SPECIFIC_ESTIMATORS_ALLOWED,
            answer_a=plant,
            answer_b=pollinator,
            relation_space_kind=RelationSpaceKind.INTERACTION_OPPORTUNITY,
            relation_keys_semantics="plant site x flowering window",
            relation_event_semantics="pollinator-mediated reproductive opportunity",
            answer_a_projection="project plant reproductive demand/support to flowering opportunities",
            answer_b_projection="project pollinator visitation/reachability to the same flowering opportunities",
            same_accessible_area_required=False,
            raw_output_scale_comparison_allowed=False,
            adapter_frozen_before_focal_outcome=True,
        )
        self.assertEqual(validate_relation_space_contract(contract), ())

        relation = PairedRelationContract(
            relation_id="PLANT_POLLINATOR",
            relation_kind=PairedRelationKind.DIRECTIONAL_DEPENDENCY,
            strength=RelationStrength.HARD_INVARIANT,
            answer_a_role="plant",
            answer_b_role="pollinator",
            declared_scale="plant site x flowering window",
            external_relation_basis="obligate pollination evidence",
            discordance_metric="dedicated_directional_classifier",
            reference_ceiling=None,
            relation_frozen_before_focal_outcome=True,
            threshold_frozen_before_focal_outcome=True,
            answers_fit_independently=True,
        )
        self.assertEqual(validate_paired_relation_with_space(relation, contract), ())

    def test_combined_validator_rejects_relation_space_kind_mismatch(self):
        plant = answer(
            answer_id="p",
            role="plant",
            target="plant",
            estimator_id="pmodel",
            estimator_family="plant_model",
            estimand=AnswerEstimand.REPRODUCTIVE_SUPPORT,
            m="plant M",
        )
        animal = answer(
            answer_id="a",
            role="pollinator",
            target="pollinator",
            estimator_id="amodel",
            estimator_family="movement_model",
            estimand=AnswerEstimand.VISITATION_SUPPORT,
            m="pollinator M",
        )
        space = RelationSpaceContract(
            relation_id="PAIR",
            relation_kind=PairedRelationKind.DIRECTIONAL_DEPENDENCY,
            estimator_policy=EstimatorPolicy.ROLE_SPECIFIC_ESTIMATORS_ALLOWED,
            answer_a=plant,
            answer_b=animal,
            relation_space_kind=RelationSpaceKind.INTERACTION_OPPORTUNITY,
            relation_keys_semantics="site x flowering window",
            relation_event_semantics="pollination",
            answer_a_projection="plant projection",
            answer_b_projection="pollinator projection",
            same_accessible_area_required=False,
            raw_output_scale_comparison_allowed=False,
            adapter_frozen_before_focal_outcome=True,
        )
        relation = PairedRelationContract(
            relation_id="PAIR",
            relation_kind=PairedRelationKind.MUTUAL_DEPENDENCY,
            strength=RelationStrength.HARD_INVARIANT,
            answer_a_role="plant",
            answer_b_role="pollinator",
            declared_scale="site x flowering window",
            external_relation_basis="external biology",
            discordance_metric="dedicated_mutual_classifier",
            reference_ceiling=None,
            relation_frozen_before_focal_outcome=True,
            threshold_frozen_before_focal_outcome=True,
            answers_fit_independently=True,
        )
        self.assertIn(
            "paired_relation_and_relation_space_kinds_differ",
            validate_paired_relation_with_space(relation, space),
        )

    def test_cross_species_relation_cannot_require_one_universal_M(self):
        plant = answer(
            answer_id="p",
            role="plant",
            target="plant",
            estimator_id="pmodel",
            estimator_family="plant_model",
            estimand=AnswerEstimand.PERSISTENCE_SUPPORT,
            m="plant M",
        )
        animal = answer(
            answer_id="a",
            role="animal",
            target="pollinator",
            estimator_id="amodel",
            estimator_family="movement_model",
            estimand=AnswerEstimand.REACHABILITY_SUPPORT,
            m="animal M",
        )
        contract = RelationSpaceContract(
            relation_id="BAD_M",
            relation_kind=PairedRelationKind.DIRECTIONAL_DEPENDENCY,
            estimator_policy=EstimatorPolicy.ROLE_SPECIFIC_ESTIMATORS_ALLOWED,
            answer_a=plant,
            answer_b=animal,
            relation_space_kind=RelationSpaceKind.REPRODUCTIVE_DEPENDENCY,
            relation_keys_semantics="site x reproductive season",
            relation_event_semantics="reproductive persistence",
            answer_a_projection="plant projection",
            answer_b_projection="animal projection",
            same_accessible_area_required=True,
            raw_output_scale_comparison_allowed=False,
            adapter_frozen_before_focal_outcome=True,
        )
        self.assertIn(
            "cross_role_relation_must_not_require_one_universal_accessible_area",
            validate_relation_space_contract(contract),
        )

    def test_cross_role_raw_score_comparison_is_forbidden(self):
        plant = answer(
            answer_id="p",
            role="plant",
            target="plant",
            estimator_id="pmodel",
            estimator_family="plant_model",
            estimand=AnswerEstimand.REPRODUCTIVE_SUPPORT,
            m="plant M",
        )
        animal = answer(
            answer_id="a",
            role="animal",
            target="pollinator",
            estimator_id="amodel",
            estimator_family="movement_model",
            estimand=AnswerEstimand.VISITATION_SUPPORT,
            m="animal M",
        )
        contract = RelationSpaceContract(
            relation_id="BAD_RAW",
            relation_kind=PairedRelationKind.DIRECTIONAL_DEPENDENCY,
            estimator_policy=EstimatorPolicy.ROLE_SPECIFIC_ESTIMATORS_ALLOWED,
            answer_a=plant,
            answer_b=animal,
            relation_space_kind=RelationSpaceKind.INTERACTION_OPPORTUNITY,
            relation_keys_semantics="site x flowering window",
            relation_event_semantics="visitation opportunity",
            answer_a_projection="plant projection",
            answer_b_projection="pollinator projection",
            same_accessible_area_required=False,
            raw_output_scale_comparison_allowed=True,
            adapter_frozen_before_focal_outcome=True,
        )
        reasons = validate_relation_space_contract(contract)
        self.assertIn("cross_role_raw_output_scale_comparison_forbidden", reasons)
        self.assertIn("different_estimands_cannot_be_compared_on_raw_output_scale", reasons)


class AdaptedAnswerTests(unittest.TestCase):
    def test_adapter_alignment_reorders_keys_not_scores_semantics(self):
        plant = AdaptedAnswer(
            answer_id="plant",
            role="plant",
            relation_keys=("site1|week1", "site2|week1"),
            support=(0.8, 0.2),
            event_semantics="reproductive demand/support",
        )
        pollinator = AdaptedAnswer(
            answer_id="pollinator",
            role="pollinator",
            relation_keys=("site2|week1", "site1|week1"),
            support=(0.1, 0.9),
            event_semantics="visitation/reachability support",
        )
        aligned = align_adapted_answers(plant, pollinator)
        self.assertEqual(aligned.relation_keys, plant.relation_keys)
        self.assertEqual(aligned.support_b, (0.9, 0.1))

    def test_directional_containment_is_evaluated_after_adaptation(self):
        pollinator = AdaptedAnswer(
            answer_id="pollinator",
            role="required pollinator",
            relation_keys=("site1", "site2", "site3"),
            support=(0.8, 0.15, 0.05),
            event_semantics="visitation opportunity",
        )
        plant_reproduction = AdaptedAnswer(
            answer_id="plant",
            role="dependent plant reproduction",
            relation_keys=("site1", "site2", "site3"),
            support=(0.9, 0.08, 0.02),
            event_semantics="pollinator-dependent reproductive success",
        )
        containment = directional_containment_on_relation_space(
            required_answer=pollinator,
            dependent_answer=plant_reproduction,
            support_quantile=0.80,
        )
        self.assertAlmostEqual(containment, 0.9)

    def test_relation_keys_must_match_exactly(self):
        a = AdaptedAnswer("a", "plant", ("s1", "s2"), (0.5, 0.5), "event")
        b = AdaptedAnswer("b", "pollinator", ("s1", "s3"), (0.5, 0.5), "event")
        with self.assertRaises(ValueError):
            align_adapted_answers(a, b)


if __name__ == "__main__":
    unittest.main()
