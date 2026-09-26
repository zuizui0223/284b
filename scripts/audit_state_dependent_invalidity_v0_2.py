#!/usr/bin/env python3
"""Outcome-blind generalization of the invalid-key decomposition.

The original pre-field benchmark used one valid-key fraction a. This audit
makes the implicit symmetry explicit by allowing validity to differ between
biologically compatible keys (F=true) and true violations (F=false).
No focal Level-C values are read.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from relation_endpoint_contract import hard_rule_operating_characteristics


def build_summary() -> dict:
    representative = hard_rule_operating_characteristics(
        valid_if_function_present=0.70,
        valid_if_function_absent=0.90,
        key_sensitivity=0.95,
        specificity=0.99,
    )
    equal_validity = hard_rule_operating_characteristics(
        valid_if_function_present=0.684,
        valid_if_function_absent=0.684,
        key_sensitivity=0.8653439695383153,
        specificity=0.95,
    )
    return {
        "audit_version": "pre_field_state_dependent_invalidity_v0_2",
        "focal_level_c_values_read": False,
        "general_result": {
            "notation": {
                "a1": "P(valid key | F=true)",
                "a0": "P(valid key | F=false)",
                "q": "key sensitivity conditional on F=true and valid key",
                "sp": "specificity conditional on F=false and valid key",
            },
            "false_violation_inflation": "1-a1",
            "apparent_true_violation_sensitivity_gain": "1-a0",
            "equal_validity_corollary": "if a1=a0=a, both increments equal 1-a",
        },
        "representative_state_dependent_scenario": {
            "parameters": {"a1": 0.70, "a0": 0.90, "q": 0.95, "sp": 0.99},
            "result": representative,
        },
        "original_mixed_qualified_equal_validity_corollary": {
            "parameters": {
                "a1": 0.684,
                "a0": 0.684,
                "q": 0.8653439695383153,
                "sp": 0.95,
            },
            "result": equal_validity,
        },
        "interpretation": (
            "The original 1-a identity is exact when validity is class-independent. "
            "With state-dependent validity, the two increments remain exact but are "
            "indexed by their own invalid-state masses. This audit is synthetic and "
            "does not estimate candidate-specific missingness or detection."
        ),
        "empirical_ledger_increment": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/pre_field_state_dependent_invalidity_v0_2.json"),
    )
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(build_summary(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
