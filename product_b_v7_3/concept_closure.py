"""Pure taxonomy concept-closure gate for fresh same-target calibration taxa.

The historical occurrence snapshot can expose multiple ``specieskey`` values for
one biological species concept.  This successor therefore does not demand one
key.  It accepts a closed set of historical keys only when every distinct
snapshot taxonomic name represented under the exact frozen ``species`` field has
been independently resolved by current taxonomy to the same frozen accepted
species concept.

No function here reads occurrence rows or calls taxonomy services.  Callers pass
only sanitized five-column taxonomy tuples and separately obtained taxonomy-only
name resolutions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .taxonomy_identity import SnapshotTaxonomyTuple

ALLOWED_CONCEPT_RANKS = {"SPECIES", "SUBSPECIES", "VARIETY", "FORM"}


@dataclass(frozen=True)
class CurrentConceptResolution:
    snapshot_scientific_name: str
    resolved: bool
    accepted_species_name: str | None
    accepted_usage_key: str | None = None
    match_type: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class SnapshotConceptClosureDecision:
    passed: bool
    terminal_state: str
    reasons: tuple[str, ...]
    frozen_current_accepted_species: str
    frozen_historical_specieskeys: tuple[str, ...]
    reviewed_snapshot_scientific_names: tuple[str, ...]
    distinct_taxonomy_tuples: tuple[SnapshotTaxonomyTuple, ...]


def evaluate_snapshot_species_concept_closure(
    *,
    current_accepted_species: str,
    taxonomy_tuples: Sequence[SnapshotTaxonomyTuple],
    current_name_resolutions: Mapping[str, CurrentConceptResolution],
) -> SnapshotConceptClosureDecision:
    """Freeze all snapshot keys only when every represented name closes to one species.

    ``current_accepted_species`` is frozen before snapshot access.  Snapshot rows
    must have exactly that value in their ``species`` field.  Multiple historical
    ``specieskey`` values are allowed.  Every distinct ``scientificname`` then
    requires a taxonomy-only current resolution whose accepted species parent is
    the same frozen species.  Any missing/unresolved/conflicting name fails the
    whole taxon; no subset of keys or names may be rescued post hoc.
    """

    focal = str(current_accepted_species).strip()
    if not focal:
        raise ValueError("current_accepted_species must not be blank")

    rows = tuple(sorted(set(taxonomy_tuples)))
    reasons: list[str] = []
    if not rows:
        reasons.append("no_snapshot_taxonomy_tuple")

    species_values = {str(row.species).strip() for row in rows}
    if any(not value for value in species_values):
        reasons.append("snapshot_species_name_blank")
    conflicting_species = sorted(
        value for value in species_values if value and value.casefold() != focal.casefold()
    )
    if conflicting_species:
        reasons.append("snapshot_species_field_conflicts_with_frozen_current_species")

    if any(not str(row.specieskey).strip() for row in rows):
        reasons.append("snapshot_specieskey_blank")
    keys = tuple(sorted({str(row.specieskey).strip() for row in rows if str(row.specieskey).strip()}))
    if not keys:
        reasons.append("snapshot_historical_specieskey_set_empty")

    if any(str(row.taxonrank).strip().upper() not in ALLOWED_CONCEPT_RANKS for row in rows):
        reasons.append("snapshot_taxonrank_outside_species_concept")
    if any(not str(row.scientificname).strip() for row in rows):
        reasons.append("snapshot_scientificname_blank")

    names = tuple(sorted({str(row.scientificname).strip() for row in rows if str(row.scientificname).strip()}))
    missing_reviews = [name for name in names if name not in current_name_resolutions]
    if missing_reviews:
        reasons.append("current_taxonomy_closure_review_missing")

    unresolved_names: list[str] = []
    conflicting_names: list[str] = []
    for name in names:
        resolution = current_name_resolutions.get(name)
        if resolution is None:
            continue
        if str(resolution.snapshot_scientific_name).strip() != name:
            reasons.append("current_taxonomy_closure_review_name_mismatch")
            continue
        accepted = str(resolution.accepted_species_name or "").strip()
        if not resolution.resolved or not accepted:
            unresolved_names.append(name)
        elif accepted.casefold() != focal.casefold():
            conflicting_names.append(name)
    if unresolved_names:
        reasons.append("snapshot_name_current_taxonomy_unresolved")
    if conflicting_names:
        reasons.append("snapshot_name_resolves_to_different_current_species")

    passed = not reasons
    return SnapshotConceptClosureDecision(
        passed=passed,
        terminal_state=(
            "fresh_snapshot_species_concept_closure_passed"
            if passed
            else "fresh_snapshot_species_concept_closure_unresolved"
        ),
        reasons=tuple(dict.fromkeys(reasons)),
        frozen_current_accepted_species=focal,
        frozen_historical_specieskeys=keys if passed else (),
        reviewed_snapshot_scientific_names=names,
        distinct_taxonomy_tuples=rows,
    )


__all__ = [
    "ALLOWED_CONCEPT_RANKS",
    "CurrentConceptResolution",
    "SnapshotConceptClosureDecision",
    "evaluate_snapshot_species_concept_closure",
]
