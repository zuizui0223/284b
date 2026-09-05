import unittest

from product_b_v7.preflight import (
    FrameDeclaration,
    LiteratureWitness,
    LiteratureWitnessState,
    evaluate_literature_witness_preflight,
    evaluate_witness_frame_preflight,
    validate_frame_declaration,
    validate_new_pair_id,
)


def witness(witness_id, lon, lat=0.0, uncertainty=1000.0):
    return LiteratureWitness(
        witness_id=witness_id,
        source_doi="10.1234/primary",
        longitude=lon,
        latitude=lat,
        uncertainty_m=uncertainty,
        coordinate_source_type="primary_literature_text",
    )


def independent_frame():
    return FrameDeclaration(
        frame_id="FRAME001",
        source_type="preexisting_admin_boundary",
        source_authority="example-authority",
        source_version="2026-01",
        geometry_type="admin_codes",
        geometry_value="AA-1;AA-2",
        witness_coordinates_used_to_derive_geometry=False,
        occurrence_information_used_to_derive_geometry=False,
    )


class LiteratureWitnessPreflightTests(unittest.TestCase):
    def test_unchanged_five_witness_three_cell_floor_passes(self):
        result = evaluate_literature_witness_preflight(
            [
                witness("w1", 0.0),
                witness("w2", 0.01),
                witness("w3", 1.0),
                witness("w4", 1.01),
                witness("w5", 2.0),
            ]
        )
        self.assertEqual(result.state, LiteratureWitnessState.PASSED)
        self.assertGreaterEqual(len(result.unique_10km_cells), 3)
        self.assertEqual(result.retained_witness_count, 5)

    def test_high_uncertainty_is_excluded_not_rescued(self):
        result = evaluate_literature_witness_preflight(
            [
                witness("w1", 0.0, uncertainty=10001.0),
                witness("w2", 1.0),
                witness("w3", 2.0),
                witness("w4", 3.0),
                witness("w5", 4.0),
            ]
        )
        self.assertEqual(result.state, LiteratureWitnessState.UNRESOLVED)
        self.assertIn("literature_witness_record_floor_failed", result.reasons)
        self.assertEqual(result.excluded_witness_count, 1)

    def test_exact_duplicate_source_id_collapses(self):
        row = witness("w1", 0.0)
        result = evaluate_literature_witness_preflight(
            [row, row, witness("w2", 1.0), witness("w3", 2.0), witness("w4", 3.0), witness("w5", 4.0)]
        )
        self.assertEqual(result.raw_witness_count, 6)
        self.assertEqual(result.duplicate_collapsed_count, 1)
        self.assertEqual(result.retained_witness_count, 5)

    def test_conflicting_duplicate_source_id_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "conflicting metadata"):
            evaluate_literature_witness_preflight(
                [witness("same", 0.0), witness("same", 1.0)]
            )

    def test_geocoded_or_nonprimary_coordinate_source_is_rejected(self):
        bad = LiteratureWitness(
            witness_id="w1",
            source_doi="10.1234/primary",
            longitude=0.0,
            latitude=0.0,
            uncertainty_m=1000.0,
            coordinate_source_type="project_geocoded_locality",
        )
        with self.assertRaisesRegex(ValueError, "primary source"):
            evaluate_literature_witness_preflight([bad])


class FrameAndFirewallTests(unittest.TestCase):
    def test_independent_preexisting_frame_passes(self):
        self.assertEqual(validate_frame_declaration(independent_frame()), ())

    def test_witness_derived_convex_hull_is_forbidden(self):
        frame = FrameDeclaration(
            frame_id="bad",
            source_type="preexisting_admin_boundary",
            source_authority="authority",
            source_version="1",
            geometry_type="polygon_wkt",
            geometry_value="POLYGON((0 0,1 0,0 1,0 0))",
            witness_coordinates_used_to_derive_geometry=True,
            occurrence_information_used_to_derive_geometry=False,
        )
        self.assertIn("witness_derived_frame_forbidden", validate_frame_declaration(frame))

    def test_occurrence_derived_frame_is_forbidden(self):
        frame = independent_frame()
        bad = FrameDeclaration(
            frame_id=frame.frame_id,
            source_type=frame.source_type,
            source_authority=frame.source_authority,
            source_version=frame.source_version,
            geometry_type=frame.geometry_type,
            geometry_value=frame.geometry_value,
            witness_coordinates_used_to_derive_geometry=False,
            occurrence_information_used_to_derive_geometry=True,
        )
        self.assertIn("occurrence_derived_frame_forbidden", validate_frame_declaration(bad))

    def test_v5_v6_pairs_are_firewalled(self):
        for pair_id in ("OPM_FIG_001", "SEN001", "EPV001", "HTR001"):
            with self.assertRaisesRegex(ValueError, "firewalled"):
                validate_new_pair_id(pair_id)
        validate_new_pair_id("NEW001")

    def test_combined_preflight_requires_witness_and_frame(self):
        result = evaluate_witness_frame_preflight(
            pair_id="NEW001",
            witnesses=[
                witness("w1", 0.0),
                witness("w2", 0.01),
                witness("w3", 1.0),
                witness("w4", 1.01),
                witness("w5", 2.0),
            ],
            frame=independent_frame(),
        )
        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
