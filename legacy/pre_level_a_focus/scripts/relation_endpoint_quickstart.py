#!/usr/bin/env python3
"""Minimal executable examples for the relation-endpoint method.

All examples are synthetic. They demonstrate endpoint semantics only and do not
read or summarize any focal Level-C biological values.
"""

from __future__ import annotations

import json

from relation_endpoint_contract import (
    RelationEndpointContract,
    evaluate_hard_directional_key,
    evaluate_soft_key,
    hard_rule_operating_characteristics,
)


def build_demo_payload() -> dict:
    soft = RelationEndpointContract(
        contract_id="quickstart_level_a",
        relation_level="A_same_target",
        relation="same-target cross-source soft coherence",
        key_space="matched comparison rows",
        left_adapter="source_A_answer_to_common_rows",
        right_adapter="source_B_answer_to_common_rows",
        left_adequacy_gate="source_A_answer_exists",
        right_adequacy_gate="source_B_answer_exists",
        opening_rule="calibrated_soft_ceiling",
        opening_rule_reference="synthetic_reference_envelope_v1",
    )

    hard = RelationEndpointContract(
        contract_id="quickstart_level_c",
        relation_level="C_directional_dependency",
        relation="E(k) -> F(k)",
        key_space="site x biological opportunity window",
        left_adapter="dependent_event_to_key",
        right_adapter="required_function_to_key",
        left_adequacy_gate="event_answer_exists",
        right_adequacy_gate="function_answer_exists",
        opening_rule="hard_implication",
        opening_rule_reference="synthetic_negative_state_qualification_v1",
    )

    payload = {
        "soft_contract": {
            "relation": soft.relation,
            "key_space": soft.key_space,
            "opening_rule_reference": soft.opening_rule_reference,
            "fingerprint_sha256": soft.fingerprint_sha256(),
            "consistent_example": evaluate_soft_key(
                soft,
                left_adequate=True,
                right_adequate=True,
                discordance=0.12,
                frozen_ceiling=0.20,
            ),
            "attention_example": evaluate_soft_key(
                soft,
                left_adequate=True,
                right_adequate=True,
                discordance=0.27,
                frozen_ceiling=0.20,
            ),
            "unresolved_example": evaluate_soft_key(
                soft,
                left_adequate=True,
                right_adequate=False,
                discordance=0.05,
                frozen_ceiling=0.20,
            ),
        },
        "hard_contract": {
            "relation": hard.relation,
            "key_space": hard.key_space,
            "opening_rule_reference": hard.opening_rule_reference,
            "fingerprint_sha256": hard.fingerprint_sha256(),
            "function_present": evaluate_hard_directional_key(
                hard,
                event_adequate=True,
                function_answer_adequate=True,
                event_positive=True,
                function_state="present",
                observation_process_qualified=True,
                key_valid_for_negative_inference=True,
            ),
            "unqualified_absence": evaluate_hard_directional_key(
                hard,
                event_adequate=True,
                function_answer_adequate=True,
                event_positive=True,
                function_state="absent",
                observation_process_qualified=False,
                key_valid_for_negative_inference=True,
            ),
            "qualified_absence": evaluate_hard_directional_key(
                hard,
                event_adequate=True,
                function_answer_adequate=True,
                event_positive=True,
                function_state="absent",
                observation_process_qualified=True,
                key_valid_for_negative_inference=True,
            ),
            "antecedent_false": evaluate_hard_directional_key(
                hard,
                event_adequate=True,
                function_answer_adequate=True,
                event_positive=False,
                function_state="absent",
                observation_process_qualified=True,
                key_valid_for_negative_inference=True,
            ),
        },
        "invalid_state_ablation": hard_rule_operating_characteristics(
            valid_if_function_present=0.70,
            valid_if_function_absent=0.90,
            key_sensitivity=0.95,
            specificity=0.99,
        ),
        "claim_boundary": {
            "synthetic_only": True,
            "focal_level_c_values_read": False,
            "empirical_ledger_increment": 0,
        },
    }
    return payload


def main() -> None:
    print(json.dumps(build_demo_payload(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
