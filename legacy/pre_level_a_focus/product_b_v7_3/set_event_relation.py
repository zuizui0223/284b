"""Pure set-valued event dependency helpers for Product-B Level C.

This module generalizes the single-required-role event implication to a frozen
set of biologically admissible alternatives::

    dependent_event(k) -> OR_{r in R(k)} required_support_r(k)

The member set ``R(k)`` is part of the external relation contract. It must not be
expanded, contracted, or selected after focal outcomes are seen.

A positive dependent event is consistent as soon as at least one frozen member
has an adequate positive support answer. By contrast, absence of all *known*
members is a hard violation only when the required-member set is itself externally
certified complete. If set completeness is unresolved, all-known-negative remains
unresolved because an unrepresented alternative could satisfy the dependency.

No occurrence access, model fitting, threshold selection, member discovery, or
focal outcome opening is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from product_b_v5.invariants import InvariantState
from product_b_v7_3.event_relation import EventKeyState


@dataclass(frozen=True)
class RequiredAlternativeAnswer:
    """Frozen required-role answer for one member of an externally defined set."""

    member_id: str
    support_positive: bool | None
    answer_adequate: bool
    evidence_complete: bool = True


@dataclass(frozen=True)
class SetEventRelationKey:
    """One frozen event key for ``E -> OR(R)``.

    ``required_set_complete`` concerns the *membership universe*, not whether an
    individual member's answer is complete. Hard violation requires both kinds of
    completeness.
    """

    key_id: str
    dependent_event_positive: bool | None
    dependent_answer_adequate: bool
    alternatives: tuple[RequiredAlternativeAnswer, ...]
    required_set_complete: bool
    evidence_complete: bool = True


@dataclass(frozen=True)
class SetEventRelationKeyDecision:
    key_id: str
    state: EventKeyState
    positive_alternatives: int
    resolved_negative_alternatives: int
    unresolved_alternatives: int
    required_set_complete: bool


@dataclass(frozen=True)
class SetDirectionalEventRelationDecision:
    state: InvariantState
    total_keys: int
    consistent_triggered_keys: int
    violated_keys: int
    unresolved_keys: int
    not_triggered_keys: int
    key_decisions: tuple[SetEventRelationKeyDecision, ...]


def _validate_alternatives(
    alternatives: Sequence[RequiredAlternativeAnswer],
) -> tuple[RequiredAlternativeAnswer, ...]:
    frozen = tuple(alternatives)
    if not frozen:
        raise ValueError("at least one frozen required alternative is required")
    member_ids = [member.member_id for member in frozen]
    if any(not member_id for member_id in member_ids):
        raise ValueError("required alternative member_id must not be empty")
    if len(member_ids) != len(set(member_ids)):
        raise ValueError("required alternative member_id values must be unique")
    return frozen


def classify_set_event_relation_key(
    key: SetEventRelationKey,
) -> SetEventRelationKeyDecision:
    """Classify one ``dependent event -> OR(required alternatives)`` key."""

    if not key.key_id:
        raise ValueError("key_id must not be empty")
    alternatives = _validate_alternatives(key.alternatives)

    if not key.evidence_complete or not key.dependent_answer_adequate:
        return SetEventRelationKeyDecision(
            key_id=key.key_id,
            state=EventKeyState.UNRESOLVED,
            positive_alternatives=0,
            resolved_negative_alternatives=0,
            unresolved_alternatives=len(alternatives),
            required_set_complete=key.required_set_complete,
        )

    if key.dependent_event_positive is None:
        return SetEventRelationKeyDecision(
            key_id=key.key_id,
            state=EventKeyState.UNRESOLVED,
            positive_alternatives=0,
            resolved_negative_alternatives=0,
            unresolved_alternatives=len(alternatives),
            required_set_complete=key.required_set_complete,
        )

    if key.dependent_event_positive is False:
        return SetEventRelationKeyDecision(
            key_id=key.key_id,
            state=EventKeyState.NOT_TRIGGERED,
            positive_alternatives=0,
            resolved_negative_alternatives=0,
            unresolved_alternatives=0,
            required_set_complete=key.required_set_complete,
        )

    positive = 0
    negative = 0
    unresolved = 0
    for member in alternatives:
        if not member.evidence_complete or not member.answer_adequate:
            unresolved += 1
        elif member.support_positive is None:
            unresolved += 1
        elif member.support_positive:
            positive += 1
        else:
            negative += 1

    # OR semantics: one adequately established frozen alternative is sufficient.
    # Unknown states of other members cannot undo a positive witness.
    if positive > 0:
        state = EventKeyState.CONSISTENT
    elif unresolved > 0:
        state = EventKeyState.UNRESOLVED
    elif not key.required_set_complete:
        # All represented members are adequately negative, but an unrepresented
        # admissible alternative may still satisfy the biological dependency.
        state = EventKeyState.UNRESOLVED
    else:
        state = EventKeyState.VIOLATED

    return SetEventRelationKeyDecision(
        key_id=key.key_id,
        state=state,
        positive_alternatives=positive,
        resolved_negative_alternatives=negative,
        unresolved_alternatives=unresolved,
        required_set_complete=key.required_set_complete,
    )


def classify_set_directional_event_relation(
    keys: Sequence[SetEventRelationKey],
) -> SetDirectionalEventRelationDecision:
    """Aggregate a frozen set of set-valued event keys.

    One complete key-level violation is sufficient for hard invariant violation.
    Otherwise any unresolved predeclared key keeps the aggregate unresolved.
    Consistency requires at least one positively triggered key and no violation or
    unresolved key. A collection of only non-triggered dependent events is not
    promoted by vacuous truth.
    """

    frozen = tuple(keys)
    if not frozen:
        raise ValueError("at least one frozen relation key is required")
    key_ids = [key.key_id for key in frozen]
    if len(key_ids) != len(set(key_ids)):
        raise ValueError("relation key IDs must be unique")

    decisions = tuple(classify_set_event_relation_key(key) for key in frozen)
    counts = {state: 0 for state in EventKeyState}
    for decision in decisions:
        counts[decision.state] += 1

    if counts[EventKeyState.VIOLATED] > 0:
        state = InvariantState.VIOLATED
    elif counts[EventKeyState.UNRESOLVED] > 0:
        state = InvariantState.UNRESOLVED
    elif counts[EventKeyState.CONSISTENT] > 0:
        state = InvariantState.CONSISTENT
    else:
        state = InvariantState.UNRESOLVED

    return SetDirectionalEventRelationDecision(
        state=state,
        total_keys=len(decisions),
        consistent_triggered_keys=counts[EventKeyState.CONSISTENT],
        violated_keys=counts[EventKeyState.VIOLATED],
        unresolved_keys=counts[EventKeyState.UNRESOLVED],
        not_triggered_keys=counts[EventKeyState.NOT_TRIGGERED],
        key_decisions=decisions,
    )


__all__ = [
    "RequiredAlternativeAnswer",
    "SetEventRelationKey",
    "SetEventRelationKeyDecision",
    "SetDirectionalEventRelationDecision",
    "classify_set_event_relation_key",
    "classify_set_directional_event_relation",
]
