import json
from pathlib import Path
import unittest

from product_b_v7_3.event_relation import EventKeyState, EventRelationKey, classify_event_relation_key
from product_b_v7_3.set_event_relation import (
    RequiredAlternativeAnswer,
    SetEventRelationKey,
    classify_set_event_relation_key,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "product_b_level_c_functional_pool_bridge_v1.json"


def member(name, positive):
    return RequiredAlternativeAnswer(
        member_id=name,
        support_positive=positive,
        answer_adequate=True,
        evidence_complete=True,
    )


class FunctionalPoolBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(CONFIG.read_text(encoding="utf-8"))

    def _set_state(self, values, *, complete=True):
        return classify_set_event_relation_key(SetEventRelationKey(
            key_id="k",
            dependent_event_positive=True,
            dependent_answer_adequate=True,
            alternatives=tuple(member(f"m{i}", value) for i, value in enumerate(values)),
            required_set_complete=complete,
            evidence_complete=True,
        )).state

    def _functional_state(self, positive):
        return classify_event_relation_key(EventRelationKey(
            key_id="k",
            dependent_event_positive=True,
            required_support_positive=positive,
            dependent_answer_adequate=True,
            required_answer_adequate=True,
            evidence_complete=True,
        )).state

    def test_complete_member_union_equals_direct_function_when_positive(self):
        values = (False, True, False)
        self.assertEqual(self._set_state(values, complete=True), EventKeyState.CONSISTENT)
        self.assertEqual(self._functional_state(any(values)), EventKeyState.CONSISTENT)

    def test_complete_member_union_equals_direct_function_when_absent(self):
        values = (False, False, False)
        self.assertEqual(self._set_state(values, complete=True), EventKeyState.VIOLATED)
        self.assertEqual(self._functional_state(any(values)), EventKeyState.VIOLATED)

    def test_incomplete_member_union_and_direct_complete_function_can_diverge(self):
        values = (False, False)
        self.assertEqual(self._set_state(values, complete=False), EventKeyState.UNRESOLVED)
        # This second arm represents a separately validated aggregate functional
        # channel, not an inference from the two known negative members.
        self.assertEqual(self._functional_state(False), EventKeyState.VIOLATED)

    def test_direct_functional_absence_must_not_be_inferred_from_incomplete_members(self):
        hard = self.c["hard_boundaries"]
        self.assertFalse(hard["known_member_absence_without_set_completeness_is_functional_absence"])
        self.assertFalse(hard["zero_observed_visits_without_detection_adequacy_is_functional_absence"])

    def test_functional_support_is_not_generic_occurrence(self):
        self.assertFalse(
            self.c["hard_boundaries"]["generic_occurrence_or_suitability_is_functional_support"]
        )

    def test_bridge_is_frozen_pre_search_and_nonempirical(self):
        self.assertEqual(
            self.c["bridge_state"],
            "pure_equivalence_design_frozen_before_any_functional_pool_candidate_search",
        )
        self.assertFalse(self.c["future_candidate_search_authorized_now"])
        self.assertFalse(self.c["focal_data_opening_authorized"])
        self.assertFalse(self.c["hard_invariant_opening_authorized"])
        self.assertFalse(self.c["soft_crosscheck_opening_authorized"])
        self.assertFalse(self.c["process_knockout_authorized"])
        self.assertFalse(self.c["counts_as_empirical_evidence"])
        self.assertFalse(self.c["counts_as_empirical_conclusion"])
        self.assertEqual(self.c["empirical_ledger_increment"], 0)
        self.assertEqual(self.c["global_284b_empirical_ledger_at_bridge_freeze"], 1)


if __name__ == "__main__":
    unittest.main()
