import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "relation_endpoint_contract", ROOT / "scripts" / "relation_endpoint_contract.py"
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def soft_contract():
    return MOD.RelationEndpointContract(
        contract_id="level_a_demo",
        relation_level="A_same_target",
        key_space="same 2000 comparison rows",
        left_adapter="identity_to_common_rows",
        right_adapter="identity_to_common_rows",
        left_adequacy_gate="source_A_adequate",
        right_adequacy_gate="source_B_adequate",
        opening_rule="calibrated_soft_ceiling",
    )


def hard_contract():
    return MOD.RelationEndpointContract(
        contract_id="level_c_demo",
        relation_level="C_directional_dependency",
        key_space="site x opportunity window",
        left_adapter="event_to_key",
        right_adapter="function_to_key",
        left_adequacy_gate="event_answer_adequate",
        right_adequacy_gate="function_answer_adequate",
        opening_rule="hard_implication",
    )


def test_soft_endpoint_preserves_inadequacy_as_unresolved():
    c = soft_contract()
    assert MOD.evaluate_soft_key(
        c,
        left_adequate=False,
        right_adequate=True,
        discordance=0.9,
        frozen_ceiling=0.2,
    ) == "unresolved"


def test_soft_endpoint_uses_frozen_ceiling_only_after_both_answers_exist():
    c = soft_contract()
    assert MOD.evaluate_soft_key(
        c,
        left_adequate=True,
        right_adequate=True,
        discordance=0.19,
        frozen_ceiling=0.20,
    ) == "consistent"
    assert MOD.evaluate_soft_key(
        c,
        left_adequate=True,
        right_adequate=True,
        discordance=0.21,
        frozen_ceiling=0.20,
    ) == "attention_required"


def test_hard_endpoint_never_turns_unqualified_absence_into_violation():
    c = hard_contract()
    assert MOD.evaluate_hard_directional_key(
        c,
        event_adequate=True,
        function_answer_adequate=True,
        event_positive=True,
        function_state="absent",
        observation_process_qualified=False,
        key_valid_for_negative_inference=True,
    ) == "unresolved"
    assert MOD.evaluate_hard_directional_key(
        c,
        event_adequate=True,
        function_answer_adequate=True,
        event_positive=True,
        function_state="absent",
        observation_process_qualified=True,
        key_valid_for_negative_inference=False,
    ) == "unresolved"


def test_hard_endpoint_authorizes_only_qualified_valid_negative():
    c = hard_contract()
    assert MOD.evaluate_hard_directional_key(
        c,
        event_adequate=True,
        function_answer_adequate=True,
        event_positive=True,
        function_state="absent",
        observation_process_qualified=True,
        key_valid_for_negative_inference=True,
    ) == "hard_violation_authorized"


def test_implication_is_noninformative_when_antecedent_is_false():
    c = hard_contract()
    assert MOD.evaluate_hard_directional_key(
        c,
        event_adequate=True,
        function_answer_adequate=True,
        event_positive=False,
        function_state="absent",
        observation_process_qualified=True,
        key_valid_for_negative_inference=True,
    ) == "noninformative_for_implication"


def test_state_dependent_validity_generalizes_equal_a_identity():
    r = MOD.hard_rule_operating_characteristics(
        valid_if_function_present=0.70,
        valid_if_function_absent=0.90,
        key_sensitivity=0.95,
        specificity=0.99,
    )
    assert abs(r["false_violation_inflation"] - 0.30) < 1e-12
    assert abs(r["apparent_sensitivity_gain"] - 0.10) < 1e-12

    equal = MOD.hard_rule_operating_characteristics(
        valid_if_function_present=0.68,
        valid_if_function_absent=0.68,
        key_sensitivity=0.90,
        specificity=0.98,
    )
    assert abs(equal["false_violation_inflation"] - 0.32) < 1e-12
    assert abs(equal["apparent_sensitivity_gain"] - 0.32) < 1e-12
