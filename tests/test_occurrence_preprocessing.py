import unittest

from product_b_v5.occurrence_preprocessing import (
    OccurrenceRecord,
    build_occurrence_sampling_preflight,
    canonical_coordinate_key,
    canonical_event_day,
    cross_partner_collision_components,
    occurrence_quality_reasons,
    sampling_cell_id,
)
from product_b_v5.sampling import SamplingState, SamplingThresholds


SMALL_THRESHOLDS = SamplingThresholds(
    minimum_independent_records=3,
    minimum_unique_cells=3,
    minimum_effective_cells=2.0,
    maximum_record_asymmetry_ratio=2.0,
    maximum_unique_cell_asymmetry_ratio=2.0,
    maximum_effective_cell_asymmetry_ratio=2.0,
)


def make_record(row_id, partner, east, north=0.0, **overrides):
    values = dict(
        row_id=row_id,
        partner=partner,
        decimal_latitude=10.0 + east / 1_000_000.0,
        decimal_longitude=120.0,
        projected_easting_m=float(east),
        projected_northing_m=float(north),
        occurrence_id_lineage="",
        event_id="",
        catalog_or_specimen_number="",
        dataset_key="",
        event_date="",
        recorder="",
        coordinate_uncertainty_m=None,
    )
    values.update(overrides)
    return OccurrenceRecord(**values)


class NormalizationTests(unittest.TestCase):
    def test_event_day_uses_only_valid_full_date_prefix(self):
        self.assertEqual(canonical_event_day("2026-09-03T12:30:00"), "2026-09-03")
        self.assertEqual(canonical_event_day("2026-02-30"), "")
        self.assertEqual(canonical_event_day("2026-09"), "")

    def test_coordinate_key_is_fixed_to_five_decimals(self):
        self.assertEqual(
            canonical_coordinate_key(10.123456, 120.987654),
            "10.12346,120.98765",
        )
        self.assertEqual(canonical_coordinate_key(-0.0, 0.0), "0.00000,0.00000")

    def test_equal_area_cell_index_uses_floor_for_negative_coordinates(self):
        self.assertEqual(sampling_cell_id(9_999.0, 0.0), (0, 0))
        self.assertEqual(sampling_cell_id(10_000.0, 0.0), (1, 0))
        self.assertEqual(sampling_cell_id(-1.0, -10_001.0), (-1, -2))


class CollisionGraphTests(unittest.TestCase):
    def test_direct_shared_event_excludes_cross_partner_component(self):
        records = (
            make_record("x1", "x", 0, event_id="EVENT-1"),
            make_record("y1", "y", 10_000, event_id="EVENT-1"),
            make_record("x2", "x", 20_000, event_id="OTHER"),
        )
        components = cross_partner_collision_components(records)
        self.assertEqual(len(components), 1)
        self.assertEqual(components[0].row_ids, ("x1", "y1"))
        self.assertEqual(components[0].witness_types, ("event_id",))

    def test_transitive_closure_excludes_entire_mixed_component(self):
        records = (
            make_record("x1", "x", 0, event_id="EVENT-1"),
            make_record(
                "y1",
                "y",
                10_000,
                event_id="EVENT-1",
                catalog_or_specimen_number="SPEC-9",
            ),
            make_record(
                "x2",
                "x",
                20_000,
                catalog_or_specimen_number="SPEC-9",
            ),
        )
        components = cross_partner_collision_components(records)
        self.assertEqual(len(components), 1)
        self.assertEqual(components[0].row_ids, ("x1", "x2", "y1"))
        self.assertEqual(
            components[0].witness_types,
            ("catalog_or_specimen_number", "event_id"),
        )

    def test_single_partner_identity_group_is_not_a_cross_partner_collision(self):
        records = (
            make_record("x1", "x", 0, event_id="EVENT-X"),
            make_record("x2", "x", 10_000, event_id="EVENT-X"),
            make_record("y1", "y", 20_000, event_id="EVENT-Y"),
        )
        self.assertEqual(cross_partner_collision_components(records), ())

    def test_dataset_day_coordinate_witness_uses_frozen_normalization(self):
        records = (
            make_record(
                "x1",
                "x",
                0,
                decimal_latitude=10.1234561,
                decimal_longitude=120.0,
                dataset_key="DATASET",
                event_date="2026-09-03T01:00:00",
            ),
            make_record(
                "y1",
                "y",
                10_000,
                decimal_latitude=10.1234564,
                decimal_longitude=120.0,
                dataset_key="DATASET",
                event_date="2026-09-03",
            ),
        )
        components = cross_partner_collision_components(records)
        self.assertEqual(len(components), 1)
        self.assertIn(
            "dataset_key_plus_event_day_plus_coordinate_key",
            components[0].witness_types,
        )

    def test_recorder_normalization_is_case_and_spacing_insensitive(self):
        records = (
            make_record(
                "x1",
                "x",
                0,
                recorder="Rachel  Zhang",
                event_date="2026-09-03",
                decimal_latitude=10.0,
                decimal_longitude=120.0,
            ),
            make_record(
                "y1",
                "y",
                10_000,
                recorder="  RACHEL ZHANG ",
                event_date="2026-09-03T20:00:00",
                decimal_latitude=10.0,
                decimal_longitude=120.0,
            ),
        )
        components = cross_partner_collision_components(records)
        self.assertEqual(len(components), 1)
        self.assertIn(
            "recorder_plus_event_day_plus_coordinate_key",
            components[0].witness_types,
        )


