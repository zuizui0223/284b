import unittest

from product_b_v5.paired_relations import PairedRelationKind
from product_b_v5.relation_space import (
    AnswerEstimand,
    EcologicalAnswerContract,
    EstimatorPolicy,
    RelationSpaceContract,
    RelationSpaceKind,
    validate_relation_space_contract,
)


def answer(*, role: str, target: str, m: str, spatial: str = "10-km cells", temporal: str = "season"):
    return EcologicalAnswerContract(
        answer_id=role,
        role=role,
        biological_target=target,
        estimator_id="fixed_estimator",
        estimator_family="fixed_family",
        estimand=AnswerEstimand.REALIZED_ENVIRONMENTAL_SUPPORT,
        spatial_unit=spatial,
        temporal_unit=temporal,
        accessible_area_semantics=m,
        observation_process=f"{role}_evidence",
        estimator_frozen_before_outcome=True,
    )


def same_target_space(a: EcologicalAnswerContract, b: EcologicalAnswerContract):
    return RelationSpaceContract(
        relation_id="SELF",
        relation_kind=PairedRelationKind.SAME_TARGET_INDEPENDENT_SOURCE,
        estimator_policy=EstimatorPolicy.SAME_TARGET_COMMON_ESTIMATOR,
        answer_a=a,
        answer_b=b,
        relation_space_kind=RelationSpaceKind.SAME_TARGET_SUPPORT,
        relation_keys_semantics="same comparison rows",
        relation_event_semantics="same target support",
        answer_a_projection="projection a",
        answer_b_projection="projection b",
        same_accessible_area_required=True,
        raw_output_scale_comparison_allowed=False,
        adapter_frozen_before_focal_outcome=True,
    )


class StrictComparabilityTests(unittest.TestCase):
    def test_same_target_requires_identical_accessible_area_semantics(self):
        contract = same_target_space(
            answer(role="specimen", target="Taxon A", m="M=150km"),
            answer(role="observation", target="Taxon A", m="M=300km"),
        )
        self.assertIn(
            "same_target_calibration_accessible_area_semantics_differ",
            validate_relation_space_contract(contract),
        )

    def test_same_target_requires_identical_spatial_and_temporal_units(self):
        contract = same_target_space(
            answer(role="specimen", target="Taxon A", m="M=150km", spatial="10-km cells", temporal="season"),
            answer(role="observation", target="Taxon A", m="M=150km", spatial="25-km cells", temporal="year"),
        )
        reasons = validate_relation_space_contract(contract)
        self.assertIn("same_target_calibration_spatial_units_differ", reasons)
        self.assertIn("same_target_calibration_temporal_units_differ", reasons)

    def test_cross_role_cannot_fake_comparability_with_same_target_space(self):
        plant = EcologicalAnswerContract(
            answer_id="plant",
            role="plant",
            biological_target="Plant A",
            estimator_id="plant_model",
            estimator_family="plant_sdm",
            estimand=AnswerEstimand.REPRODUCTIVE_SUPPORT,
            spatial_unit="plant sites",
            temporal_unit="flowering windows",
            accessible_area_semantics="plant M",
            observation_process="plant reproductive evidence",
            estimator_frozen_before_outcome=True,
        )
        pollinator = EcologicalAnswerContract(
            answer_id="pollinator",
            role="pollinator",
            biological_target="Pollinator B",
            estimator_id="movement_model",
            estimator_family="eog_or_dynamic_movement",
            estimand=AnswerEstimand.VISITATION_SUPPORT,
            spatial_unit="movement graph nodes",
            temporal_unit="activity windows",
            accessible_area_semantics="pollinator M",
            observation_process="visitation evidence",
            estimator_frozen_before_outcome=True,
        )
        contract = RelationSpaceContract(
            relation_id="PAIR",
            relation_kind=PairedRelationKind.DIRECTIONAL_DEPENDENCY,
            estimator_policy=EstimatorPolicy.ROLE_SPECIFIC_ESTIMATORS_ALLOWED,
            answer_a=plant,
            answer_b=pollinator,
            relation_space_kind=RelationSpaceKind.SAME_TARGET_SUPPORT,
            relation_keys_semantics="incorrectly reused support cells",
            relation_event_semantics="pollination",
            answer_a_projection="plant projection",
            answer_b_projection="pollinator projection",
            same_accessible_area_required=False,
            raw_output_scale_comparison_allowed=False,
            adapter_frozen_before_focal_outcome=True,
        )
        self.assertIn(
            "cross_role_relation_cannot_use_same_target_support_space",
            validate_relation_space_contract(contract),
        )


if __name__ == "__main__":
    unittest.main()
