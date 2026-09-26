import unittest

from product_b_v5.occurrence_adapter import adapt_gbif_pair_rows
from product_b_v5.occurrence_preprocessing import (
    build_occurrence_sampling_preflight,
    cross_partner_collision_components,
)
from product_b_v5.sampling import SamplingThresholds, SamplingState


SMALL = SamplingThresholds(
    minimum_independent_records=1,
    minimum_unique_cells=1,
    minimum_effective_cells=1.0,
    maximum_record_asymmetry_ratio=10.0,
    maximum_unique_cell_asymmetry_ratio=10.0,
    maximum_effective_cell_asymmetry_ratio=10.0,
)


def row(key, lon, lat, **overrides):
    values = {
        "key": key,
        "datasetKey": "dataset-a",
        "occurrenceID": f"occ-{key}",
        "eventID": "",
        "catalogNumber": "",
        "otherCatalogNumbers": [],
        "eventDate": "2020-01-02",
        "recordedBy": "Collector",
        "decimalLatitude": lat,
        "decimalLongitude": lon,
        "coordinateUncertaintyInMeters": None,
        "taxonKey": 1,
        "acceptedTaxonKey": 1,
        "scientificName": "Synthetic species",
        "basisOfRecord": "PRESERVED_SPECIMEN",
        "occurrenceStatus": "PRESENT",
    }
    values.update(overrides)
    return values


class GBIFOccurrenceAdapterTests(unittest.TestCase):
    def test_raw_coordinate_is_projected_by_frozen_epsg6933_formula(self):
        batch = adapt_gbif_pair_rows(
            x_rows=(row(1, 100.42, 13.83),),
            y_rows=(row(2, 101.27, 21.90),),
        )
        x = batch.records[0]
        self.assertAlmostEqual(x.projected_easting_m, 9_689_152.262795, places=6)
        self.assertAlmostEqual(x.projected_northing_m, 1_747_701.298764, places=6)
        self.assertEqual(batch.raw_records_x, 1)
        self.assertEqual(batch.raw_records_y, 1)

    def test_other_catalog_number_alias_links_cross_partner_records(self):
        x = row(10, 100.0, 20.0, catalogNumber="SPEC-77", occurrenceID="X-OCC")
        y = row(
            11,
            101.0,
            21.0,
            occurrenceID="Y-OCC",
            otherCatalogNumbers=["OLD-2", "SPEC-77"],
        )
        batch = adapt_gbif_pair_rows(x_rows=(x,), y_rows=(y,))
        self.assertEqual(len(batch.identity_components), 1)
        component = batch.identity_components[0]
        self.assertEqual(component.row_ids, ("10", "11"))
        self.assertEqual(component.partners, ("x", "y"))
        self.assertIn("catalog_or_specimen_number", component.witness_types)

        downstream = cross_partner_collision_components(batch.records)
        self.assertEqual(len(downstream), 1)
        self.assertEqual(downstream[0].row_ids, ("10", "11"))

    def test_alias_chain_preserves_transitive_closure_without_inflating_rows(self):
        x1 = row(20, 100.0, 20.0, eventID="EVENT-A", occurrenceID="X1")
        y1 = row(
            21,
            101.0,
            21.0,
            eventID="EVENT-A",
            catalogNumber="SPEC-B",
            occurrenceID="Y1",
        )
        x2 = row(
            22,
            102.0,
            22.0,
            occurrenceID="X2",
            otherCatalogNumbers="SPEC-B;OLD-X2",
        )
        batch = adapt_gbif_pair_rows(x_rows=(x1, x2), y_rows=(y1,))
        self.assertEqual(len(batch.records), 3)
        self.assertEqual(len(batch.identity_components), 1)
        self.assertEqual(batch.identity_components[0].row_ids, ("20", "21", "22"))
        downstream = cross_partner_collision_components(batch.records)
        self.assertEqual(len(downstream), 1)
        self.assertEqual(downstream[0].row_ids, ("20", "21", "22"))

    def test_cross_partner_alias_collision_is_excluded_before_sampling_counts(self):
        x = row(30, 100.0, 20.0, catalogNumber="SAME")
        y = row(31, 101.0, 21.0, otherCatalogNumbers=["SAME"])
        batch = adapt_gbif_pair_rows(x_rows=(x,), y_rows=(y,))
        result = build_occurrence_sampling_preflight(
            batch.records,
            taxonomy_eligible=True,
            thresholds=SMALL,
        )
        self.assertEqual(result.audit.collision_excluded_x, 1)
        self.assertEqual(result.audit.collision_excluded_y, 1)
        self.assertEqual(result.sampling_result.state, SamplingState.UNRESOLVED)

    def test_malformed_uncertainty_reaches_frozen_quality_exclusion(self):
        batch = adapt_gbif_pair_rows(
            x_rows=(row(40, 100.0, 20.0, coordinateUncertaintyInMeters="bad"),),
            y_rows=(row(41, 101.0, 21.0),),
        )
        result = build_occurrence_sampling_preflight(
            batch.records,
            taxonomy_eligible=True,
            thresholds=SMALL,
        )
        self.assertEqual(result.audit.quality_excluded_x, 1)
        self.assertIn(
            ("invalid_coordinate_uncertainty", 1),
            result.audit.quality_exclusion_reason_counts,
        )

    def test_duplicate_gbif_key_across_partner_batch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            adapt_gbif_pair_rows(
                x_rows=(row(50, 100.0, 20.0),),
                y_rows=(row(50, 101.0, 21.0),),
            )


if __name__ == "__main__":
    unittest.main()
