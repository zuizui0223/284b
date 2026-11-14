"""Regression tests for FDF prevalence conditioning; no focal biological data read."""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from relation_endpoint_contract import (
    qualified_violation_false_discovery_fraction as fdf,
    valid_key_violation_prevalence,
)


def test_predeclared_fdf_anchor_under_equal_validity():
    for a in (0.2, 0.7, 1.0):
        observed = fdf(violation_prevalence=0.1,
                       valid_if_function_present=a,
                       valid_if_function_absent=a,
                       key_sensitivity=0.8, specificity=0.99)
        assert math.isclose(observed, 0.18 / (0.18 + 0.099),
                            rel_tol=0, abs_tol=1e-12)


def test_population_prevalence_requires_class_specific_validity():
    pi, a1, a0, q, sp = 0.1, 0.7, 0.9, 0.8, 0.99
    actual = fdf(violation_prevalence=pi,
                 valid_if_function_present=a1,
                 valid_if_function_absent=a0,
                 key_sensitivity=q, specificity=sp)
    assert math.isclose(actual, 0.126 / (0.126 + 0.0891),
                        rel_tol=0, abs_tol=1e-12)
    assert not math.isclose(actual, 0.18 / (0.18 + 0.099),
                            rel_tol=0, abs_tol=0.01)
    pi_valid = valid_key_violation_prevalence(
        violation_prevalence=pi,
        valid_if_function_present=a1,
        valid_if_function_absent=a0)
    assert math.isclose(pi_valid, 0.125, rel_tol=0, abs_tol=1e-12)
    recovered = fdf(violation_prevalence=pi_valid,
                    valid_if_function_present=1,
                    valid_if_function_absent=1,
                    key_sensitivity=q, specificity=sp)
    assert math.isclose(actual, recovered, rel_tol=0, abs_tol=1e-12)


def test_zero_qualified_calls_are_undefined_not_perfect():
    assert fdf(violation_prevalence=0, valid_if_function_present=1,
               valid_if_function_absent=1, key_sensitivity=1,
               specificity=0.99) is None
    assert fdf(violation_prevalence=0.5, valid_if_function_present=0,
               valid_if_function_absent=0, key_sensitivity=0.8,
               specificity=0.99) is None
    assert valid_key_violation_prevalence(
        violation_prevalence=0.5,
        valid_if_function_present=0,
        valid_if_function_absent=0) is None


def test_extremes_and_invalid_parameters():
    assert fdf(violation_prevalence=1, valid_if_function_present=1,
               valid_if_function_absent=1, key_sensitivity=0.8,
               specificity=1) == 0.0
    assert fdf(violation_prevalence=0, valid_if_function_present=1,
               valid_if_function_absent=1, key_sensitivity=0,
               specificity=1) == 1.0
    import pytest
    with pytest.raises(ValueError):
        fdf(violation_prevalence=1.2, valid_if_function_present=1,
            valid_if_function_absent=1, key_sensitivity=0.8,
            specificity=0.99)
