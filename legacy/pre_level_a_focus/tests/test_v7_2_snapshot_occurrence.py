from datetime import datetime, timezone
import unittest

from product_b_v7_2.snapshot_occurrence import (
    MAX_MATCHED_ROWS_PER_TAXON,
    SNAPSHOT_IDENTITY_FIELDS_UNAVAILABLE,
    SnapshotTaxonQuery,
    adapt_snapshot_host_rows,
    normalize_snapshot_occurrence_row,
    validate_snapshot_taxon_query,
)


def row(*, key="1", species_key="2775561", country="US", status="PRESENT"):
    return {
        "gbifid": key,
        "datasetkey": "dataset-1",
        "occurrenceid": "occ-" + key,
        "catalognumber": "cat-" + key,
        "recordedby": [{"array_element": "Alice Example"}, {"array_element": "Bob Example"}],
        "eventdate": datetime(2020, 6, 1, tzinfo=timezone.utc),
        "countrycode": country,
        "occurrencestatus": status,
        "decimallatitude": 30.0,
        "decimallongitude": -85.0,
        "coordinateuncertaintyinmeters": 100.0,
        "taxonkey": species_key,
        "specieskey": species_key,
        "scientificname": "Yucca filamentosa L.",
    }


class SnapshotQueryTests(unittest.TestCase):
    def test_frozen_query_uses_specieskey_not_taxonkey(self):
        query = SnapshotTaxonQuery(group_id="focal", species_keys=("2775561",))
        self.assertEqual(validate_snapshot_taxon_query(query), ())
        self.assertEqual(query.species_filter_field, "specieskey")
        mutated = SnapshotTaxonQuery(
            group_id="focal",
            species_keys=("2775561",),
            species_filter_field="taxonkey",
        )
        self.assertIn("query_species_filter_field_mismatch", validate_snapshot_taxon_query(mutated))

    def test_country_status_and_row_ceiling_are_frozen(self):
        self.assertIn(
            "query_country_code_mismatch",
            validate_snapshot_taxon_query(
                SnapshotTaxonQuery(group_id="x", species_keys=("1",), country_code="CA")
            ),
        )
        self.assertIn(
            "query_occurrence_status_mismatch",
            validate_snapshot_taxon_query(
                SnapshotTaxonQuery(group_id="x", species_keys=("1",), occurrence_status="ABSENT")
            ),
        )
        self.assertIn(
            "query_row_ceiling_mismatch",
            validate_snapshot_taxon_query(
                SnapshotTaxonQuery(
                    group_id="x",
                    species_keys=("1",),
                    max_rows_per_taxon=MAX_MATCHED_ROWS_PER_TAXON - 1,
                )
            ),
        )


class SnapshotAdapterTests(unittest.TestCase):
    def test_missing_live_identity_fields_are_not_synthesized(self):
        normalized = normalize_snapshot_occurrence_row(
            row(), expected_species_keys=("2775561",)
        )
        self.assertEqual(normalized["eventID"], "")
        self.assertEqual(normalized["otherCatalogNumbers"], [])
        self.assertEqual(normalized["recordedBy"], "Alice Example; Bob Example")
        self.assertTrue(str(normalized["eventDate"]).startswith("2020-06-01"))
        self.assertEqual(SNAPSHOT_IDENTITY_FIELDS_UNAVAILABLE, ("eventID", "otherCatalogNumbers"))

    def test_species_country_and_status_mismatch_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "specieskey filter"):
            normalize_snapshot_occurrence_row(row(species_key="999"), expected_species_keys=("2775561",))
        with self.assertRaisesRegex(ValueError, "country filter"):
            normalize_snapshot_occurrence_row(row(country="CA"), expected_species_keys=("2775561",))
        with self.assertRaisesRegex(ValueError, "PRESENT filter"):
            normalize_snapshot_occurrence_row(row(status="ABSENT"), expected_species_keys=("2775561",))

    def test_snapshot_rows_feed_existing_quality_and_projection_adapter(self):
        adapted = adapt_snapshot_host_rows((row(),), expected_species_key="2775561")
        self.assertEqual(adapted.audit.raw_rows, 1)
        self.assertEqual(adapted.audit.normalized_rows, 1)
        self.assertEqual(adapted.batch.raw_records_x, 1)
        record = adapted.batch.records[0]
        self.assertIsNotNone(record.projected_easting_m)
        self.assertIsNotNone(record.projected_northing_m)
        self.assertEqual(record.event_id, "")

    def test_duplicate_gbifid_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "gbifid values must be unique"):
            adapt_snapshot_host_rows((row(key="1"), row(key="1")), expected_species_key="2775561")


if __name__ == "__main__":
    unittest.main()
