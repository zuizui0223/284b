"""Pure scan-plan validation for Product-B v7.3 snapshot taxonomy identity.

This module never opens snapshot data. It defines the only admissible query shape
for the separately executed scanner: exact predeclared species names and the five
frozen taxonomy columns. Spatial, occurrence-identifier, recorder, dataset, and
count projections are structurally unavailable here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from product_b_v7_3.taxonomy_identity import ALLOWED_COLUMNS, SnapshotIdentityDeclaration, validate_identity_declaration


@dataclass(frozen=True)
class SnapshotIdentityScanPlan:
    scan_id: str
    declarations: tuple[SnapshotIdentityDeclaration, ...]
    projected_columns: tuple[str, ...] = ALLOWED_COLUMNS
    raw_rows_persisted: bool = False
    matched_row_counts_persisted: bool = False


@dataclass(frozen=True)
class SnapshotIdentityScanPlanDecision:
    passed: bool
    reasons: tuple[str, ...]
    frozen_species_names: tuple[str, ...]


def evaluate_snapshot_identity_scan_plan(plan: SnapshotIdentityScanPlan) -> SnapshotIdentityScanPlanDecision:
    reasons: list[str] = []
    if not plan.scan_id.strip():
        reasons.append("scan_id_blank")
    if tuple(plan.projected_columns) != ALLOWED_COLUMNS:
        reasons.append("projected_columns_changed")
    if plan.raw_rows_persisted is not False:
        reasons.append("raw_rows_persistence_forbidden")
    if plan.matched_row_counts_persisted is not False:
        reasons.append("matched_row_count_persistence_forbidden")
    if not plan.declarations:
        reasons.append("declarations_empty")

    identities: set[tuple[str, str]] = set()
    all_names: list[str] = []
    for declaration in plan.declarations:
        errors = validate_identity_declaration(declaration)
        if errors:
            reasons.extend(f"{declaration.taxon_role}:{reason}" for reason in errors)
        key = (declaration.taxon_role, declaration.biological_name.strip())
        if key in identities:
            reasons.append("duplicate_taxon_declaration")
        identities.add(key)
        all_names.extend(name.strip() for name in declaration.admissible_species_names if name.strip())

    frozen_names = tuple(sorted(set(all_names)))
    if not frozen_names:
        reasons.append("frozen_species_names_empty")
    return SnapshotIdentityScanPlanDecision(
        passed=not reasons,
        reasons=tuple(reasons),
        frozen_species_names=frozen_names,
    )


__all__ = [
    "SnapshotIdentityScanPlan",
    "SnapshotIdentityScanPlanDecision",
    "evaluate_snapshot_identity_scan_plan",
]
