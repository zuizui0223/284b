"""Response-blind GBIF legacy-backbone taxonomy resolution helpers.

This module never queries occurrences. It validates direct GBIF species-match and
species-usage responses for literature-declared taxa before any sampling
availability can be inspected.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


LEGACY_GBIF_BACKBONE_CHECKLIST_KEY = "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"
GBIF_SPECIES_MATCH_ENDPOINT = "https://api.gbif.org/v2/species/match"
GBIF_SPECIES_USAGE_ENDPOINT = "https://api.gbif.org/v1/species/{usage_key}"


@dataclass(frozen=True)
class TaxonomyResolutionRequest:
    pair_id: str
    partner: str
    scientific_name: str
    kingdom: str
    expected_key_hint: str = ""


@dataclass(frozen=True)
class DirectTaxonomyResolution:
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
    expected_key_hint: str
    expected_key_hint_agrees: bool | None


def build_species_match_params(request: TaxonomyResolutionRequest) -> tuple[tuple[str, str], ...]:
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
        ("checklistKey", LEGACY_GBIF_BACKBONE_CHECKLIST_KEY),
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


def parse_direct_taxonomy_resolution(
    *,
    request: TaxonomyResolutionRequest,
    match_payload: Mapping[str, object],
    usage_payload: Mapping[str, object],
) -> DirectTaxonomyResolution:
    """Require an exact species-level direct legacy-backbone match and usage page."""

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
        raise ValueError("taxonomy match must be EXACT")
    if rank != "SPECIES":
        raise ValueError("taxonomy match must be species rank")
    if canonical.casefold() != request.scientific_name.strip().casefold():
        raise ValueError("matched canonical name differs from literature-declared name")
    if status not in {"ACCEPTED", "DOUBTFUL"}:
        raise ValueError("taxonomy usage has inadmissible status")
    if match_payload.get("synonym") is True:
        raise ValueError("literature-declared name resolved as synonym; manual concept review required")

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
        raise ValueError("direct GBIF usage page key disagrees with match usage key")
    if direct_canonical.casefold() != canonical.casefold():
        raise ValueError("direct GBIF usage page canonical name disagrees with match")
    if direct_rank != "SPECIES":
        raise ValueError("direct GBIF usage page is not species rank")

    hint = request.expected_key_hint.strip()
    hint_agrees = None if not hint else hint == usage_key
    if hint and not hint_agrees:
        raise ValueError("direct GBIF key disagrees with pre-existing secondary key hint")

    return DirectTaxonomyResolution(
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
        expected_key_hint=hint,
        expected_key_hint_agrees=hint_agrees,
    )
