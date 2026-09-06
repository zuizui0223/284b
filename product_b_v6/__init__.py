"""Product-B v6 directed dependency-witness prototype."""

from .witness import (
    HostSamplingSummary,
    WitnessSamplingSummary,
    WitnessPreflightState,
    WitnessConstraintState,
    evaluate_witness_sampling_preflight,
    directed_witness_containment,
    host_support_fraction,
    empirical_nearest_rank_quantile,
    classify_witness_constraint,
    knockout_preferential_drop,
)

__all__ = [
    "HostSamplingSummary",
    "WitnessSamplingSummary",
    "WitnessPreflightState",
    "WitnessConstraintState",
    "evaluate_witness_sampling_preflight",
    "directed_witness_containment",
    "host_support_fraction",
    "empirical_nearest_rank_quantile",
    "classify_witness_constraint",
    "knockout_preferential_drop",
]
