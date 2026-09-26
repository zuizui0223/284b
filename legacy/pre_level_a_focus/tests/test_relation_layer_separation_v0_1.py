import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_relation_layer_separation_v0_1.py"
RESULT = ROOT / "results" / "relation_layer_separation_v0_1.json"
MEMO = ROOT / "manuscript" / "RELATION_LAYER_SEPARATION_V0_1.md"

SPEC = importlib.util.spec_from_file_location("relation_separation", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_sharp_violation_bounds_are_correct_on_known_cases():
    assert MOD.violation_bounds(0.5, 0.5) == (0.0, 0.5)
    assert MOD.violation_bounds(0.25, 0.75) == (0.0, 0.25)
    assert MOD.violation_bounds(0.75, 0.25) == (0.5, 0.75)
    assert MOD.violation_bounds(0.0, 0.5) == (0.0, 0.0)
    assert MOD.violation_bounds(0.5, 1.0) == (0.0, 0.0)


def test_two_worlds_have_identical_marginals_and_opposite_relation_status():
    good = MOD.coupling_from_cells(0.5, 0.0, 0.0, 0.5)
    bad = MOD.coupling_from_cells(0.0, 0.5, 0.5, 0.0)
    assert good["p_E"] == bad["p_E"] == 0.5
    assert good["p_F"] == bad["p_F"] == 0.5
    assert good["hard_implication_E_to_F_holds_almost_surely"] is True
    assert bad["hard_implication_E_to_F_holds_almost_surely"] is False
    assert good["violation_probability_P_E1_F0"] == 0.0
    assert bad["violation_probability_P_E1_F0"] == 0.5


def test_nonidentifiable_region_classification():
    for p_e, p_f in [(0.25, 0.25), (0.25, 0.5), (0.5, 0.5), (0.5, 0.75)]:
        assert MOD.classify_from_marginals(p_e, p_f) == "hard_implication_status_not_identified_from_marginals"
    assert MOD.classify_from_marginals(0.75, 0.25) == "some_violation_forced_by_marginals"
    assert MOD.classify_from_marginals(0.0, 0.5) == "hard_implication_forced_by_marginals_trivial_boundary"
    assert MOD.classify_from_marginals(0.5, 1.0) == "hard_implication_forced_by_marginals_trivial_boundary"


def test_result_receipt_preserves_claim_boundary():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["two_world_counterexample"]["same_marginal_answers_opposite_relation_status"] is True
    assert result["two_world_counterexample"]["sharp_violation_bounds"] == {"lower": 0.0, "upper": 0.5}
    boundary = result["claim_boundary"]
    assert boundary["does_not_claim_frechet_hoeffding_bounds_are_new"] is True
    assert boundary["does_not_replace_joint_species_distribution_models"] is True
    assert boundary["does_not_replace_detection_models_or_LIES"] is True
    assert boundary["does_not_read_focal_level_c_values"] is True
    assert boundary["empirical_ledger_increment"] == 0


def test_memo_frames_classical_math_as_separation_not_novel_theorem():
    memo = MEMO.read_text(encoding="utf-8")
    assert "not to claim new probability theory" in memo
    assert "Even perfect marginal answers do not" in memo
    assert "identical marginal answers and opposite hard-relation status" in memo
    assert "Improving layer 1 cannot, by itself, supply layers 2 or 3" in memo
    assert "statistical adequacy does not itself choose the biological relation endpoint" in memo
    assert "No focal Level-C values are opened" in memo
