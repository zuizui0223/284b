import json
from pathlib import Path
import unittest

from product_b_v5.invariants import InvariantState
from product_b_v7_3.event_relation import EventKeyState
from product_b_v7_3.set_event_relation import (
    RequiredAlternativeAnswer,
    SetEventRelationKey,
    classify_set_directional_event_relation,
    classify_set_event_relation_key,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "product_b_level_c_set_valued_dependency_v2.json"
MODULE = ROOT / "product_b_v7_3" / "set_event_relation.py"


def alt(member_id, support, adequate=True, complete=True):
    return RequiredAlternativeAnswer(
        member_id=member_id,
        support_positive=support,
        answer_adequate=adequate,
        evidence_complete=complete,
    )


def key(*, key_id="k", dependent=True, dependent_adequate=True,
        alternatives=(alt("a", True),), set_complete=True, evidence_complete=True):
    return SetEventRelationKey(
        key_id=key_id,
        dependent_event_positive=dependent,
        dependent_answer_adequate=dependent_adequate,
        alternatives=tuple(alternatives),
        required_set_complete=set_complete,
        evidence_complete=evidence_complete,
    )


class SetValuedEventRelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.module_text = MODULE.read_text(encoding="utf-8").lower()

    def test_one_positive_frozen_alternative_is_sufficient_for_or_relation(self):
        decision = classify_set_event_relation_key(key(
            alternatives=(alt("pollinator_a", False), alt("pollinator_b", True)),
            set_complete=False,
        ))
        self.assertEqual(decision.state, EventKeyState.CONSISTENT)
        self.assertEqual(decision.positive_alternatives, 1)

    def test_all_known_negative_is_unresolved_when_required_set_is_incomplete(self):
        decision = classify_set_event_relation_key(key(
            alternatives=(alt("host_a", False), alt("host_b", False)),
            set_complete=False,
        ))
        self.assertEqual(decision.state, EventKeyState.UNRESOLVED)
        self.assertEqual(decision.resolved_negative_alternatives, 2)

    def test_all_negative_is_violation_only_when_set_is_complete(self):
        decision = classify_set_event_relation_key(key(
            alternatives=(alt("host_a", False), alt("host_b", False)),
            set_complete=True,
        ))
        self.assertEqual(decision.state, EventKeyState.VIOLATED)

    def test_inadequate_member_prevents_negative_inference_when_no_positive_witness(self):
        decision = classify_set_event_relation_key(key(
            alternatives=(alt("host_a", False), alt("host_b", None, adequate=False)),
            set_complete=True,
        ))
        self.assertEqual(decision.state, EventKeyState.UNRESOLVED)
        self.assertEqual(decision.unresolved_alternatives, 1)

    def test_positive_witness_is_enough_even_if_other_member_is_unresolved(self):
        decision = classify_set_event_relation_key(key(
            alternatives=(alt("host_a", True), alt("host_b", None, adequate=False)),
            set_complete=False,
        ))
        self.assertEqual(decision.state, EventKeyState.CONSISTENT)

    def test_negative_dependent_event_does_not_trigger_relation(self):
        decision = classify_set_event_relation_key(key(dependent=False))
        self.assertEqual(decision.state, EventKeyState.NOT_TRIGGERED)

    def test_aggregate_violation_dominates(self):
        result = classify_set_directional_event_relation([
            key(key_id="consistent", alternatives=(alt("a", True),), set_complete=True),
            key(key_id="violated", alternatives=(alt("a", False),), set_complete=True),
        ])
        self.assertEqual(result.state, InvariantState.VIOLATED)
        self.assertEqual(result.violated_keys, 1)

    def test_all_not_triggered_is_not_vacuous_consistency(self):
        result = classify_set_directional_event_relation([
            key(key_id="a", dependent=False),
            key(key_id="b", dependent=False),
        ])
        self.assertEqual(result.state, InvariantState.UNRESOLVED)
        self.assertEqual(result.not_triggered_keys, 2)

    def test_duplicate_required_member_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "member_id values must be unique"):
            classify_set_event_relation_key(key(
                alternatives=(alt("same", False), alt("same", True)),
            ))

    def test_membership_change_can_rescue_violation_so_post_outcome_edits_are_forbidden(self):
        violated = classify_set_event_relation_key(key(
            alternatives=(alt("a", False),),
            set_complete=True,
        ))
        rescued = classify_set_event_relation_key(key(
            alternatives=(alt("a", False), alt("b", True)),
            set_complete=True,
        ))
        self.assertEqual(violated.state, EventKeyState.VIOLATED)
        self.assertEqual(rescued.state, EventKeyState.CONSISTENT)
        rc = self.c["required_set_contract"]
        self.assertTrue(rc["member_addition_after_focal_outcome_forbidden"])
        self.assertTrue(rc["member_removal_after_focal_outcome_forbidden"])

    def test_set_completeness_is_explicit_and_required_for_hard_violation(self):
        rc = self.c["required_set_contract"]
        self.assertTrue(rc["set_completeness_is_a_separate_external_claim"])
        self.assertTrue(rc["absence_of_reported_alternatives_is_not_set_completeness"])
        self.assertTrue(rc["hard_violation_requires_set_completeness"])

    def test_v2_cannot_repackage_v1_or_post_cap_seen_candidates(self):
        fresh = self.c["v2_confirmatory_freshness_boundary"]
        self.assertEqual(len(fresh["v1_screened_candidate_ids_excluded"]), 12)
        self.assertIn("SMIL001", fresh["v1_screened_candidate_ids_excluded"])
        self.assertIn(
            "Ganaspis kimorum -> Drosophila suzukii",
            fresh["v1_post_cap_seen_systems_excluded"],
        )
        self.assertFalse(fresh["future_candidate_search_authorized_now"])

    def test_v2_design_is_pre_outcome_and_nonempirical(self):
        self.assertEqual(
            self.c["design_state"],
            "pure_relation_design_frozen_before_any_v2_candidate_search",
        )
        self.assertFalse(self.c["focal_occurrence_or_answer_data_opening_authorized"])
        self.assertFalse(self.c["hard_invariant_opening_authorized"])
        self.assertFalse(self.c["soft_crosscheck_opening_authorized"])
        self.assertFalse(self.c["process_knockout_authorized"])
        self.assertFalse(self.c["counts_as_empirical_evidence"])
        self.assertFalse(self.c["counts_as_empirical_conclusion"])
        self.assertEqual(self.c["empirical_ledger_increment"], 0)
        self.assertEqual(self.c["global_284b_empirical_ledger_at_v2_design_freeze"], 1)

    def test_module_is_pure_and_does_not_discover_members_or_open_data(self):
        for token in (
            "requests", "urllib", "subprocess", "github", "gbif", "inat",
            "pandas", "numpy", "read_csv", "open(", "fetch", "download",
        ):
            self.assertNotIn(token, self.module_text)


if __name__ == "__main__":
    unittest.main()