class CoordinateQualityTests(unittest.TestCase):
    def test_known_uncertainty_above_cell_edge_is_excluded(self):
        record = make_record("x1", "x", 0, coordinate_uncertainty_m=10_001.0)
        self.assertIn(
            "coordinate_uncertainty_ceiling_failed",
            occurrence_quality_reasons(record),
        )

    def test_missing_uncertainty_is_not_an_exclusion_reason(self):
        record = make_record("x1", "x", 0, coordinate_uncertainty_m=None)
        self.assertEqual(occurrence_quality_reasons(record), ())

    def test_invalid_wgs84_coordinate_is_excluded_even_if_projection_present(self):
        record = make_record("x1", "x", 0, decimal_latitude=95.0)
        self.assertIn(
            "decimal_coordinate_out_of_range",
            occurrence_quality_reasons(record),
        )


class EndToEndPurePreflightTests(unittest.TestCase):
    def _balanced_records(self):
        return (
            make_record("x1", "x", 1_000),
            make_record("x2", "x", 11_000),
            make_record("x3", "x", 21_000),
            make_record("y1", "y", 31_000),
            make_record("y2", "y", 41_000),
            make_record("y3", "y", 51_000),
        )

    def test_balanced_synthetic_pair_passes_small_frozen_gate(self):
        result = build_occurrence_sampling_preflight(
            self._balanced_records(),
            taxonomy_eligible=True,
            thresholds=SMALL_THRESHOLDS,
        )
        self.assertEqual(result.sampling_result.state, SamplingState.PASSED)
        self.assertEqual(result.audit.retained_records_x, 3)
        self.assertEqual(result.audit.retained_records_y, 3)
        self.assertEqual(result.audit.unique_cells_x, 3)
        self.assertEqual(result.audit.unique_cells_y, 3)
        self.assertEqual(result.audit.missing_uncertainty_x, 3)
        self.assertEqual(result.audit.missing_uncertainty_y, 3)

    def test_taxonomy_failure_cannot_be_rescued_by_good_sampling(self):
        result = build_occurrence_sampling_preflight(
            self._balanced_records(),
            taxonomy_eligible=False,
            thresholds=SMALL_THRESHOLDS,
        )
        self.assertEqual(result.sampling_result.state, SamplingState.UNRESOLVED)
        self.assertIn("taxonomy_gate_not_passed", result.sampling_result.reasons)

    def test_collision_exclusion_can_drive_pair_below_floor(self):
        records = list(self._balanced_records())
        records[0] = make_record("x1", "x", 1_000, event_id="SHARED")
        records[3] = make_record("y1", "y", 31_000, event_id="SHARED")
        result = build_occurrence_sampling_preflight(
            tuple(records),
            taxonomy_eligible=True,
            thresholds=SMALL_THRESHOLDS,
        )
        self.assertEqual(result.audit.collision_excluded_x, 1)
        self.assertEqual(result.audit.collision_excluded_y, 1)
        self.assertEqual(result.sampling_result.state, SamplingState.UNRESOLVED)
        self.assertIn(
            "x_independent_record_floor_failed",
            result.sampling_result.reasons,
        )
        self.assertIn(
            "y_independent_record_floor_failed",
            result.sampling_result.reasons,
        )

    def test_quality_exclusion_is_audited_before_collision_graph(self):
        records = list(self._balanced_records())
        records[0] = make_record(
            "x1",
            "x",
            1_000,
            event_id="SHARED",
            coordinate_uncertainty_m=20_000.0,
        )
        records[3] = make_record("y1", "y", 31_000, event_id="SHARED")
        result = build_occurrence_sampling_preflight(
            tuple(records),
            taxonomy_eligible=True,
            thresholds=SMALL_THRESHOLDS,
        )
        self.assertEqual(result.audit.quality_excluded_x, 1)
        self.assertEqual(result.audit.collision_excluded_x, 0)
        self.assertEqual(result.audit.collision_excluded_y, 0)
        self.assertIn(
            ("coordinate_uncertainty_ceiling_failed", 1),
            result.audit.quality_exclusion_reason_counts,
        )


if __name__ == "__main__":
    unittest.main()
