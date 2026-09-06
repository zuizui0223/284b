"""Role-specific answer construction and relation-space adaptation.

Same-target source replication and cross-species biological checks solve different
problems. The former may deliberately hold the estimator/procedure and accessible
area fixed as an experimental control. The latter must not require biologically
different roles to share one estimator, one accessible area, or one raw output
scale merely to make the final answer-check convenient.

Cross-species comparability is created *after* answer construction by a frozen
relation-space adapter. For example, plant reproductive support and pollinator
reachability/visitation support may be projected onto plant-site x flowering-window
interaction opportunities before a directional dependency is evaluated.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite

from .invariants import directed_containment
from .paired_relations import (
    PairedRelationContract,
    PairedRelationKind,
    validate_paired_relation_contract,
)


class AnswerEstimand(str, Enum):
    REALIZED_ENVIRONMENTAL_SUPPORT = "realized_environmental_support"
    REPRODUCTIVE_SUPPORT = "reproductive_support"
    PERSISTENCE_SUPPORT = "persistence_support"
    REACHABILITY_SUPPORT = "reachability_support"
    VISITATION_SUPPORT = "visitation_support"
    OBSERVATION_SUPPORT = "observation_support"
    INTERACTION_OPPORTUNITY_SUPPORT = "interaction_opportunity_support"
    CUSTOM = "custom"


class EstimatorPolicy(str, Enum):
    """Whether estimator equality is part of the scientific design."""

    SAME_TARGET_COMMON_ESTIMATOR = "same_target_common_estimator"
    ROLE_SPECIFIC_ESTIMATORS_ALLOWED = "role_specific_estimators_allowed"


class RelationSpaceKind(str, Enum):
    SAME_TARGET_SUPPORT = "same_target_support"
    INTERACTION_OPPORTUNITY = "interaction_opportunity"
    REPRODUCTIVE_DEPENDENCY = "reproductive_dependency"
    PERSISTENCE_DEPENDENCY = "persistence_dependency"
    LIFE_STAGE_TRANSITION = "life_stage_transition"
    CUSTOM = "custom"


@dataclass(frozen=True)
class EcologicalAnswerContract:
    answer_id: str
    role: str
    biological_target: str
    estimator_id: str
    estimator_family: str
    estimand: AnswerEstimand
    spatial_unit: str
    temporal_unit: str
    accessible_area_semantics: str
    observation_process: str
    estimator_frozen_before_outcome: bool
    focal_outcome_opened: bool = False


@dataclass(frozen=True)
class RelationSpaceContract:
    relation_id: str
    relation_kind: PairedRelationKind
    estimator_policy: EstimatorPolicy
    answer_a: EcologicalAnswerContract
    answer_b: EcologicalAnswerContract
    relation_space_kind: RelationSpaceKind
    relation_keys_semantics: str
    relation_event_semantics: str
    answer_a_projection: str
    answer_b_projection: str
    same_accessible_area_required: bool
    raw_output_scale_comparison_allowed: bool
    adapter_frozen_before_focal_outcome: bool
    focal_outcome_opened: bool = False


@dataclass(frozen=True)
class AdaptedAnswer:
    """One answer after projection to a common biological relation space."""

    answer_id: str
    role: str
    relation_keys: tuple[str, ...]
    support: tuple[float, ...]
    event_semantics: str


@dataclass(frozen=True)
class RelationSpacePair:
    relation_keys: tuple[str, ...]
    support_a: tuple[float, ...]
    support_b: tuple[float, ...]


def _blank(value: str) -> bool:
    return not str(value).strip()


def _validate_answer(answer: EcologicalAnswerContract, prefix: str) -> list[str]:
    reasons: list[str] = []
    for field_name, value in (
        ("answer_id", answer.answer_id),
        ("role", answer.role),
        ("biological_target", answer.biological_target),
        ("estimator_id", answer.estimator_id),
        ("estimator_family", answer.estimator_family),
        ("spatial_unit", answer.spatial_unit),
        ("temporal_unit", answer.temporal_unit),
        ("accessible_area_semantics", answer.accessible_area_semantics),
        ("observation_process", answer.observation_process),
    ):
        if _blank(value):
            reasons.append(f"{prefix}_{field_name}_blank")
    if not answer.estimator_frozen_before_outcome:
        reasons.append(f"{prefix}_estimator_not_frozen_before_outcome")
    if answer.focal_outcome_opened:
        reasons.append(f"{prefix}_answer_contract_created_after_outcome")
    return reasons


def validate_relation_space_contract(contract: RelationSpaceContract) -> tuple[str, ...]:
    """Validate estimator/adapter separation without opening focal outcomes."""

    reasons: list[str] = []
    reasons.extend(_validate_answer(contract.answer_a, "answer_a"))
    reasons.extend(_validate_answer(contract.answer_b, "answer_b"))

    for field_name, value in (
        ("relation_id", contract.relation_id),
        ("relation_keys_semantics", contract.relation_keys_semantics),
        ("relation_event_semantics", contract.relation_event_semantics),
        ("answer_a_projection", contract.answer_a_projection),
        ("answer_b_projection", contract.answer_b_projection),
    ):
        if _blank(value):
            reasons.append(f"{field_name}_blank")

    if contract.answer_a.role.strip() == contract.answer_b.role.strip():
        reasons.append("answer_roles_must_be_distinguishable")
    if not contract.adapter_frozen_before_focal_outcome:
        reasons.append("relation_space_adapter_not_frozen_before_focal_outcome")
    if contract.focal_outcome_opened:
        reasons.append("relation_space_contract_created_after_focal_outcome")

    same_target = contract.relation_kind == PairedRelationKind.SAME_TARGET_INDEPENDENT_SOURCE
    if same_target:
        if contract.answer_a.biological_target.strip() != contract.answer_b.biological_target.strip():
            reasons.append("same_target_relation_requires_same_biological_target")
        if contract.answer_a.estimand != contract.answer_b.estimand:
            reasons.append("same_target_relation_requires_same_estimand")
        if contract.estimator_policy != EstimatorPolicy.SAME_TARGET_COMMON_ESTIMATOR:
            reasons.append("same_target_calibration_requires_common_estimator_policy")
        if contract.answer_a.estimator_id.strip() != contract.answer_b.estimator_id.strip():
            reasons.append("same_target_calibration_requires_same_estimator_id")
        if contract.answer_a.estimator_family.strip() != contract.answer_b.estimator_family.strip():
            reasons.append("same_target_calibration_requires_same_estimator_family")
        if not contract.same_accessible_area_required:
            reasons.append("same_target_calibration_requires_same_accessible_area")
        if contract.relation_space_kind != RelationSpaceKind.SAME_TARGET_SUPPORT:
            reasons.append("same_target_calibration_requires_same_target_relation_space")
    else:
        if contract.estimator_policy != EstimatorPolicy.ROLE_SPECIFIC_ESTIMATORS_ALLOWED:
            reasons.append("cross_role_relation_must_allow_role_specific_estimators")
        if contract.same_accessible_area_required:
            reasons.append("cross_role_relation_must_not_require_one_universal_accessible_area")
        if contract.raw_output_scale_comparison_allowed:
            reasons.append("cross_role_raw_output_scale_comparison_forbidden")

    if contract.answer_a.estimand != contract.answer_b.estimand and contract.raw_output_scale_comparison_allowed:
        reasons.append("different_estimands_cannot_be_compared_on_raw_output_scale")

    return tuple(dict.fromkeys(reasons))


def validate_paired_relation_with_space(
    relation: PairedRelationContract,
    relation_space: RelationSpaceContract,
) -> tuple[str, ...]:
    """Require the biological relation and estimator/adapter contract together."""

    reasons = list(validate_paired_relation_contract(relation))
    reasons.extend(validate_relation_space_contract(relation_space))
    if relation.relation_id.strip() != relation_space.relation_id.strip():
        reasons.append("paired_relation_and_relation_space_ids_differ")
    if relation.relation_kind != relation_space.relation_kind:
        reasons.append("paired_relation_and_relation_space_kinds_differ")
    if relation.answer_a_role.strip() != relation_space.answer_a.role.strip():
        reasons.append("answer_a_role_differs_between_contracts")
    if relation.answer_b_role.strip() != relation_space.answer_b.role.strip():
        reasons.append("answer_b_role_differs_between_contracts")
    return tuple(dict.fromkeys(reasons))


def validate_adapted_answer(answer: AdaptedAnswer) -> tuple[str, ...]:
    reasons: list[str] = []
    if _blank(answer.answer_id):
        reasons.append("adapted_answer_id_blank")
    if _blank(answer.role):
        reasons.append("adapted_answer_role_blank")
    if _blank(answer.event_semantics):
        reasons.append("adapted_answer_event_semantics_blank")
    if not answer.relation_keys:
        reasons.append("adapted_answer_relation_keys_empty")
    if len(set(answer.relation_keys)) != len(answer.relation_keys):
        reasons.append("adapted_answer_relation_keys_not_unique")
    if len(answer.relation_keys) != len(answer.support):
        reasons.append("adapted_answer_key_support_length_mismatch")
    if any((not isfinite(float(x))) or float(x) < 0.0 for x in answer.support):
        reasons.append("adapted_answer_support_invalid")
    if answer.support and sum(float(x) for x in answer.support) <= 0.0:
        reasons.append("adapted_answer_support_has_no_positive_mass")
    return tuple(reasons)


def align_adapted_answers(answer_a: AdaptedAnswer, answer_b: AdaptedAnswer) -> RelationSpacePair:
    """Align two already-adapted answers on exactly the same relation keys."""

    reasons_a = validate_adapted_answer(answer_a)
    reasons_b = validate_adapted_answer(answer_b)
    if reasons_a or reasons_b:
        raise ValueError(f"invalid adapted answer: A={reasons_a}, B={reasons_b}")
    if set(answer_a.relation_keys) != set(answer_b.relation_keys):
        raise ValueError("adapted answers must cover exactly the same relation-space keys")
    b_by_key = dict(zip(answer_b.relation_keys, answer_b.support))
    return RelationSpacePair(
        relation_keys=answer_a.relation_keys,
        support_a=tuple(float(x) for x in answer_a.support),
        support_b=tuple(float(b_by_key[key]) for key in answer_a.relation_keys),
    )


def directional_containment_on_relation_space(
    *,
    required_answer: AdaptedAnswer,
    dependent_answer: AdaptedAnswer,
    support_quantile: float,
) -> float:
    """Evaluate ``dependent requires required`` after role-specific adaptation."""

    pair = align_adapted_answers(required_answer, dependent_answer)
    return directed_containment(pair.support_a, pair.support_b, support_quantile)


__all__ = [
    "AnswerEstimand",
    "EstimatorPolicy",
    "RelationSpaceKind",
    "EcologicalAnswerContract",
    "RelationSpaceContract",
    "AdaptedAnswer",
    "RelationSpacePair",
    "validate_relation_space_contract",
    "validate_paired_relation_with_space",
    "validate_adapted_answer",
    "align_adapted_answers",
    "directional_containment_on_relation_space",
]
