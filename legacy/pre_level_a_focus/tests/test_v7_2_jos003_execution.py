import json
from pathlib import Path
import unittest

from product_b_v7_2.jos003_execution import (
    EXPECTED_CONTROLS,
    JOS003ExecutionNotAuthorized,
    evaluate_jos003_execution_manifest,
    execute_jos003_snapshot_sampling_preflight,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config/product_b_v7_2_jos003_execution_manifest_v0_1.json"
FROZEN_HEAD = "bf50327db91500943399d47952ada8fb18122682"


def authorized_manifest():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload.update(
        execution_authorized=True,
        snapshot_occurrence_rows_allowed=True,
        execution_consumed=False,
    )
    return payload


def snapshot_rows(n, *, species_key, prefix="r"):
    rows = []
    for i in range(n):
        rows.append(
            {
                "gbifid": f"{prefix}-{i}",
                "datasetkey": f"dataset-{prefix}-{i}",
                "occurrenceid": f"occ-{prefix}-{i}",
                "catalognumber": f"cat-{prefix}-{i}",
                "recordedby": [{"array_element": f"Recorder {prefix} {i}"}],
                "eventdate": "2020-06-01T00:00:00+00:00",
                "countrycode": "US",
                "occurrencestatus": "PRESENT",
                "decimallatitude": 25.0 + (i % 12) * 0.35,
                "decimallongitude": -110.0 + i * 0.21,
                "coordinateuncertaintyinmeters": 100.0,
                "taxonkey": species_key,
                "specieskey": species_key,
                "scientificname": "synthetic taxon",
            }
        )
    return rows


class JOS003ExecutionTests(unittest.TestCase):
    def test_committed_manifest_is_frozen_and_in_legal_execution_state(self):
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue(payload["contract_frozen"])
        self.assertEqual(payload["pre_execution_package_commit"], FROZEN_HEAD)
        state = (
            payload["execution_authorized"],
            payload["snapshot_occurrence_rows_allowed"],
            payload["execution_consumed"],
        )
        self.assertIn(
            state,
            {
                (False, False, False),
                (True, True, False),
                (False, False, True),
            },
        )
        if state == (True, True, False):
            decision = evaluate_jos003_execution_manifest(payload)
            self.assertTrue(decision.authorized, decision.reasons)
        else:
            calls = []

            def transport(query):
                calls.append(query.group_id)
                raise AssertionError("transport must remain fail-closed")

            with self.assertRaises(JOS003ExecutionNotAuthorized):
                execute_jos003_snapshot_sampling_preflight(manifest=payload, transport=transport)
            self.assertEqual(calls, [])

    def test_synthetic_frozen_authorized_copy_passes_guard(self):
        decision = evaluate_jos003_execution_manifest(authorized_manifest())
        self.assertTrue(decision.authorized, decision.reasons)

    def test_consumed_copy_is_fail_closed_even_if_reopened(self):
        payload = authorized_manifest()
        payload["execution_consumed"] = True
        decision = evaluate_jos003_execution_manifest(payload)
        self.assertFalse(decision.authorized)
        self.assertIn("execution_already_consumed", decision.reasons)

    def test_model_invariant_and_knockout_layers_remain_closed(self):
        payload = authorized_manifest()
        self.assertFalse(payload["model_fit_reads_allowed"])
        self.assertFalse(payload["invariant_reads_allowed"])
        self.assertFalse(payload["process_knockout_reads_allowed"])

    def test_focal_sampling_failure_never_opens_controls(self):
        calls = []

        def transport(query):
            calls.append((query.group_id, query.species_keys))
            if query.group_id != "JOS003_focal":
                raise AssertionError("control rows must remain unopened")
            return {"2775561": snapshot_rows(5, species_key="2775561", prefix="focal")}

        result = execute_jos003_snapshot_sampling_preflight(
            manifest=authorized_manifest(), transport=transport
        )
        self.assertEqual(result.terminal_state, "unresolved_host_sampling")
        self.assertFalse(result.controls_opened)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "JOS003_focal")

    def test_focal_pass_opens_one_batched_frozen_control_query(self):
        calls = []

        def transport(query):
            calls.append((query.group_id, query.species_keys))
            if query.group_id == "JOS003_focal":
                return {"2775561": snapshot_rows(80, species_key="2775561", prefix="focal")}
            return {
                key: snapshot_rows(80, species_key=key, prefix=key)
                for key in query.species_keys
            }

        result = execute_jos003_snapshot_sampling_preflight(
            manifest=authorized_manifest(), transport=transport
        )
        self.assertEqual([item[0] for item in calls], ["JOS003_focal", "JOS003_controls"])
        self.assertEqual(calls[1][1], tuple(item[2] for item in EXPECTED_CONTROLS))
        self.assertTrue(result.focal.sampling_adequate)
        self.assertTrue(result.controls_opened)
        self.assertEqual(result.adequate_control_host_count, 8)
        self.assertEqual(result.terminal_state, "engineering_snapshot_sampling_preflight_passed")

    def test_transport_cannot_return_undeclared_species_key(self):
        def transport(query):
            return {
                "2775561": snapshot_rows(80, species_key="2775561", prefix="focal"),
                "9999999": [],
            }

        with self.assertRaisesRegex(ValueError, "undeclared species keys"):
            execute_jos003_snapshot_sampling_preflight(
                manifest=authorized_manifest(), transport=transport
            )

    def test_snapshot_row_country_mismatch_fails_closed(self):
        def transport(query):
            rows = snapshot_rows(80, species_key="2775561", prefix="focal")
            rows[0]["countrycode"] = "CA"
            return {"2775561": rows}

        with self.assertRaisesRegex(ValueError, "country filter"):
            execute_jos003_snapshot_sampling_preflight(
                manifest=authorized_manifest(), transport=transport
            )


if __name__ == "__main__":
    unittest.main()
