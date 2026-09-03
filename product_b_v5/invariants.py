"""Pure functions for the Product-B v5 obligate-association answer-check.

This module is deliberately data-source agnostic. It must not fetch occurrences,
open sealed outcomes, refit models, or select support quantiles from results.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite, sqrt
from typing import Mapping, Sequence


class InvariantState(str, Enum):
    """Contract-relative terminal state for one directed obligate statement."""

    VIOLATED = "invariant_violated"
    CONSISTENT = "invariant_consistent_under_frozen_contract"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class ProcedureDescriptor:
    """Response-blind structural description of one admissible procedure member."""

    procedure_id: str
    selected_predictors: tuple[str, ...]

    @property
    def predictor_signature(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.selected_predictors)))


@dataclass(frozen=True)
class PreflightResult:
    """Result of the response-blind differentiability pre-check."""

    passed: bool
    admissible_member_count: int
    distinct_predictor_signature_count: int
    inadmissible_process_knockouts: tuple[str, ...]
    reasons: tuple[str, ...]


def _normalize_support(values: Sequence[float]) -> tuple[float, ...]:
    weights = tuple(float(value) for value in values)
    if not weights:
        raise ValueError("support must not be empty")
    if any((not isfinite(value)) or value < 0.0 for value in weights):
        raise ValueError("support values must be finite and non-negative")

    total = sum(weights)
    if total <= 0.0:
        raise ValueError("support must have positive total mass")
    return tuple(value / total for value in weights)


def _validate_common_length(a: Sequence[object], b: Sequence[object]) -> None:
    if len(a) != len(b):
        raise ValueError("inputs must be defined on the same audit cells")


def _validate_coordinates(
    coordinates: Sequence[Sequence[float]], expected_length: int
) -> tuple[tuple[float, ...], ...]:
    if len(coordinates) != expected_length:
        raise ValueError("coordinates and support must have the same number of cells")
    if not coordinates:
        raise ValueError("coordinates must not be empty")

    converted = tuple(tuple(float(value) for value in row) for row in coordinates)
    dimension = len(converted[0])
    if dimension == 0:
        raise ValueError("audit coordinates must have at least one dimension")
    if any(len(row) != dimension for row in converted):
        raise ValueError("all audit coordinates must have the same dimension")
    if any(not isfinite(value) for row in converted for value in row):
        raise ValueError("audit coordinates must be finite")
    return converted


def _highest_density_region(
    support: Sequence[float], support_quantile: float
) -> tuple[int, ...]:
    """Return a deterministic highest-density support region.

    The cutoff is the recovered-mass value at which cumulative mass first reaches
    the predeclared quantile. All cells tied at that cutoff are retained, avoiding
    index-order-dependent tie breaking.
    """

    if not (0.0 < support_quantile <= 1.0):
        raise ValueError("support_quantile must be in (0, 1]")

    normalized = _normalize_support(support)
    cumulative = 0.0
    cutoff = min(normalized)
    for value in sorted(normalized, reverse=True):
        cumulative += value
        cutoff = value
        if cumulative + 1e-15 >= support_quantile:
            break

    return tuple(
        index
        for index, value in enumerate(normalized)
        if value + 1e-15 >= cutoff
    )


def directed_containment(
    required_support: Sequence[float],
    dependent_support: Sequence[float],
    support_quantile: float,
) -> float:
    """Mass of dependent Y support contained in required-partner X support.

    Parameters follow the biological direction `Y requires X`: X is
    `required_support`; Y is `dependent_support`.
    """

    required = _normalize_support(required_support)
    dependent = _normalize_support(dependent_support)
    _validate_common_length(required, dependent)

    required_region = set(_highest_density_region(required, support_quantile))
    return sum(
        dependent[index]
        for index in range(len(dependent))
        if index in required_region
    )


def schoener_d_pair(
    support_x: Sequence[float], support_y: Sequence[float]
) -> float:
    """Schoener's D overlap on a common audit grid."""

    x = _normalize_support(support_x)
    y = _normalize_support(support_y)
    _validate_common_length(x, y)
    return 1.0 - 0.5 * sum(abs(px - py) for px, py in zip(x, y))


def _weighted_centroid(
    support: Sequence[float], coordinates: Sequence[Sequence[float]]
) -> tuple[float, ...]:
    weights = _normalize_support(support)
    coords = _validate_coordinates(coordinates, len(weights))
    dimension = len(coords[0])
    return tuple(
        sum(weight * coords[index][axis] for index, weight in enumerate(weights))
        for axis in range(dimension)
    )


