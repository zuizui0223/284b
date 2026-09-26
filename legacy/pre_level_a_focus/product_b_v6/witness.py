"""Pure Product-B v6 directed dependency-witness functions.

This module does not read occurrences, fit models, query taxonomy, or open v5
outcomes. It evaluates already-computed host sampling summaries, unique dependent
witness cells, binary recovered host support, shuffled-host controls, and frozen
process-knockout contrasts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import ceil, isfinite
from statistics import mean
from typing import Mapping, Sequence


HOST_MIN_RECORDS = 50
HOST_MIN_UNIQUE_CELLS = 30
HOST_MIN_EFFECTIVE_CELLS = 10.0
WITNESS_MIN_RECORDS = 5
WITNESS_MIN_UNIQUE_CELLS = 3
MAXIMUM_HOST_SUPPORT_FRACTION = 0.80
MINIMUM_REPLACEMENT_HOSTS = 5
CONTROL_DRAW_COUNT = 100
LOWER_CONTROL_QUANTILE = 0.05
UPPER_CONTROL_QUANTILE = 0.95


class WitnessPreflightState(str, Enum):
    PASSED = "witness_preflight_passed"
    UNRESOLVED = "unresolved_witness_sampling"


class WitnessConstraintState(str, Enum):
    COMPATIBLE = "compatible_with_dependency_witnesses"
    VIOLATION = "violates_dependency_witness_constraint"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class HostSamplingSummary:
    independent_records: int
    unique_cells: int
    effective_cells: float


@dataclass(frozen=True)
class WitnessSamplingSummary:
    independent_records: int
    unique_cells: int


@dataclass(frozen=True)
class WitnessPreflightResult:
    state: WitnessPreflightState
    reasons: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.state is WitnessPreflightState.PASSED


@dataclass(frozen=True)
class WitnessConstraintResult:
    state: WitnessConstraintState
    reasons: tuple[str, ...]
    actual_containment: float
    control_q05: float | None
    control_q95: float | None
    host_support_fraction: float


def _validate_host_summary(summary: HostSamplingSummary) -> None:
    if summary.independent_records < 0:
        raise ValueError("host independent_records must be non-negative")
    if summary.unique_cells < 0:
        raise ValueError("host unique_cells must be non-negative")
    if not isfinite(summary.effective_cells) or summary.effective_cells < 0.0:
        raise ValueError("host effective_cells must be finite and non-negative")


def _validate_witness_summary(summary: WitnessSamplingSummary) -> None:
    if summary.independent_records < 0:
        raise ValueError("witness independent_records must be non-negative")
    if summary.unique_cells < 0:
        raise ValueError("witness unique_cells must be non-negative")
    if summary.unique_cells > summary.independent_records:
        raise ValueError("witness unique_cells cannot exceed independent_records")


def evaluate_witness_sampling_preflight(
    host: HostSamplingSummary,
    witness: WitnessSamplingSummary,
) -> WitnessPreflightResult:
    """Apply the frozen asymmetric v6 host/witness sampling floors."""

    _validate_host_summary(host)
    _validate_witness_summary(witness)
    reasons: list[str] = []

    if host.independent_records < HOST_MIN_RECORDS:
        reasons.append("host_independent_record_floor_failed")
    if host.unique_cells < HOST_MIN_UNIQUE_CELLS:
        reasons.append("host_unique_cell_floor_failed")
    if host.effective_cells < HOST_MIN_EFFECTIVE_CELLS:
        reasons.append("host_effective_cell_floor_failed")
    if witness.independent_records < WITNESS_MIN_RECORDS:
        reasons.append("witness_independent_record_floor_failed")
    if witness.unique_cells < WITNESS_MIN_UNIQUE_CELLS:
        reasons.append("witness_unique_cell_floor_failed")

    return WitnessPreflightResult(
        state=(
            WitnessPreflightState.UNRESOLVED
            if reasons
            else WitnessPreflightState.PASSED
        ),
        reasons=tuple(reasons),
    )


def _binary_indicator(value: object) -> float:
    if value is True:
        return 1.0
    if value is False:
        return 0.0
    if isinstance(value, (int, float)) and value in (0, 1, 0.0, 1.0):
        return float(value)
    raise ValueError("host support indicator values must be binary")


def _unique_witness_cells(witness_cells: Sequence[str]) -> tuple[str, ...]:
    cleaned = tuple(str(value).strip() for value in witness_cells)
    if not cleaned or any(not value for value in cleaned):
        raise ValueError("witness cells must be non-empty identifiers")
    return tuple(sorted(set(cleaned)))


def directed_witness_containment(
    host_support_indicator: Mapping[str, object],
    witness_cells: Sequence[str],
) -> float:
    """Fraction of unique dependent witness cells inside recovered X support."""

    cells = _unique_witness_cells(witness_cells)
    values: list[float] = []
    for cell in cells:
        if cell not in host_support_indicator:
            raise ValueError("witness cell absent from host audit support: " + cell)
        values.append(_binary_indicator(host_support_indicator[cell]))
    return mean(values)


def host_support_fraction(host_support_indicator: Mapping[str, object]) -> float:
    """Fraction of the full audit space classified as recovered host support."""

    if not host_support_indicator:
        raise ValueError("host support audit space must not be empty")
    return mean(_binary_indicator(value) for value in host_support_indicator.values())


def empirical_nearest_rank_quantile(values: Sequence[float], probability: float) -> float:
    """Deterministic nearest-rank empirical quantile.

    For p > 0, rank = ceil(p * n), using 1-based rank. p=0 returns the minimum.
    """

    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")
    converted = tuple(float(value) for value in values)
    if not converted:
        raise ValueError("quantile values must not be empty")
    if any(not isfinite(value) for value in converted):
        raise ValueError("quantile values must be finite")
    ordered = sorted(converted)
    if probability == 0.0:
        return ordered[0]
    rank = ceil(probability * len(ordered))
    return ordered[min(max(rank, 1), len(ordered)) - 1]


def classify_witness_constraint(
    *,
    preflight_passed: bool,
    actual_containment: float,
    shuffled_control_containments: Sequence[float],
    eligible_replacement_host_count: int,
    support_fraction: float,
) -> WitnessConstraintResult:
    """Three-state v6 classifier under the frozen shuffled-host contract."""

    actual = float(actual_containment)
    breadth = float(support_fraction)
    if not isfinite(actual) or not 0.0 <= actual <= 1.0:
        raise ValueError("actual_containment must lie in [0, 1]")
    if not isfinite(breadth) or not 0.0 <= breadth <= 1.0:
        raise ValueError("support_fraction must lie in [0, 1]")
    if eligible_replacement_host_count < 0:
        raise ValueError("eligible_replacement_host_count must be non-negative")

    controls = tuple(float(value) for value in shuffled_control_containments)
    if any(not isfinite(value) or not 0.0 <= value <= 1.0 for value in controls):
        raise ValueError("control containments must lie in [0, 1]")

    reasons: list[str] = []
    if not preflight_passed:
        reasons.append("witness_sampling_preflight_not_passed")
    if eligible_replacement_host_count < MINIMUM_REPLACEMENT_HOSTS:
        reasons.append("insufficient_eligible_replacement_hosts")
    if len(controls) != CONTROL_DRAW_COUNT:
        reasons.append("shuffled_control_draw_count_mismatch")
    if breadth > MAXIMUM_HOST_SUPPORT_FRACTION:
        reasons.append("host_support_breadth_guardrail_failed")

    if reasons:
        return WitnessConstraintResult(
            state=WitnessConstraintState.UNRESOLVED,
            reasons=tuple(reasons),
            actual_containment=actual,
            control_q05=None,
            control_q95=None,
            host_support_fraction=breadth,
        )

    q05 = empirical_nearest_rank_quantile(controls, LOWER_CONTROL_QUANTILE)
    q95 = empirical_nearest_rank_quantile(controls, UPPER_CONTROL_QUANTILE)

    if actual > q95:
        state = WitnessConstraintState.COMPATIBLE
        final_reasons = ("actual_containment_above_shuffled_q95",)
    elif actual < q05:
        state = WitnessConstraintState.VIOLATION
        final_reasons = ("actual_containment_below_shuffled_q05",)
    else:
        state = WitnessConstraintState.UNRESOLVED
        final_reasons = ("actual_containment_inside_shuffled_reference_band",)

    return WitnessConstraintResult(
        state=state,
        reasons=final_reasons,
        actual_containment=actual,
        control_q05=q05,
        control_q95=q95,
        host_support_fraction=breadth,
    )


def knockout_preferential_drop(
    *,
    actual_full_containment: float,
    actual_knockout_containment: float,
    shuffled_full_containments: Sequence[float],
    shuffled_knockout_containments: Sequence[float],
) -> float:
    """Actual process-knockout drop minus mean shuffled-host knockout drop."""

    actual_full = float(actual_full_containment)
    actual_knockout = float(actual_knockout_containment)
    for value in (actual_full, actual_knockout):
        if not isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("actual containments must lie in [0, 1]")

    full = tuple(float(value) for value in shuffled_full_containments)
    knockout = tuple(float(value) for value in shuffled_knockout_containments)
    if not full or len(full) != len(knockout):
        raise ValueError("shuffled full/knockout sequences must be non-empty and equal length")
    if any(
        not isfinite(value) or not 0.0 <= value <= 1.0
        for value in (*full, *knockout)
    ):
        raise ValueError("shuffled containments must lie in [0, 1]")

    actual_drop = actual_full - actual_knockout
    shuffled_drop = mean(a - b for a, b in zip(full, knockout))
    return actual_drop - shuffled_drop
