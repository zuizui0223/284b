"""Pure held-out same-target cross-source classification semantics."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class HeldoutCrosscheckDecision:
    state: str
    discordance: float | None
    reference_ceiling: float | None
    exceedance: float | None
    reasons: tuple[str, ...]


def classify_heldout_crosscheck(
    *,
    both_answers_adequate: bool,
    discordance: float | None,
    reference_state: str,
    reference_ceiling: float | None,
) -> HeldoutCrosscheckDecision:
    """Classify one held-out procedure×M answer-check under a frozen reference.

    This helper never computes discordance. Callers must keep prediction vectors
    closed when either source answer is inadequate. A missing reference ceiling
    therefore cannot be replaced by a post-hoc threshold. Equality to the frozen
    ceiling is classified as within-reference; only a strict exceedance is
    attention-required.
    """
    if not both_answers_adequate:
        if discordance is not None:
            raise ValueError("discordance must remain closed when either answer is inadequate")
        return HeldoutCrosscheckDecision(
            state="paired_crosscheck_unresolved",
            discordance=None,
            reference_ceiling=None if reference_ceiling is None else float(reference_ceiling),
            exceedance=None,
            reasons=("one_or_both_source_answers_inadequate",),
        )

    if discordance is None or not math.isfinite(float(discordance)):
        raise ValueError("finite discordance required when both answers are adequate")
    d = float(discordance)
    if not 0.0 <= d <= 1.0:
        raise ValueError("discordance must lie in [0,1]")

    if reference_state != "reference_ceiling_frozen":
        if reference_ceiling is not None:
            raise ValueError("unfrozen reference state may not carry a ceiling")
        return HeldoutCrosscheckDecision(
            state="paired_crosscheck_calibration_unresolved",
            discordance=d,
            reference_ceiling=None,
            exceedance=None,
            reasons=("procedure_M_reference_ceiling_unavailable",),
        )

    if reference_ceiling is None or not math.isfinite(float(reference_ceiling)):
        raise ValueError("frozen reference state requires finite ceiling")
    ceiling = float(reference_ceiling)
    if not 0.0 <= ceiling <= 1.0:
        raise ValueError("reference ceiling must lie in [0,1]")
    exceedance = d - ceiling
    if exceedance <= 1e-12:
        return HeldoutCrosscheckDecision(
            state="paired_crosscheck_consistent",
            discordance=d,
            reference_ceiling=ceiling,
            exceedance=float(exceedance),
            reasons=(),
        )
    return HeldoutCrosscheckDecision(
        state="paired_crosscheck_attention_required",
        discordance=d,
        reference_ceiling=ceiling,
        exceedance=float(exceedance),
        reasons=("heldout_discordance_exceeds_frozen_q95_reference",),
    )


__all__ = ["HeldoutCrosscheckDecision", "classify_heldout_crosscheck"]
