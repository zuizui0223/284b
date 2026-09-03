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
        self.assertFalse(self.manifest["execution_authorized"])
        self.assertFalse(self.manifest["occurrence_reads_allowed"])
        decision = evaluate_execution_manifest(self.manifest)
        self.assertFalse(decision.authorized)
        self.assertIn("execution_not_authorized", decision.reasons)
        self.assertIn("occurrence_reads_not_allowed", decision.reasons)

    def test_only_taxonomy_eligible_pair_is_in_frozen_execution_set(self):
        self.assertEqual(self.manifest["eligible_pair_ids"], ["OPM_FIG_001"])

    def test_current_manifest_raises_before_occurrence_access(self):
        with self.assertRaises(ExecutionNotAuthorized):
            require_execution_authorization(
                self.manifest, requested_pair_ids=["OPM_FIG_001"]
            )

    def test_even_authorized_manifest_rejects_pair_outside_frozen_set(self):
        authorized = dict(self.manifest)
        authorized["execution_authorized"] = True
        authorized["occurrence_reads_allowed"] = True

        with self.assertRaises(ExecutionNotAuthorized):
            require_execution_authorization(
                authorized, requested_pair_ids=["OPM_YUC_002"]
            )

    def test_authorized_copy_accepts_only_frozen_pair(self):
        authorized = dict(self.manifest)
        authorized["execution_authorized"] = True
        authorized["occurrence_reads_allowed"] = True
        decision = require_execution_authorization(
            authorized, requested_pair_ids=["OPM_FIG_001"]
        )
        self.assertTrue(decision.authorized)


if __name__ == "__main__":
    unittest.main()
