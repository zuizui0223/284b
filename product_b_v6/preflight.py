"""Pure occurrence-to-witness sampling preflight for Product-B v6.

No network access occurs here. The module reuses the frozen v5 occurrence quality,
projection/cell, and cross-partner collision semantics but evaluates the asymmetric
v6 sampling contract: a recoverable required host X and sparse dependent Y witness
cells. Y is never fit as a niche by this module.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Mapping, Sequence

from product_b_v5.occurrence_adapter import AdaptedOccurrenceBatch, adapt_gbif_pair_rows
from product_b_v5.occurrence_preprocessing import (
    DEFAULT_CELL_EDGE_M,
    DEFAULT_MAXIMUM_KNOWN_UNCERTAINTY_M,
    CollisionComponent,
    OccurrenceRecord,
    cross_partner_collision_components,
    occurrence_quality_reasons,
    sampling_cell_id,
)
from product_b_v5.sampling import inverse_simpson_effective_cells

from .witness import (
    HostSamplingSummary,
    WitnessPreflightResult,
    WitnessSamplingSummary,
    evaluate_witness_sampling_preflight,
)


@dataclass(frozen=True)
class DirectedWitnessSamplingAudit:
    raw_records_x: int
    raw_records_y: int
    quality_excluded_x: int
    quality_excluded_y: int
    quality_exclusion_reason_counts: tuple[tuple[str, int], ...]
    collision_excluded_x: int
    collision_excluded_y: int
    collision_components: tuple[CollisionComponent, ...]
    retained_records_x: int
    retained_records_y: int
    host_unique_cells: int
    host_effective_cells: float
    witness_unique_cells: int


@dataclass(frozen=True)
class DirectedWitnessSamplingPreflight:
    host_summary: HostSamplingSummary
    witness_summary: WitnessSamplingSummary
    unique_witness_cells: tuple[str, ...]
    preflight: WitnessPreflightResult
    audit: DirectedWitnessSamplingAudit


def _cell_token(cell: tuple[int, int]) -> str:
    return f"{cell[0]}:{cell[1]}"


def build_directed_witness_sampling_preflight_from_records(
    records: Sequence[OccurrenceRecord],
    *,
    edge_m: float = DEFAULT_CELL_EDGE_M,
    maximum_known_uncertainty_m: float = DEFAULT_MAXIMUM_KNOWN_UNCERTAINTY_M,
) -> DirectedWitnessSamplingPreflight:
    """Apply frozen v5 preprocessing, then the asymmetric v6 witness floors."""

    rows = tuple(records)
    row_ids = tuple(record.row_id for record in rows)
    if any(not value.strip() for value in row_ids):
        raise ValueError("row_id must not be blank")
    if len(set(row_ids)) != len(row_ids):
        raise ValueError("row_id values must be unique")
    if set(record.partner for record in rows) - {"x", "y"}:
        raise ValueError("partner must be x or y")

    quality_reason_counts: Counter[str] = Counter()
    quality_eligible: list[OccurrenceRecord] = []
    quality_excluded_ids: set[str] = set()
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
        row_id for component in components for row_id in component.row_ids
    }
    retained = tuple(
        record
        for record in quality_eligible
        if record.row_id not in collision_excluded_ids
    )

    host_records = tuple(record for record in retained if record.partner == "x")
    witness_records = tuple(record for record in retained if record.partner == "y")

    host_cell_counts: Counter[tuple[int, int]] = Counter()
    for record in host_records:
        if record.projected_easting_m is None or record.projected_northing_m is None:
            raise ValueError("quality-retained host record lacks projected coordinate")
        host_cell_counts[
            sampling_cell_id(
                record.projected_easting_m,
                record.projected_northing_m,
                edge_m=edge_m,
            )
        ] += 1

    witness_cells: set[tuple[int, int]] = set()
    for record in witness_records:
        if record.projected_easting_m is None or record.projected_northing_m is None:
            raise ValueError("quality-retained witness record lacks projected coordinate")
        witness_cells.add(
            sampling_cell_id(
                record.projected_easting_m,
                record.projected_northing_m,
                edge_m=edge_m,
            )
        )

    host_effective = (
        inverse_simpson_effective_cells(tuple(host_cell_counts.values()))
        if host_cell_counts
        else 0.0
    )
    host_summary = HostSamplingSummary(
        independent_records=len(host_records),
        unique_cells=len(host_cell_counts),
        effective_cells=host_effective,
    )
    witness_summary = WitnessSamplingSummary(
        independent_records=len(witness_records),
        unique_cells=len(witness_cells),
    )

    raw_x = sum(record.partner == "x" for record in rows)
    raw_y = sum(record.partner == "y" for record in rows)
    quality_x = sum(
        record.partner == "x" and record.row_id in quality_excluded_ids
        for record in rows
    )
    quality_y = sum(
        record.partner == "y" and record.row_id in quality_excluded_ids
        for record in rows
    )
    collision_x = sum(
        record.partner == "x" and record.row_id in collision_excluded_ids
        for record in quality_eligible
    )
    collision_y = sum(
        record.partner == "y" and record.row_id in collision_excluded_ids
        for record in quality_eligible
    )

    audit = DirectedWitnessSamplingAudit(
        raw_records_x=raw_x,
        raw_records_y=raw_y,
        quality_excluded_x=quality_x,
        quality_excluded_y=quality_y,
        quality_exclusion_reason_counts=tuple(sorted(quality_reason_counts.items())),
        collision_excluded_x=collision_x,
        collision_excluded_y=collision_y,
        collision_components=components,
        retained_records_x=len(host_records),
        retained_records_y=len(witness_records),
        host_unique_cells=len(host_cell_counts),
        host_effective_cells=host_effective,
        witness_unique_cells=len(witness_cells),
    )
    return DirectedWitnessSamplingPreflight(
        host_summary=host_summary,
        witness_summary=witness_summary,
        unique_witness_cells=tuple(sorted(_cell_token(cell) for cell in witness_cells)),
        preflight=evaluate_witness_sampling_preflight(host_summary, witness_summary),
        audit=audit,
    )


def adapt_and_build_directed_witness_sampling_preflight(
    *,
    x_rows: Sequence[Mapping[str, object]],
    y_rows: Sequence[Mapping[str, object]],
) -> tuple[AdaptedOccurrenceBatch, DirectedWitnessSamplingPreflight]:
    """Adapt complete raw GBIF rows, then run the pure v6 sampling preflight."""

    adapted = adapt_gbif_pair_rows(x_rows=x_rows, y_rows=y_rows)
    return adapted, build_directed_witness_sampling_preflight_from_records(adapted.records)
