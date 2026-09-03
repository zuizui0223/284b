"""One-shot Product-B v5 sampling-preflight orchestration.

The committed repository still has no real network transport and the committed
manifest remains unauthorized. This module makes the later authorized execution
mechanical: one frozen pair spec, both partner reads, post-fetch scope validation,
raw alias closure, and simultaneous primary/strict sampling decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import re
from typing import Mapping, Sequence

from .authorization import AuthorizationDecision, require_execution_authorization
from .occurrence_adapter import AdaptedOccurrenceBatch, adapt_gbif_pair_rows
from .occurrence_preprocessing import (
    OccurrenceSamplingPreflight,
    build_occurrence_sampling_preflight,
)
from .occurrence_source import (
    LogicalOccurrenceQuery,
    OccurrenceTransport,
    build_logical_occurrence_query,
    execute_guarded_occurrence_read,
)
from .sampling import PRIMARY_THRESHOLDS, STRICT_SENSITIVITY_THRESHOLDS
from .scope import GeographicScopeDeclaration


@dataclass(frozen=True)
class FrozenPairExecutionSpec:
    pair_id: str
    x_taxon_key: str
    y_taxon_key: str


OPM_FIG_001_SPEC = FrozenPairExecutionSpec(
    pair_id="OPM_FIG_001",
    x_taxon_key="5361904",
    y_taxon_key="1359124",
)


@dataclass(frozen=True)
class PairSamplingExecutionResult:
    authorization: AuthorizationDecision
    x_query: LogicalOccurrenceQuery
    y_query: LogicalOccurrenceQuery
    adapted_batch: AdaptedOccurrenceBatch
    primary: OccurrenceSamplingPreflight
    strict_sensitivity: OccurrenceSamplingPreflight


_POLYGON_RE = re.compile(
    r"^\s*POLYGON\s*\(\(\s*(.*?)\s*\)\)\s*$",
    flags=re.IGNORECASE,
)


def _polygon_ring(wkt: str) -> tuple[tuple[float, float], ...]:
    match = _POLYGON_RE.match(wkt)
    if match is None:
        raise ValueError("post-fetch scope validation requires single-ring POLYGON WKT")
    ring: list[tuple[float, float]] = []
    for raw_point in match.group(1).split(","):
        pieces = raw_point.strip().split()
        if len(pieces) != 2:
            raise ValueError("invalid polygon coordinate")
        lon, lat = float(pieces[0]), float(pieces[1])
        ring.append((lon, lat))
    if len(ring) < 4 or ring[0] != ring[-1]:
        raise ValueError("polygon ring must be closed")
    return tuple(ring)


def _point_on_segment(
    point: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float],
    *,
    tolerance: float = 1e-10,
) -> bool:
    px, py = point
    ax, ay = a
    bx, by = b
    cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
    if abs(cross) > tolerance:
        return False
    dot = (px - ax) * (px - bx) + (py - ay) * (py - by)
    return dot <= tolerance


def point_in_polygon_wkt(longitude: float, latitude: float, wkt: str) -> bool:
    """Boundary-inclusive ray-cast used only to audit returned GBIF rows."""

    lon = float(longitude)
    lat = float(latitude)
    if not isfinite(lon) or not isfinite(lat):
        return False
    ring = _polygon_ring(wkt)
    point = (lon, lat)
    inside = False
    for a, b in zip(ring, ring[1:]):
        if _point_on_segment(point, a, b):
            return True
        ax, ay = a
        bx, by = b
        crosses = (ay > lat) != (by > lat)
        if crosses:
            intersection_lon = (bx - ax) * (lat - ay) / (by - ay) + ax
            if lon < intersection_lon:
                inside = not inside
    return inside


def validate_returned_rows_against_query(
    query: LogicalOccurrenceQuery,
    rows: Sequence[Mapping[str, object]],
) -> None:
    """Detect a transport/query mismatch before sampling preprocessing.

    Malformed/missing coordinates remain quality-audit inputs downstream. A valid
    coordinate demonstrably outside the frozen polygon, however, means the
    transport did not honour the frozen geographic query and the execution stops.
    """

    if query.geographic_filter_type != "polygon_wkt":
        raise ValueError("v0.2 post-fetch validation only supports polygon_wkt")

    for row in rows:
        row_id = str(row.get("key", "<missing-key>"))
        status = row.get("occurrenceStatus")
        if status is not None and str(status) != "PRESENT":
            raise ValueError("returned occurrence violates PRESENT filter: " + row_id)

        raw_lat = row.get("decimalLatitude")
        raw_lon = row.get("decimalLongitude")
        try:
            lat = float(raw_lat) if raw_lat is not None else None
            lon = float(raw_lon) if raw_lon is not None else None
        except (TypeError, ValueError):
            continue
        if lat is None or lon is None or not isfinite(lat) or not isfinite(lon):
            continue
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            continue
        if not point_in_polygon_wkt(lon, lat, query.geographic_filter_value):
            raise ValueError("returned occurrence lies outside frozen query geometry: " + row_id)


def execute_frozen_pair_sampling_preflight(
    *,
    manifest: Mapping[str, object],
    scope_declarations: Sequence[GeographicScopeDeclaration],
    transport: OccurrenceTransport,
    spec: FrozenPairExecutionSpec = OPM_FIG_001_SPEC,
) -> PairSamplingExecutionResult:
    """Execute the complete sampling preflight only after explicit authorization.

    No custom thresholds are accepted here: the primary and stricter sensitivity
    contracts are both computed from the exact same retained records. The current
    contract admits exactly OPM_FIG_001; a new pair requires a new frozen version.
    """

    if spec != OPM_FIG_001_SPEC:
        raise ValueError("execution spec differs from the currently frozen OPM_FIG_001 spec")

    authorization = require_execution_authorization(
        manifest,
        requested_pair_ids=[spec.pair_id],
    )
    if spec.pair_id not in authorization.taxonomy_eligible_pair_ids:
        raise ValueError("frozen execution spec is not taxonomy eligible")

    x_query = build_logical_occurrence_query(
        pair_id=spec.pair_id,
        partner="x",
        taxon_key=spec.x_taxon_key,
        scope_declarations=scope_declarations,
    )
    y_query = build_logical_occurrence_query(
        pair_id=spec.pair_id,
        partner="y",
        taxon_key=spec.y_taxon_key,
        scope_declarations=scope_declarations,
    )

    _, x_rows = execute_guarded_occurrence_read(
        manifest=manifest,
        query=x_query,
        transport=transport,
    )
    validate_returned_rows_against_query(x_query, x_rows)

    _, y_rows = execute_guarded_occurrence_read(
        manifest=manifest,
        query=y_query,
        transport=transport,
    )
    validate_returned_rows_against_query(y_query, y_rows)

    adapted = adapt_gbif_pair_rows(x_rows=x_rows, y_rows=y_rows)
    primary = build_occurrence_sampling_preflight(
        adapted.records,
        taxonomy_eligible=True,
        thresholds=PRIMARY_THRESHOLDS,
    )
    strict = build_occurrence_sampling_preflight(
        adapted.records,
        taxonomy_eligible=True,
        thresholds=STRICT_SENSITIVITY_THRESHOLDS,
    )
    return PairSamplingExecutionResult(
        authorization=authorization,
        x_query=x_query,
        y_query=y_query,
        adapted_batch=adapted,
        primary=primary,
        strict_sensitivity=strict,
    )
