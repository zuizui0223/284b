"""Guarded logical occurrence-source boundary for Product-B v5.

There is intentionally no HTTP client in this module.  The empirical transport is
injected by a caller and cannot be invoked until the frozen execution manifest
passes every upstream authorization gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

from .authorization import (
    EXPECTED_CHECKLIST_KEY,
    AuthorizationDecision,
    require_execution_authorization,
)
from .scope import GeographicScopeDeclaration, require_scope_resolved


FIXED_REQUIRED_FIELDS = (
    "key",
    "datasetKey",
    "occurrenceID",
    "eventID",
    "catalogNumber",
    "otherCatalogNumbers",
    "eventDate",
    "recordedBy",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters",
    "taxonKey",
    "acceptedTaxonKey",
    "scientificName",
    "basisOfRecord",
    "occurrenceStatus",
)


@dataclass(frozen=True)
class LogicalOccurrenceQuery:
    pair_id: str
    partner: str
    taxon_key: str
    checklist_key: str
    geographic_filter_type: str
    geographic_filter_value: str
    has_coordinate: bool = True
    occurrence_status: str = "PRESENT"
    required_fields: tuple[str, ...] = FIXED_REQUIRED_FIELDS


class OccurrenceTransport(Protocol):
    def __call__(
        self, query: LogicalOccurrenceQuery
    ) -> Sequence[Mapping[str, object]]: ...


def build_logical_occurrence_query(
    *,
    pair_id: str,
    partner: str,
    taxon_key: str | int,
    scope_declarations: Sequence[GeographicScopeDeclaration],
    checklist_key: str = EXPECTED_CHECKLIST_KEY,
) -> LogicalOccurrenceQuery:
    """Build a response-blind logical query only after geographic scope resolves."""

    if partner not in {"x", "y"}:
        raise ValueError("partner must be x or y")
    pair = pair_id.strip()
    if not pair:
        raise ValueError("pair_id must not be blank")
    taxon = str(taxon_key).strip()
    if not taxon:
        raise ValueError("taxon_key must not be blank")
    if checklist_key != EXPECTED_CHECKLIST_KEY:
        raise ValueError("checklist_key does not match frozen taxonomy contract")

    scope = require_scope_resolved(scope_declarations, pair_id=pair)
    return LogicalOccurrenceQuery(
        pair_id=pair,
        partner=partner,
        taxon_key=taxon,
        checklist_key=checklist_key,
        geographic_filter_type=scope.filter_type,
        geographic_filter_value=scope.filter_value,
    )


def execute_guarded_occurrence_read(
    *,
    manifest: Mapping[str, object],
    query: LogicalOccurrenceQuery,
    transport: OccurrenceTransport,
) -> tuple[AuthorizationDecision, tuple[Mapping[str, object], ...]]:
    """Invoke an injected occurrence transport only after fail-closed authorization.

    The guard runs before the transport is called.  Tests use a sentinel transport
    to prove that the committed unauthorized manifest cannot trigger even a fake
    read, preserving the same control-flow boundary required for future GBIF code.
    """

    if query.checklist_key != EXPECTED_CHECKLIST_KEY:
        raise ValueError("query checklist_key does not match frozen taxonomy contract")
    if not query.has_coordinate:
        raise ValueError("frozen occurrence query requires coordinates")
    if query.occurrence_status != "PRESENT":
        raise ValueError("frozen occurrence query requires PRESENT occurrence status")

    decision = require_execution_authorization(
        manifest,
        requested_pair_ids=[query.pair_id],
    )
    rows = tuple(transport(query))
    return decision, rows
