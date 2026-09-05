"""Pure prospective pair-admission rules for Product-B v7.3.

This module performs no web, taxonomy, snapshot, or occurrence access. It validates
only declarations frozen from biology/literature before any snapshot taxonomy
identity scan is permitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

MIN_DIRECT_WITNESS_SITES = 10
MIN_INDEPENDENT_HOST_REGIONS = 2
MIN_PREDECLARED_CONTROLS = 8
MIN_TAXONOMY_ADMITTED_CONTROLS = 5
FIREWALLED_PAIR_IDS = frozenset({
    "OPM_FIG_001", "OPM_YUC_001", "OPM_YUC_002",
    "SEN001", "EPV001", "HTR001", "KIM001", "JOS001", "JOS002", "JOS003",
})


@dataclass(frozen=True)
class ProspectivePairDeclaration:
    pair_id: str
    x_biological_name: str
    y_biological_name: str
    direction: str
    dependency_class: str
    y_obligately_requires_x: bool
    y_host_specificity_supported: bool
    direct_primary_witness_site_ids: tuple[str, ...]
    independent_host_regions: tuple[str, ...]
    predeclared_control_taxa: tuple[str, ...]
    snapshot_occurrence_information_used_for_selection: bool
    declaration_frozen: bool


@dataclass(frozen=True)
class PairAdmissionDecision:
    passed: bool
    reasons: tuple[str, ...]
    direct_witness_site_count: int
    independent_host_region_count: int
    predeclared_control_count: int


def _unique_nonblank(values: Sequence[str]) -> tuple[str, ...]:
    cleaned = tuple(str(value).strip() for value in values)
    return tuple(sorted({value for value in cleaned if value}))


def evaluate_pair_admission(declaration: ProspectivePairDeclaration) -> PairAdmissionDecision:
    reasons: list[str] = []
    pair_id = str(declaration.pair_id).strip()
    if not pair_id:
        reasons.append("pair_id_blank")
    if pair_id in FIREWALLED_PAIR_IDS:
        reasons.append("pair_is_firewalled")
    if not declaration.x_biological_name.strip() or not declaration.y_biological_name.strip():
        reasons.append("biological_name_blank")
    if declaration.direction != "Y_requires_X":
        reasons.append("direction_must_be_Y_requires_X")
    if not declaration.dependency_class.strip():
        reasons.append("dependency_class_blank")
    if declaration.y_obligately_requires_x is not True:
        reasons.append("dependent_obligacy_not_supported")
    if declaration.y_host_specificity_supported is not True:
        reasons.append("dependent_host_specificity_not_supported")
    if declaration.snapshot_occurrence_information_used_for_selection:
        reasons.append("snapshot_occurrence_selection_forbidden")
    if declaration.declaration_frozen is not True:
        reasons.append("declaration_not_frozen")

    witness_ids = _unique_nonblank(declaration.direct_primary_witness_site_ids)
    if len(witness_ids) < MIN_DIRECT_WITNESS_SITES:
        reasons.append("direct_primary_witness_site_floor_failed")
    if len(witness_ids) != len(tuple(declaration.direct_primary_witness_site_ids)):
        reasons.append("witness_site_ids_blank_or_duplicate")

    regions = _unique_nonblank(declaration.independent_host_regions)
    if len(regions) < MIN_INDEPENDENT_HOST_REGIONS:
        reasons.append("independent_host_region_floor_failed")

    controls = _unique_nonblank(declaration.predeclared_control_taxa)
    if len(controls) < MIN_PREDECLARED_CONTROLS:
        reasons.append("predeclared_control_floor_failed")
    if len(controls) != len(tuple(declaration.predeclared_control_taxa)):
        reasons.append("control_taxa_blank_or_duplicate")
    if declaration.x_biological_name.strip() in controls:
        reasons.append("focal_host_cannot_be_control")

    return PairAdmissionDecision(
        passed=not reasons,
        reasons=tuple(reasons),
        direct_witness_site_count=len(witness_ids),
        independent_host_region_count=len(regions),
        predeclared_control_count=len(controls),
    )


__all__ = [
    "MIN_DIRECT_WITNESS_SITES",
    "MIN_INDEPENDENT_HOST_REGIONS",
    "MIN_PREDECLARED_CONTROLS",
    "MIN_TAXONOMY_ADMITTED_CONTROLS",
    "FIREWALLED_PAIR_IDS",
    "ProspectivePairDeclaration",
    "PairAdmissionDecision",
    "evaluate_pair_admission",
]
