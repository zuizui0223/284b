import unittest

from product_b_v5.invariants import InvariantState
from product_b_v7_3.event_relation import (
    EventKeyState,
    EventRelationKey,
    classify_directional_event_relation,
    classify_event_relation_key,
)


class EventRelationTests(unittest.TestCase):
    def test_positive_event_with_required_support_is_consistent(self):
        decision = classify_event_relation_key(
            EventRelationKey(
                key_id="site-a|window-1",
                dependent_event_positive=True,
                required_support_positive=True,
                dependent_answer_adequate=True,
                required_answer_adequate=True,
            )
        )
        self.assertEqual(decision.state, EventKeyState.CONSISTENT)

    def test_positive_event_with_required_absence_is_violation(self):
        decision = classify_event_relation_key(
            EventRelationKey(
                key_id="site-a|window-1",
                dependent_event_positive=True,
                required_support_positive=False,
                dependent_answer_adequate=True,
                required_answer_adequate=True,
            )
        )
        self.assertEqual(decision.state, EventKeyState.VIOLATED)

    def test_missing_required_answer_is_unresolved_not_violation(self):
        decision = classify_event_relation_key(
            EventRelationKey(
                key_id="site-a|window-1",
                dependent_event_positive=True,
                required_support_positive=None,
                dependent_answer_adequate=True,
                required_answer_adequate=False,
            )
        )
        self.assertEqual(decision.state, EventKeyState.UNRESOLVED)

    def test_negative_dependent_event_does_not_create_consistency_evidence(self):
        decision = classify_event_relation_key(
            EventRelationKey(
                key_id="site-a|window-1",
                dependent_event_positive=False,
                required_support_positive=False,
                dependent_answer_adequate=True,
                required_answer_adequate=False,
            )
        )
        self.assertEqual(decision.state, EventKeyState.NOT_TRIGGERED)

    def test_any_complete_violation_controls_aggregate_state(self):
        result = classify_directional_event_relation(
            [
                EventRelationKey("a", True, True, True, True),
                EventRelationKey("b", True, False, True, True),
                EventRelationKey("c", True, None, True, False),
            ]
        )
        self.assertEqual(result.state, InvariantState.VIOLATED)
        self.assertEqual(result.violated_keys, 1)

    def test_unresolved_key_prevents_aggregate_consistency(self):
        result = classify_directional_event_relation(
            [
                EventRelationKey("a", True, True, True, True),
                EventRelationKey("b", True, None, True, False),
            ]
        )
        self.assertEqual(result.state, InvariantState.UNRESOLVED)
        self.assertEqual(result.consistent_triggered_keys, 1)
        self.assertEqual(result.unresolved_keys, 1)

    def test_all_resolved_triggered_keys_can_be_consistent(self):
        result = classify_directional_event_relation(
            [
                EventRelationKey("a", True, True, True, True),
                EventRelationKey("b", False, None, True, False),
                EventRelationKey("c", True, True, True, True),
            ]
        )
        self.assertEqual(result.state, InvariantState.CONSISTENT)
        self.assertEqual(result.consistent_triggered_keys, 2)
        self.assertEqual(result.not_triggered_keys, 1)

    def test_all_not_triggered_is_unresolved_not_vacuous_consistency(self):
        result = classify_directional_event_relation(
            [
                EventRelationKey("a", False, None, True, False),
                EventRelationKey("b", False, False, True, True),
            ]
        )
        self.assertEqual(result.state, InvariantState.UNRESOLVED)
        self.assertEqual(result.not_triggered_keys, 2)

    def test_duplicate_relation_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            classify_directional_event_relation(
                [
                    EventRelationKey("same", True, True, True, True),
                    EventRelationKey("same", True, True, True, True),
                ]
            )


if __name__ == "__main__":
    unittest.main()
