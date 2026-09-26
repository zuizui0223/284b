"""Pure source-specific sampling adequacy for Layer-1 paired calibration.

Unlike the original symmetric two-partner sampling gate, this module does not
penalize cross-source evidence asymmetry. Each observation source must independently
clear the frozen 50 records / 30 10-km cells / 10 effective-cell floor. The
magnitude of source asymmetry is part of what Layer 1 is meant to calibrate.
"""
from __future__ import annotations

from dataclasses import dataclass

from .sampling import SamplingSummary


@dataclass(frozen=True)
class SourceModeAdequacyDecision:
    passed: bool
    reasons: tuple[str, ...]


def evaluate_source_mode_adequacy(
    summary: SamplingSummary,
    *,
    label: str,
    minimum_independent_records: int = 50,
    minimum_unique_cells: int = 30,
    minimum_effective_cells: float = 10.0,
) -> SourceModeAdequacyDecision:
    if not label.strip():
        raise ValueError("label must not be blank")
    if minimum_independent_records < 1 or minimum_unique_cells < 1 or minimum_effective_cells <= 0:
        raise ValueError("sampling floors must be positive")

    reasons: list[str] = []
    if summary.independent_records < minimum_independent_records:
        reasons.append(f"{label}_independent_record_floor_failed")
    if summary.unique_cells < minimum_unique_cells:
        reasons.append(f"{label}_unique_cell_floor_failed")
    if summary.effective_cells < minimum_effective_cells:
        reasons.append(f"{label}_effective_cell_floor_failed")
    return SourceModeAdequacyDecision(passed=not reasons, reasons=tuple(reasons))


def evaluate_paired_source_mode_adequacy(
    mode_a: SamplingSummary,
    mode_b: SamplingSummary,
    *,
    label_a: str = "preserved_specimen",
    label_b: str = "human_observation",
) -> SourceModeAdequacyDecision:
    a = evaluate_source_mode_adequacy(mode_a, label=label_a)
    b = evaluate_source_mode_adequacy(mode_b, label=label_b)
    reasons = (*a.reasons, *b.reasons)
    return SourceModeAdequacyDecision(passed=not reasons, reasons=tuple(reasons))


__all__ = [
    "SourceModeAdequacyDecision",
    "evaluate_source_mode_adequacy",
    "evaluate_paired_source_mode_adequacy",
]
