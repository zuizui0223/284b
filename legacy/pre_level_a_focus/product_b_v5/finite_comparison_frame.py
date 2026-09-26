"""Outcome-blind finite comparison-frame construction for same-target repair.

This module is deliberately upstream of model fitting and paired discordance.
It may inspect only the already-declared environmental predictor matrix.  It
never inspects source labels, model scores, Schoener D, held-out outcomes, or
process-knockout results.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FiniteComparisonFrameAudit:
    state: str
    candidate_rows: int
    all_predictor_finite_rows: int
    selected_rows: int
    required_rows: int
    predictor_count: int
    selection_random_state: int


def freeze_finite_comparison_frame(
    frame: pd.DataFrame,
    predictors: Sequence[str],
    *,
    required_rows: int,
    random_state: int,
) -> tuple[pd.DataFrame, FiniteComparisonFrameAudit]:
    """Freeze a fixed-size comparison frame using predictor availability only.

    All declared predictors must be finite before a row can enter the sampling
    pool.  If fewer than ``required_rows`` survive, no partial frame is
    returned: the cell stays unresolved.  When enough rows survive, exactly
    ``required_rows`` are selected without replacement using the predeclared
    random state.  Selection happens before any model score is available.
    """
    names = tuple(str(x) for x in predictors)
    if required_rows < 1:
        raise ValueError("required_rows must be >= 1")
    if not names or len(set(names)) != len(names):
        raise ValueError("predictors must be a non-empty unique sequence")
    missing = set(names) - set(frame.columns)
    if missing:
        raise ValueError(f"comparison frame missing predictors: {sorted(missing)}")

    numeric = frame.loc[:, list(names)].apply(pd.to_numeric, errors="coerce")
    finite_mask = np.isfinite(numeric.to_numpy(float)).all(axis=1)
    complete = frame.loc[finite_mask].copy().reset_index(drop=True)

    if len(complete) < int(required_rows):
        audit = FiniteComparisonFrameAudit(
            state="finite_comparison_frame_unresolved",
            candidate_rows=int(len(frame)),
            all_predictor_finite_rows=int(len(complete)),
            selected_rows=0,
            required_rows=int(required_rows),
            predictor_count=len(names),
            selection_random_state=int(random_state),
        )
        return complete.iloc[0:0].copy(), audit

    rng = np.random.default_rng(int(random_state))
    chosen = np.sort(rng.choice(len(complete), size=int(required_rows), replace=False))
    selected = complete.iloc[chosen].copy().reset_index(drop=True)
    if not np.isfinite(selected.loc[:, list(names)].apply(pd.to_numeric, errors="coerce").to_numpy(float)).all():
        raise RuntimeError("frozen finite comparison frame contains a non-finite predictor")
    audit = FiniteComparisonFrameAudit(
        state="finite_comparison_frame_frozen",
        candidate_rows=int(len(frame)),
        all_predictor_finite_rows=int(len(complete)),
        selected_rows=int(len(selected)),
        required_rows=int(required_rows),
        predictor_count=len(names),
        selection_random_state=int(random_state),
    )
    return selected, audit


__all__ = ["FiniteComparisonFrameAudit", "freeze_finite_comparison_frame"]
