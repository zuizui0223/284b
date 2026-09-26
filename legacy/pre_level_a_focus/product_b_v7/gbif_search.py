"""Pure GBIF occurrence-search planning for Product-B v7 admin-code frames.

v7 keeps the v5 paging and 100k search ceilings but does not mutate the frozen v5
polygon serializer.  KIM001's independently declared China ADM0 frame is executed
as the ISO-3166-1 alpha-2 GBIF country filter CN.  No occurrence access occurs in
this module.
"""
from __future__ import annotations

from product_b_v5.gbif_search import (
    GBIF_MAX_PAGE_SIZE,
    GBIF_SEARCH_HARD_LIMIT,
    GBIF_OCCURRENCE_SEARCH_ENDPOINT,
    GBIFSearchEnvelope,
    GBIFSearchRequest,
    parse_search_envelope,
)
from product_b_v5.occurrence_source import LogicalOccurrenceQuery


def serialize_v7_gbif_search_request(
    query: LogicalOccurrenceQuery,
    *,
    offset: int = 0,
    limit: int = GBIF_MAX_PAGE_SIZE,
) -> GBIFSearchRequest:
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")
    if not isinstance(limit, int) or not (1 <= limit <= GBIF_MAX_PAGE_SIZE):
        raise ValueError(f"limit must be an integer in [1, {GBIF_MAX_PAGE_SIZE}]")
    if offset + limit > GBIF_SEARCH_HARD_LIMIT:
        raise ValueError("GBIF occurrence search offset + limit exceeds 100000")
    if query.geographic_filter_type != "country_code_iso2":
        raise ValueError("Product-B v7 KIM001 serializer requires country_code_iso2")
    country = str(query.geographic_filter_value).strip().upper()
    if country != "CN":
        raise ValueError("KIM001 frozen operational country filter must remain CN")
    if not query.has_coordinate:
        raise ValueError("Product-B v7 query requires hasCoordinate=true")
    if query.occurrence_status != "PRESENT":
        raise ValueError("Product-B v7 query requires occurrenceStatus=PRESENT")
    try:
        taxon_key = int(query.taxon_key)
    except (TypeError, ValueError) as exc:
        raise ValueError("legacy GBIF taxon key must be numeric") from exc
    if taxon_key <= 0:
        raise ValueError("legacy GBIF taxon key must be positive")

    params = (
        ("taxonKey", str(taxon_key)),
        ("checklistKey", query.checklist_key),
        ("country", country),
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


def next_v7_search_request(
    query: LogicalOccurrenceQuery,
    envelope: GBIFSearchEnvelope,
) -> GBIFSearchRequest | None:
    if envelope.end_of_records:
        return None
    if envelope.result_count <= 0:
        raise ValueError("non-terminal GBIF page must advance by at least one result")
    next_offset = envelope.offset + envelope.result_count
    if next_offset >= GBIF_SEARCH_HARD_LIMIT:
        raise ValueError("GBIF search reached 100000-record ceiling; do not switch transport adaptively")
    return serialize_v7_gbif_search_request(
        query,
        offset=next_offset,
        limit=min(GBIF_MAX_PAGE_SIZE, GBIF_SEARCH_HARD_LIMIT - next_offset),
    )


__all__ = [
    "GBIF_SEARCH_HARD_LIMIT",
    "GBIFSearchEnvelope",
    "GBIFSearchRequest",
    "parse_search_envelope",
    "serialize_v7_gbif_search_request",
    "next_v7_search_request",
]
