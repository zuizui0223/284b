"""Pure validation for Product-B v5 literature-only pair declarations.

This module validates declaration structure only. It must not resolve taxonomy,
fetch occurrences, inspect occurrence counts, or open invariant/model outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


PHASE1_OBLIGACY_CLASS = "obligate_pollination_mutualism"
PHASE1_DIRECTION = "Y_requires_X"
PHASE1_ASSOCIATION_SCALE = "reproductive_host_dependence"
PENDING_TAXON_KEY_STATUS = "pending_response_blind_taxonomy_resolution"
ELIGIBLE_LITERATURE_STATE = "eligible_literature_only"


@dataclass(frozen=True)
class LiteraturePairDeclaration:
    pair_id: str
    x_taxon_name: str
    y_taxon_name: str
    x_taxon_key: str
    y_taxon_key: str
    taxon_key_status: str
    obligacy_class: str
    direction: str
    literature_doi: str
    evidence_type: str
    association_scale: str
    declared_geographic_scope: str
    registry_state: str
    known_boundary: str


@dataclass(frozen=True)
class RegistryValidationResult:
    passed: bool
    errors: tuple[str, ...]


def _nonempty(value: str) -> bool:
    return bool(value and value.strip())


def _looks_like_doi(value: str) -> bool:
    """Minimal structural check; DOI existence is an external literature task."""

    parts = [part.strip() for part in value.split(";") if part.strip()]
    return bool(parts) and all(part.startswith("10.") and "/" in part for part in parts)


def validate_literature_pair(row: LiteraturePairDeclaration) -> tuple[str, ...]:
    """Validate one Phase-1 literature declaration without external lookups."""

    errors: list[str] = []

    required_text = {
        "pair_id": row.pair_id,
        "x_taxon_name": row.x_taxon_name,
        "y_taxon_name": row.y_taxon_name,
        "literature_doi": row.literature_doi,
        "evidence_type": row.evidence_type,
        "declared_geographic_scope": row.declared_geographic_scope,
        "known_boundary": row.known_boundary,
    }
    for field, value in required_text.items():
        if not _nonempty(value):
            errors.append(f"missing_required_field:{field}")

    if row.x_taxon_name.strip() == row.y_taxon_name.strip():
        errors.append("partners_must_be_distinct_taxa")

    if row.obligacy_class != PHASE1_OBLIGACY_CLASS:
        errors.append("phase1_obligacy_class_not_allowed")

    if row.direction != PHASE1_DIRECTION:
        errors.append("phase1_direction_must_be_Y_requires_X")

    if row.association_scale != PHASE1_ASSOCIATION_SCALE:
        errors.append("phase1_association_scale_not_allowed")

    if row.registry_state != ELIGIBLE_LITERATURE_STATE:
        errors.append("eligible_registry_requires_eligible_literature_only_state")

    if row.taxon_key_status != PENDING_TAXON_KEY_STATUS:
        errors.append("literature_step_requires_pending_taxon_key_status")

    if row.x_taxon_key.strip() or row.y_taxon_key.strip():
        errors.append("literature_step_must_not_prepopulate_taxon_keys")

    if _nonempty(row.literature_doi) and not _looks_like_doi(row.literature_doi):
        errors.append("invalid_doi_structure")

    return tuple(errors)


def validate_literature_registry(
    rows: Sequence[LiteraturePairDeclaration],
) -> RegistryValidationResult:
    """Validate a whole literature-only registry and uniqueness constraints."""

    errors: list[str] = []
    pair_ids: set[str] = set()
    directed_pairs: set[tuple[str, str, str]] = set()

    if not rows:
        errors.append("registry_must_not_be_empty")

    for index, row in enumerate(rows):
        row_errors = validate_literature_pair(row)
        errors.extend(f"row_{index}:{error}" for error in row_errors)

        pair_id = row.pair_id.strip()
        if pair_id in pair_ids:
            errors.append(f"row_{index}:duplicate_pair_id")
        pair_ids.add(pair_id)

        signature = (
            row.x_taxon_name.strip(),
            row.y_taxon_name.strip(),
            row.direction.strip(),
        )
        if signature in directed_pairs:
            errors.append(f"row_{index}:duplicate_directed_pair")
        directed_pairs.add(signature)

    return RegistryValidationResult(passed=not errors, errors=tuple(errors))
