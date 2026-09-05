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

    def _fresh_authorized_copy(self):
        manifest = dict(self.manifest)
        manifest["execution_consumed"] = False
        manifest["execution_authorized"] = True
        manifest["occurrence_reads_allowed"] = True
        return manifest

    def test_committed_manifest_is_frozen_consumed_and_closed(self):
        self.assertTrue(self.manifest["contract_frozen"])
        self.assertTrue(self.manifest["scope_gate_frozen"])
        self.assertTrue(self.manifest["preprocessing_contract_frozen"])
        self.assertTrue(self.manifest["transport_contract_frozen"])
        self.assertTrue(self.manifest["negative_control_contract_frozen"])
        self.assertTrue(self.manifest["execution_consumed"])
        self.assertFalse(self.manifest["execution_authorized"])
        self.assertFalse(self.manifest["occurrence_reads_allowed"])
        decision = evaluate_execution_manifest(self.manifest)
        self.assertFalse(decision.authorized)
        self.assertIn("execution_already_consumed", decision.reasons)
        self.assertIn("execution_not_authorized", decision.reasons)
        self.assertIn("occurrence_reads_not_allowed", decision.reasons)

    def test_fig_pair_remains_taxonomy_and_scope_eligible_but_execution_is_consumed(self):
        self.assertEqual(self.manifest["taxonomy_eligible_pair_ids"], ["OPM_FIG_001"])
        self.assertEqual(self.manifest["scope_eligible_pair_ids"], ["OPM_FIG_001"])
        with self.assertRaises(ExecutionNotAuthorized):
            require_execution_authorization(
                self.manifest, requested_pair_ids=["OPM_FIG_001"]
            )

    def test_synthetic_fresh_authorized_copy_can_pass_guard(self):
        fresh = self._fresh_authorized_copy()
        decision = require_execution_authorization(
            fresh, requested_pair_ids=["OPM_FIG_001"]
        )
        self.assertTrue(decision.authorized)
        self.assertEqual(decision.reasons, ())

    def test_setting_flags_true_cannot_bypass_consumed_state(self):
        invalid = dict(self.manifest)
        invalid["execution_authorized"] = True
        invalid["occurrence_reads_allowed"] = True
        decision = evaluate_execution_manifest(invalid)
        self.assertFalse(decision.authorized)
        self.assertIn("execution_already_consumed", decision.reasons)

    def test_fresh_authorized_manifest_rejects_pair_outside_frozen_set(self):
        fresh = self._fresh_authorized_copy()
        with self.assertRaises(ExecutionNotAuthorized):
            require_execution_authorization(
                fresh, requested_pair_ids=["OPM_YUC_002"]
            )

    def test_scope_pair_must_also_be_taxonomy_eligible(self):
        invalid = self._fresh_authorized_copy()
        invalid["scope_eligible_pair_ids"] = ["OPM_YUC_002"]
        decision = evaluate_execution_manifest(invalid)
        self.assertFalse(decision.authorized)
        self.assertIn("scope_pair_not_taxonomy_eligible", decision.reasons)

    def test_removing_scope_pair_fails_closed_even_if_freshly_authorized(self):
        invalid = self._fresh_authorized_copy()
        invalid["scope_eligible_pair_ids"] = []
        decision = evaluate_execution_manifest(invalid)
        self.assertFalse(decision.authorized)
        self.assertIn("no_scope_eligible_pairs", decision.reasons)

    def test_unfreezing_transport_contract_fails_closed(self):
        invalid = self._fresh_authorized_copy()
        invalid["transport_contract_frozen"] = False
        decision = evaluate_execution_manifest(invalid)
        self.assertFalse(decision.authorized)
        self.assertIn("transport_contract_not_frozen", decision.reasons)

    def test_unfreezing_negative_control_contract_fails_closed(self):
        invalid = self._fresh_authorized_copy()
        invalid["negative_control_contract_frozen"] = False
        decision = evaluate_execution_manifest(invalid)
        self.assertFalse(decision.authorized)
        self.assertIn("negative_control_contract_not_frozen", decision.reasons)


if __name__ == "__main__":
    unittest.main()