def centroid_separation_pair(
    support_x: Sequence[float],
    support_y: Sequence[float],
    coordinates: Sequence[Sequence[float]],
) -> float:
    """Euclidean separation of recovered support centroids."""

    _validate_common_length(support_x, support_y)
    centroid_x = _weighted_centroid(support_x, coordinates)
    centroid_y = _weighted_centroid(support_y, coordinates)
    return sqrt(sum((x - y) ** 2 for x, y in zip(centroid_x, centroid_y)))


def support_breadth(
    support: Sequence[float], coordinates: Sequence[Sequence[float]]
) -> float:
    """Weighted RMS distance from the recovered support centroid."""

    weights = _normalize_support(support)
    coords = _validate_coordinates(coordinates, len(weights))
    centroid = _weighted_centroid(weights, coords)

    mean_squared_distance = 0.0
    for index, weight in enumerate(weights):
        squared_distance = sum(
            (coords[index][axis] - centroid[axis]) ** 2
            for axis in range(len(centroid))
        )
        mean_squared_distance += weight * squared_distance
    return sqrt(mean_squared_distance)


def breadth_ratio_pair(
    dependent_support: Sequence[float],
    required_support: Sequence[float],
    coordinates: Sequence[Sequence[float]],
) -> float:
    """Recovered breadth ratio Y/X for the directed statement `Y requires X`."""

    _validate_common_length(dependent_support, required_support)
    dependent_breadth = support_breadth(dependent_support, coordinates)
    required_breadth = support_breadth(required_support, coordinates)
    if required_breadth <= 0.0:
        raise ValueError("required-partner breadth is zero; breadth ratio is unresolved")
    return dependent_breadth / required_breadth


def classify_directed_invariant(
    *,
    containment: float | None,
    adequacy_required: bool,
    adequacy_dependent: bool,
    minimum_containment: float,
    required_breadth: float | None,
    maximum_required_breadth: float | None,
    evidence_complete: bool = True,
) -> InvariantState:
    """Classify one directed invariant without combining metrics into a score.

    A failed adequacy gate, incomplete evidence, missing/non-finite breadth, or a
    predeclared broad-support guardrail failure is unresolved. Only sufficiently
    low directed containment with otherwise complete admissible evidence is a
    directional invariant violation.
    """

    if not (0.0 <= minimum_containment <= 1.0):
        raise ValueError("minimum_containment must be in [0, 1]")
    if maximum_required_breadth is not None:
        if not isfinite(maximum_required_breadth) or maximum_required_breadth < 0.0:
            raise ValueError("maximum_required_breadth must be finite and non-negative")

    if not evidence_complete:
        return InvariantState.UNRESOLVED
    if not adequacy_required or not adequacy_dependent:
        return InvariantState.UNRESOLVED
    if containment is None or not isfinite(containment):
        return InvariantState.UNRESOLVED
    if not (0.0 <= containment <= 1.0):
        raise ValueError("containment must be in [0, 1]")
    if required_breadth is None or not isfinite(required_breadth) or required_breadth < 0.0:
        return InvariantState.UNRESOLVED
    if (
        maximum_required_breadth is not None
        and required_breadth > maximum_required_breadth
    ):
        return InvariantState.UNRESOLVED

    if containment < minimum_containment:
        return InvariantState.VIOLATED
    return InvariantState.CONSISTENT


def response_blind_differentiability_precheck(
    procedures: Sequence[ProcedureDescriptor],
    process_knockout_admissible: Mapping[str, bool],
    *,
    minimum_members: int = 2,
    minimum_distinct_predictor_signatures: int = 2,
) -> PreflightResult:
    """Check whether the candidate architecture can discriminate before opening outcomes.

    The inputs are structural metadata only. Passing this function is not an
    execution authorization and reveals no invariant result.
    """

    if minimum_members < 2:
        raise ValueError("minimum_members must be at least 2")
    if minimum_distinct_predictor_signatures < 2:
        raise ValueError("minimum_distinct_predictor_signatures must be at least 2")

    procedure_ids = [procedure.procedure_id for procedure in procedures]
    if len(procedure_ids) != len(set(procedure_ids)):
        raise ValueError("procedure_id values must be unique")

    signatures = {procedure.predictor_signature for procedure in procedures}
    inadmissible_processes = tuple(
        sorted(
            process
            for process, is_admissible in process_knockout_admissible.items()
            if not is_admissible
        )
    )

    reasons: list[str] = []
    if len(procedures) < minimum_members:
        reasons.append("candidate_set_degenerate")
    if len(signatures) < minimum_distinct_predictor_signatures:
        reasons.append("predictor_signatures_not_differentiated")
    if inadmissible_processes:
        reasons.append("one_or_more_process_knockouts_inadmissible")

    return PreflightResult(
        passed=not reasons,
        admissible_member_count=len(procedures),
        distinct_predictor_signature_count=len(signatures),
        inadmissible_process_knockouts=inadmissible_processes,
        reasons=tuple(reasons),
    )
