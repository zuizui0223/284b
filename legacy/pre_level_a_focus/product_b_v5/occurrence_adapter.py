"""Deterministic GBIF-row adapter for Product-B v5 sampling preflight.

This module performs no network access. It accepts complete already-retrieved raw
GBIF search rows for both partners, resolves all declared identity aliases into a
connected-component token, projects WGS84 coordinates with the repository's
frozen EPSG:6933 implementation, and emits :class:`OccurrenceRecord` values for
the pure preprocessing layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from typing import Mapping, Sequence
import unicodedata

from .occurrence_preprocessing import (
    OccurrenceRecord,
    canonical_coordinate_key,
    canonical_event_day,
)
from .projection import wgs84_to_epsg6933


@dataclass(frozen=True)
class RawIdentityComponent:
    row_ids: tuple[str, ...]
    partners: tuple[str, ...]
    witness_types: tuple[str, ...]
    component_token: str


@dataclass(frozen=True)
class AdaptedOccurrenceBatch:
    records: tuple[OccurrenceRecord, ...]
    identity_components: tuple[RawIdentityComponent, ...]
    raw_records_x: int
    raw_records_y: int


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


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _recorder(value: object) -> str:
    normalized = unicodedata.normalize("NFKC", _text(value))
    return " ".join(normalized.split()).casefold()


def _number_or_none(value: object) -> float | None:
    if value is None or _text(value) == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _other_catalog_numbers(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
        raw = tuple(_text(item) for item in value)
    else:
        raw = tuple(_text(item) for item in str(value).split(";"))
    return tuple(sorted({item for item in raw if item}))


def _raw_row_id(row: Mapping[str, object]) -> str:
    value = _text(row.get("key"))
    if not value:
        raise ValueError("GBIF occurrence row is missing key")
    return value


def _identity_witnesses(row: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    witnesses: list[tuple[str, str]] = []

    occurrence_id = _text(row.get("occurrenceID"))
    if occurrence_id:
        witnesses.append(("occurrence_id_lineage", occurrence_id))

    event_id = _text(row.get("eventID"))
    if event_id:
        witnesses.append(("event_id", event_id))

    catalog_values = set(_other_catalog_numbers(row.get("otherCatalogNumbers")))
    catalog_number = _text(row.get("catalogNumber"))
    if catalog_number:
        catalog_values.add(catalog_number)
    for value in sorted(catalog_values):
        witnesses.append(("catalog_or_specimen_number", value))

    latitude = _number_or_none(row.get("decimalLatitude"))
    longitude = _number_or_none(row.get("decimalLongitude"))
    coordinate_key = canonical_coordinate_key(latitude, longitude)
    event_day = canonical_event_day(_text(row.get("eventDate")))

    dataset_key = _text(row.get("datasetKey"))
    if dataset_key and event_day and coordinate_key:
        witnesses.append(
            (
                "dataset_key_plus_event_day_plus_coordinate_key",
                "|".join((dataset_key, event_day, coordinate_key)),
            )
        )

    recorder = _recorder(row.get("recordedBy"))
    if recorder and event_day and coordinate_key:
        witnesses.append(
            (
                "recorder_plus_event_day_plus_coordinate_key",
                "|".join((recorder, event_day, coordinate_key)),
            )
        )

    return tuple(witnesses)


def _component_token(
    row_ids: Sequence[str], witnesses: Sequence[tuple[str, str]]
) -> str:
    payload = "\n".join(
        [*(f"row:{value}" for value in sorted(row_ids)),
         *(f"witness:{kind}:{value}" for kind, value in sorted(set(witnesses)))]
    )
    return "raw_identity_component:" + sha256(payload.encode("utf-8")).hexdigest()


def _project_if_possible(
    longitude: float | None, latitude: float | None
) -> tuple[float | None, float | None]:
    if longitude is None or latitude is None:
        return None, None
    if not isfinite(longitude) or not isfinite(latitude):
        return None, None
    try:
        return wgs84_to_epsg6933(longitude, latitude)
    except ValueError:
        return None, None


def adapt_gbif_pair_rows(
    *,
    x_rows: Sequence[Mapping[str, object]],
    y_rows: Sequence[Mapping[str, object]],
) -> AdaptedOccurrenceBatch:
    """Adapt complete raw partner pages only after retrieval has finished.

    The connected-component token encodes all raw identity aliases. It is placed
    into ``OccurrenceRecord.occurrence_id_lineage`` so the downstream frozen
    collision graph preserves alias and transitive collision closure without
    inflating the occurrence denominator.
    """

    labelled = tuple(("x", row) for row in x_rows) + tuple(
        ("y", row) for row in y_rows
    )
    if not labelled:
        return AdaptedOccurrenceBatch((), (), 0, 0)

    row_ids = tuple(_raw_row_id(row) for _, row in labelled)
    if len(set(row_ids)) != len(row_ids):
        raise ValueError("GBIF occurrence keys must be unique across the pair batch")

    witnesses_by_index = tuple(_identity_witnesses(row) for _, row in labelled)
    union_find = _UnionFind(len(labelled))
    token_owner: dict[tuple[str, str], int] = {}
    for index, witnesses in enumerate(witnesses_by_index):
        for witness in witnesses:
            previous = token_owner.get(witness)
            if previous is None:
                token_owner[witness] = index
            else:
                union_find.union(index, previous)

    members_by_root: dict[int, list[int]] = {}
    for index in range(len(labelled)):
        members_by_root.setdefault(union_find.find(index), []).append(index)

    component_token_by_index: dict[int, str] = {}
    component_audits: list[RawIdentityComponent] = []
    for member_indices in members_by_root.values():
        member_ids = tuple(sorted(row_ids[index] for index in member_indices))
        member_witnesses = tuple(
            witness
            for index in member_indices
            for witness in witnesses_by_index[index]
        )
        token = _component_token(member_ids, member_witnesses)
        for index in member_indices:
            component_token_by_index[index] = token

        if len(member_indices) > 1:
            component_audits.append(
                RawIdentityComponent(
                    row_ids=member_ids,
                    partners=tuple(sorted({labelled[index][0] for index in member_indices})),
                    witness_types=tuple(sorted({kind for kind, _ in member_witnesses})),
                    component_token=token,
                )
            )

    records: list[OccurrenceRecord] = []
    for index, (partner, row) in enumerate(labelled):
        latitude = _number_or_none(row.get("decimalLatitude"))
        longitude = _number_or_none(row.get("decimalLongitude"))
        easting, northing = _project_if_possible(longitude, latitude)
        catalog_number = _text(row.get("catalogNumber"))
        aliases = _other_catalog_numbers(row.get("otherCatalogNumbers"))
        if not catalog_number and aliases:
            catalog_number = aliases[0]

        records.append(
            OccurrenceRecord(
                row_id=row_ids[index],
                partner=partner,
                decimal_latitude=latitude,
                decimal_longitude=longitude,
                projected_easting_m=easting,
                projected_northing_m=northing,
                occurrence_id_lineage=component_token_by_index[index],
                event_id=_text(row.get("eventID")),
                catalog_or_specimen_number=catalog_number,
                dataset_key=_text(row.get("datasetKey")),
                event_date=_text(row.get("eventDate")),
                recorder=_text(row.get("recordedBy")),
                coordinate_uncertainty_m=_number_or_none(
                    row.get("coordinateUncertaintyInMeters")
                ),
            )
        )

    return AdaptedOccurrenceBatch(
        records=tuple(records),
        identity_components=tuple(sorted(component_audits, key=lambda item: item.row_ids)),
        raw_records_x=len(tuple(x_rows)),
        raw_records_y=len(tuple(y_rows)),
    )
