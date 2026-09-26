import unittest

from product_b_v5.occurrence_preprocessing import OccurrenceRecord
from product_b_v6.preflight import build_directed_witness_sampling_preflight_from_records
from product_b_v6.witness import WitnessPreflightState


def record(row_id, partner, east, north=0.0, **overrides):
    values = dict(
        row_id=row_id,
        partner=partner,
        decimal_latitude=30.0,
        decimal_longitude=-110.0,
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


def passing_records():
    rows = [
        record(f"x{i}", "x", i * 10_000.0, 0.0)
        for i in range(50)
    ]
    # Five independent records occupying exactly three cells.
    rows.extend(
        (
            record("y1", "y", 600_000.0, 0.0),
            record("y2", "y", 600_001.0, 0.0),
            record("y3", "y", 610_000.0, 0.0),
            record("y4", "y", 610_001.0, 0.0),
            record("y5", "y", 620_000.0, 0.0),
        )
    )
    return tuple(rows)


class DirectedWitnessOccurrencePreflightTests(unittest.TestCase):
    def test_asymmetric_frozen_gate_passes_with_adequate_host_and_five_witnesses(self):
        result = build_directed_witness_sampling_preflight_from_records(passing_records())
        self.assertEqual(result.preflight.state, WitnessPreflightState.PASSED)
        self.assertEqual(result.host_summary.independent_records, 50)
        self.assertEqual(result.host_summary.unique_cells, 50)
        self.assertEqual(result.host_summary.effective_cells, 50.0)
        self.assertEqual(result.witness_summary.independent_records, 5)
        self.assertEqual(result.witness_summary.unique_cells, 3)
        self.assertEqual(len(result.unique_witness_cells), 3)

    def test_same_witness_cell_counts_once_for_witness_scoring_support(self):
        result = build_directed_witness_sampling_preflight_from_records(passing_records())
        self.assertEqual(
            result.unique_witness_cells,
            ("60:0", "61:0", "62:0"),
        )

    def test_cross_partner_collision_can_drive_witness_below_floor(self):
        rows = list(passing_records())
        rows[0] = record("x0", "x", 0.0, event_id="SHARED")
        rows[-1] = record("y5", "y", 620_000.0, event_id="SHARED")
        result = build_directed_witness_sampling_preflight_from_records(tuple(rows))
        self.assertEqual(result.audit.collision_excluded_x, 1)
        self.assertEqual(result.audit.collision_excluded_y, 1)
        self.assertEqual(result.witness_summary.independent_records, 4)
        self.assertEqual(result.preflight.state, WitnessPreflightState.UNRESOLVED)
        self.assertIn("host_independent_record_floor_failed", result.preflight.reasons)
        self.assertIn("witness_independent_record_floor_failed", result.preflight.reasons)

    def test_quality_exclusion_precedes_witness_floor(self):
        rows = list(passing_records())
        rows[-1] = record(
            "y5",
            "y",
            620_000.0,
            coordinate_uncertainty_m=10_001.0,
        )
        result = build_directed_witness_sampling_preflight_from_records(tuple(rows))
        self.assertEqual(result.audit.quality_excluded_y, 1)
        self.assertEqual(
            result.audit.quality_exclusion_reason_counts,
            (("coordinate_uncertainty_ceiling_failed", 1),),
        )
        self.assertEqual(result.witness_summary.independent_records, 4)
        self.assertEqual(result.preflight.state, WitnessPreflightState.UNRESOLVED)

    def test_host_floor_is_not_relaxed_by_abundant_witnesses(self):
        rows = list(passing_records())[1:]
        result = build_directed_witness_sampling_preflight_from_records(tuple(rows))
        self.assertEqual(result.host_summary.independent_records, 49)
        self.assertEqual(result.preflight.state, WitnessPreflightState.UNRESOLVED)
        self.assertIn("host_independent_record_floor_failed", result.preflight.reasons)


if __name__ == "__main__":
    unittest.main()
