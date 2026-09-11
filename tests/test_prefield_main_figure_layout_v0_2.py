import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "prefield_figures_v2", ROOT / "scripts" / "build_prefield_main_figures_v0_2.py"
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

LEVEL_A = json.loads((ROOT / "results" / "reviewer2_level_a_structure_audit_v0_1.json").read_text(encoding="utf-8"))
GENERALIZED = json.loads((ROOT / "results" / "pre_field_state_dependent_invalidity_v0_2.json").read_text(encoding="utf-8"))


def test_figure2_canvas_contains_margin_diagnostics():
    svg = MOD.build_figure2(LEVEL_A)
    assert 'height="970" viewBox="0 0 1200 970"' in svg
    assert "D  Margin diagnostics" in svg
    assert "Interpretation: conditional cross-source reproducibility" in svg


def test_figure5_parameter_line_is_moved_above_bar_plot():
    svg = MOD.build_figure5(GENERALIZED)
    assert 'x="315" y="371"' in svg
    assert 'x="315" y="579"' not in svg
    assert "False violation" in svg
    assert "True-violation sensitivity" in svg


def test_layout_repair_does_not_change_generalized_scientific_claims():
    svg = MOD.build_figure5(GENERALIZED)
    assert "FPRzero − FPRgated = 1 − a₁" in svg
    assert "TPRzero − TPRgated = 1 − a₀" in svg
    assert "Equal-validity corollary" in svg
    assert "FDF≈0.645" in svg
