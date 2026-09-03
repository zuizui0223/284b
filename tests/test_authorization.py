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
        self.assertTrue(self.manifest["transport_contract_frozen"])
        self.assertFalse(self.manifest["execution_authorized"])
        self.assertFalse(self.manifest["occurrence_reads_allowed"])
        decision = evaluate_execution_manifest(self.manifest)
        self.assertFalse(decision.authorized)
        self.assertNotIn("no_scope_eligible_pairs", decision.reasons)
        self.assertNotIn("transport_contract_not_frozen", decision.reasons)
        self.assertIn("execution_not_authorized", decision.reasons)
        self.assertIn("occurrence_reads_not_allowed", decision.reasons)

    def test_fig_pair_passes_taxonomy_and_scope_gates_but_not_execution_gate(self):
        self.assertEqual(
            self.manifest["taxonomy_eligible_pair_ids"],
            ["OPM_FIG_001"],
        )
        self.assertEqual(
            self.manifest["scope_eligible_pair_ids"],
            ["OPM_FIG_001"],
        )

    def test_current_manifest_raises_before_occurrence_access(self):
        with self.assertRaises(ExecutionNotAuthorized):
            require_execution_authorization(
                self.manifest, requested_pair_ids=["OPM_FIG_001"]
            )

    def test_fully_authorized_copy_accepts_only_frozen_fig_pair(self):
        authorized = dict(self.manifest)
        authorized["execution_authorized"] = True
        authorized["occurrence_reads_allowed"] = True
        decision = require_execution_authorization(
            authorized, requested_pair_ids=["OPM_FIG_001"]
        )
        self.assertTrue(decision.authorized)
        self.assertEqual(decision.eligible_pair_ids, ("OPM_FIG_001",))

    def test_authorized_manifest_rejects_pair_outside_frozen_set(self):
        authorized = dict(self.manifest)
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

    def test_removing_scope_pair_fails_closed_even_if_flags_are_true(self):
        invalid = dict(self.manifest)
        invalid["scope_eligible_pair_ids"] = []
        invalid["execution_authorized"] = True
        invalid["occurrence_reads_allowed"] = True
        decision = evaluate_execution_manifest(invalid)
        self.assertFalse(decision.authorized)
        self.assertIn("no_scope_eligible_pairs", decision.reasons)

    def test_unfreezing_transport_contract_fails_closed(self):
        invalid = dict(self.manifest)
        invalid["transport_contract_frozen"] = False
        invalid["execution_authorized"] = True
        invalid["occurrence_reads_allowed"] = True
        decision = evaluate_execution_manifest(invalid)
        self.assertFalse(decision.authorized)
        self.assertIn("transport_contract_not_frozen", decision.reasons)


if __name__ == "__main__":
    unittest.main()
