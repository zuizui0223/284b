"""Product-B biological-constraint and paired answer-check prototype."""

from .crosscheck import (
    PairedAnswerCheckDecision,
    PairedCheckState,
    classify_paired_answer_check,
    reciprocal_containment_discordance,
)
from .invariants import (
    InvariantState,
    PreflightResult,
    ProcedureDescriptor,
    breadth_ratio_pair,
    centroid_separation_pair,
    classify_directed_invariant,
    directed_containment,
    response_blind_differentiability_precheck,
    schoener_d_pair,
    support_breadth,
)
from .mutual import (
    ConstraintClass,
    MutualContainmentResult,
    MutualInvariantDecision,
    classify_mutual_obligacy,
    mutual_obligacy_containment,
    rank_profile_discordance_pair,
)
from .paired_relations import (
    PairedRelationContract,
    PairedRelationKind,
    RelationStrength,
    bidirectional_containment_discordance,
    containment_discordance,
    overlap_discordance,
    validate_paired_relation_contract,
)

__all__ = [
    "PairedAnswerCheckDecision",
    "PairedCheckState",
    "classify_paired_answer_check",
    "reciprocal_containment_discordance",
    "InvariantState",
    "PreflightResult",
    "ProcedureDescriptor",
    "breadth_ratio_pair",
    "centroid_separation_pair",
    "classify_directed_invariant",
    "directed_containment",
    "response_blind_differentiability_precheck",
    "schoener_d_pair",
    "support_breadth",
    "ConstraintClass",
    "MutualContainmentResult",
    "MutualInvariantDecision",
    "classify_mutual_obligacy",
    "mutual_obligacy_containment",
    "rank_profile_discordance_pair",
    "PairedRelationContract",
    "PairedRelationKind",
    "RelationStrength",
    "validate_paired_relation_contract",
    "containment_discordance",
    "bidirectional_containment_discordance",
    "overlap_discordance",
]
