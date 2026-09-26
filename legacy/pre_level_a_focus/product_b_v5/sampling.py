"""Pure Product-B v5 sampling-availability preflight functions.

These functions accept synthetic or already-computed summaries. They do not fetch,
search, map, or count occurrences themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Mapping, Sequence


class SamplingState(str, Enum):
    PASSED = "sampling_preflight_passed"
    UNRESOLVED = "unresolved_sampling"


@dataclass(frozen=True)
class SamplingThresholds:
    minimum_independent_records: int
    minimum_unique_cells: int
    minimum_effective_cells: float
    maximum_record_asymmetry_ratio: float
    maximum_unique_cell_asymmetry_ratio: float
    maximum_effective_cell_asymmetry_ratio: float


PRIMARY_THRESHOLDS = SamplingThresholds(
    minimum_independent_records=50,
    minimum_unique_cells=30,
    minimum_effective_cells=10.0,
    maximum_record_asymmetry_ratio=10.0,
    maximum_unique_cell_asymmetry_ratio=5.0,
    maximum_effective_cell_asymmetry_ratio=5.0,
)

STRICT_SENSITIVITY_THRESHOLDS = SamplingThresholds(
    minimum_independent_records=100,
    minimum_unique_cells=50,
    minimum_effective_cells=20.0,
    maximum_record_asymmetry_ratio=5.0,
    maximum_unique_cell_asymmetry_ratio=3.0,
    maximum_effective_cell_asymmetry_ratio=3.0,
)


@dataclass(frozen=True)
class SamplingSummary:
    independent_records: int
    unique_cells: int
    effective_cells: float
    raw_records: int | None = None
    collision_excluded_records: int = 0


@dataclass(frozen=True)
class SamplingPreflightResult:
    state: SamplingState
    reasons: tuple[str, ...]
    record_asymmetry_ratio: float | None
    unique_cell_asymmetry_ratio: float | None
    effective_cell_asymmetry_ratio: float | None

    @property
    def passed(self) -> bool:
        return self.state is SamplingState.PASSED


@dataclass(frozen=True)
class RecordIdentity:
    occurrence_id_lineage: str = ""
    event_id: str = ""
    catalog_or_specimen_number: str = ""
    dataset_key: str = ""
    event_date: str = ""
    coordinate_key: str = ""
    recorder: str = ""


def _clean(value: str) -> str:
    return value.strip()


def _same_nonempty(a: str, b: str) -> bool:
    return bool(_clean(a)) and _clean(a) == _clean(b)


def cross_partner_collision_reasons(
    x: RecordIdentity, y: RecordIdentity
) -> tuple[str, ...]:
    """Return declared same-record collision witnesses for one cross-partner pair."""

    reasons: list[str] = []
    if _same_nonempty(x.occurrence_id_lineage, y.occurrence_id_lineage):
        reasons.append("occurrence_id_lineage")
    if _same_nonempty(x.event_id, y.event_id):
        reasons.append("event_id")
    if _same_nonempty(
        x.catalog_or_specimen_number, y.catalog_or_specimen_number
    ):
        reasons.append("catalog_or_specimen_number")

    same_dataset_date_coordinate = (
        _same_nonempty(x.dataset_key, y.dataset_key)
        and _same_nonempty(x.event_date, y.event_date)
        and _same_nonempty(x.coordinate_key, y.coordinate_key)
    )
    if same_dataset_date_coordinate:
        reasons.append("dataset_key_plus_event_date_plus_coordinate")

    same_recorder_date_coordinate = (
        _same_nonempty(x.recorder, y.recorder)
        and _same_nonempty(x.event_date, y.event_date)
        and _same_nonempty(x.coordinate_key, y.coordinate_key)
    )
    if same_recorder_date_coordinate:
        reasons.append("recorder_plus_date_plus_coordinate")

    return tuple(reasons)


def inverse_simpson_effective_cells(
    cell_record_counts: Sequence[int],
) -> float:
    """Effective occupied-cell count from non-negative integer record counts."""

    counts = tuple(int(value) for value in cell_record_counts)
    if not counts:
        raise ValueError("cell_record_counts must not be empty")
    if any(value < 0 for value in counts):
        raise ValueError("cell_record_counts must be non-negative")
    total = sum(counts)
    if total <= 0:
        raise ValueError("cell_record_counts must contain positive total mass")

    probabilities = (value / total for value in counts if value > 0)
    concentration = sum(value * value for value in probabilities)
    return 1.0 / concentration


def _validate_thresholds(thresholds: SamplingThresholds) -> None:
    if thresholds.minimum_independent_records < 1:
        raise ValueError("minimum_independent_records must be positive")
    if thresholds.minimum_unique_cells < 1:
        raise ValueError("minimum_unique_cells must be positive")
    if (
        not isfinite(thresholds.minimum_effective_cells)
        or thresholds.minimum_effective_cells <= 0.0
    ):
        raise ValueError("minimum_effective_cells must be finite and positive")
    for name, value in {
        "maximum_record_asymmetry_ratio": thresholds.maximum_record_asymmetry_ratio,
        "maximum_unique_cell_asymmetry_ratio": thresholds.maximum_unique_cell_asymmetry_ratio,
        "maximum_effective_cell_asymmetry_ratio": thresholds.maximum_effective_cell_asymmetry_ratio,
    }.items():
        if not isfinite(value) or value < 1.0:
            raise ValueError(f"{name} must be finite and at least 1")


def _validate_summary(summary: SamplingSummary) -> None:
    if summary.independent_records < 0:
        raise ValueError("independent_records must be non-negative")
    if summary.unique_cells < 0:
        raise ValueError("unique_cells must be non-negative")
    if not isfinite(summary.effective_cells) or summary.effective_cells < 0.0:
        raise ValueError("effective_cells must be finite and non-negative")
    if summary.collision_excluded_records < 0:
        raise ValueError("collision_excluded_records must be non-negative")
    if summary.raw_records is not None:
        if summary.raw_records < 0:
            raise ValueError("raw_records must be non-negative")
        if summary.independent_records + summary.collision_excluded_records > summary.raw_records:
            raise ValueError("retained plus collision-excluded records cannot exceed raw_records")


def asymmetry_ratio(a: float, b: float) -> float | None:
    """Return max/min; zero denominators are unresolved and represented as None."""

    if not isfinite(a) or not isfinite(b) or a < 0.0 or b < 0.0:
        raise ValueError("asymmetry inputs must be finite and non-negative")
    if min(a, b) <= 0.0:
        return None
    return max(a, b) / min(a, b)


def evaluate_sampling_pair(
    x: SamplingSummary,
    y: SamplingSummary,
    *,
    taxonomy_eligible: bool,
    thresholds: SamplingThresholds = PRIMARY_THRESHOLDS,
) -> SamplingPreflightResult:
    """Apply frozen sampling floors/ceilings to already-computed summaries."""

    _validate_thresholds(thresholds)
    _validate_summary(x)
    _validate_summary(y)

    reasons: list[str] = []
    if not taxonomy_eligible:
        reasons.append("taxonomy_gate_not_passed")

    for label, summary in (("x", x), ("y", y)):
        if summary.independent_records < thresholds.minimum_independent_records:
            reasons.append(f"{label}_independent_record_floor_failed")
        if summary.unique_cells < thresholds.minimum_unique_cells:
            reasons.append(f"{label}_unique_cell_floor_failed")
        if summary.effective_cells < thresholds.minimum_effective_cells:
            reasons.append(f"{label}_effective_cell_floor_failed")

    record_ratio = asymmetry_ratio(x.independent_records, y.independent_records)
    unique_ratio = asymmetry_ratio(x.unique_cells, y.unique_cells)
    effective_ratio = asymmetry_ratio(x.effective_cells, y.effective_cells)

    if record_ratio is None:
        reasons.append("record_asymmetry_unresolved_zero_denominator")
    elif record_ratio > thresholds.maximum_record_asymmetry_ratio:
        reasons.append("record_asymmetry_ceiling_failed")

    if unique_ratio is None:
        reasons.append("unique_cell_asymmetry_unresolved_zero_denominator")
    elif unique_ratio > thresholds.maximum_unique_cell_asymmetry_ratio:
        reasons.append("unique_cell_asymmetry_ceiling_failed")

    if effective_ratio is None:
        reasons.append("effective_cell_asymmetry_unresolved_zero_denominator")
    elif effective_ratio > thresholds.maximum_effective_cell_asymmetry_ratio:
        reasons.append("effective_cell_asymmetry_ceiling_failed")

    return SamplingPreflightResult(
        state=SamplingState.UNRESOLVED if reasons else SamplingState.PASSED,
        reasons=tuple(reasons),
        record_asymmetry_ratio=record_ratio,
        unique_cell_asymmetry_ratio=unique_ratio,
        effective_cell_asymmetry_ratio=effective_ratio,
    )
