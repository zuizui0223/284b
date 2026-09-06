"""Product-B obligate-association invariant prototype."""

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

__all__ = [
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
]
