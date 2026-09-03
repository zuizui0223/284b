"""Response-blind geographic-scope gate for Product-B v5.

Literature scope text is not automatically equivalent to an executable occurrence
filter.  This module keeps that distinction explicit and prevents occurrence
availability from being used to define or widen the evidence scope.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class ScopeState(str, Enum):
    RESOLVED = "operational_scope_resolved"
    UNRESOLVED = "unresolved_operational_scope"


ALLOWED_FILTER_TYPES = {"country_codes", "bbox", "polygon_wkt"}
ALLOWED_RESOLVED_SOURCE_TYPES = {
    "primary_literature_methods",
    "primary_literature_supplement",
    "preexisting_admin_boundary",
}
FORBIDDEN_SOURCE_TYPES = {
    "occurrence_availability",
    "occurrence_range",
    "occurrence_convex_hull",
    "occurrence_density",
}


@dataclass(frozen=True)
class GeographicScopeDeclaration:
    pair_id: str
    literature_scope_text: str
    evidence_doi: str
    state: ScopeState
    filter_type: str = ""
    filter_value: str = ""
    scope_source_type: str = ""
    note: str = ""


@dataclass(frozen=True)
class ScopeRegistryValidation:
    passed: bool
    errors: tuple[str, ...]
    execution_eligible_pair_ids: tuple[str, ...]


def validate_scope_declaration(
    declaration: GeographicScopeDeclaration,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not declaration.pair_id.strip():
        errors.append("missing_pair_id")
    if not declaration.literature_scope_text.strip():
        errors.append("missing_literature_scope_text")
    if not declaration.evidence_doi.strip():
        errors.append("missing_evidence_doi")

    source_type = declaration.scope_source_type.strip()
    if source_type in FORBIDDEN_SOURCE_TYPES:
        errors.append("occurrence_derived_scope_source_forbidden")

    if declaration.state is ScopeState.RESOLVED:
        if declaration.filter_type not in ALLOWED_FILTER_TYPES:
            errors.append("resolved_scope_requires_allowed_filter_type")
        if not declaration.filter_value.strip():
            errors.append("resolved_scope_requires_filter_value")
        if source_type not in ALLOWED_RESOLVED_SOURCE_TYPES:
            errors.append("resolved_scope_requires_independent_machine_scope_source")
    elif declaration.state is ScopeState.UNRESOLVED:
        if declaration.filter_type.strip() or declaration.filter_value.strip():
            errors.append("unresolved_scope_must_not_carry_executable_filter")
    else:
        errors.append("unknown_scope_state")

    return tuple(errors)


def validate_scope_registry(
    declarations: Sequence[GeographicScopeDeclaration],
) -> ScopeRegistryValidation:
    rows = tuple(declarations)
    errors: list[str] = []
    if not rows:
        errors.append("scope_registry_must_not_be_empty")

    seen: set[str] = set()
    eligible: list[str] = []
    for index, declaration in enumerate(rows):
        if declaration.pair_id in seen:
            errors.append(f"row_{index}:duplicate_pair_id")
        seen.add(declaration.pair_id)

        for error in validate_scope_declaration(declaration):
            errors.append(f"row_{index}:{error}")
        if declaration.state is ScopeState.RESOLVED and not validate_scope_declaration(
            declaration
        ):
            eligible.append(declaration.pair_id)

    return ScopeRegistryValidation(
        passed=not errors,
        errors=tuple(errors),
        execution_eligible_pair_ids=tuple(sorted(eligible)),
    )


def require_scope_resolved(
    declarations: Sequence[GeographicScopeDeclaration], *, pair_id: str
) -> GeographicScopeDeclaration:
    matches = [row for row in declarations if row.pair_id == pair_id]
    if len(matches) != 1:
        raise ValueError("pair_id must resolve to exactly one scope declaration")
    declaration = matches[0]
    errors = validate_scope_declaration(declaration)
    if errors:
        raise ValueError("invalid scope declaration: " + ",".join(errors))
    if declaration.state is not ScopeState.RESOLVED:
        raise ValueError("operational geographic scope is unresolved")
    return declaration
