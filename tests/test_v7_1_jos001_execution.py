import json
from pathlib import Path
import unittest

from product_b_v5.occurrence_source import LogicalOccurrenceQuery
from product_b_v7_1.gbif_search import serialize_v7_1_gbif_search_request
from product_b_v7_1.jos001_execution import (
    EXPECTED_CONTROLS,
    JOS001ExecutionNotAuthorized,
    evaluate_jos001_execution_manifest,
    execute_jos001_sampling_preflight,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config/product_b_v7_1_jos001_execution_manifest_v0_1.json"
TERMINAL = ROOT / "results/product_b_v7_1_jos001_engineering_terminal_v0_1.json"
FROZEN_HEAD = "c699a4672eb3b84fb17b00547f966fac05b86908"


def authorized_manifest():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload.update(
        execution_authorized=True,
        occurrence_reads_allowed=True,
        execution_consumed=False,
    )
    return payload


def occurrence_rows(n, *, prefix="r"):
    rows = []
    for i in range(n):
        rows.append(
            {
                "key": f"{prefix}-{i}",
                "datasetKey": f"dataset-{prefix}-{i}",
                "occurrenceID": f"occ-{prefix}-{i}",
                "eventID": f"event-{prefix}-{i}",
                "catalogNumber": f"cat-{prefix}-{i}",
                "otherCatalogNumbers": [],
                "eventDate": "2020-06-01",
                "recordedBy": f"recorder-{prefix}-{i}",
                "decimalLatitude": 32.0 + (i % 4) * 0.6,
                "decimalLongitude": -119.0 + i * 0.22,
                "coordinateUncertaintyInMeters": 100.0,
                "occurrenceStatus": "PRESENT",
                "countryCode": "US",
            }
        )
    return rows


class JOS001ExecutionTests(unittest.TestCase):
    def test_committed_manifest_is_consumed_closed_and_engineering_only(self):
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue(payload["engineering_only"])
        self.assertFalse(payload["confirmatory_promotion_allowed"])
        self.assertTrue(payload["contract_frozen"])
        self.assertEqual(payload["pre_execution_package_commit"], FROZEN_HEAD)
        self.assertFalse(payload["model_fit_reads_allowed"])
        self.assertFalse(payload["invariant_reads_allowed"])
        self.assertFalse(payload["process_knockout_reads_allowed"])
        self.assertFalse(payload["execution_authorized"])
        self.assertFalse(payload["occurrence_reads_allowed"])
        self.assertTrue(payload["execution_consumed"])
        self.assertEqual(payload["execution_terminal_state"], "engineering_execution_unresolved")
        self.assertEqual(
            payload["execution_terminal_result"],
            "results/product_b_v7_1_jos001_engineering_terminal_v0_1.json",
        )

    def test_terminal_result_is_transport_unresolved_not_sampling_result(self):
        result = json.loads(TERMINAL.read_text(encoding="utf-8"))
        self.assertEqual(result["terminal_state"], "engineering_execution_unresolved")
        self.assertEqual(result["terminal_gate"], "occurrence_transport")
        self.assertTrue(result["occurrence_boundary_crossed"])
        self.assertFalse(result["focal_sampling_decision_available"])
        self.assertFalse(result["controls_opened"])
        self.assertFalse(result["model_fit_reads_opened"])
        self.assertFalse(result["invariant_reads_opened"])
        self.assertFalse(result["process_knockout_reads_opened"])
        self.assertTrue(result["rerun_forbidden"])
        self.assertEqual(result["github_actions_run_id"], 33867091389)
        self.assertEqual(result["artifact_id"], 9934927281)

    def test_synthetic_authorized_copy_passes_guard(self):
        decision = evaluate_jos001_execution_manifest(authorized_manifest())
        self.assertTrue(decision.authorized, decision.reasons)

    def test_country_serializer_is_US_without_geometry(self):
        query = LogicalOccurrenceQuery(
            pair_id="JOS001",
            partner="x",
            taxon_key="2775592",
            checklist_key="d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
            geographic_filter_type="country_code_iso2",
            geographic_filter_value="US",
        )
        params = serialize_v7_1_gbif_search_request(query).as_mapping()
        self.assertEqual(params["country"], "US")
        self.assertNotIn("geometry", params)
        self.assertEqual(params["hasCoordinate"], "true")
        self.assertEqual(params["occurrenceStatus"], "PRESENT")

    def test_closed_copy_blocks_transport_before_call(self):
        calls = []
        def transport(query):
            calls.append(query)
            raise AssertionError("transport must remain closed")
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        payload.update(
            execution_authorized=False,
            occurrence_reads_allowed=False,
            execution_consumed=False,
        )
        with self.assertRaises(JOS001ExecutionNotAuthorized):
            execute_jos001_sampling_preflight(manifest=payload, transport=transport)
        self.assertEqual(calls, [])

    def test_consumed_copy_is_fail_closed_even_if_flags_are_reopened(self):
        payload = authorized_manifest()
        payload["execution_consumed"] = True
        decision = evaluate_jos001_execution_manifest(payload)
        self.assertFalse(decision.authorized)
        self.assertIn("execution_already_consumed", decision.reasons)

    def test_focal_failure_never_opens_controls(self):
        calls = []
        def transport(query):
            calls.append(query.pair_id)
            if query.pair_id != "JOS001":
                raise AssertionError("controls must remain unopened")
            return occurrence_rows(5, prefix="focal")
        result = execute_jos001_sampling_preflight(
            manifest=authorized_manifest(), transport=transport
        )
        self.assertEqual(result.terminal_state, "unresolved_host_sampling")
        self.assertFalse(result.controls_opened)
        self.assertEqual(calls, ["JOS001"])

    def test_focal_pass_opens_only_the_seven_frozen_controls(self):
        calls = []
        def transport(query):
            calls.append(query.pair_id)
            return occurrence_rows(60, prefix=query.pair_id)
        result = execute_jos001_sampling_preflight(
            manifest=authorized_manifest(), transport=transport
        )
        expected = ["JOS001"] + [f"JOS001_{control_id}" for control_id, _, _ in EXPECTED_CONTROLS]
        self.assertEqual(calls, expected)
        self.assertTrue(result.focal.sampling_adequate)
        self.assertTrue(result.controls_opened)
        self.assertEqual(result.adequate_control_host_count, 7)
        self.assertEqual(result.terminal_state, "engineering_sampling_preflight_passed")

    def test_country_mismatch_fails_closed(self):
        def transport(query):
            rows = occurrence_rows(60, prefix=query.pair_id)
            rows[0]["countryCode"] = "CA"
            return rows
        with self.assertRaisesRegex(ValueError, "country filter"):
            execute_jos001_sampling_preflight(
                manifest=authorized_manifest(), transport=transport
            )


if __name__ == "__main__":
    unittest.main()
