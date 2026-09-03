import json
import unittest
from pathlib import Path

from product_b_v5.authorization import (
    ExecutionNotAuthorized,
    evaluate_execution_manifest,
    require_execution_authorization,
)


class AuthorizationGuardTests(unittest.TestCase):
    def setUp(self):
        path = Path("config/product_b_v5_sampling_execution_manifest.json")
        self.manifest = json.loads(path.read_text(encoding="utf-8"))

    def test_committed_manifest_is_frozen_but_not_authorized(self):
        self.assertTrue(self.manifest["contract_frozen"])
        self.assertTrue(self.manifest["scope_gate_frozen"])
        self.assertTrue(self.manifest["preprocessing_contract_frozen"])
        self.assertFalse(self.manifest["execution_authorized"])
        self.assertFalse(self.manifest["occurrence_reads_allowed"])
        decision = evaluate_execution_manifest(self.manifest)
        self.assertFalse(decision.authorized)
        self.assertIn("no_scope_eligible_pairs", decision.reasons)
        self.assertIn("execution_not_authorized", decision.reasons)
        self.assertIn("occurrence_reads_not_allowed", decision.reasons)

    def test_taxonomy_candidate_is_not_yet_occurrence_eligible(self):
        self.assertEqual(
            self.manifest["taxonomy_eligible_pair_ids"],
            ["OPM_FIG_001"],
        )
        self.assertEqual(self.manifest["scope_eligible_pair_ids"], [])

    def test_current_manifest_raises_before_occurrence_access(self):
        with self.assertRaises(ExecutionNotAuthorized):
            require_execution_authorization(
                self.manifest, requested_pair_ids=["OPM_FIG_001"]
            )

    def test_flipping_execution_flags_cannot_bypass_unresolved_scope(self):
        unauthorized = dict(self.manifest)
        unauthorized["execution_authorized"] = True
        unauthorized["occurrence_reads_allowed"] = True
        decision = evaluate_execution_manifest(unauthorized)
        self.assertFalse(decision.authorized)
        self.assertIn("no_scope_eligible_pairs", decision.reasons)

    def test_scope_resolved_authorized_copy_accepts_frozen_fig_pair(self):
        authorized = dict(self.manifest)
        authorized["scope_eligible_pair_ids"] = ["OPM_FIG_001"]
        authorized["execution_authorized"] = True
        authorized["occurrence_reads_allowed"] = True
        decision = require_execution_authorization(
            authorized, requested_pair_ids=["OPM_FIG_001"]
        )
        self.assertTrue(decision.authorized)
        self.assertEqual(decision.eligible_pair_ids, ("OPM_FIG_001",))

    def test_even_scope_resolved_manifest_rejects_pair_outside_frozen_set(self):
        authorized = dict(self.manifest)
        authorized["scope_eligible_pair_ids"] = ["OPM_FIG_001"]
        authorized["execution_authorized"] = True
        authorized["occurrence_reads_allowed"] = True

        with self.assertRaises(ExecutionNotAuthorized):
            require_execution_authorization(
                authorized, requested_pair_ids=["OPM_YUC_002"]
            )

    def test_scope_pair_must_also_be_taxonomy_eligible(self):
        invalid = dict(self.manifest)
        invalid["scope_eligible_pair_ids"] = ["OPM_YUC_002"]
        invalid["execution_authorized"] = True
        invalid["occurrence_reads_allowed"] = True
        decision = evaluate_execution_manifest(invalid)
        self.assertFalse(decision.authorized)
        self.assertIn("scope_pair_not_taxonomy_eligible", decision.reasons)


if __name__ == "__main__":
    unittest.main()
