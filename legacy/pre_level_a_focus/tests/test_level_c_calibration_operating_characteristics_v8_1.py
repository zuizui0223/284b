import importlib.util
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location(
    "level_c_v8_1_oc",
    SCRIPTS / "audit_level_c_calibration_operating_characteristics_v8_1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def test_minimum_design_critical_counts_are_28_of_30_and_60_of_60():
    assert MOD.critical_successes(30, 0.80) == 28
    assert MOD.critical_successes(60, 0.95) == 60


def test_minimum_specificity_pass_probability_matches_all_success_probability():
    result = MOD.pass_probability(60, 0.99, 0.95)
    assert result["critical_successes"] == 60
    assert math.isclose(result["pass_probability"], 0.99 ** 60, rel_tol=0.0, abs_tol=1e-14)


def test_true_threshold_has_low_probability_of_lower_bound_clearing_it():
    sens = MOD.pass_probability(30, 0.80, 0.80)
    spec = MOD.pass_probability(60, 0.95, 0.95)
    assert sens["pass_probability"] < 0.05
    assert spec["pass_probability"] < 0.05


def test_first_n_for_80_percent_power_examples_are_deterministic():
    sensitivity = MOD.first_n_for_power(0.90, 0.80, n_min=30)
    specificity = MOD.first_n_for_power(0.99, 0.95, n_min=60)
    assert sensitivity["n"] == 82
    assert sensitivity["critical_successes"] == 72
    assert specificity["n"] == 124
    assert specificity["critical_successes"] == 122


def test_summary_is_outcome_blind_and_nonempirical():
    summary = MOD.build_summary()
    assert summary["field_calibration_values_read"] is False
    assert summary["focal_level_c_values_read"] is False
    assert summary["empirical_ledger_increment"] == 0
