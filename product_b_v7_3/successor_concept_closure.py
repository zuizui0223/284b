"""Rank-agnostic species-concept closure for the independent successor panel.

The snapshot ``taxonrank`` field remains audited but is not an exclusion gate.
The biological gate is the frozen snapshot parent ``species`` plus complete review
of every represented historical scientific name against current taxonomy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .concept_closure import CurrentConceptResolution
from .taxonomy_identity import SnapshotTaxonomyTuple


@dataclass(frozen=True)
class SuccessorSnapshotConceptClosureDecision:
    passed: bool
    terminal_state: str
    reasons: tuple[str, ...]
    frozen_current_accepted_species: str
    frozen_historical_specieskeys: tuple[str, ...]
    reviewed_snapshot_scientific_names: tuple[str, ...]
    current_unresolved_historical_names: tuple[str, ...]
    observed_taxonranks: tuple[str, ...]
    distinct_taxonomy_tuples: tuple[SnapshotTaxonomyTuple, ...]


def evaluate_successor_snapshot_species_concept_closure(
    *,
    current_accepted_species: str,
    taxonomy_tuples: Sequence[SnapshotTaxonomyTuple],
    current_name_resolutions: Mapping[str, CurrentConceptResolution],
) -> SuccessorSnapshotConceptClosureDecision:
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
    if any(value and value.casefold() != focal.casefold() for value in species_values):
        reasons.append("snapshot_species_field_conflicts_with_frozen_current_species")

    if any(not str(row.specieskey).strip() for row in rows):
        reasons.append("snapshot_specieskey_blank")
    keys = tuple(sorted({str(row.specieskey).strip() for row in rows if str(row.specieskey).strip()}))
    if not keys:
        reasons.append("snapshot_historical_specieskey_set_empty")
    if any(not str(row.scientificname).strip() for row in rows):
        reasons.append("snapshot_scientificname_blank")

    names = tuple(sorted({str(row.scientificname).strip() for row in rows if str(row.scientificname).strip()}))
    missing = [name for name in names if name not in current_name_resolutions]
    if missing:
        reasons.append("current_taxonomy_closure_review_missing")

    incomplete: list[str] = []
    unresolved: list[str] = []
    conflicts: list[str] = []
    for name in names:
        resolution = current_name_resolutions.get(name)
        if resolution is None:
            continue
        if str(resolution.snapshot_scientific_name).strip() != name:
            reasons.append("current_taxonomy_closure_review_name_mismatch")
            continue
        if not resolution.review_complete:
            incomplete.append(name)
            continue
        accepted = str(resolution.accepted_species_name or "").strip()
        if not resolution.resolved or not accepted:
            unresolved.append(name)
        elif accepted.casefold() != focal.casefold():
            conflicts.append(name)
    if incomplete:
        reasons.append("current_taxonomy_closure_review_incomplete")
    if conflicts:
        reasons.append("snapshot_name_resolves_to_different_current_species")

    passed = not reasons
    return SuccessorSnapshotConceptClosureDecision(
        passed=passed,
        terminal_state=("successor_snapshot_species_concept_closure_passed" if passed else "successor_snapshot_species_concept_closure_unresolved"),
        reasons=tuple(dict.fromkeys(reasons)),
        frozen_current_accepted_species=focal,
        frozen_historical_specieskeys=keys if passed else (),
        reviewed_snapshot_scientific_names=names,
        current_unresolved_historical_names=tuple(sorted(unresolved)),
        observed_taxonranks=tuple(sorted({str(row.taxonrank).strip().upper() for row in rows})),
        distinct_taxonomy_tuples=rows,
    )


__all__ = ["SuccessorSnapshotConceptClosureDecision", "evaluate_successor_snapshot_species_concept_closure"]
