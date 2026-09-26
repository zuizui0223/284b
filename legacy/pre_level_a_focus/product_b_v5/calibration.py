"""Deterministic calibration of soft paired-answer discordance ceilings."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import ceil, isfinite
from typing import Sequence


class CalibrationState(str, Enum):
    READY = "paired_crosscheck_calibration_ready"
    UNRESOLVED = "paired_crosscheck_calibration_unresolved"


@dataclass(frozen=True)
class CalibrationTaxonResult:
    taxon_name: str
    mode_a_adequate: bool
    mode_b_adequate: bool
    discordance: float | None


@dataclass(frozen=True)
class CalibrationDecision:
    state: CalibrationState
    reference_ceiling: float | None
    quantile: float
    quantile_method: str
    total_taxa: int
    complete_taxa: int
    unresolved_taxa: int
    included_taxa: tuple[str, ...]
    unresolved_taxon_names: tuple[str, ...]
    reasons: tuple[str, ...]


def _is_complete(result: CalibrationTaxonResult) -> bool:
    return (
        bool(result.taxon_name.strip())
        and result.mode_a_adequate
        and result.mode_b_adequate
        and result.discordance is not None
        and isfinite(result.discordance)
        and result.discordance >= 0.0
    )


def calibrate_reference_ceiling(
    results: Sequence[CalibrationTaxonResult],
    *,
    quantile: float = 0.95,
    minimum_complete_taxa: int = 30,
) -> CalibrationDecision:
    """Freeze a nearest-rank empirical ceiling from all complete calibration taxa.

    No taxon is dropped because its discordance is high. A taxon is unresolved
    only when one observation mode is inadequate or its discordance cannot be
    computed. If fewer than ``minimum_complete_taxa`` remain, no ceiling is
    emitted and the calibration is unresolved.
    """

    if not 0.0 < quantile <= 1.0:
        raise ValueError("quantile must be in (0, 1]")
    if minimum_complete_taxa < 1:
        raise ValueError("minimum_complete_taxa must be positive")

    names = [result.taxon_name.strip() for result in results]
    if any(not name for name in names):
        raise ValueError("calibration taxon names must be nonblank")
    if len(names) != len(set(names)):
        raise ValueError("calibration taxon names must be unique")

    complete = tuple(result for result in results if _is_complete(result))
    unresolved = tuple(result for result in results if not _is_complete(result))
    included_taxa = tuple(result.taxon_name.strip() for result in complete)
    unresolved_names = tuple(result.taxon_name.strip() for result in unresolved)

    if len(complete) < minimum_complete_taxa:
        return CalibrationDecision(
            state=CalibrationState.UNRESOLVED,
            reference_ceiling=None,
            quantile=quantile,
            quantile_method="nearest_rank",
            total_taxa=len(results),
            complete_taxa=len(complete),
            unresolved_taxa=len(unresolved),
            included_taxa=included_taxa,
            unresolved_taxon_names=unresolved_names,
            reasons=("insufficient_complete_calibration_taxa",),
        )

    values = sorted(float(result.discordance) for result in complete if result.discordance is not None)
    rank = max(1, ceil(quantile * len(values)))
    ceiling = values[rank - 1]
    return CalibrationDecision(
        state=CalibrationState.READY,
        reference_ceiling=ceiling,
        quantile=quantile,
        quantile_method="nearest_rank",
        total_taxa=len(results),
        complete_taxa=len(complete),
        unresolved_taxa=len(unresolved),
        included_taxa=included_taxa,
        unresolved_taxon_names=unresolved_names,
        reasons=(),
    )


__all__ = [
    "CalibrationState",
    "CalibrationTaxonResult",
    "CalibrationDecision",
    "calibrate_reference_ceiling",
]
