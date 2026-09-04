import copy
import json
from pathlib import Path
import unittest

from product_b_v5.occurrence_source import LogicalOccurrenceQuery
from product_b_v7.gbif_search import serialize_v7_gbif_search_request
from product_b_v7.kim001_execution import (
    EXPECTED_CONTROLS,
    KIM001ExecutionNotAuthorized,
    evaluate_kim001_execution_manifest,
    execute_kim001_sampling_preflight,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config/product_b_v7_kim001_execution_manifest_v0_1.json"
FROZEN_HEAD = "c38aea5af607213b4b3038dc94df52c1410ab79b"


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
                "decimalLatitude": 25.0 + (i % 3) * 0.25,
                "decimalLongitude": 75.0 + i * 0.20,
                "coordinateUncertaintyInMeters": 100.0,
                "occurrenceStatus": "PRESENT",
                "countryCode": "CN",
            }
        )
    return rows


class KIM001ExecutionTests(unittest.TestCase):
    def test_committed_manifest_is_frozen_and_in_one_valid_execution_state(self):
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue(payload["contract_frozen"])
        self.assertEqual(payload["pre_execution_package_commit"], FROZEN_HEAD)
        self.assertFalse(payload["model_fit_reads_allowed"])
        self.assertFalse(payload["invariant_reads_allowed"])
        self.assertFalse(payload["process_knockout_reads_allowed"])
        state = (
            bool(payload["execution_authorized"]),
            bool(payload["occurrence_reads_allowed"]),
            bool(payload["execution_consumed"]),
        )
        self.assertIn(
            state,
            {
                (False, False, False),  # frozen but not yet authorized
                (True, True, False),    # one-shot authorized, not yet consumed
                (False, False, True),   # terminalized/consumed
            },
        )

    def test_synthetic_authorized_copy_passes_guard(self):
        decision = evaluate_kim001_execution_manifest(authorized_manifest())
        self.assertTrue(decision.authorized, decision.reasons)

    def test_country_serializer_has_no_geometry_and_is_frozen_to_cn(self):
        query = LogicalOccurrenceQuery(
            pair_id="KIM001",
            partner="x",
            taxon_key="5382668",
            checklist_key="d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
            geographic_filter_type="country_code_iso2",
            geographic_filter_value="CN",
        )
        request = serialize_v7_gbif_search_request(query)
        params = request.as_mapping()
        self.assertEqual(params["country"], "CN")
        self.assertNotIn("geometry", params)
        self.assertEqual(params["hasCoordinate"], "true")
        self.assertEqual(params["occurrenceStatus"], "PRESENT")
        bad = copy.copy(query)
        object.__setattr__(bad, "geographic_filter_value", "US")
        with self.assertRaisesRegex(ValueError, "must remain CN"):
            serialize_v7_gbif_search_request(bad)

    def test_committed_manifest_blocks_transport_unless_authorized(self):
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        state = (
            bool(payload["execution_authorized"]),
            bool(payload["occurrence_reads_allowed"]),
            bool(payload["execution_consumed"]),
        )
        if state == (True, True, False):
            self.skipTest("committed manifest is intentionally in the one-shot authorized state")
        calls = []
        def transport(query):
            calls.append(query)
            raise AssertionError("transport must not be called")
        with self.assertRaises(KIM001ExecutionNotAuthorized):
            execute_kim001_sampling_preflight(manifest=payload, transport=transport)
        self.assertEqual(calls, [])

    def test_focal_failure_never_opens_controls(self):
        calls = []
        def transport(query):
            calls.append(query.pair_id)
            if query.pair_id != "KIM001":
                raise AssertionError("control occurrence must stay closed after focal failure")
            return occurrence_rows(5, prefix="focal")
        result = execute_kim001_sampling_preflight(
            manifest=authorized_manifest(), transport=transport
        )
        self.assertEqual(result.terminal_state, "unresolved_host_sampling")
        self.assertFalse(result.controls_opened)
        self.assertEqual(calls, ["KIM001"])

    def test_focal_pass_opens_exact_frozen_control_pool(self):
        calls = []
        def transport(query):
            calls.append(query.pair_id)
            return occurrence_rows(60, prefix=query.pair_id)
        result = execute_kim001_sampling_preflight(
            manifest=authorized_manifest(), transport=transport
        )
        expected = ["KIM001"] + [f"KIM001_{control_id}" for control_id, _, _ in EXPECTED_CONTROLS]
        self.assertEqual(calls, expected)
        self.assertTrue(result.focal.sampling_adequate)
        self.assertTrue(result.controls_opened)
        self.assertEqual(result.adequate_control_host_count, 8)
        self.assertEqual(result.terminal_state, "sampling_preflight_passed")

    def test_returned_country_mismatch_fails(self):
        def transport(query):
            rows = occurrence_rows(60, prefix=query.pair_id)
            rows[0]["countryCode"] = "US"
            return rows
        with self.assertRaisesRegex(ValueError, "country filter"):
            execute_kim001_sampling_preflight(
                manifest=authorized_manifest(), transport=transport
            )


if __name__ == "__main__":
    unittest.main()
