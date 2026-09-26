"""Pure response-blind preflight for Product-B v7 literature witnesses.

v7 never fits the dependent Y taxon. Independently published georeferenced Y
records are test-only witnesses. This module validates their provenance, frozen
sampling-cell support, the independence of the geographic evaluation frame, and
the non-retroactivity firewall. No network or occurrence access occurs here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Sequence

from product_b_v5.occurrence_preprocessing import sampling_cell_id
from product_b_v5.projection import wgs84_to_epsg6933
from product_b_v6.witness import WITNESS_MIN_RECORDS, WITNESS_MIN_UNIQUE_CELLS


MAXIMUM_WITNESS_UNCERTAINTY_M = 10_000.0
ALLOWED_COORDINATE_SOURCE_TYPES = {
    "primary_literature_text",
    "primary_literature_supplement",
}
ALLOWED_FRAME_SOURCE_TYPES = {
    "preexisting_admin_boundary",
    "protected_area_boundary",
    "ecoregion_boundary",
    "primary_literature_study_region_geometry",
}
ALLOWED_FRAME_GEOMETRY_TYPES = {
    "polygon_wkt",
    "multipolygon_wkt",
    "admin_codes",
    "protected_area_ids",
    "ecoregion_ids",
}
FIREWALLED_PAIR_IDS = frozenset(
    {
        "OPM_FIG_001",
        "OPM_YUC_001",
        "OPM_YUC_002",
        "OPM_GLO_001",
        "OPM_GLO_002",
        "OPM_GLO_003",
        "OPM_GLO_004",
        "SEN001",
        "EPV001",
        "HTR001",
    }
)


class LiteratureWitnessState(str, Enum):
    PASSED = "literature_witness_preflight_passed"
    UNRESOLVED = "unresolved_literature_witnesses"


@dataclass(frozen=True)
class LiteratureWitness:
    witness_id: str
    source_doi: str
    longitude: float
    latitude: float
    uncertainty_m: float
    coordinate_source_type: str


@dataclass(frozen=True)
class LiteratureWitnessPreflight:
    state: LiteratureWitnessState
    reasons: tuple[str, ...]
    raw_witness_count: int
    retained_witness_count: int
    excluded_witness_count: int
    duplicate_collapsed_count: int
    unique_10km_cells: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.state is LiteratureWitnessState.PASSED


@dataclass(frozen=True)
class FrameDeclaration:
    frame_id: str
    source_type: str
    source_authority: str
    source_version: str
    geometry_type: str
    geometry_value: str
    witness_coordinates_used_to_derive_geometry: bool
    occurrence_information_used_to_derive_geometry: bool


@dataclass(frozen=True)
class WitnessFramePreflight:
    pair_id: str
    witness_preflight: LiteratureWitnessPreflight
    frame_errors: tuple[str, ...]
    passed: bool


def validate_new_pair_id(pair_id: str) -> None:
    value = str(pair_id).strip()
    if not value:
        raise ValueError("pair_id must not be blank")
    if value in FIREWALLED_PAIR_IDS:
        raise ValueError("pair_id was admitted to a v5/v6 development endpoint and is firewalled")


def _normalize_witness(witness: LiteratureWitness) -> LiteratureWitness:
    witness_id = str(witness.witness_id).strip()
    doi = str(witness.source_doi).strip()
    source_type = str(witness.coordinate_source_type).strip()
    if not witness_id:
        raise ValueError("literature witness_id must not be blank")
    if not doi:
        raise ValueError("literature witness source_doi must not be blank")
    lon = float(witness.longitude)
    lat = float(witness.latitude)
    uncertainty = float(witness.uncertainty_m)
    if not isfinite(lon) or not isfinite(lat):
        raise ValueError("literature witness coordinate must be finite")
    if not (-180.0 <= lon <= 180.0 and -86.0 <= lat <= 86.0):
        raise ValueError("literature witness coordinate falls outside frozen projection domain")
    if not isfinite(uncertainty) or uncertainty < 0.0:
        raise ValueError("literature witness uncertainty must be finite and non-negative")
    if source_type not in ALLOWED_COORDINATE_SOURCE_TYPES:
        raise ValueError("literature witness coordinate must be printed in a primary source")
    return LiteratureWitness(
        witness_id=witness_id,
        source_doi=doi,
        longitude=lon,
        latitude=lat,
        uncertainty_m=uncertainty,
        coordinate_source_type=source_type,
    )


def _deduplicate_witness_ids(
    witnesses: Sequence[LiteratureWitness],
) -> tuple[tuple[LiteratureWitness, ...], int]:
    by_id: dict[str, LiteratureWitness] = {}
    duplicates = 0
    for raw in witnesses:
        witness = _normalize_witness(raw)
        existing = by_id.get(witness.witness_id)
        if existing is None:
            by_id[witness.witness_id] = witness
            continue
        if existing != witness:
            raise ValueError("duplicate literature witness_id has conflicting metadata")
        duplicates += 1
    return tuple(by_id[key] for key in sorted(by_id)), duplicates


def _cell_token(longitude: float, latitude: float) -> str:
    easting, northing = wgs84_to_epsg6933(longitude, latitude)
    cell = sampling_cell_id(easting, northing)
    return f"{cell[0]}:{cell[1]}"


def evaluate_literature_witness_preflight(
    witnesses: Sequence[LiteratureWitness],
) -> LiteratureWitnessPreflight:
    """Apply the unchanged v6 5-witness / 3-cell floor to primary-source points."""

    rows, duplicate_count = _deduplicate_witness_ids(tuple(witnesses))
    retained: list[LiteratureWitness] = []
    excluded = 0
    for witness in rows:
        if witness.uncertainty_m > MAXIMUM_WITNESS_UNCERTAINTY_M:
            excluded += 1
        else:
            retained.append(witness)

    cells = tuple(sorted({_cell_token(row.longitude, row.latitude) for row in retained}))
    reasons: list[str] = []
    if len(retained) < WITNESS_MIN_RECORDS:
        reasons.append("literature_witness_record_floor_failed")
    if len(cells) < WITNESS_MIN_UNIQUE_CELLS:
        reasons.append("literature_witness_unique_cell_floor_failed")

    return LiteratureWitnessPreflight(
        state=(LiteratureWitnessState.UNRESOLVED if reasons else LiteratureWitnessState.PASSED),
        reasons=tuple(reasons),
        raw_witness_count=len(tuple(witnesses)),
        retained_witness_count=len(retained),
        excluded_witness_count=excluded,
        duplicate_collapsed_count=duplicate_count,
        unique_10km_cells=cells,
    )


def validate_frame_declaration(frame: FrameDeclaration) -> tuple[str, ...]:
    errors: list[str] = []
    for field, value in (
        ("frame_id", frame.frame_id),
        ("source_authority", frame.source_authority),
        ("source_version", frame.source_version),
        ("geometry_value", frame.geometry_value),
    ):
        if not str(value).strip():
            errors.append(f"missing_{field}")
    if frame.source_type not in ALLOWED_FRAME_SOURCE_TYPES:
        errors.append("frame_source_type_not_allowed")
    if frame.geometry_type not in ALLOWED_FRAME_GEOMETRY_TYPES:
        errors.append("frame_geometry_type_not_allowed")
    if frame.witness_coordinates_used_to_derive_geometry:
        errors.append("witness_derived_frame_forbidden")
    if frame.occurrence_information_used_to_derive_geometry:
        errors.append("occurrence_derived_frame_forbidden")
    return tuple(errors)


def evaluate_witness_frame_preflight(
    *,
    pair_id: str,
    witnesses: Sequence[LiteratureWitness],
    frame: FrameDeclaration,
) -> WitnessFramePreflight:
    validate_new_pair_id(pair_id)
    witness_preflight = evaluate_literature_witness_preflight(witnesses)
    frame_errors = validate_frame_declaration(frame)
    return WitnessFramePreflight(
        pair_id=str(pair_id).strip(),
        witness_preflight=witness_preflight,
        frame_errors=frame_errors,
        passed=witness_preflight.passed and not frame_errors,
    )
