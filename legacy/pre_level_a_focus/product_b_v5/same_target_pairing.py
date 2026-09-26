"""Pure Layer-1 same-target paired-answer metrics.

These helpers consume only already-sealed prediction vectors and source-specific
outer-CV diagnostics. They do not fit models, choose procedures/M, calibrate a
reference ceiling, or run process knockouts.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from collections.abc import Sequence


@dataclass(frozen=True)
class PredictionAdequacy:
    adequate: bool
    evidence_complete: bool
    n_folds: int
    mean_presence_rank: float | None
    sem_presence_rank: float | None
    lower_evidence_bound: float | None
    mean_floor: float
    chance_floor: float
    reasons: tuple[str, ...]


def evaluate_prediction_adequacy(
    values: Sequence[float],
    *,
    expected_folds: int,
    chance_auc: float = 0.50,
    minimum_auc_margin: float = 0.01,
    auc_sem_multiplier: float = 1.0,
) -> PredictionAdequacy:
    """Apply the frozen Product-A prediction-adequacy gate to one answer.

    Passing requires complete outer-fold evidence, mean presence-rank at least
    ``chance_auc + minimum_auc_margin``, and mean minus the frozen SEM multiple
    at least ``chance_auc``.
    """

    if expected_folds < 2:
        raise ValueError("expected_folds must be >= 2")
    if not 0.0 <= chance_auc < 1.0:
        raise ValueError("chance_auc must lie in [0,1)")
    if minimum_auc_margin < 0.0 or chance_auc + minimum_auc_margin > 1.0:
        raise ValueError("invalid minimum_auc_margin")
    if auc_sem_multiplier < 0.0:
        raise ValueError("auc_sem_multiplier must be >= 0")

    finite = [float(x) for x in values if isfinite(float(x))]
    n = len(finite)
    complete = n == int(expected_folds)
    reasons: list[str] = []
    if not complete:
        reasons.append("outer_fold_evidence_incomplete")
    if not finite:
        reasons.append("presence_rank_unavailable")
        return PredictionAdequacy(
            adequate=False,
            evidence_complete=False,
            n_folds=0,
            mean_presence_rank=None,
            sem_presence_rank=None,
            lower_evidence_bound=None,
            mean_floor=float(chance_auc + minimum_auc_margin),
            chance_floor=float(chance_auc),
            reasons=tuple(reasons),
        )

    mean = sum(finite) / n
    if n >= 2:
        variance = sum((x - mean) ** 2 for x in finite) / (n - 1)
        sem = sqrt(variance) / sqrt(n)
    else:
        sem = 0.0
    lower = mean - float(auc_sem_multiplier) * sem
    mean_floor = float(chance_auc + minimum_auc_margin)
    if mean < mean_floor - 1e-12:
        reasons.append("mean_presence_rank_below_frozen_floor")
    if lower < float(chance_auc) - 1e-12:
        reasons.append("presence_rank_lower_bound_below_chance")
    adequate = complete and not reasons
    return PredictionAdequacy(
        adequate=bool(adequate),
        evidence_complete=bool(complete),
        n_folds=n,
        mean_presence_rank=float(mean),
        sem_presence_rank=float(sem),
        lower_evidence_bound=float(lower),
        mean_floor=mean_floor,
        chance_floor=float(chance_auc),
        reasons=tuple(reasons),
    )


def schoener_d_from_sealed_vectors(
    row_ids_a: Sequence[str],
    scores_a: Sequence[float],
    row_ids_b: Sequence[str],
    scores_b: Sequence[float],
) -> float:
    """Compute Schoener's D only on exactly matched sealed comparison rows.

    Each non-negative suitability vector is normalized to sum to one before
    ``D = 1 - 0.5 * sum(abs(p_i - q_i))``. Missing/non-finite scores, duplicate
    row IDs, negative scores, or row-set mismatch fail closed.
    """

    if len(row_ids_a) != len(scores_a) or len(row_ids_b) != len(scores_b):
        raise ValueError("row ids and scores must align")
    if not row_ids_a or not row_ids_b:
        raise ValueError("sealed vectors must not be empty")
    ids_a = [str(x) for x in row_ids_a]
    ids_b = [str(x) for x in row_ids_b]
    if len(set(ids_a)) != len(ids_a) or len(set(ids_b)) != len(ids_b):
        raise ValueError("comparison_row_id must be unique within each source")
    if set(ids_a) != set(ids_b):
        raise ValueError("sealed comparison row sets differ between sources")

    a_map = {rid: float(score) for rid, score in zip(ids_a, scores_a, strict=True)}
    b_map = {rid: float(score) for rid, score in zip(ids_b, scores_b, strict=True)}
    ordered = sorted(a_map)
    a = [a_map[rid] for rid in ordered]
    b = [b_map[rid] for rid in ordered]
    if not all(isfinite(x) for x in (*a, *b)):
        raise ValueError("sealed prediction scores must all be finite")
    if any(x < 0.0 for x in (*a, *b)):
        raise ValueError("sealed prediction scores must be non-negative")
    sum_a = sum(a)
    sum_b = sum(b)
    if sum_a <= 0.0 or sum_b <= 0.0:
        raise ValueError("sealed prediction vectors must have positive mass")
    p = [x / sum_a for x in a]
    q = [x / sum_b for x in b]
    d = 1.0 - 0.5 * sum(abs(x - y) for x, y in zip(p, q, strict=True))
    if d < -1e-12 or d > 1.0 + 1e-12:
        raise RuntimeError("Schoener D escaped [0,1]")
    return float(min(1.0, max(0.0, d)))


def schoener_d_if_both_answers_adequate(
    *,
    adequacy_a: PredictionAdequacy,
    adequacy_b: PredictionAdequacy,
    row_ids_a: Sequence[str],
    scores_a: Sequence[float],
    row_ids_b: Sequence[str],
    scores_b: Sequence[float],
) -> float | None:
    """Open paired prediction discordance only after both answers pass adequacy.

    If either independently fitted answer is inadequate, the sealed prediction
    vectors are deliberately not inspected and ``None`` is returned. This keeps
    cross-source disagreement unavailable for cells that cannot support a valid
    answer-check in the first place.
    """

    if not adequacy_a.adequate or not adequacy_b.adequate:
        return None
    return schoener_d_from_sealed_vectors(row_ids_a, scores_a, row_ids_b, scores_b)


__all__ = [
    "PredictionAdequacy",
    "evaluate_prediction_adequacy",
    "schoener_d_from_sealed_vectors",
    "schoener_d_if_both_answers_adequate",
]
