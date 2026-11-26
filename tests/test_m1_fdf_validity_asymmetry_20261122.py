"""Guard class-dependent qualified-call FDF and the historical 284b boundary.

This is an analytic/synthetic assertion only, never a fresh ecological endpoint.
Run: python -m unittest discover -s tests -p test_m1_fdf_validity_asymmetry_20261122.py
"""
from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from relation_endpoint_contract import (
    hard_rule_operating_characteristics,
    qualified_violation_false_discovery_fraction,
)

PI = 0.10
Q = 0.80
SP = 0.99


def fdf(a1: float, a0: float, pi: float = PI) -> float | None:
    return qualified_violation_false_discovery_fraction(
        violation_prevalence=pi,
        valid_if_function_present=a1,
        valid_if_function_absent=a0,
        key_sensitivity=Q,
        specificity=SP,
    )


class ValidityDependentFalseDiscoveryTest(unittest.TestCase):
    def test_equal_validity_corollary(self):
        expected = (0.9 * 0.2) / (0.9 * 0.2 + 0.1 * 0.99)
        for a in (0.15, 0.70, 1.0):
            self.assertAlmostEqual(fdf(a, a), expected, places=12)
        self.assertAlmostEqual(expected, 0.6451612903225806, places=12)

    def test_asymmetry_changes_qualified_call_reliability(self):
        self.assertAlmostEqual(fdf(0.70, 0.90), 0.5857740585774057, places=12)
        self.assertAlmostEqual(fdf(0.90, 0.70), 0.7003891050583658, places=12)
        self.assertLess(fdf(0.70, 0.90), fdf(1.0, 1.0))
        self.assertGreater(fdf(0.90, 0.70), fdf(1.0, 1.0))

    def test_condition_on_valid_uses_shorter_formula_with_new_prevalence(self):
        for a1, a0 in ((0.7, 0.9), (0.9, 0.7), (1.0, 1.0), (0.2, 0.9)):
            p_valid = PI * a0 / ((1 - PI) * a1 + PI * a0)
            conditional = ((1 - p_valid) * (1 - Q)) / (
                (1 - p_valid) * (1 - Q) + p_valid * SP
            )
            self.assertAlmostEqual(fdf(a1, a0), conditional, places=12)

    def test_zero_call_denominator_is_unresolved_not_zero(self):
        self.assertIsNone(fdf(0.0, 0.0))
        self.assertIsNone(fdf(0.0, 1.0, pi=0.0))
        self.assertIsNone(fdf(1.0, 0.0, pi=1.0))
        self.assertAlmostEqual(fdf(1.0, 0.0), 1.0)
        self.assertAlmostEqual(fdf(0.0, 1.0), 0.0)

    def test_out_of_range_parameters_rejected(self):
        invalid = (
            dict(violation_prevalence=-0.01),
            dict(valid_if_function_present=1.01),
            dict(valid_if_function_absent=-0.01),
            dict(key_sensitivity=1.01),
            dict(specificity=-0.01),
        )
        baseline = dict(
            violation_prevalence=PI, valid_if_function_present=0.7,
            valid_if_function_absent=0.9, key_sensitivity=Q, specificity=SP
        )
        for overrides in invalid:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    qualified_violation_false_discovery_fraction(
                        **(baseline | overrides)
                    )

    def test_historical_invalid_state_identities_unchanged(self):
        x = hard_rule_operating_characteristics(
            valid_if_function_present=0.7,
            valid_if_function_absent=0.9,
            key_sensitivity=0.95,
            specificity=0.99,
        )
        self.assertAlmostEqual(x["false_violation_inflation"], 0.3)
        self.assertAlmostEqual(x["apparent_sensitivity_gain"], 0.1)
        self.assertAlmostEqual(x["gated_false_violation_rate"], 0.035)
        self.assertAlmostEqual(x["zero_false_violation_rate"], 0.335)

    def test_manuscript_and_claim_ledger_state_the_assumptions(self):
        manuscript = (ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md").read_text()
        ledger = (ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_CLAIM_LEDGER_V1.md").read_text()
        note = (ROOT / "docs/evidence_boundary_structural_result.md").read_text()
        for label, body in (("manuscript", manuscript), ("ledger", ledger), ("note", note)):
            with self.subTest(label=label):
                self.assertIn("(1-pi)a1(1-q)", body.replace("*", ""))
                self.assertIn("a0", body)
                self.assertIn("0.645", body)
        self.assertIn("a1=a0>0", manuscript)
        self.assertIn("FDF is undefined", manuscript)
        self.assertIn("0/12", manuscript)
        self.assertIn("282 of the original 283", manuscript)
        self.assertNotIn("The valid-key fraction cancels.", manuscript)
        manifest = json.loads(
            (ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_MANIFEST_V1.json").read_text()
        )
        self.assertEqual(manifest["status"], "HOLD_FOR_SENSITIVITY_REVIEW")
        self.assertFalse(manifest["postfreeze_repaired_GBIF_source_sensitivity"][
            "strict_full_historical_283_cell_retention_robust"
        ])
        self.assertEqual(
            manifest["postfreeze_repaired_GBIF_source_sensitivity"][
                "additional_independent_biological_endpoints"
            ], 0
        )


if __name__ == "__main__":
    unittest.main()
