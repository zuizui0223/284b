"""Symmetric mutual-obligacy constraint helpers for Product-B.

This module extends the existing directed obligate-association answer-check without
changing its semantics. A mutual-obligacy statement ``X <-> Y`` is represented as
two necessary directed statements: ``Y requires X`` and ``X requires Y``.

Raw suitability probabilities are deliberately not compared across taxa. The
primary answer-check is bidirectional containment on a common frozen audit space.
Rank-profile discordance is descriptive only and cannot replace the two directed
invariant decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Sequence

from .invariants import InvariantState, classify_directed_invariant, directed_containment


class ConstraintClass(str, Enum):
    """External biological constraint classes supported by the invariant layer."""

    DIRECTED_DEPENDENCY = "directed_dependency"
    MUTUAL_OBLIGACY = "mutual_obligacy"


@dataclass(frozen=True)
class MutualContainmentResult:
    """The two directional containment quantities for ``X <-> Y``."""

    y_in_x: float
    x_in_y: float


@dataclass(frozen=True)
class MutualInvariantDecision:
    """Contract-relative result for one mutual-obligacy constraint."""

    state: InvariantState
    y_requires_x_state: InvariantState
    x_requires_y_state: InvariantState


def mutual_obligacy_containment(
    support_x: Sequence[float],
    support_y: Sequence[float],
    support_quantile: float,
) -> MutualContainmentResult:
    """Evaluate both necessary directed containments for ``X <-> Y``.

    ``y_in_x`` is the mass of Y contained in the highest-density support region
    of X. ``x_in_y`` is the converse. Neither value is a raw probability
    comparison between taxa.
    """

    return MutualContainmentResult(
        y_in_x=directed_containment(support_x, support_y, support_quantile),
        x_in_y=directed_containment(support_y, support_x, support_quantile),
    )


def _normalize(values: Sequence[float]) -> tuple[float, ...]:
    weights = tuple(float(value) for value in values)
    if not weights:
        raise ValueError("support must not be empty")
    if any((not isfinite(value)) or value < 0.0 for value in weights):
        raise ValueError("support values must be finite and non-negative")
    total = sum(weights)
    if total <= 0.0:
        raise ValueError("support must have positive total mass")
    return tuple(value / total for value in weights)


def _percentile_ranks(values: Sequence[float]) -> tuple[float, ...]:
    """Return deterministic tie-aware percentile ranks in [0, 1]."""

    numbers = tuple(float(value) for value in values)
    if not numbers:
        raise ValueError("values must not be empty")
    if len(numbers) == 1:
        return (1.0,)

    ordered = sorted(range(len(numbers)), key=lambda index: numbers[index])
    ranks = [0.0] * len(numbers)
    start = 0
    while start < len(ordered):
        end = start + 1
        value = numbers[ordered[start]]
        while end < len(ordered) and numbers[ordered[end]] == value:
            end += 1
        # Average 1-based rank for the tie group, scaled to [0, 1].
        average_rank = ((start + 1) + end) / 2.0
        percentile = (average_rank - 1.0) / (len(numbers) - 1.0)
        for position in range(start, end):
            ranks[ordered[position]] = percentile
        start = end
    return tuple(ranks)


def rank_profile_discordance_pair(
    support_x: Sequence[float], support_y: Sequence[float]
) -> float:
    """Joint-support-weighted discordance between taxon-specific suitability ranks.

    The metric is scale-free: each taxon's support is converted to its own
    percentile-rank profile before comparison. Cells receive weight equal to the
    mean normalized mass of X and Y, so disagreement in biologically relevant
    support regions matters more than disagreement in shared low-support
    background. The result lies in [0, 1] and is descriptive only.
    """

    x = _normalize(support_x)
    y = _normalize(support_y)
    if len(x) != len(y):
        raise ValueError("inputs must be defined on the same audit cells")

    rank_x = _percentile_ranks(x)
    rank_y = _percentile_ranks(y)
    return sum(
        0.5 * (px + py) * abs(rx - ry)
        for px, py, rx, ry in zip(x, y, rank_x, rank_y)
    )


def classify_mutual_obligacy(
    *,
    containment_y_in_x: float | None,
    containment_x_in_y: float | None,
    adequacy_x: bool,
    adequacy_y: bool,
    minimum_containment: float,
    breadth_x: float | None,
    breadth_y: float | None,
    maximum_partner_breadth: float,
    evidence_complete: bool = True,
) -> MutualInvariantDecision:
    """Classify ``X <-> Y`` as two necessary directed constraints.

    A complete violation of either direction is sufficient to falsify mutual
    compatibility. Consistency requires both directions to pass. If neither
    direction is violated but at least one direction is unresolved, the mutual
    result is unresolved.
    """

    y_requires_x = classify_directed_invariant(
        containment=containment_y_in_x,
        adequacy_required=adequacy_x,
        adequacy_dependent=adequacy_y,
        minimum_containment=minimum_containment,
        required_breadth=breadth_x,
        maximum_required_breadth=maximum_partner_breadth,
        evidence_complete=evidence_complete,
    )
    x_requires_y = classify_directed_invariant(
        containment=containment_x_in_y,
        adequacy_required=adequacy_y,
        adequacy_dependent=adequacy_x,
        minimum_containment=minimum_containment,
        required_breadth=breadth_y,
        maximum_required_breadth=maximum_partner_breadth,
        evidence_complete=evidence_complete,
    )

    directed_states = (y_requires_x, x_requires_y)
    if InvariantState.VIOLATED in directed_states:
        state = InvariantState.VIOLATED
    elif directed_states == (InvariantState.CONSISTENT, InvariantState.CONSISTENT):
        state = InvariantState.CONSISTENT
    else:
        state = InvariantState.UNRESOLVED

    return MutualInvariantDecision(
        state=state,
        y_requires_x_state=y_requires_x,
        x_requires_y_state=x_requires_y,
    )


__all__ = [
    "ConstraintClass",
    "MutualContainmentResult",
    "MutualInvariantDecision",
    "mutual_obligacy_containment",
    "rank_profile_discordance_pair",
    "classify_mutual_obligacy",
]
