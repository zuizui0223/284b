"""Pure event-space dependency helpers for cross-role Product-B checks.

This module intentionally does not accept raw suitability surfaces. It classifies
predeclared relation keys only after each role has produced its own adequate,
frozen answer on the same biological event key.

For a directional statement ``dependent event requires required-role support``:

- an observed dependent event with adequate required-role support is consistent;
- an observed dependent event with adequate evidence of required-role absence is
  a hard invariant violation;
- missing or inadequate answers are unresolved;
- keys where the dependent event is adequately absent do not trigger the
  implication and therefore do not count as positive consistency evidence.

No occurrence access, model fitting, threshold selection, or focal outcome
opening is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from product_b_v5.invariants import InvariantState


class EventKeyState(str, Enum):
    """State of one predeclared event-level directional relation key."""

    CONSISTENT = "event_relation_consistent"
    VIOLATED = "event_relation_violated"
    UNRESOLVED = "unresolved"
    NOT_TRIGGERED = "dependent_event_not_triggered"


@dataclass(frozen=True)
class EventRelationKey:
    """Frozen answers for one common biological event key.

    ``dependent_event_positive`` represents the event whose occurrence implies a
    requirement (for SMIL001: successful plant reproduction). ``required_support_positive``
    is the independently estimated required-role condition (for SMIL001: adequate
    midge visitation/reachability support at the same opportunity).
    """

    key_id: str
    dependent_event_positive: bool | None
    required_support_positive: bool | None
    dependent_answer_adequate: bool
    required_answer_adequate: bool
    evidence_complete: bool = True


@dataclass(frozen=True)
class EventRelationKeyDecision:
    key_id: str
    state: EventKeyState


@dataclass(frozen=True)
class DirectionalEventRelationDecision:
    """Aggregate hard-invariant state across the full frozen relation-key set."""

    state: InvariantState
    total_keys: int
    consistent_triggered_keys: int
    violated_keys: int
    unresolved_keys: int
    not_triggered_keys: int
    key_decisions: tuple[EventRelationKeyDecision, ...]


def classify_event_relation_key(key: EventRelationKey) -> EventRelationKeyDecision:
    """Classify one directional event relation without imputing missing answers."""

    if not key.key_id:
        raise ValueError("key_id must not be empty")

    if not key.evidence_complete or not key.dependent_answer_adequate:
        return EventRelationKeyDecision(key.key_id, EventKeyState.UNRESOLVED)

    if key.dependent_event_positive is None:
        return EventRelationKeyDecision(key.key_id, EventKeyState.UNRESOLVED)

    if key.dependent_event_positive is False:
        return EventRelationKeyDecision(key.key_id, EventKeyState.NOT_TRIGGERED)

    # The dependent event is positively established, so the required-role answer
    # must now be adequate and resolved on this same key.
    if not key.required_answer_adequate or key.required_support_positive is None:
        return EventRelationKeyDecision(key.key_id, EventKeyState.UNRESOLVED)

    if key.required_support_positive is False:
        return EventRelationKeyDecision(key.key_id, EventKeyState.VIOLATED)

    return EventRelationKeyDecision(key.key_id, EventKeyState.CONSISTENT)


def classify_directional_event_relation(
    keys: Sequence[EventRelationKey],
) -> DirectionalEventRelationDecision:
    """Classify a frozen set of event keys under one hard directional implication.

    A complete violation at any key is sufficient for ``invariant_violated``.
    In the absence of violations, any unresolved predeclared key keeps the whole
    result unresolved because it may hide a required-role failure. Consistency is
    emitted only when at least one dependent event triggers the implication, all
    predeclared keys are resolved, and every triggered key is consistent.

    A set containing only adequately negative dependent events is unresolved
    rather than vacuously promoted to empirical consistency.
    """

    frozen = tuple(keys)
    if not frozen:
        raise ValueError("at least one frozen relation key is required")

    key_ids = [key.key_id for key in frozen]
    if len(key_ids) != len(set(key_ids)):
        raise ValueError("relation key IDs must be unique")

    decisions = tuple(classify_event_relation_key(key) for key in frozen)
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

    return DirectionalEventRelationDecision(
        state=state,
        total_keys=len(decisions),
        consistent_triggered_keys=counts[EventKeyState.CONSISTENT],
        violated_keys=counts[EventKeyState.VIOLATED],
        unresolved_keys=counts[EventKeyState.UNRESOLVED],
        not_triggered_keys=counts[EventKeyState.NOT_TRIGGERED],
        key_decisions=decisions,
    )


__all__ = [
    "EventKeyState",
    "EventRelationKey",
    "EventRelationKeyDecision",
    "DirectionalEventRelationDecision",
    "classify_event_relation_key",
    "classify_directional_event_relation",
]
