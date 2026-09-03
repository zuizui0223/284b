"""Product-B v5 obligate-association invariant prototype."""

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
]
