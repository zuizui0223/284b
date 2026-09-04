import hashlib
import json
from pathlib import Path
import unittest

from product_b_v7_2.snapshot_transport import (
    REQUIRED_SNAPSHOT_FIELDS,
    SnapshotObject,
    build_metadata_audit,
    canonicalize_object_manifest,
    evaluate_snapshot_contract,
    extract_citation_doi,
    object_manifest_sha256,
    validate_completed_metadata_audit,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_v7_2_snapshot_transport_contract_v0_1.json"


def objects():
    return (
        SnapshotObject(
            key="occurrence/2026-08-01/citation.txt",
            size=123,
            etag='"citation-etag"',
            last_modified="2026-08-02T00:00:00.000Z",
        ),
        SnapshotObject(
            key="occurrence/2026-08-01/occurrence.parquet/000001",
            size=1000,
            etag='"etag-1"',
            last_modified="2026-08-02T00:01:00.000Z",
        ),
        SnapshotObject(
            key="occurrence/2026-08-01/occurrence.parquet/000000",
            size=900,
            etag='"etag-0"',
            last_modified="2026-08-02T00:00:30.000Z",
        ),
    )


class SnapshotContractTests(unittest.TestCase):
    def test_committed_contract_is_pre_pair_closed_and_preserves_floors(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        decision = evaluate_snapshot_contract(contract)
        self.assertTrue(decision.passed, decision.reasons)
        self.assertFalse(contract["occurrence_row_reads_allowed"])
        self.assertFalse(contract["new_pair_selection_allowed"])
        self.assertTrue(contract["live_occurrence_search_forbidden"])
        self.assertEqual(
            contract["future_pair_sampling_floor"],
            {
                "minimum_independent_records": 50,
                "minimum_unique_10km_cells": 30,
                "minimum_effective_10km_cells": 10.0,
            },
        )
        self.assertEqual(
            tuple(contract["required_snapshot_fields_before_occurrence_execution"]),
            REQUIRED_SNAPSHOT_FIELDS,
        )
        self.assertIn("JOS001", contract["firewalled_consumed_pairs"])

    def test_live_search_or_open_rows_fail_contract(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        contract["live_occurrence_search_forbidden"] = False
        contract["occurrence_row_reads_allowed"] = True
        decision = evaluate_snapshot_contract(contract)
        self.assertFalse(decision.passed)
        self.assertIn("live_search_not_forbidden", decision.reasons)
        self.assertIn("occurrence_rows_must_remain_closed", decision.reasons)

    def test_snapshot_date_or_bucket_cannot_drift(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        contract["snapshot"]["snapshot_date"] = "2026-09-01"
        contract["snapshot"]["bucket"] = "some-other-bucket"
        decision = evaluate_snapshot_contract(contract)
        self.assertFalse(decision.passed)
        self.assertIn("snapshot_date_mismatch", decision.reasons)
        self.assertIn("snapshot_bucket_mismatch", decision.reasons)

    def test_required_snapshot_schema_cannot_be_weakened(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        contract["required_snapshot_fields_before_occurrence_execution"].remove("coordinateuncertaintyinmeters")
        decision = evaluate_snapshot_contract(contract)
        self.assertFalse(decision.passed)
        self.assertIn("required_snapshot_schema_changed", decision.reasons)


class SnapshotMetadataTests(unittest.TestCase):
    def test_object_manifest_digest_is_order_invariant_and_content_sensitive(self):
        forward = object_manifest_sha256(objects())
        reversed_digest = object_manifest_sha256(tuple(reversed(objects())))
        self.assertEqual(forward, reversed_digest)
        changed = list(objects())
        changed[1] = SnapshotObject(
            key=changed[1].key,
            size=changed[1].size + 1,
            etag=changed[1].etag,
            last_modified=changed[1].last_modified,
        )
        self.assertNotEqual(forward, object_manifest_sha256(tuple(changed)))

    def test_canonical_manifest_is_sorted_and_newline_terminated(self):
        payload = canonicalize_object_manifest(tuple(reversed(objects())))
        self.assertTrue(payload.endswith(b"\n"))
        rows = json.loads(payload.decode("utf-8"))
        self.assertEqual([row["key"] for row in rows], sorted(row["key"] for row in rows))

    def test_outside_snapshot_object_fails_closed(self):
        invalid = objects() + (
            SnapshotObject(
                key="occurrence/2026-07-01/occurrence.parquet/000000",
                size=1,
                etag='"bad"',
                last_modified="2026-07-02T00:00:00Z",
            ),
        )
        with self.assertRaisesRegex(ValueError, "outside frozen date prefix"):
            object_manifest_sha256(invalid)

    def test_metadata_audit_requires_parquet_and_citation_and_extracts_doi(self):
        citation = b"Please cite https://doi.org/10.15468/dl.AbC123 for this snapshot.\n"
        audit = build_metadata_audit(objects=objects(), citation_bytes=citation)
        self.assertEqual(audit.snapshot_date, "2026-08-01")
        self.assertEqual(audit.object_count, 3)
        self.assertEqual(audit.parquet_object_count, 2)
        self.assertEqual(audit.total_object_bytes, 2023)
        self.assertEqual(audit.citation_doi, "10.15468/dl.abc123")
        self.assertEqual(audit.citation_sha256, hashlib.sha256(citation).hexdigest())
        self.assertEqual(validate_completed_metadata_audit(audit.__dict__), ())

    def test_doi_is_mandatory(self):
        with self.assertRaisesRegex(ValueError, "does not contain"):
            extract_citation_doi("GBIF occurrence snapshot without DOI")

    def test_pair_selection_cannot_be_opened_by_invalid_audit(self):
        invalid = {
            "snapshot_date": "2026-08-01",
            "object_manifest_sha256": "x",
            "object_count": 0,
            "total_object_bytes": 0,
            "citation_sha256": "y",
            "citation_doi": "",
            "parquet_object_count": 0,
        }
        reasons = validate_completed_metadata_audit(invalid)
        self.assertTrue(reasons)
        self.assertIn("audit_has_no_parquet_objects", reasons)


if __name__ == "__main__":
    unittest.main()
