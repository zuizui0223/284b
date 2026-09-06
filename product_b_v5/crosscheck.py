"""General paired answer-check helpers for Product-B.

The scientific idea is broader than obligate mutualism. Two independently fitted
answers can be expected, from external biology, to agree in a declared way even
when neither answer is used to fit the other. Large disagreement is therefore a
warning signal.

Hard biological invariants (for example mutual obligacy) remain handled by the
existing invariant classifiers. This module provides a softer, general-purpose
cross-check: disagreement beyond a predeclared reference ceiling is
``attention_required`` rather than an automatic biological violation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite


class PairedCheckState(str, Enum):
    """Terminal state for a soft paired answer-check."""

    CONSISTENT = "paired_crosscheck_consistent"
    ATTENTION_REQUIRED = "paired_crosscheck_attention_required"
    UNRESOLVED = "paired_crosscheck_unresolved"


@dataclass(frozen=True)
class PairedAnswerCheckDecision:
    """Decision for two independently obtained but biologically coupled answers."""

    state: PairedCheckState
    observed_discordance: float | None
    reference_ceiling: float
    excess_discordance: float | None
    reasons: tuple[str, ...]


def classify_paired_answer_check(
    *,
    discordance: float | None,
    reference_ceiling: float,
    adequacy_a: bool,
    adequacy_b: bool,
    evidence_complete: bool = True,
) -> PairedAnswerCheckDecision:
    """Flag unexpectedly divergent independent answers without overclaiming.

    ``reference_ceiling`` must be frozen independently of the focal outcome. It
    may come from a preregistered tolerance, an external calibration panel, or a
    held-out/matched reference distribution whose construction rule was fixed
    before the focal pair was opened.

    This is deliberately softer than a biological invariant. Exceeding the
    ceiling yields ``attention_required``; it does not by itself prove that one
    model, one taxon, or the external biological relation is wrong.
    """

    if not isfinite(reference_ceiling) or reference_ceiling < 0.0:
        raise ValueError("reference_ceiling must be finite and non-negative")

    reasons: list[str] = []
    if not evidence_complete:
        reasons.append("evidence_incomplete")
    if not adequacy_a:
        reasons.append("answer_a_inadequate")
    if not adequacy_b:
        reasons.append("answer_b_inadequate")
    if discordance is None or not isfinite(discordance) or discordance < 0.0:
        reasons.append("discordance_unavailable")

    if reasons:
        return PairedAnswerCheckDecision(
            state=PairedCheckState.UNRESOLVED,
            observed_discordance=discordance,
            reference_ceiling=reference_ceiling,
            excess_discordance=None,
            reasons=tuple(reasons),
        )

    assert discordance is not None
    excess = discordance - reference_ceiling
    state = (
        PairedCheckState.ATTENTION_REQUIRED
        if discordance > reference_ceiling
        else PairedCheckState.CONSISTENT
    )
    return PairedAnswerCheckDecision(
        state=state,
        observed_discordance=discordance,
        reference_ceiling=reference_ceiling,
        excess_discordance=excess,
        reasons=(),
    )


def reciprocal_containment_discordance(
    containment_b_in_a: float,
    containment_a_in_b: float,
) -> float:
    """Simple asymmetry diagnostic for two reciprocal containment answers.

    The metric is zero when the two directions agree and approaches one as they
    diverge. It is descriptive unless a biological contract explicitly upgrades
    one or both directions to a hard invariant.
    """

    for value in (containment_b_in_a, containment_a_in_b):
        if not isfinite(value) or not (0.0 <= value <= 1.0):
            raise ValueError("containment values must be finite and in [0, 1]")
    return abs(containment_b_in_a - containment_a_in_b)


__all__ = [
    "PairedCheckState",
    "PairedAnswerCheckDecision",
    "classify_paired_answer_check",
    "reciprocal_containment_discordance",
]
