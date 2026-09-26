"""Pure prospective reference-ceiling calibration helpers."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


@dataclass(frozen=True)
class ReferenceCeilingDecision:
    state: str
    n: int
    quantile: float
    nearest_rank_index_1_based: int | None
    ceiling: float | None


def nearest_rank_quantile(values: Iterable[float], quantile: float) -> tuple[float, int]:
    """Return the classical nearest-rank empirical quantile and 1-based rank.

    All supplied calibration values must be finite. Non-finite authorized
    discordances are an integrity failure and are never silently dropped.
    """
    q = float(quantile)
    if not (0.0 < q <= 1.0):
        raise ValueError("quantile must lie in (0, 1]")
    ordered = [float(value) for value in values]
    if not ordered:
        raise ValueError("nearest-rank quantile requires at least one value")
    if any(not math.isfinite(value) for value in ordered):
        raise ValueError("reference calibration values must all be finite")
    ordered.sort()
    rank = max(1, int(math.ceil(q * len(ordered))))
    return ordered[rank - 1], rank


def freeze_reference_ceiling(
    values: Iterable[float],
    *,
    minimum_n: int = 30,
    quantile: float = 0.95,
) -> ReferenceCeilingDecision:
    """Freeze a reference ceiling only when the prospective sample floor is met."""
    observed = [float(value) for value in values]
    if minimum_n < 1:
        raise ValueError("minimum_n must be positive")
    if any(not math.isfinite(value) for value in observed):
        raise ValueError("reference calibration values must all be finite")
    if len(observed) < minimum_n:
        return ReferenceCeilingDecision(
            state="reference_ceiling_unresolved",
            n=len(observed),
            quantile=float(quantile),
            nearest_rank_index_1_based=None,
            ceiling=None,
        )
    ceiling, rank = nearest_rank_quantile(observed, quantile)
    return ReferenceCeilingDecision(
        state="reference_ceiling_frozen",
        n=len(observed),
        quantile=float(quantile),
        nearest_rank_index_1_based=rank,
        ceiling=ceiling,
    )


__all__ = [
    "ReferenceCeilingDecision",
    "nearest_rank_quantile",
    "freeze_reference_ceiling",
]
