"""Response-blind contracts for paired ecological answer checks.

A paired answer-check does not require two different species. The two answers may
come from different taxa, life stages, observation systems, or independent data
sources. What matters is that external biology declares how the answers should
relate before either focal comparison outcome is opened.

Every soft comparison is reduced to a non-negative discordance quantity where
smaller means more coherent. The numerical tolerance is relation-specific and
must be frozen independently of the focal outcome. Hard biological invariants
remain classified by their dedicated invariant functions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite


class RelationStrength(str, Enum):
    HARD_INVARIANT = "hard_invariant"
    SOFT_CROSSCHECK = "soft_crosscheck"


class PairedRelationKind(str, Enum):
    """Biological reasons for expecting two independently fitted answers to cohere."""

    SAME_TARGET_INDEPENDENT_SOURCE = "same_target_independent_source"
    EXPECTED_SYMMETRIC_CONCORDANCE = "expected_symmetric_concordance"
    DIRECTIONAL_DEPENDENCY = "directional_dependency"
    MUTUAL_DEPENDENCY = "mutual_dependency"
    LIFE_STAGE_COUPLING = "life_stage_coupling"


@dataclass(frozen=True)
class PairedRelationContract:
    relation_id: str
    relation_kind: PairedRelationKind
    strength: RelationStrength
    answer_a_role: str
    answer_b_role: str
    declared_scale: str
    external_relation_basis: str
    discordance_metric: str
    reference_ceiling: float | None
    relation_frozen_before_focal_outcome: bool
    threshold_frozen_before_focal_outcome: bool
    answers_fit_independently: bool
    focal_outcomes_opened: bool = False


def validate_paired_relation_contract(contract: PairedRelationContract) -> tuple[str, ...]:
    """Validate a paired relation without opening or interpreting focal outcomes."""

    reasons: list[str] = []
    for field_name, value in (
        ("relation_id", contract.relation_id),
        ("answer_a_role", contract.answer_a_role),
        ("answer_b_role", contract.answer_b_role),
        ("declared_scale", contract.declared_scale),
        ("external_relation_basis", contract.external_relation_basis),
        ("discordance_metric", contract.discordance_metric),
    ):
        if not value.strip():
            reasons.append(f"{field_name}_blank")

    if contract.answer_a_role.strip() == contract.answer_b_role.strip():
        reasons.append("answer_roles_must_be_distinguishable")
    if not contract.relation_frozen_before_focal_outcome:
        reasons.append("relation_not_frozen_before_focal_outcome")
    if not contract.answers_fit_independently:
        reasons.append("answers_not_independently_fit")
    if contract.focal_outcomes_opened:
        reasons.append("contract_created_after_focal_outcome")

    if contract.strength == RelationStrength.SOFT_CROSSCHECK:
        ceiling = contract.reference_ceiling
        if ceiling is None or not isfinite(ceiling) or ceiling < 0.0:
            reasons.append("soft_crosscheck_reference_ceiling_invalid")
        if not contract.threshold_frozen_before_focal_outcome:
            reasons.append("soft_crosscheck_threshold_not_frozen")
    else:
        # Hard invariants use their dedicated predeclared biological thresholds;
        # this generic soft-discordance ceiling must not silently substitute for them.
        if contract.reference_ceiling is not None:
            reasons.append("hard_invariant_must_use_dedicated_classifier")

    return tuple(reasons)


def containment_discordance(containment: float) -> float:
    """Convert directional containment in [0,1] to discordance in [0,1]."""

    if not isfinite(containment) or not 0.0 <= containment <= 1.0:
        raise ValueError("containment must be finite and in [0, 1]")
    return 1.0 - containment


def bidirectional_containment_discordance(
    containment_b_in_a: float,
    containment_a_in_b: float,
) -> float:
    """Worst-direction discordance for a reciprocal answer-check.

    A reciprocal relation is only as coherent as its weaker direction. This is a
    soft diagnostic; hard mutual obligacy must still use ``classify_mutual_obligacy``.
    """

    return max(
        containment_discordance(containment_b_in_a),
        containment_discordance(containment_a_in_b),
    )


def overlap_discordance(overlap: float) -> float:
    """Convert a bounded similarity such as Schoener's D to discordance."""

    if not isfinite(overlap) or not 0.0 <= overlap <= 1.0:
        raise ValueError("overlap must be finite and in [0, 1]")
    return 1.0 - overlap


__all__ = [
    "RelationStrength",
    "PairedRelationKind",
    "PairedRelationContract",
    "validate_paired_relation_contract",
    "containment_discordance",
    "bidirectional_containment_discordance",
    "overlap_discordance",
]
