"""Taxonomy-only resolution for Product-B v7.2 snapshot-native taxa.

Unlike the v5 legacy-backbone resolver, this module deliberately omits checklistKey
and resolves against GBIF's current default taxonomy.  It never queries occurrence
rows.  Only exact, accepted, species-rank matches are auto-admitted; synonyms must
stop for a separately frozen manual concept review.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

GBIF_CURRENT_SPECIES_MATCH_ENDPOINT = "https://api.gbif.org/v2/species/match"
GBIF_CURRENT_SPECIES_USAGE_ENDPOINT = "https://api.gbif.org/v1/species/{usage_key}"


@dataclass(frozen=True)
class SnapshotTaxonomyRequest:
    pair_id: str
    partner: str
    scientific_name: str
    kingdom: str


@dataclass(frozen=True)
class SnapshotTaxonomyResolution:
    pair_id: str
    partner: str
    requested_name: str
    requested_kingdom: str
    usage_key: str
    canonical_name: str
    scientific_name: str
    rank: str
    status: str
    match_type: str
    confidence: int | None
    direct_usage_key: str
    direct_usage_canonical_name: str
    direct_usage_rank: str
    direct_usage_status: str


def build_current_species_match_params(request: SnapshotTaxonomyRequest) -> tuple[tuple[str, str], ...]:
    if request.partner not in {"x", "y"}:
        raise ValueError("partner must be x or y")
    if not request.pair_id.strip():
        raise ValueError("pair_id must not be blank")
    if not request.scientific_name.strip():
        raise ValueError("scientific_name must not be blank")
    if request.kingdom not in {"Plantae", "Animalia"}:
        raise ValueError("kingdom must be Plantae or Animalia")
    return (
        ("scientificName", request.scientific_name.strip()),
        ("taxonRank", "SPECIES"),
        ("kingdom", request.kingdom),
    )


def _mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


def _text(value: object, field: str) -> str:
    if value is None:
        raise ValueError(f"{field} is missing")
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field} must not be blank")
    return text


def parse_current_direct_taxonomy_resolution(
    *,
    request: SnapshotTaxonomyRequest,
    match_payload: Mapping[str, object],
    usage_payload: Mapping[str, object],
) -> SnapshotTaxonomyResolution:
    usage = _mapping(match_payload.get("usage"), "match.usage")
    diagnostics = _mapping(match_payload.get("diagnostics"), "match.diagnostics")

    usage_key = _text(usage.get("key"), "match.usage.key")
    canonical = _text(usage.get("canonicalName"), "match.usage.canonicalName")
    scientific = _text(usage.get("name"), "match.usage.name")
    rank = _text(usage.get("rank"), "match.usage.rank").upper()
    status = _text(usage.get("status"), "match.usage.status").upper()
    match_type = _text(diagnostics.get("matchType"), "match.diagnostics.matchType").upper()
    confidence_raw = diagnostics.get("confidence")
    confidence = confidence_raw if isinstance(confidence_raw, int) else None

    if match_type != "EXACT":
        raise ValueError("snapshot-native taxonomy match must be EXACT")
    if rank != "SPECIES":
        raise ValueError("snapshot-native taxonomy match must be species rank")
    if canonical.casefold() != request.scientific_name.strip().casefold():
        raise ValueError("matched canonical name differs from literature-declared name")
    if status != "ACCEPTED":
        raise ValueError("snapshot-native taxonomy usage must be ACCEPTED")
    if match_payload.get("synonym") is True:
        raise ValueError("snapshot-native name resolved as synonym; manual concept review required")

    direct_key = _text(usage_payload.get("key"), "usage.key")
    direct_canonical = _text(
        usage_payload.get("canonicalName") or usage_payload.get("canonicalNameWithMarker"),
        "usage.canonicalName",
    )
    direct_rank = _text(usage_payload.get("rank"), "usage.rank").upper()
    direct_status = _text(
        usage_payload.get("taxonomicStatus") or usage_payload.get("status"),
        "usage.status",
    ).upper()

    if direct_key != usage_key:
        raise ValueError("direct current GBIF usage page key disagrees with match usage key")
    if direct_canonical.casefold() != canonical.casefold():
        raise ValueError("direct current GBIF usage page canonical name disagrees with match")
    if direct_rank != "SPECIES":
        raise ValueError("direct current GBIF usage page is not species rank")
    if direct_status != "ACCEPTED":
        raise ValueError("direct current GBIF usage page is not accepted")

    return SnapshotTaxonomyResolution(
        pair_id=request.pair_id,
        partner=request.partner,
        requested_name=request.scientific_name,
        requested_kingdom=request.kingdom,
        usage_key=usage_key,
        canonical_name=canonical,
        scientific_name=scientific,
        rank=rank,
        status=status,
        match_type=match_type,
        confidence=confidence,
        direct_usage_key=direct_key,
        direct_usage_canonical_name=direct_canonical,
        direct_usage_rank=direct_rank,
        direct_usage_status=direct_status,
    )


__all__ = [
    "GBIF_CURRENT_SPECIES_MATCH_ENDPOINT",
    "GBIF_CURRENT_SPECIES_USAGE_ENDPOINT",
    "SnapshotTaxonomyRequest",
    "SnapshotTaxonomyResolution",
    "build_current_species_match_params",
    "parse_current_direct_taxonomy_resolution",
]
