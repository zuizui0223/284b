import importlib.util
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_pre_field_identifiability_benchmark.py"

spec = importlib.util.spec_from_file_location("pre_field_benchmark", SCRIPT)
bench = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = bench
spec.loader.exec_module(bench)


def test_single_opportunity_key_sensitivity_equals_event_detection_sensitivity():
    q = bench.conditional_key_sensitivity(0.2, 0.8, 1)
    assert math.isclose(q, 0.8, rel_tol=0.0, abs_tol=1e-12)


def test_subthreshold_process_makes_no_gated_hard_calls():
    result = bench.evaluate_scenario(
        violation_prevalence=0.1,
        event_probability=0.2,
        event_detection_sensitivity=0.5,
        opportunities=1,
        complete_window_fraction=1.0,
        missingness=0.0,
        failure_rate=0.0,
        specificity=0.99,
    )
    assert result.calibration_pass is False
    assert result.gated_false_violation_rate == 0.0
    assert result.gated_true_violation_sensitivity == 0.0
    assert result.gated_unresolved_fraction > 0.0


def test_invalid_state_inflation_identity_for_passing_process():
    result = bench.evaluate_scenario(
        violation_prevalence=0.1,
        event_probability=0.2,
        event_detection_sensitivity=0.8,
        opportunities=5,
        complete_window_fraction=0.8,
        missingness=0.1,
        failure_rate=0.05,
        specificity=0.95,
    )
    assert result.calibration_pass is True
    invalid_mass = 1.0 - result.valid_key_fraction
    assert math.isclose(
        result.naive_false_violation_rate - result.gated_false_violation_rate,
        invalid_mass,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    assert math.isclose(
        result.naive_true_violation_sensitivity
        - result.gated_true_violation_sensitivity,
        invalid_mass,
        rel_tol=0.0,
        abs_tol=1e-12,
    )


def test_passing_gate_caps_key_level_false_violation_rate_at_fnr_threshold():
    rows = list(bench.iter_grid())
    passing = [row for row in rows if row.calibration_pass]
    assert passing
    assert max(row.gated_false_violation_rate for row in passing) <= 0.20 + 1e-12


def test_grid_size_and_no_focal_data_dependency():
    rows = list(bench.iter_grid())
    summary = bench.build_summary(rows)
    assert len(rows) == 8748
    assert summary["focal_level_c_values_read"] is False
    assert summary["scenario_count"] == 8748
    assert summary["structural_results"]["gated_hard_calls_in_failing_scenarios"] == 0.0
