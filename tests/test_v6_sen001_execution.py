import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from product_b_v6.execution import (
    EXPECTED_CONTROL_HOSTS,
    V6ExecutionNotAuthorized,
    evaluate_sen001_execution_manifest,
    execute_sen001_sampling_preflight,
    host_sampling_adequate,
    require_sen001_execution_authorization,
)
from product_b_v6.witness import HostSamplingSummary


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "config/product_b_v6_sen001_execution_manifest_v0_1.json"
SCOPE_PATH = ROOT / "config/product_b_v6_scope_resolution_sen001_v0_1.json"


def authorized_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["pre_execution_package_commit"] = "a" * 40
    manifest["execution_authorized"] = True
    manifest["occurrence_reads_allowed"] = True
    manifest["execution_consumed"] = False
    manifest["invariant_reads_allowed"] = False
    return manifest


class Sen001AuthorizationTests(unittest.TestCase):
    def test_manifest_structure_and_closed_invariant_layer(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertFalse(manifest["invariant_reads_allowed"])
        controls = tuple(
            (row["control_taxon_id"], row["scientific_name"], str(row["taxon_key"]))
            for row in manifest["control_hosts"]
        )
        self.assertEqual(controls, EXPECTED_CONTROL_HOSTS)

    def test_synthetic_authorized_copy_passes(self):
        decision = evaluate_sen001_execution_manifest(authorized_manifest())
        self.assertTrue(decision.authorized, decision.reasons)

    def test_consumed_copy_is_fail_closed(self):
        manifest = authorized_manifest()
        manifest["execution_consumed"] = True
        with self.assertRaises(V6ExecutionNotAuthorized):
            require_sen001_execution_authorization(manifest)

    def test_host_sampling_floor(self):
        self.assertTrue(host_sampling_adequate(HostSamplingSummary(50, 30, 10.0)))
        self.assertFalse(host_sampling_adequate(HostSamplingSummary(49, 30, 10.0)))
        self.assertFalse(host_sampling_adequate(HostSamplingSummary(50, 29, 10.0)))
        self.assertFalse(host_sampling_adequate(HostSamplingSummary(50, 30, 9.99)))


class Sen001ExecutionOrderingTests(unittest.TestCase):
    def setUp(self):
        self.manifest = authorized_manifest()
        self.scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))

    def test_focal_failure_never_opens_controls(self):
        calls = []

        def transport(query):
            calls.append((query.pair_id, query.partner, query.taxon_key))
            return ()

        focal = SimpleNamespace(
            preflight=SimpleNamespace(passed=False, reasons=("witness_independent_record_floor_failed",))
        )
        with patch(
            "product_b_v6.execution.adapt_and_build_directed_witness_sampling_preflight",
            return_value=(None, focal),
        ):
            result = execute_sen001_sampling_preflight(
                manifest=self.manifest,
                scope=self.scope,
                transport=transport,
            )

        self.assertEqual(len(calls), 2)
        self.assertFalse(result.controls_opened)
        self.assertEqual(result.terminal_state, "unresolved_witness_sampling")

    def test_focal_pass_opens_exact_frozen_control_pool(self):
        calls = []

        def transport(query):
            calls.append((query.pair_id, query.partner, query.taxon_key))
            return ()

        focal = SimpleNamespace(preflight=SimpleNamespace(passed=True, reasons=()))
        control_preflights = []
        for index in range(6):
            adequate = index < 5
            control_preflights.append(
                SimpleNamespace(
                    host_summary=HostSamplingSummary(
                        independent_records=50 if adequate else 49,
                        unique_cells=30,
                        effective_cells=10.0,
                    ),
                    audit=SimpleNamespace(
                        raw_records_x=50 if adequate else 49,
                        retained_records_x=50 if adequate else 49,
                        quality_excluded_x=0,
                    ),
                )
            )

        side_effects = [(None, focal)] + [(None, item) for item in control_preflights]
        with patch(
            "product_b_v6.execution.adapt_and_build_directed_witness_sampling_preflight",
            side_effect=side_effects,
        ):
            result = execute_sen001_sampling_preflight(
                manifest=self.manifest,
                scope=self.scope,
                transport=transport,
            )

        self.assertEqual(len(calls), 8)
        observed_control_keys = tuple(call[2] for call in calls[2:])
        self.assertEqual(observed_control_keys, tuple(row[2] for row in EXPECTED_CONTROL_HOSTS))
        self.assertTrue(result.controls_opened)
        self.assertEqual(result.adequate_control_host_count, 5)
        self.assertEqual(result.terminal_state, "sampling_preflight_passed")


if __name__ == "__main__":
    unittest.main()
