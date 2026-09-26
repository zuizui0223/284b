"""Observation-mode partition rules for same-target paired answer checks.

This module is pure validation. It does not open occurrence rows. Its role is to
ensure that two same-target answers are built from disjoint observation modes and
that one mode cannot leak records or predictions into the other.
"""
from __future__ import annotations

from dataclasses import dataclass


ALLOWED_GBIF_OBSERVATION_MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")
EXPECTED_PARTITION_FIELD = "basisofrecord"


@dataclass(frozen=True)
class SameTargetObservationSplit:
    taxon_name: str
    partition_field: str
    mode_a: str
    mode_b: str
    same_snapshot: bool
    same_spatial_temporal_frame: bool
    answers_fit_independently: bool
    cross_mode_record_leakage: bool = False
    cross_mode_prediction_leakage: bool = False


def validate_same_target_observation_split(
    split: SameTargetObservationSplit,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not split.taxon_name.strip():
        reasons.append("taxon_name_blank")
    if split.partition_field != EXPECTED_PARTITION_FIELD:
        reasons.append("partition_field_mismatch")
    if split.mode_a not in ALLOWED_GBIF_OBSERVATION_MODES:
        reasons.append("mode_a_not_allowed")
    if split.mode_b not in ALLOWED_GBIF_OBSERVATION_MODES:
        reasons.append("mode_b_not_allowed")
    if split.mode_a == split.mode_b:
        reasons.append("observation_modes_not_disjoint")
    if not split.same_snapshot:
        reasons.append("observation_modes_not_from_same_snapshot")
    if not split.same_spatial_temporal_frame:
        reasons.append("spatial_temporal_frame_not_shared")
    if not split.answers_fit_independently:
        reasons.append("answers_not_independently_fit")
    if split.cross_mode_record_leakage:
        reasons.append("cross_mode_record_leakage")
    if split.cross_mode_prediction_leakage:
        reasons.append("cross_mode_prediction_leakage")
    return tuple(reasons)


__all__ = [
    "ALLOWED_GBIF_OBSERVATION_MODES",
    "EXPECTED_PARTITION_FIELD",
    "SameTargetObservationSplit",
    "validate_same_target_observation_split",
]
