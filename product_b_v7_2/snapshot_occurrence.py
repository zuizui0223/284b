"""Pure Product-B v7.2 adapters for frozen GBIF monthly snapshot rows.

This module performs no network access and does not import PyArrow. It defines the
only row semantics admitted for the frozen 2026-08-01 monthly snapshot. The cloud
snapshot does not expose live-search ``eventID`` or ``otherCatalogNumbers`` fields;
those identities remain explicitly unavailable and are never synthesized.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Mapping, Sequence

from product_b_v5.occurrence_adapter import AdaptedOccurrenceBatch, adapt_gbif_pair_rows

EXPECTED_COUNTRY_CODE = "US"
EXPECTED_OCCURRENCE_STATUS = "PRESENT"
MAX_MATCHED_ROWS_PER_TAXON = 100_000
SNAPSHOT_IDENTITY_FIELDS_AVAILABLE = (
    "gbifid",
    "occurrenceid",
    "catalognumber",
    "datasetkey+eventdate+coordinate",
    "recordedby+eventdate+coordinate",
)
SNAPSHOT_IDENTITY_FIELDS_UNAVAILABLE = ("eventID", "otherCatalogNumbers")


@dataclass(frozen=True)
class SnapshotTaxonQuery:
    group_id: str
    species_keys: tuple[str, ...]
    country_code: str = EXPECTED_COUNTRY_CODE
    occurrence_status: str = EXPECTED_OCCURRENCE_STATUS
    max_rows_per_taxon: int = MAX_MATCHED_ROWS_PER_TAXON


@dataclass(frozen=True)
class SnapshotRowAdapterAudit:
    raw_rows: int
    normalized_rows: int
    missing_occurrence_id_rows: int
    missing_catalog_number_rows: int
    missing_recorder_rows: int
    unavailable_identity_fields: tuple[str, ...]


@dataclass(frozen=True)
class SnapshotAdaptedHostBatch:
    batch: AdaptedOccurrenceBatch
    audit: SnapshotRowAdapterAudit


def validate_snapshot_taxon_query(query: SnapshotTaxonQuery) -> tuple[str, ...]:
    reasons: list[str] = []
    if not query.group_id.strip():
        reasons.append("query_group_id_blank")
    if not query.species_keys:
        reasons.append("query_species_keys_empty")
    if any(not str(value).strip() for value in query.species_keys):
        reasons.append("query_species_key_blank")
    if len(set(query.species_keys)) != len(query.species_keys):
        reasons.append("query_species_keys_not_unique")
    if query.country_code != EXPECTED_COUNTRY_CODE:
        reasons.append("query_country_code_mismatch")
    if query.occurrence_status != EXPECTED_OCCURRENCE_STATUS:
        reasons.append("query_occurrence_status_mismatch")
    if query.max_rows_per_taxon != MAX_MATCHED_ROWS_PER_TAXON:
        reasons.append("query_row_ceiling_mismatch")
    return tuple(reasons)


def _text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value).strip()


def _flatten_people(value: object) -> str:
    """Deterministically flatten the snapshot's list/struct recordedby value."""
    parts: list[str] = []

    def visit(item: object) -> None:
        if item is None:
            return
        if isinstance(item, Mapping):
            if "array_element" in item:
                visit(item.get("array_element"))
            else:
                for key in sorted(item):
                    visit(item[key])
            return
        if isinstance(item, (list, tuple)):
            for child in item:
                visit(child)
            return
        text = str(item).strip()
        if text:
            parts.append(text)

    visit(value)
    return "; ".join(parts)


def normalize_snapshot_occurrence_row(
    row: Mapping[str, object],
    *,
    expected_species_keys: Sequence[str],
) -> dict[str, object]:
    expected = {str(value) for value in expected_species_keys}
    gbifid = _text(row.get("gbifid"))
    if not gbifid:
        raise ValueError("snapshot occurrence row is missing gbifid")

    species_key = _text(row.get("specieskey"))
    if species_key not in expected:
        raise ValueError("snapshot occurrence row violates frozen specieskey filter: " + gbifid)
    country = _text(row.get("countrycode")).upper()
    if country != EXPECTED_COUNTRY_CODE:
        raise ValueError("snapshot occurrence row violates frozen country filter: " + gbifid)
    status = _text(row.get("occurrencestatus")).upper()
    if status != EXPECTED_OCCURRENCE_STATUS:
        raise ValueError("snapshot occurrence row violates PRESENT filter: " + gbifid)

    # Map the snapshot's lowercase schema to the already-tested Product-B adapter.
    # eventID and otherCatalogNumbers do not exist in the frozen snapshot schema and
    # are deliberately left unavailable rather than reconstructed from other fields.
    return {
        "key": gbifid,
        "datasetKey": _text(row.get("datasetkey")),
        "occurrenceID": _text(row.get("occurrenceid")),
        "eventID": "",
        "catalogNumber": _text(row.get("catalognumber")),
        "otherCatalogNumbers": [],
        "eventDate": _text(row.get("eventdate")),
        "recordedBy": _flatten_people(row.get("recordedby")),
        "decimalLatitude": row.get("decimallatitude"),
        "decimalLongitude": row.get("decimallongitude"),
        "coordinateUncertaintyInMeters": row.get("coordinateuncertaintyinmeters"),
        "occurrenceStatus": status,
        "countryCode": country,
        "taxonKey": _text(row.get("taxonkey")),
        "speciesKey": species_key,
        "scientificName": _text(row.get("scientificname")),
    }


def adapt_snapshot_host_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    expected_species_key: str,
) -> SnapshotAdaptedHostBatch:
    if len(rows) > MAX_MATCHED_ROWS_PER_TAXON:
        raise ValueError("snapshot matched-row ceiling exceeded; do not truncate")
    normalized = tuple(
        normalize_snapshot_occurrence_row(row, expected_species_keys=(expected_species_key,))
        for row in rows
    )
    row_ids = [str(row["key"]) for row in normalized]
    if len(set(row_ids)) != len(row_ids):
        raise ValueError("snapshot gbifid values must be unique within a taxon batch")

    audit = SnapshotRowAdapterAudit(
        raw_rows=len(rows),
        normalized_rows=len(normalized),
        missing_occurrence_id_rows=sum(not str(row["occurrenceID"]).strip() for row in normalized),
        missing_catalog_number_rows=sum(not str(row["catalogNumber"]).strip() for row in normalized),
        missing_recorder_rows=sum(not str(row["recordedBy"]).strip() for row in normalized),
        unavailable_identity_fields=SNAPSHOT_IDENTITY_FIELDS_UNAVAILABLE,
    )
    return SnapshotAdaptedHostBatch(
        batch=adapt_gbif_pair_rows(x_rows=normalized, y_rows=()),
        audit=audit,
    )


__all__ = [
    "EXPECTED_COUNTRY_CODE",
    "EXPECTED_OCCURRENCE_STATUS",
    "MAX_MATCHED_ROWS_PER_TAXON",
    "SNAPSHOT_IDENTITY_FIELDS_AVAILABLE",
    "SNAPSHOT_IDENTITY_FIELDS_UNAVAILABLE",
    "SnapshotTaxonQuery",
    "SnapshotRowAdapterAudit",
    "SnapshotAdaptedHostBatch",
    "validate_snapshot_taxon_query",
    "normalize_snapshot_occurrence_row",
    "adapt_snapshot_host_rows",
]
