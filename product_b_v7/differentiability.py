"""Response-blind structural sanitizer and differentiability gate for Product-B v7.

This module is deliberately forbidden from using Product-A score or recovery
columns.  It accepts a one-way sanitized structural snapshot containing only
procedure identities and fitted predictor signatures from a presealed model-pool
artifact, then checks whether the frozen architecture can actually distinguish
candidate procedures and whether every declared ecological process has at least
one structurally admissible no-refit knockout route.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from product_b_v5.invariants import ProcedureDescriptor, response_blind_differentiability_precheck


SAFE_STRUCTURE_COLUMNS = (
    "fold",
    "candidate",
    "procedure",
    "strategy",
    "model",
    "selected_predictors",
    "selected_ecological_predictors",
    "n_predictors",
    "n_ecological_predictors",
    "taxon",
    "M",
    "group",
    "excluded_process_domain",
)

FORBIDDEN_VALUE_COLUMNS = frozenset(
    {
        "presence_rank",
        "continuous_boyce",
        "or10",
        "observation_weight_ess",
        "n_model_presence",
        "n_heldout_presence",
        "n_model_background",
        "n_heldout_background",
        "n_reference",
        "n_sealed_occurrences",
        "niche_overlap_schoener_d_pc12",
        "centroid_distance",
        "breadth_log_sd_error",
        "quantile_profile_error",
        "sealed_pc12_envelope_coverage90",
    }
)


@dataclass(frozen=True)
class StructuralMember:
    fold: int
    candidate: str
    procedure: str
    strategy: str
    model: str
    selected_predictors: tuple[str, ...]
    taxon: str
    M: str
    group: str
    excluded_process_domain: str

    @property
    def member_id(self) -> str:
        return f"{self.candidate}::fold={self.fold}"


@dataclass(frozen=True)
class ProcessStructuralStatus:
    process: str
    target_member_count: int
    admissible_member_count: int

    @property
    def admissible(self) -> bool:
        return self.admissible_member_count > 0


@dataclass(frozen=True)
class StructuralDifferentiabilityResult:
    passed: bool
    member_count: int
    unique_candidate_count: int
    distinct_predictor_signature_count: int
    process_status: tuple[ProcessStructuralStatus, ...]
    reasons: tuple[str, ...]


def _split_predictors(value: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in str(value).split(",") if x.strip())


def parse_sanitized_structure_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    expected_taxon: str,
    expected_M: str,
    expected_group: str = "base",
) -> tuple[StructuralMember, ...]:
    if not rows:
        raise ValueError("sanitized structural snapshot is empty")

    members: list[StructuralMember] = []
    seen_ids: set[str] = set()
    for raw in rows:
        keys = set(raw)
        if keys != set(SAFE_STRUCTURE_COLUMNS):
            missing = sorted(set(SAFE_STRUCTURE_COLUMNS) - keys)
            extra = sorted(keys - set(SAFE_STRUCTURE_COLUMNS))
            raise ValueError(f"structural snapshot schema changed: missing={missing} extra={extra}")
        if keys & FORBIDDEN_VALUE_COLUMNS:
            raise ValueError("forbidden Product-A value column entered structural snapshot")

        predictors = _split_predictors(raw["selected_predictors"])
        ecological = _split_predictors(raw["selected_ecological_predictors"])
        if not predictors or not ecological:
            raise ValueError("structural member has no fitted ecological predictor")
        if predictors != ecological:
            raise ValueError("v7 structure source unexpectedly contains non-ecological fitted predictors")
        if int(raw["n_predictors"]) != len(predictors):
            raise ValueError("n_predictors disagrees with sanitized signature")
        if int(raw["n_ecological_predictors"]) != len(ecological):
            raise ValueError("n_ecological_predictors disagrees with sanitized signature")
        if raw["taxon"] != expected_taxon or raw["M"] != expected_M:
            raise ValueError("sanitized structure source identity changed")
        if raw["group"] != expected_group:
            raise ValueError("v7 differentiability must use base group only")
        if str(raw["excluded_process_domain"]).strip():
            raise ValueError("base structural member unexpectedly carries an excluded process")
        member = StructuralMember(
            fold=int(raw["fold"]),
            candidate=str(raw["candidate"]),
            procedure=str(raw["procedure"]),
            strategy=str(raw["strategy"]),
            model=str(raw["model"]),
            selected_predictors=predictors,
            taxon=str(raw["taxon"]),
            M=str(raw["M"]),
            group=str(raw["group"]),
            excluded_process_domain=str(raw["excluded_process_domain"]),
        )
        if member.member_id in seen_ids:
            raise ValueError("duplicate candidate-fold structural member")
        seen_ids.add(member.member_id)
        members.append(member)
    return tuple(members)


def evaluate_structural_differentiability(
    members: Sequence[StructuralMember],
    predictor_to_process: Mapping[str, str],
    process_universe: Sequence[str],
) -> StructuralDifferentiabilityResult:
    if not members:
        raise ValueError("structural members must not be empty")
    processes = tuple(str(x) for x in process_universe)
    if not processes or len(processes) != len(set(processes)):
        raise ValueError("process universe must be non-empty and unique")

    statuses: list[ProcessStructuralStatus] = []
    for process in processes:
        target_members = 0
        admissible_members = 0
        for member in members:
            mapped = tuple(predictor_to_process.get(p) for p in member.selected_predictors)
            unknown = [p for p, m in zip(member.selected_predictors, mapped) if not m]
            if unknown:
                raise ValueError(f"fitted predictor missing frozen process mapping: {unknown}")
            has_target = any(m == process for m in mapped)
            has_retained = any(m != process for m in mapped)
            if has_target:
                target_members += 1
            if has_target and has_retained:
                admissible_members += 1
        statuses.append(
            ProcessStructuralStatus(
                process=process,
                target_member_count=target_members,
                admissible_member_count=admissible_members,
            )
        )

    process_admissibility = {status.process: status.admissible for status in statuses}
    descriptors = tuple(
        ProcedureDescriptor(
            procedure_id=member.member_id,
            selected_predictors=member.selected_predictors,
        )
        for member in members
    )
    base = response_blind_differentiability_precheck(
        descriptors,
        process_admissibility,
        minimum_members=2,
        minimum_distinct_predictor_signatures=2,
    )

    candidate_count = len({member.candidate for member in members})
    reasons = list(base.reasons)
    if candidate_count < 2:
        reasons.append("fewer_than_two_unique_frozen_procedures")
    return StructuralDifferentiabilityResult(
        passed=not reasons,
        member_count=len(members),
        unique_candidate_count=candidate_count,
        distinct_predictor_signature_count=base.distinct_predictor_signature_count,
        process_status=tuple(statuses),
        reasons=tuple(reasons),
    )
