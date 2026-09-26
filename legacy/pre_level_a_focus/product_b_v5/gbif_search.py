"""Pure GBIF occurrence-search request planning for Product-B v5.

This module serializes an already authorized logical occurrence query into the
current GBIF occurrence-search parameter contract.  It contains no HTTP client
and opens no occurrence outcome.  Paging is synthetic/testable and fail-closed
at GBIF's documented search limits.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Sequence

from .occurrence_source import LogicalOccurrenceQuery


GBIF_OCCURRENCE_SEARCH_ENDPOINT = "https://api.gbif.org/v1/occurrence/search"
GBIF_MAX_PAGE_SIZE = 300
GBIF_SEARCH_HARD_LIMIT = 100_000


@dataclass(frozen=True)
class GBIFSearchRequest:
    endpoint: str
    params: tuple[tuple[str, str], ...]
    offset: int
    limit: int

    def as_mapping(self) -> dict[str, str]:
        return dict(self.params)


@dataclass(frozen=True)
class GBIFSearchEnvelope:
    offset: int
    limit: int
    count: int
    end_of_records: bool
    result_count: int


_POLYGON_RE = re.compile(
    r"^\s*POLYGON\s*\(\(\s*(.*?)\s*\)\)\s*$",
    flags=re.IGNORECASE,
)


def _polygon_ring_from_wkt(wkt: str) -> tuple[tuple[float, float], ...]:
    """Parse the deliberately narrow single-ring polygon subset used in v0.2."""

    match = _POLYGON_RE.match(wkt)
    if match is None:
        raise ValueError("GBIF v0.2 serializer requires single-ring POLYGON WKT")

    ring: list[tuple[float, float]] = []
    for raw_point in match.group(1).split(","):
        pieces = raw_point.strip().split()
        if len(pieces) != 2:
            raise ValueError("polygon coordinate must contain longitude and latitude")
        try:
            lon, lat = float(pieces[0]), float(pieces[1])
        except ValueError as exc:
            raise ValueError("polygon coordinates must be numeric") from exc
        if not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
            raise ValueError("polygon coordinates fall outside lon/lat bounds")
        ring.append((lon, lat))

    if len(ring) < 4:
        raise ValueError("polygon ring must contain at least four coordinates including closure")
    if ring[0] != ring[-1]:
        raise ValueError("polygon ring must be closed")
    if len(set(ring[:-1])) < 3:
        raise ValueError("polygon ring must contain at least three distinct vertices")
    return tuple(ring)


def polygon_signed_area(wkt: str) -> float:
    """Signed planar area in lon/lat coordinates; positive means anticlockwise."""

    ring = _polygon_ring_from_wkt(wkt)
    twice_area = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        twice_area += x1 * y2 - x2 * y1
    return twice_area / 2.0


def require_gbif_anticlockwise_polygon(wkt: str) -> str:
    """Reject clockwise/degenerate WKT before any GBIF search request exists."""

    area = polygon_signed_area(wkt)
    if area <= 0.0:
        raise ValueError("GBIF geometry polygon must be anticlockwise and non-degenerate")
    return wkt.strip()


def serialize_gbif_search_request(
    query: LogicalOccurrenceQuery,
    *,
    offset: int = 0,
    limit: int = GBIF_MAX_PAGE_SIZE,
) -> GBIFSearchRequest:
    """Serialize the frozen Product-B logical query into GBIF search parameters.

    Only the current response-blind polygon scope is executable in v0.2. Other
    geographic filter types remain design-level options and fail closed here
    until they receive their own serializer/test contract.
    """

    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")
    if not isinstance(limit, int) or not (1 <= limit <= GBIF_MAX_PAGE_SIZE):
        raise ValueError(f"limit must be an integer in [1, {GBIF_MAX_PAGE_SIZE}]")
    if offset + limit > GBIF_SEARCH_HARD_LIMIT:
        raise ValueError("GBIF occurrence search offset + limit exceeds 100000")
    if query.geographic_filter_type != "polygon_wkt":
        raise ValueError("GBIF v0.2 serializer only permits frozen polygon_wkt scopes")
    if not query.has_coordinate:
        raise ValueError("GBIF v0.2 query requires hasCoordinate=true")
    if query.occurrence_status != "PRESENT":
        raise ValueError("GBIF v0.2 query requires occurrenceStatus=PRESENT")

    geometry = require_gbif_anticlockwise_polygon(query.geographic_filter_value)
    try:
        taxon_key = int(query.taxon_key)
    except (TypeError, ValueError) as exc:
        raise ValueError("legacy GBIF taxon key must be numeric") from exc
    if taxon_key <= 0:
        raise ValueError("legacy GBIF taxon key must be positive")

    params = (
        ("taxonKey", str(taxon_key)),
        ("checklistKey", query.checklist_key),
        ("geometry", geometry),
        ("hasCoordinate", "true"),
        ("occurrenceStatus", "PRESENT"),
        ("offset", str(offset)),
        ("limit", str(limit)),
    )
    return GBIFSearchRequest(
        endpoint=GBIF_OCCURRENCE_SEARCH_ENDPOINT,
        params=params,
        offset=offset,
        limit=limit,
    )


def parse_search_envelope(payload: Mapping[str, object]) -> GBIFSearchEnvelope:
    """Validate only paging metadata from a synthetic or authorized GBIF response."""

    required = ("offset", "limit", "count", "endOfRecords", "results")
    missing = tuple(field for field in required if field not in payload)
    if missing:
        raise ValueError("GBIF search payload missing fields: " + ",".join(missing))

    offset = payload["offset"]
    limit = payload["limit"]
    count = payload["count"]
    end = payload["endOfRecords"]
    results = payload["results"]
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("GBIF payload offset must be a non-negative integer")
    if not isinstance(limit, int) or not (0 <= limit <= GBIF_MAX_PAGE_SIZE):
        raise ValueError("GBIF payload limit is outside documented search bounds")
    if not isinstance(count, int) or count < 0:
        raise ValueError("GBIF payload count must be a non-negative integer")
    if not isinstance(end, bool):
        raise ValueError("GBIF payload endOfRecords must be boolean")
    if not isinstance(results, Sequence) or isinstance(results, (str, bytes)):
        raise ValueError("GBIF payload results must be a sequence")
    if len(results) > GBIF_MAX_PAGE_SIZE:
        raise ValueError("GBIF payload result page exceeds documented maximum")

    return GBIFSearchEnvelope(
        offset=offset,
        limit=limit,
        count=count,
        end_of_records=end,
        result_count=len(results),
    )


def next_search_request(
    query: LogicalOccurrenceQuery,
    envelope: GBIFSearchEnvelope,
) -> GBIFSearchRequest | None:
    """Plan the next search page without silently crossing GBIF's 100k ceiling."""

    if envelope.end_of_records:
        return None
    next_offset = envelope.offset + envelope.result_count
    if envelope.result_count <= 0:
        raise ValueError("non-terminal GBIF page must advance by at least one result")
    if next_offset >= GBIF_SEARCH_HARD_LIMIT:
        raise ValueError("GBIF search reached 100000-record ceiling; do not switch transport adaptively")

    remaining_to_ceiling = GBIF_SEARCH_HARD_LIMIT - next_offset
    next_limit = min(GBIF_MAX_PAGE_SIZE, remaining_to_ceiling)
    return serialize_gbif_search_request(
        query,
        offset=next_offset,
        limit=next_limit,
    )
