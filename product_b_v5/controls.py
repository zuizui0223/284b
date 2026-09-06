"""Response-blind negative-control construction for Product-B v5.

The functions operate only on already-computed, frozen sampling summaries and
independently screened interaction metadata. They do not read occurrences,
calculate invariant outcomes, or relax matching criteria in response to results.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite, log2
from typing import Sequence


MATCH_FACTOR = 2.0
MINIMUM_MATCHED_CONTROLS = 5
MAXIMUM_MATCHED_CONTROLS = 20
MINIMUM_SHUFFLE_REPLACEMENTS = 5
SHUFFLE_REPETITIONS = 100
_SEED_LABEL = "product_b_v5_negative_controls_v0.1|shuffle|"


@dataclass(frozen=True)
class ControlTaxonProfile:
    taxon_id: str
    family_key: str
    independent_records: int
    unique_cells: int
    effective_cells: float
    spatial_extent_km2: float


@dataclass(frozen=True)
class FocalPairProfile:
    pair_id: str
    x: ControlTaxonProfile
    y: ControlTaxonProfile


@dataclass(frozen=True)
class NonObligatePairCandidate:
    pair_id: str
    x: ControlTaxonProfile
    y: ControlTaxonProfile
    interaction_screen_passed: bool


@dataclass(frozen=True)
class MatchedControlResult:
    passed: bool
    selected_pair_ids: tuple[str, ...]
    eligible_pair_count: int
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ReplacementCandidate:
    taxon: ControlTaxonProfile
    interaction_screen_passed_with_focal_x: bool


@dataclass(frozen=True)
class ShuffledNullResult:
    passed: bool
    eligible_taxon_ids: tuple[str, ...]
    selected_taxon_ids: tuple[str, ...]
    seeds: tuple[int, ...]
    reasons: tuple[str, ...]


def occupied_cell_centroid_convex_hull_area_km2(
    centroids_m: Sequence[Sequence[float]],
) -> float:
    """Convex-hull area of retained occupied EPSG:6933 cell centroids."""

    points: list[tuple[float, float]] = []
    for raw in centroids_m:
        if len(raw) != 2:
            raise ValueError("cell centroid must contain easting and northing")
        x, y = float(raw[0]), float(raw[1])
        if not isfinite(x) or not isfinite(y):
            raise ValueError("cell centroid coordinates must be finite")
        points.append((x, y))
    unique = sorted(set(points))
    if len(unique) < 3:
        raise ValueError("spatial extent requires at least three distinct cell centroids")

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    for point in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0.0:
            lower.pop()
        lower.append(point)

    upper: list[tuple[float, float]] = []
    for point in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0.0:
            upper.pop()
        upper.append(point)

    hull = lower[:-1] + upper[:-1]
    if len(hull) < 3:
        raise ValueError("spatial extent is undefined for collinear cell centroids")

    twice_area = 0.0
    for first, second in zip(hull, hull[1:] + hull[:1]):
        twice_area += first[0] * second[1] - second[0] * first[1]
    area_m2 = abs(twice_area) / 2.0
    if area_m2 <= 0.0:
        raise ValueError("spatial extent must be positive")
    return area_m2 / 1_000_000.0


def _validate_profile(profile: ControlTaxonProfile) -> None:
    if not profile.taxon_id.strip():
        raise ValueError("taxon_id must not be blank")
    if not profile.family_key.strip():
        raise ValueError("family_key must not be blank")
    if profile.independent_records <= 0:
        raise ValueError("independent_records must be positive")
    if profile.unique_cells <= 0:
        raise ValueError("unique_cells must be positive")
    if not isfinite(profile.effective_cells) or profile.effective_cells <= 0.0:
        raise ValueError("effective_cells must be finite and positive")
    if not isfinite(profile.spatial_extent_km2) or profile.spatial_extent_km2 <= 0.0:
        raise ValueError("spatial_extent_km2 must be finite and positive")


def _ratio_within_factor(a: float, b: float, factor: float = MATCH_FACTOR) -> bool:
    if a <= 0.0 or b <= 0.0:
        return False
    return max(a, b) / min(a, b) <= factor


def _profile_matches(target: ControlTaxonProfile, candidate: ControlTaxonProfile) -> bool:
    _validate_profile(target)
    _validate_profile(candidate)
    if target.family_key != candidate.family_key:
        return False
    return all(
        (
            _ratio_within_factor(target.independent_records, candidate.independent_records),
            _ratio_within_factor(target.unique_cells, candidate.unique_cells),
            _ratio_within_factor(target.effective_cells, candidate.effective_cells),
            _ratio_within_factor(target.spatial_extent_km2, candidate.spatial_extent_km2),
        )
    )


def _abs_log2_ratio(a: float, b: float) -> float:
    return abs(log2(a / b))


def _pair_sort_key(
    focal: FocalPairProfile, candidate: NonObligatePairCandidate
) -> tuple[float, float, float, float, str]:
    record_dev = max(
        _abs_log2_ratio(focal.x.independent_records, candidate.x.independent_records),
        _abs_log2_ratio(focal.y.independent_records, candidate.y.independent_records),
    )
    unique_dev = max(
        _abs_log2_ratio(focal.x.unique_cells, candidate.x.unique_cells),
        _abs_log2_ratio(focal.y.unique_cells, candidate.y.unique_cells),
    )
    effective_dev = max(
        _abs_log2_ratio(focal.x.effective_cells, candidate.x.effective_cells),
        _abs_log2_ratio(focal.y.effective_cells, candidate.y.effective_cells),
    )
    extent_dev = max(
        _abs_log2_ratio(focal.x.spatial_extent_km2, candidate.x.spatial_extent_km2),
        _abs_log2_ratio(focal.y.spatial_extent_km2, candidate.y.spatial_extent_km2),
    )
    return record_dev, unique_dev, effective_dev, extent_dev, candidate.pair_id


def match_non_obligate_controls(
    focal: FocalPairProfile,
    candidates: Sequence[NonObligatePairCandidate],
) -> MatchedControlResult:
    """Select deterministic matched controls under frozen family/caliper rules."""

    _validate_profile(focal.x)
    _validate_profile(focal.y)
    if not focal.pair_id.strip():
        raise ValueError("focal pair_id must not be blank")

    eligible: list[NonObligatePairCandidate] = []
    seen_ids: set[str] = set()
    for candidate in candidates:
        if not candidate.pair_id.strip():
            raise ValueError("candidate pair_id must not be blank")
        if candidate.pair_id in seen_ids:
            raise ValueError("candidate pair_id values must be unique")
        seen_ids.add(candidate.pair_id)
        if not candidate.interaction_screen_passed:
            continue
        if candidate.x.taxon_id == focal.x.taxon_id:
            continue
        if candidate.y.taxon_id == focal.y.taxon_id:
            continue
        if not _profile_matches(focal.x, candidate.x):
            continue
        if not _profile_matches(focal.y, candidate.y):
            continue
        eligible.append(candidate)

    ordered = sorted(eligible, key=lambda item: _pair_sort_key(focal, item))
    selected = tuple(item.pair_id for item in ordered[:MAXIMUM_MATCHED_CONTROLS])
    reasons: list[str] = []
    if len(eligible) < MINIMUM_MATCHED_CONTROLS:
        reasons.append("insufficient_matched_non_obligate_controls")
    return MatchedControlResult(
        passed=not reasons,
        selected_pair_ids=selected,
        eligible_pair_count=len(eligible),
        reasons=tuple(reasons),
    )


def shuffle_seed(iteration: int) -> int:
    if not isinstance(iteration, int) or not (0 <= iteration < SHUFFLE_REPETITIONS):
        raise ValueError(f"iteration must be in [0, {SHUFFLE_REPETITIONS - 1}]")
    digest = sha256(f"{_SEED_LABEL}{iteration}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big", signed=False)


def build_shuffled_partner_null(
    focal: FocalPairProfile,
    replacements: Sequence[ReplacementCandidate],
) -> ShuffledNullResult:
    """Build 100 deterministic matched dependent-partner replacements."""

    _validate_profile(focal.x)
    _validate_profile(focal.y)
    eligible_by_id: dict[str, ReplacementCandidate] = {}
    for candidate in replacements:
        _validate_profile(candidate.taxon)
        taxon_id = candidate.taxon.taxon_id
        if taxon_id in eligible_by_id:
            raise ValueError("replacement taxon_id values must be unique")
        if not candidate.interaction_screen_passed_with_focal_x:
            continue
        if taxon_id == focal.y.taxon_id:
            continue
        if not _profile_matches(focal.y, candidate.taxon):
            continue
        eligible_by_id[taxon_id] = candidate

    eligible_ids = tuple(sorted(eligible_by_id))
    reasons: list[str] = []
    if len(eligible_ids) < MINIMUM_SHUFFLE_REPLACEMENTS:
        reasons.append("insufficient_distinct_shuffled_replacements")
        return ShuffledNullResult(
            passed=False,
            eligible_taxon_ids=eligible_ids,
            selected_taxon_ids=(),
            seeds=tuple(shuffle_seed(i) for i in range(SHUFFLE_REPETITIONS)),
            reasons=tuple(reasons),
        )

    seeds = tuple(shuffle_seed(i) for i in range(SHUFFLE_REPETITIONS))
    selected = tuple(eligible_ids[seed % len(eligible_ids)] for seed in seeds)
    return ShuffledNullResult(
        passed=True,
        eligible_taxon_ids=eligible_ids,
        selected_taxon_ids=selected,
        seeds=seeds,
        reasons=(),
    )
