"""Pure validators for the Product-B v7.3 snapshot-internal taxonomy gate.

No function in this module downloads snapshot data. Callers must supply only the
sanitized distinct taxonomy tuples produced by a separately frozen scanner.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

EXPECTED_CONTRACT_VERSION = "product_b_v7_3_snapshot_taxonomy_identity_v0.1"
EXPECTED_SNAPSHOT_DATE = "2026-08-01"
EXPECTED_OBJECT_MANIFEST_SHA256 = "1b5b2dde8a23e78beafac1d122830e0552c2fbdac4086e9d9d8c161814a7163e"
EXPECTED_SCHEMA_SHA256 = "8298545ad22ddc1e064ae6e2ca8dbc592fcd47ab87f1018e0699fc68474571aa"
ALLOWED_COLUMNS = ("species", "specieskey", "taxonkey", "scientificname", "taxonrank")
FIREWALLED = {
    "OPM_FIG_001",
    "OPM_YUC_001",
    "OPM_YUC_002",
    "SEN001",
    "EPV001",
    "HTR001",
    "KIM001",
    "JOS001",
    "JOS002",
    "JOS003",
}


@dataclass(frozen=True, order=True)
class SnapshotTaxonomyTuple:
    species: str
    specieskey: str
    taxonkey: str
    scientificname: str
    taxonrank: str


@dataclass(frozen=True)
class SnapshotIdentityDeclaration:
    pair_id: str
    taxon_role: str
    biological_name: str
    current_accepted_name: str
    admissible_species_names: tuple[str, ...]
    declaration_frozen: bool
    snapshot_taxonomy_access_started: bool = False


@dataclass(frozen=True)
class SnapshotIdentityDecision:
    passed: bool
    terminal_state: str
    reasons: tuple[str, ...]
    resolved_specieskey: str | None
    distinct_taxonomy_tuples: tuple[SnapshotTaxonomyTuple, ...]


def _clean(value: object) -> str:
    return str(value or "").strip()


def canonicalize_taxonomy_rows(rows: Iterable[Mapping[str, object]]) -> tuple[SnapshotTaxonomyTuple, ...]:
    """Return only distinct allowlisted taxonomy tuples; no row counts survive."""
    tuples = {
        SnapshotTaxonomyTuple(
            species=_clean(row.get("species")),
            specieskey=_clean(row.get("specieskey")),
            taxonkey=_clean(row.get("taxonkey")),
            scientificname=_clean(row.get("scientificname")),
            taxonrank=_clean(row.get("taxonrank")).upper(),
        )
        for row in rows
    }
    return tuple(sorted(tuples))


def validate_identity_declaration(declaration: SnapshotIdentityDeclaration) -> tuple[str, ...]:
    reasons: list[str] = []
    if not declaration.pair_id.strip():
        reasons.append("pair_id_blank")
    if declaration.pair_id in FIREWALLED:
        reasons.append("pair_is_firewalled")
    if declaration.taxon_role not in {"x", "control"}:
        reasons.append("taxon_role_invalid")
    if not declaration.biological_name.strip():
        reasons.append("biological_name_blank")
    if not declaration.current_accepted_name.strip():
        reasons.append("current_accepted_name_blank")
    names = tuple(name.strip() for name in declaration.admissible_species_names if name.strip())
    if not names:
        reasons.append("admissible_species_names_empty")
    if len(set(names)) != len(names):
        reasons.append("admissible_species_names_not_unique")
    if declaration.current_accepted_name not in names:
        reasons.append("current_accepted_name_not_predeclared")
    if declaration.declaration_frozen is not True:
        reasons.append("declaration_not_frozen")
    if declaration.snapshot_taxonomy_access_started:
        reasons.append("declaration_created_after_snapshot_access")
    return tuple(reasons)


def evaluate_snapshot_taxonomy_identity(
    *,
    declaration: SnapshotIdentityDeclaration,
    taxonomy_tuples: Sequence[SnapshotTaxonomyTuple],
) -> SnapshotIdentityDecision:
    declaration_errors = validate_identity_declaration(declaration)
    if declaration_errors:
        return SnapshotIdentityDecision(
            passed=False,
            terminal_state="unresolved_snapshot_taxonomy_identity",
            reasons=declaration_errors,
            resolved_specieskey=None,
            distinct_taxonomy_tuples=tuple(sorted(set(taxonomy_tuples))),
        )

    rows = tuple(sorted(set(taxonomy_tuples)))
    reasons: list[str] = []
    if not rows:
        reasons.append("no_snapshot_taxonomy_tuple")

    allowed_names = set(declaration.admissible_species_names)
    undeclared = sorted({row.species for row in rows if row.species not in allowed_names})
    if undeclared:
        reasons.append("undeclared_species_concept_returned")

    blank_species = any(not row.species for row in rows)
    if blank_species:
        reasons.append("snapshot_species_name_blank")

    keys = {row.specieskey for row in rows if row.specieskey}
    if any(not row.specieskey for row in rows):
        reasons.append("snapshot_specieskey_blank")
    if len(keys) != 1:
        reasons.append("snapshot_specieskey_not_unique")

    invalid_rank = any(row.taxonrank not in {"SPECIES", "SUBSPECIES", "VARIETY", "FORM"} for row in rows)
    if invalid_rank:
        reasons.append("snapshot_taxonrank_outside_species_concept")

    passed = not reasons
    return SnapshotIdentityDecision(
        passed=passed,
        terminal_state="snapshot_taxonomy_identity_passed" if passed else "unresolved_snapshot_taxonomy_identity",
        reasons=tuple(reasons),
        resolved_specieskey=next(iter(keys)) if passed else None,
        distinct_taxonomy_tuples=rows,
    )


def evaluate_v7_3_contract(contract: Mapping[str, object]) -> tuple[str, ...]:
    reasons: list[str] = []
    if contract.get("contract_version") != EXPECTED_CONTRACT_VERSION:
        reasons.append("contract_version_mismatch")
    if contract.get("engineering_only") is not True:
        reasons.append("engineering_only_boundary_changed")
    if contract.get("confirmatory_claims_allowed") is not False:
        reasons.append("confirmatory_boundary_changed")
    if contract.get("snapshot_date") != EXPECTED_SNAPSHOT_DATE:
        reasons.append("snapshot_date_mismatch")
    if contract.get("snapshot_object_manifest_sha256") != EXPECTED_OBJECT_MANIFEST_SHA256:
        reasons.append("snapshot_manifest_mismatch")
    if contract.get("snapshot_schema_sha256") != EXPECTED_SCHEMA_SHA256:
        reasons.append("snapshot_schema_mismatch")
    if tuple(contract.get("allowed_snapshot_columns", ())) != ALLOWED_COLUMNS:
        reasons.append("allowed_snapshot_columns_changed")
    for field in (
        "raw_rows_may_be_persisted",
        "matched_row_counts_may_be_persisted",
        "per_file_counts_may_be_persisted",
        "spatial_columns_may_be_projected",
        "occurrence_identifiers_may_be_projected",
        "dataset_or_recorder_columns_may_be_projected",
        "sampling_authorization_from_this_gate",
    ):
        if contract.get(field) is not False:
            reasons.append(field + "_must_be_false")
    for field in (
        "pair_must_be_frozen_before_snapshot_taxonomy_access",
        "admissible_name_set_must_be_frozen_before_snapshot_taxonomy_access",
        "new_names_after_snapshot_taxonomy_access_forbidden",
    ):
        if contract.get(field) is not True:
            reasons.append(field + "_must_be_true")
    firewall = contract.get("firewalled_pairs")
    if not isinstance(firewall, list) or set(firewall) != FIREWALLED:
        reasons.append("firewall_changed")
    floor = contract.get("sampling_floors_unchanged")
    if not isinstance(floor, Mapping) or (
        floor.get("minimum_independent_records"),
        floor.get("minimum_unique_10km_cells"),
        floor.get("minimum_effective_10km_cells"),
    ) != (50, 30, 10.0):
        reasons.append("sampling_floor_changed")
    return tuple(reasons)


__all__ = [
    "SnapshotTaxonomyTuple",
    "SnapshotIdentityDeclaration",
    "SnapshotIdentityDecision",
    "ALLOWED_COLUMNS",
    "FIREWALLED",
    "canonicalize_taxonomy_rows",
    "validate_identity_declaration",
    "evaluate_snapshot_taxonomy_identity",
    "evaluate_v7_3_contract",
]
