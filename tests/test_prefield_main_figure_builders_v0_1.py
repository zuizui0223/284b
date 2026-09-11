import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "prefield_figures", ROOT / "scripts" / "build_prefield_main_figures_v0_1.py"
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

LEVEL_A = json.loads((ROOT / "results" / "reviewer2_level_a_structure_audit_v0_1.json").read_text(encoding="utf-8"))
GENERALIZED = json.loads((ROOT / "results" / "pre_field_state_dependent_invalidity_v0_2.json").read_text(encoding="utf-8"))


def test_figure2_keeps_taxon_replication_distinct_from_cell_diagnostics():
    svg = MOD.build_figure2(LEVEL_A)
    assert "12" in svg
    assert "independent biological units" in svg
    assert "288" in svg
    assert "prespecified diagnostics" in svg
    assert "283" in svg
    assert "evaluable cell diagnostics" in svg
    assert "not 283 independent successes" in svg
    assert "0 / 12" in svg


def test_figure2_labels_q95_as_empirical_envelope():
    svg = MOD.build_figure2(LEVEL_A)
    assert "nearest-rank empirical envelope" in svg
    assert "not a nominal 95% predictive interval" in svg
    assert "34–47 adequate successor taxa / cell" in svg


def test_figure5_uses_generalized_state_dependent_validity():
    svg = MOD.build_figure5(GENERALIZED)
    assert "a₁ = P(valid | F=true)" in svg
    assert "a₀ = P(valid | F=false)" in svg
    assert "false-violation inflation = 1 − a₁" in svg
    assert "apparent sensitivity gain = 1 − a₀" in svg
    assert "Equal-validity corollary" in svg


def test_figure5_explicitly_frames_zero_collapsing_as_ablation():
    svg = MOD.build_figure5(GENERALIZED)
    assert "ablation of the unresolved-state guard" in svg
    assert "not a competitor to occupancy" in svg
    assert "FDF≈0.645" in svg


def test_builders_write_both_svg_files(tmp_path):
    level_svg = MOD.build_figure2(LEVEL_A)
    method_svg = MOD.build_figure5(GENERALIZED)
    f2 = tmp_path / "figure2.svg"
    f5 = tmp_path / "figure5.svg"
    f2.write_text(level_svg, encoding="utf-8")
    f5.write_text(method_svg, encoding="utf-8")
    assert f2.read_text(encoding="utf-8").startswith("<svg")
    assert f5.read_text(encoding="utf-8").startswith("<svg")
