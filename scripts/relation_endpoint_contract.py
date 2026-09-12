#!/usr/bin/env python3
"""Estimator-agnostic relation-endpoint contract engine.

This module is intentionally small. It does not fit ecological models. It
formalizes the layer above them: what relation independently generated answers
are allowed to test, when an endpoint is openable, and which observations must
remain unresolved.

The reference implementation covers the two endpoint classes demonstrated in
the pre-field paper:

* calibrated soft coherence (Level A and relation-specific Level B checks);
* hard directional implication E(k) -> F(k) (Level C).

Levels D/E can be composed from these primitives after their relation-specific
biology is frozen. No focal Level-C values are read here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SOFT_LEVELS = {"A_same_target", "B_soft_cross_role"}
HARD_LEVELS = {"C_directional_dependency"}
ALL_LEVELS = SOFT_LEVELS | HARD_LEVELS | {"D_mutual_dependency", "E_stage_coupling"}

SoftState = Literal["consistent", "attention_required", "unresolved"]
HardState = Literal[
    "hard_violation_authorized",
    "no_observed_violation",
    "noninformative_for_implication",
    "unresolved",
]


@dataclass(frozen=True)
class RelationEndpointContract:
    contract_id: str
    relation_level: str
    relation: str
    key_space: str
    left_adapter: str
    right_adapter: str
    left_adequacy_gate: str
    right_adequacy_gate: str
    opening_rule: str

    def validate(self) -> None:
        for name, value in (
            ("contract_id", self.contract_id),
            ("relation", self.relation),
            ("key_space", self.key_space),
            ("left_adapter", self.left_adapter),
            ("right_adapter", self.right_adapter),
            ("left_adequacy_gate", self.left_adequacy_gate),
            ("right_adequacy_gate", self.right_adequacy_gate),
            ("opening_rule", self.opening_rule),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.relation_level not in ALL_LEVELS:
            raise ValueError(f"unsupported relation_level: {self.relation_level}")
        if self.relation_level in SOFT_LEVELS and self.opening_rule != "calibrated_soft_ceiling":
            raise ValueError("soft endpoints require calibrated_soft_ceiling")
        if self.relation_level in HARD_LEVELS and self.opening_rule != "hard_implication":
            raise ValueError("directional hard endpoints require hard_implication")


def evaluate_soft_key(
    contract: RelationEndpointContract,
    *,
    left_adequate: bool,
    right_adequate: bool,
    discordance: float | None,
    frozen_ceiling: float | None,
) -> SoftState:
    """Evaluate one calibrated soft-relation key.

    `attention_required` is relation discordance under the frozen comparison
    rule. It is not automatically a biological falsification.
    """
    contract.validate()
    if contract.relation_level not in SOFT_LEVELS:
        raise ValueError("evaluate_soft_key requires a soft relation level")
    if not left_adequate or not right_adequate:
        return "unresolved"
    if discordance is None or frozen_ceiling is None:
        return "unresolved"
    if discordance < 0 or frozen_ceiling < 0:
        raise ValueError("discordance and frozen_ceiling must be non-negative")
    return "consistent" if discordance <= frozen_ceiling else "attention_required"


def evaluate_hard_directional_key(
    contract: RelationEndpointContract,
    *,
    event_adequate: bool,
    function_answer_adequate: bool,
    event_positive: bool | None,
    function_state: Literal["present", "absent", "unresolved"],
    observation_process_qualified: bool,
    key_valid_for_negative_inference: bool,
) -> HardState:
    """Evaluate one frozen directional implication E(k) -> F(k).

    A hard biological contradiction is emitted only when the antecedent event
    is adequately positive and a negative function state is authorized by both
    process qualification and focal-key validity. Unqualified zeros remain
    unresolved by construction.
    """
    contract.validate()
    if contract.relation_level != "C_directional_dependency":
        raise ValueError("evaluate_hard_directional_key requires Level C")
    if function_state not in {"present", "absent", "unresolved"}:
        raise ValueError("invalid function_state")
    if not event_adequate or not function_answer_adequate or event_positive is None:
        return "unresolved"
    if not event_positive:
        return "noninformative_for_implication"
    if function_state == "present":
        return "no_observed_violation"
    if function_state == "unresolved":
        return "unresolved"
    if observation_process_qualified and key_valid_for_negative_inference:
        return "hard_violation_authorized"
    return "unresolved"


def hard_rule_operating_characteristics(
    *,
    valid_if_function_present: float,
    valid_if_function_absent: float,
    key_sensitivity: float,
    specificity: float,
) -> dict[str, float]:
    """Exact class-conditional decomposition for the hard-rule ablation.

    Let a1=P(valid | F=true) for biologically compatible keys and
    a0=P(valid | F=false) for true violations. Then collapsing invalid keys
    into biological negatives inflates false violations by 1-a1 and apparent
    true-violation sensitivity by 1-a0. The familiar equal-validity identity
    is the special case a1=a0=a.
    """
    for name, value in (
        ("valid_if_function_present", valid_if_function_present),
        ("valid_if_function_absent", valid_if_function_absent),
        ("key_sensitivity", key_sensitivity),
        ("specificity", specificity),
    ):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0, 1]")

    a1 = valid_if_function_present
    a0 = valid_if_function_absent
    q = key_sensitivity
    sp = specificity

    zero_fpr = 1.0 - a1 * q
    gated_fpr = a1 * (1.0 - q)
    zero_tpr = 1.0 - a0 * (1.0 - sp)
    gated_tpr = a0 * sp

    return {
        "zero_false_violation_rate": zero_fpr,
        "gated_false_violation_rate": gated_fpr,
        "false_violation_inflation": zero_fpr - gated_fpr,
        "zero_true_violation_sensitivity": zero_tpr,
        "gated_true_violation_sensitivity": gated_tpr,
        "apparent_sensitivity_gain": zero_tpr - gated_tpr,
        "invalid_mass_if_function_present": 1.0 - a1,
        "invalid_mass_if_function_absent": 1.0 - a0,
    }
