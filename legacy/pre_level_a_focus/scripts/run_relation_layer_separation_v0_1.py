#!/usr/bin/env python3
"""Exact counterexample showing that valid marginal answers do not identify a hard relation.

The probability mathematics is classical Fréchet-Hoeffding coupling logic.
The ecological use here is narrower: demonstrate that perfect role-specific
marginal answers are insufficient to identify a directional relation endpoint
without a common event key / joint relation specification.

No focal Level-C values are read.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "relation_layer_separation_v0_1.json"


def violation_bounds(p_e: float, p_f: float) -> tuple[float, float]:
    """Sharp bounds for v=P(E=1,F=0) given only Bernoulli marginals.

    If j=P(E=1,F=1), Fréchet-Hoeffding gives
      max(0,p_e+p_f-1) <= j <= min(p_e,p_f).
    Because v=p_e-j,
      max(0,p_e-p_f) <= v <= min(p_e,1-p_f).
    """
    if not (0.0 <= p_e <= 1.0 and 0.0 <= p_f <= 1.0):
        raise ValueError("marginal probabilities must lie in [0,1]")
    lo = max(0.0, p_e - p_f)
    hi = min(p_e, 1.0 - p_f)
    return lo, hi


def classify_from_marginals(p_e: float, p_f: float, tol: float = 1e-12) -> str:
    lo, hi = violation_bounds(p_e, p_f)
    if hi <= tol:
        return "hard_implication_forced_by_marginals_trivial_boundary"
    if lo > tol:
        return "some_violation_forced_by_marginals"
    return "hard_implication_status_not_identified_from_marginals"


def coupling_from_cells(p00: float, p01: float, p10: float, p11: float) -> dict:
    vals = [p00, p01, p10, p11]
    if any(v < -1e-12 for v in vals) or abs(sum(vals) - 1.0) > 1e-12:
        raise ValueError("invalid 2x2 coupling")
    p_e = p10 + p11
    p_f = p01 + p11
    v = p10
    return {
        "cells": {"E0_F0": p00, "E0_F1": p01, "E1_F0": p10, "E1_F1": p11},
        "p_E": p_e,
        "p_F": p_f,
        "violation_probability_P_E1_F0": v,
        "hard_implication_E_to_F_holds_almost_surely": abs(v) <= 1e-12,
    }


def main() -> None:
    p_e = 0.5
    p_f = 0.5
    lo, hi = violation_bounds(p_e, p_f)

    compatible_world = coupling_from_cells(0.5, 0.0, 0.0, 0.5)
    violating_world = coupling_from_cells(0.0, 0.5, 0.5, 0.0)

    assert compatible_world["p_E"] == violating_world["p_E"] == p_e
    assert compatible_world["p_F"] == violating_world["p_F"] == p_f
    assert compatible_world["violation_probability_P_E1_F0"] == lo == 0.0
    assert violating_world["violation_probability_P_E1_F0"] == hi == 0.5

    grid = []
    for p_e_grid in (0.0, 0.25, 0.5, 0.75, 1.0):
        for p_f_grid in (0.0, 0.25, 0.5, 0.75, 1.0):
            b_lo, b_hi = violation_bounds(p_e_grid, p_f_grid)
            grid.append(
                {
                    "p_E": p_e_grid,
                    "p_F": p_f_grid,
                    "violation_lower": b_lo,
                    "violation_upper": b_hi,
                    "classification": classify_from_marginals(p_e_grid, p_f_grid),
                }
            )

    payload = {
        "result_version": "relation_layer_separation_v0_1",
        "mathematical_status": "exact_classical_frechet_hoeffding_construction_not_new_probability_theory",
        "ecological_question": "Do individually valid marginal answers identify the hard relation E(k)->F(k)?",
        "general_result": {
            "violation_quantity": "v=P(E=1,F=0)",
            "lower_bound": "max(0,p_E-p_F)",
            "upper_bound": "min(p_E,1-p_F)",
            "nonidentifiable_region": "0<p_E<=p_F<1 gives lower=0 and upper>0, so both zero-violation and positive-violation couplings are compatible with the same marginals",
            "interpretation": "Marginal answer validity is not sufficient for hard relation validity. Joint/event-key information or an externally frozen adapter/relation is a separate inferential requirement.",
        },
        "two_world_counterexample": {
            "shared_marginals": {"p_E": p_e, "p_F": p_f},
            "sharp_violation_bounds": {"lower": lo, "upper": hi},
            "dependency_compatible_world": compatible_world,
            "dependency_violating_world": violating_world,
            "same_marginal_answers_opposite_relation_status": True,
        },
        "coarse_grid": grid,
        "claim_boundary": {
            "does_not_claim_frechet_hoeffding_bounds_are_new": True,
            "does_not_replace_joint_species_distribution_models": True,
            "does_not_replace_detection_models_or_LIES": True,
            "does_not_read_focal_level_c_values": True,
            "empirical_ledger_increment": 0,
        },
    }

    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
