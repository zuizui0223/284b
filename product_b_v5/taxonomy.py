"""Pure validation for the response-blind Product-B v5 taxonomy overlay.

No function in this module performs taxonomy lookup or occurrence access. It only
validates an already-declared taxonomy overlay and its stop/eligibility semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


LEGACY_GBIF_BACKBONE = "GBIF_Backbone_Taxonomy"
LEGACY_GBIF_CHECKLIST_KEY = "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"
DIRECT_PROVENANCE = "direct_gbif_backbone_species_page"
SECONDARY_PROVENANCE = "secondary_identifier_source"

RESOLVED = "resolved_exact_legacy_key"
UNRESOLVED_MISSING_KEY = "unresolved_missing_exact_legacy_key"
UNRESOLVED_CONCEPT = "unresolved_taxonomic_concept_conflict"
UNRESOLVED_OTHER = "unresolved_other_taxonomy"

PAIR_ELIGIBLE = "eligible_for_sampling_preflight"
PAIR_UNRESOLVED = "unresolved_taxonomy"

ALLOWED_PARTNER_STATES = {
    RESOLVED,
    UNRESOLVED_MISSING_KEY,
    UNRESOLVED_CONCEPT,
    UNRESOLVED_OTHER,
}
ALLOWED_PROVENANCE = {"", DIRECT_PROVENANCE, SECONDARY_PROVENANCE}


@dataclass(frozen=True)
class TaxonomyOverlayRow:
    pair_id: str
    x_literature_name: str
    y_literature_name: str
    matching_checklist: str
    checklist_key: str
    x_resolved_name: str
    x_legacy_gbif_key: str
    x_key_provenance: str
    x_taxonomy_state: str
    y_resolved_name: str
    y_legacy_gbif_key: str
    y_key_provenance: str
    y_taxonomy_state: str
    pair_taxonomy_state: str
    sampling_preflight_eligible: str
    taxonomy_note: str

    @property
    def eligible_bool(self) -> bool:
        value = self.sampling_preflight_eligible.strip().lower()
        if value not in {"true", "false"}:
            raise ValueError("sampling_preflight_eligible must be true or false")
        return value == "true"


@dataclass(frozen=True)
class TaxonomyValidationResult:
    passed: bool
    errors: tuple[str, ...]


def _nonempty(value: str) -> bool:
    return bool(value and value.strip())


def _numeric_key_or_empty(value: str) -> bool:
    return not value.strip() or value.strip().isdigit()


def _partner_errors(
    *,
    prefix: str,
    resolved_name: str,
    key: str,
    provenance: str,
    state: str,
) -> list[str]:
    errors: list[str] = []

    if not _nonempty(resolved_name):
        errors.append(f"{prefix}:missing_resolved_name")
    if state not in ALLOWED_PARTNER_STATES:
        errors.append(f"{prefix}:invalid_taxonomy_state")
    if provenance not in ALLOWED_PROVENANCE:
        errors.append(f"{prefix}:invalid_key_provenance")
    if not _numeric_key_or_empty(key):
        errors.append(f"{prefix}:legacy_key_must_be_numeric_or_empty")

    if state == RESOLVED:
        if not key.strip():
            errors.append(f"{prefix}:resolved_state_requires_key")
        if not provenance:
            errors.append(f"{prefix}:resolved_state_requires_provenance")
    else:
        if state == UNRESOLVED_MISSING_KEY and key.strip():
            errors.append(f"{prefix}:missing_key_state_must_not_have_key")

    if provenance and not key.strip():
        errors.append(f"{prefix}:provenance_without_key")

    return errors


def validate_taxonomy_row(row: TaxonomyOverlayRow) -> tuple[str, ...]:
    errors: list[str] = []

    for field, value in {
        "pair_id": row.pair_id,
        "x_literature_name": row.x_literature_name,
        "y_literature_name": row.y_literature_name,
        "matching_checklist": row.matching_checklist,
        "checklist_key": row.checklist_key,
        "taxonomy_note": row.taxonomy_note,
    }.items():
        if not _nonempty(value):
            errors.append(f"missing_required_field:{field}")

    if row.matching_checklist != LEGACY_GBIF_BACKBONE:
        errors.append("matching_checklist_not_frozen_legacy_gbif")
    if row.checklist_key != LEGACY_GBIF_CHECKLIST_KEY:
        errors.append("checklist_key_not_frozen")

    errors.extend(
        _partner_errors(
            prefix="x",
            resolved_name=row.x_resolved_name,
            key=row.x_legacy_gbif_key,
            provenance=row.x_key_provenance,
            state=row.x_taxonomy_state,
        )
    )
    errors.extend(
        _partner_errors(
            prefix="y",
            resolved_name=row.y_resolved_name,
            key=row.y_legacy_gbif_key,
            provenance=row.y_key_provenance,
            state=row.y_taxonomy_state,
        )
    )

    if row.pair_taxonomy_state not in {PAIR_ELIGIBLE, PAIR_UNRESOLVED}:
        errors.append("invalid_pair_taxonomy_state")

    try:
        eligible = row.eligible_bool
    except ValueError:
        errors.append("sampling_preflight_eligible_not_boolean")
        eligible = False

    directly_resolved = (
        row.x_taxonomy_state == RESOLVED
        and row.y_taxonomy_state == RESOLVED
        and row.x_key_provenance == DIRECT_PROVENANCE
        and row.y_key_provenance == DIRECT_PROVENANCE
    )

    if eligible:
        if row.pair_taxonomy_state != PAIR_ELIGIBLE:
            errors.append("eligible_boolean_requires_eligible_pair_state")
        if not directly_resolved:
            errors.append("sampling_eligibility_requires_two_direct_exact_keys")
    else:
        if row.pair_taxonomy_state == PAIR_ELIGIBLE:
            errors.append("eligible_pair_state_requires_true_boolean")

    if row.pair_taxonomy_state == PAIR_UNRESOLVED and eligible:
        errors.append("unresolved_pair_cannot_be_sampling_eligible")

    return tuple(errors)


def validate_taxonomy_registry(
    rows: Sequence[TaxonomyOverlayRow],
) -> TaxonomyValidationResult:
    errors: list[str] = []
    seen_ids: set[str] = set()

    if not rows:
        errors.append("taxonomy_registry_must_not_be_empty")

    for index, row in enumerate(rows):
        errors.extend(
            f"row_{index}:{error}" for error in validate_taxonomy_row(row)
        )
        if row.pair_id in seen_ids:
            errors.append(f"row_{index}:duplicate_pair_id")
        seen_ids.add(row.pair_id)

    return TaxonomyValidationResult(passed=not errors, errors=tuple(errors))
