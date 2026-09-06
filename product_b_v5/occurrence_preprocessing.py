"""Pure occurrence preprocessing for the Product-B v5 sampling preflight.

This module deliberately performs no network access, taxonomy lookup, CRS lookup,
or occurrence search.  It accepts already-retrieved records with already-projected
EPSG:6933 coordinates, applies the frozen quality/collision rules, and produces
sampling summaries for :mod:`product_b_v5.sampling`.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from math import floor, isfinite
import re
import unicodedata
from typing import Sequence

from .sampling import (
    PRIMARY_THRESHOLDS,
    SamplingPreflightResult,
    SamplingSummary,
    SamplingThresholds,
    evaluate_sampling_pair,
    inverse_simpson_effective_cells,
)


DEFAULT_CELL_EDGE_M = 10_000.0
DEFAULT_MAXIMUM_KNOWN_UNCERTAINTY_M = 10_000.0
_EVENT_DAY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


@dataclass(frozen=True)
class OccurrenceRecord:
    """One source occurrence row after adapter-level field extraction.

    ``projected_easting_m`` and ``projected_northing_m`` must already be EPSG:6933
    metres.  Requiring the projection outside this pure module prevents hidden CRS
    lookups and keeps the audit transformation deterministic and unit-testable.
    """

    row_id: str
    partner: str
    decimal_latitude: float | None
    decimal_longitude: float | None
    projected_easting_m: float | None
    projected_northing_m: float | None
    occurrence_id_lineage: str = ""
    event_id: str = ""
    catalog_or_specimen_number: str = ""
    dataset_key: str = ""
    event_date: str = ""
    recorder: str = ""
    coordinate_uncertainty_m: float | None = None


@dataclass(frozen=True)
class CollisionComponent:
    row_ids: tuple[str, ...]
    partners: tuple[str, ...]
    witness_types: tuple[str, ...]


@dataclass(frozen=True)
class PreprocessingAudit:
    raw_records_x: int
    raw_records_y: int
    quality_excluded_x: int
    quality_excluded_y: int
    quality_exclusion_reason_counts: tuple[tuple[str, int], ...]
    missing_uncertainty_x: int
    missing_uncertainty_y: int
    collision_excluded_x: int
    collision_excluded_y: int
    collision_components: tuple[CollisionComponent, ...]
    retained_records_x: int
    retained_records_y: int
    unique_cells_x: int
    unique_cells_y: int
    effective_cells_x: float
    effective_cells_y: float


@dataclass(frozen=True)
class OccurrenceSamplingPreflight:
    x_summary: SamplingSummary
    y_summary: SamplingSummary
    sampling_result: SamplingPreflightResult
    audit: PreprocessingAudit


class _UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, a: int, b: int) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1


def _identifier(value: str) -> str:
    return value.strip()


def _recorder(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return " ".join(normalized.split()).casefold()


def canonical_event_day(value: str) -> str:
    """Return a validated YYYY-MM-DD prefix or an empty unavailable marker."""

    match = _EVENT_DAY_RE.match(value.strip())
    if match is None:
        return ""
    candidate = match.group(1)
    try:
        date.fromisoformat(candidate)
    except ValueError:
        return ""
    return candidate


def _format_coordinate_component(value: float) -> str:
    if abs(value) < 0.000005:
        value = 0.0
    return f"{value:.5f}"


def canonical_coordinate_key(
    latitude: float | None, longitude: float | None
) -> str:
    """Return the frozen five-decimal WGS84 identity key, or empty if invalid."""

    if latitude is None or longitude is None:
        return ""
    lat = float(latitude)
    lon = float(longitude)
    if not isfinite(lat) or not isfinite(lon):
        return ""
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return ""
    return f"{_format_coordinate_component(lat)},{_format_coordinate_component(lon)}"


def occurrence_identity_witnesses(
    record: OccurrenceRecord,
) -> tuple[tuple[str, str], ...]:
    """Return all available frozen identity witnesses for one record."""

    witnesses: list[tuple[str, str]] = []
    for witness_type, raw_value in (
        ("occurrence_id_lineage", record.occurrence_id_lineage),
        ("event_id", record.event_id),
        ("catalog_or_specimen_number", record.catalog_or_specimen_number),
    ):
        value = _identifier(raw_value)
        if value:
            witnesses.append((witness_type, value))

    event_day = canonical_event_day(record.event_date)
    coordinate_key = canonical_coordinate_key(
        record.decimal_latitude, record.decimal_longitude
    )
    dataset_key = _identifier(record.dataset_key)
    if dataset_key and event_day and coordinate_key:
        witnesses.append(
            (
                "dataset_key_plus_event_day_plus_coordinate_key",
                "|".join((dataset_key, event_day, coordinate_key)),
            )
        )

    recorder = _recorder(record.recorder)
    if recorder and event_day and coordinate_key:
        witnesses.append(
            (
                "recorder_plus_event_day_plus_coordinate_key",
                "|".join((recorder, event_day, coordinate_key)),
            )
        )

    return tuple(witnesses)


def occurrence_quality_reasons(
    record: OccurrenceRecord,
    *,
    maximum_known_uncertainty_m: float = DEFAULT_MAXIMUM_KNOWN_UNCERTAINTY_M,
) -> tuple[str, ...]:
    """Return exclusion reasons from the frozen coordinate-quality contract."""

    if not isfinite(maximum_known_uncertainty_m) or maximum_known_uncertainty_m <= 0:
        raise ValueError("maximum_known_uncertainty_m must be finite and positive")

    reasons: list[str] = []
    lat = record.decimal_latitude
    lon = record.decimal_longitude
    if lat is None or lon is None:
        reasons.append("missing_decimal_coordinate")
    else:
        lat_value = float(lat)
        lon_value = float(lon)
        if not isfinite(lat_value) or not isfinite(lon_value):
            reasons.append("nonfinite_decimal_coordinate")
        elif not (-90.0 <= lat_value <= 90.0 and -180.0 <= lon_value <= 180.0):
            reasons.append("decimal_coordinate_out_of_range")

    east = record.projected_easting_m
    north = record.projected_northing_m
    if east is None or north is None:
        reasons.append("missing_projected_coordinate")
    elif not isfinite(float(east)) or not isfinite(float(north)):
        reasons.append("nonfinite_projected_coordinate")

    uncertainty = record.coordinate_uncertainty_m
    if uncertainty is not None:
        value = float(uncertainty)
        if not isfinite(value) or value < 0.0:
            reasons.append("invalid_coordinate_uncertainty")
        elif value > maximum_known_uncertainty_m:
            reasons.append("coordinate_uncertainty_ceiling_failed")

    return tuple(reasons)


def sampling_cell_id(
    projected_easting_m: float,
    projected_northing_m: float,
    *,
    edge_m: float = DEFAULT_CELL_EDGE_M,
) -> tuple[int, int]:
    """Index the frozen equal-area grid with a zero-origin floor rule."""

    east = float(projected_easting_m)
    north = float(projected_northing_m)
    if not isfinite(east) or not isfinite(north):
        raise ValueError("projected coordinates must be finite")
    if not isfinite(edge_m) or edge_m <= 0.0:
        raise ValueError("edge_m must be finite and positive")
    return floor(east / edge_m), floor(north / edge_m)


def _validate_records(records: Sequence[OccurrenceRecord]) -> tuple[OccurrenceRecord, ...]:
    converted = tuple(records)
    row_ids = [record.row_id for record in converted]
    if any(not value.strip() for value in row_ids):
        raise ValueError("row_id must not be blank")
    if len(set(row_ids)) != len(row_ids):
        raise ValueError("row_id values must be unique")
    invalid_partners = sorted({record.partner for record in converted} - {"x", "y"})
    if invalid_partners:
        raise ValueError("partner must be x or y: " + ",".join(invalid_partners))
    return converted


def cross_partner_collision_components(
    records: Sequence[OccurrenceRecord],
) -> tuple[CollisionComponent, ...]:
    """Find cross-partner connected components over all identity witnesses.

    Connected-component closure is intentional.  If A shares an event with B and B
    shares a different declared identity with C, the entire A-B-C component is
    excluded when it contains both partners.
    """

    rows = _validate_records(records)
    if not rows:
        return ()

    token_to_indices: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, record in enumerate(rows):
        for token in occurrence_identity_witnesses(record):
            token_to_indices[token].append(index)

    union_find = _UnionFind(len(rows))
    for indices in token_to_indices.values():
        if len(indices) < 2:
            continue
        anchor = indices[0]
        for index in indices[1:]:
            union_find.union(anchor, index)

    members: dict[int, list[int]] = defaultdict(list)
    for index in range(len(rows)):
        members[union_find.find(index)].append(index)

    witness_types: dict[int, set[str]] = defaultdict(set)
    for (witness_type, _), indices in token_to_indices.items():
        if len(indices) < 2:
            continue
        root = union_find.find(indices[0])
        witness_types[root].add(witness_type)

    components: list[CollisionComponent] = []
    for root, indices in members.items():
        partners = {rows[index].partner for index in indices}
        if partners != {"x", "y"}:
            continue
        components.append(
            CollisionComponent(
                row_ids=tuple(sorted(rows[index].row_id for index in indices)),
                partners=("x", "y"),
                witness_types=tuple(sorted(witness_types[root])),
            )
        )

    return tuple(sorted(components, key=lambda component: component.row_ids))


def _sampling_summary(
    *,
    all_records: Sequence[OccurrenceRecord],
    retained_records: Sequence[OccurrenceRecord],
    collision_excluded_ids: set[str],
    partner: str,
    edge_m: float,
) -> SamplingSummary:
    partner_raw = [record for record in all_records if record.partner == partner]
    partner_retained = [
        record for record in retained_records if record.partner == partner
    ]

    cell_counts: Counter[tuple[int, int]] = Counter()
    for record in partner_retained:
        assert record.projected_easting_m is not None
        assert record.projected_northing_m is not None
        cell_counts[
            sampling_cell_id(
                record.projected_easting_m,
                record.projected_northing_m,
                edge_m=edge_m,
            )
        ] += 1

    effective_cells = (
        inverse_simpson_effective_cells(tuple(cell_counts.values()))
        if cell_counts
        else 0.0
    )
    collision_count = sum(
        1
        for record in partner_raw
        if record.row_id in collision_excluded_ids
    )

    return SamplingSummary(
        independent_records=len(partner_retained),
        unique_cells=len(cell_counts),
        effective_cells=effective_cells,
        raw_records=len(partner_raw),
        collision_excluded_records=collision_count,
    )


def build_occurrence_sampling_preflight(
    records: Sequence[OccurrenceRecord],
    *,
    taxonomy_eligible: bool,
    thresholds: SamplingThresholds = PRIMARY_THRESHOLDS,
    edge_m: float = DEFAULT_CELL_EDGE_M,
    maximum_known_uncertainty_m: float = DEFAULT_MAXIMUM_KNOWN_UNCERTAINTY_M,
) -> OccurrenceSamplingPreflight:
    """Apply frozen preprocessing and then the existing sampling gate.

    This is still a pure transformation: callers must obtain explicit occurrence
    execution authorization before fetching or constructing empirical input rows.
    """

    rows = _validate_records(records)
    if not isfinite(edge_m) or edge_m <= 0.0:
        raise ValueError("edge_m must be finite and positive")

    quality_reason_counts: Counter[str] = Counter()
    quality_excluded_ids: set[str] = set()
    quality_eligible: list[OccurrenceRecord] = []
    for record in rows:
        reasons = occurrence_quality_reasons(
            record,
            maximum_known_uncertainty_m=maximum_known_uncertainty_m,
        )
        if reasons:
            quality_excluded_ids.add(record.row_id)
            quality_reason_counts.update(reasons)
        else:
            quality_eligible.append(record)

    components = cross_partner_collision_components(quality_eligible)
    collision_excluded_ids = {
        row_id
        for component in components
        for row_id in component.row_ids
    }
    retained = [
        record
        for record in quality_eligible
        if record.row_id not in collision_excluded_ids
    ]

    x_summary = _sampling_summary(
        all_records=rows,
        retained_records=retained,
        collision_excluded_ids=collision_excluded_ids,
        partner="x",
        edge_m=edge_m,
    )
    y_summary = _sampling_summary(
        all_records=rows,
        retained_records=retained,
        collision_excluded_ids=collision_excluded_ids,
        partner="y",
        edge_m=edge_m,
    )
    sampling_result = evaluate_sampling_pair(
        x_summary,
        y_summary,
        taxonomy_eligible=taxonomy_eligible,
        thresholds=thresholds,
    )

    def _count(records_set: set[str], partner: str) -> int:
        return sum(
            1
            for record in rows
            if record.partner == partner and record.row_id in records_set
        )

    missing_uncertainty_x = sum(
        1
        for record in rows
        if record.partner == "x" and record.coordinate_uncertainty_m is None
    )
    missing_uncertainty_y = sum(
        1
        for record in rows
        if record.partner == "y" and record.coordinate_uncertainty_m is None
    )

    audit = PreprocessingAudit(
        raw_records_x=sum(record.partner == "x" for record in rows),
        raw_records_y=sum(record.partner == "y" for record in rows),
        quality_excluded_x=_count(quality_excluded_ids, "x"),
        quality_excluded_y=_count(quality_excluded_ids, "y"),
        quality_exclusion_reason_counts=tuple(sorted(quality_reason_counts.items())),
        missing_uncertainty_x=missing_uncertainty_x,
        missing_uncertainty_y=missing_uncertainty_y,
        collision_excluded_x=_count(collision_excluded_ids, "x"),
        collision_excluded_y=_count(collision_excluded_ids, "y"),
        collision_components=components,
        retained_records_x=x_summary.independent_records,
        retained_records_y=y_summary.independent_records,
        unique_cells_x=x_summary.unique_cells,
        unique_cells_y=y_summary.unique_cells,
        effective_cells_x=x_summary.effective_cells,
        effective_cells_y=y_summary.effective_cells,
    )

    return OccurrenceSamplingPreflight(
        x_summary=x_summary,
        y_summary=y_summary,
        sampling_result=sampling_result,
        audit=audit,
    )
