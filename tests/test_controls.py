import unittest

from product_b_v5.controls import (
    ControlTaxonProfile,
    FocalPairProfile,
    NonObligatePairCandidate,
    ReplacementCandidate,
    SHUFFLE_REPETITIONS,
    build_shuffled_partner_null,
    match_non_obligate_controls,
    occupied_cell_centroid_convex_hull_area_km2,
    shuffle_seed,
)


def profile(taxon_id, family, records=100, cells=50, effective=30.0, extent=1000.0):
    return ControlTaxonProfile(
        taxon_id=taxon_id,
        family_key=family,
        independent_records=records,
        unique_cells=cells,
        effective_cells=effective,
        spatial_extent_km2=extent,
    )


def focal_pair():
    return FocalPairProfile(
        pair_id="FOCAL",
        x=profile("X0", "MORACEAE", records=100, cells=60, effective=40, extent=1200),
        y=profile("Y0", "AGAONIDAE", records=80, cells=45, effective=30, extent=900),
    )


class SpatialExtentTests(unittest.TestCase):
    def test_square_cell_centroid_hull_area_is_100_square_km(self):
        area = occupied_cell_centroid_convex_hull_area_km2(
            ((0, 0), (10_000, 0), (10_000, 10_000), (0, 10_000))
        )
        self.assertAlmostEqual(area, 100.0)

    def test_collinear_extent_is_not_matchable(self):
        with self.assertRaisesRegex(ValueError, "collinear"):
            occupied_cell_centroid_convex_hull_area_km2(
                ((0, 0), (10_000, 0), (20_000, 0))
            )


class MatchedNonObligateControlTests(unittest.TestCase):
    def test_five_or_more_family_and_caliper_matches_pass(self):
        focal = focal_pair()
        candidates = []
        for i in range(6):
            candidates.append(
                NonObligatePairCandidate(
                    pair_id=f"C{i}",
                    x=profile(
                        f"X{i+1}",
                        "MORACEAE",
                        records=100 + i,
                        cells=60,
                        effective=40,
                        extent=1200,
                    ),
                    y=profile(
                        f"Y{i+1}",
                        "AGAONIDAE",
                        records=80 + i,
                        cells=45,
                        effective=30,
                        extent=900,
                    ),
                    interaction_screen_passed=True,
                )
            )
        result = match_non_obligate_controls(focal, tuple(candidates))
        self.assertTrue(result.passed)
        self.assertEqual(result.eligible_pair_count, 6)
        self.assertEqual(result.selected_pair_ids[0], "C0")

    def test_screen_failure_and_factor_above_two_are_not_rescued(self):
        focal = focal_pair()
        candidates = (
            NonObligatePairCandidate(
                "screened_out",
                profile("X1", "MORACEAE"),
                profile("Y1", "AGAONIDAE"),
                False,
            ),
            NonObligatePairCandidate(
                "too_many_records",
                profile("X2", "MORACEAE", records=201),
                profile("Y2", "AGAONIDAE"),
                True,
            ),
            NonObligatePairCandidate(
                "wrong_family",
                profile("X3", "ROSACEAE"),
                profile("Y3", "AGAONIDAE"),
                True,
            ),
        )
        result = match_non_obligate_controls(focal, candidates)
        self.assertFalse(result.passed)
        self.assertEqual(result.eligible_pair_count, 0)
        self.assertIn("insufficient_matched_non_obligate_controls", result.reasons)

    def test_focal_taxa_cannot_be_reused_in_matched_non_obligate_pair(self):
        focal = focal_pair()
        candidate = NonObligatePairCandidate(
            "reuse",
            focal.x,
            profile("Y1", "AGAONIDAE", records=80, cells=45, effective=30, extent=900),
            True,
        )
        result = match_non_obligate_controls(focal, (candidate,))
        self.assertEqual(result.eligible_pair_count, 0)


class ShuffledPartnerNullTests(unittest.TestCase):
    def test_seed_rule_is_fixed_and_reproducible(self):
        self.assertEqual(shuffle_seed(0), 2955972670)
        self.assertEqual(shuffle_seed(1), 1845832959)
        self.assertEqual(shuffle_seed(2), 2393992373)

    def test_five_matched_replacements_generate_exactly_100_draws(self):
        focal = focal_pair()
        replacements = tuple(
            ReplacementCandidate(
                profile(
                    f"YR{i}",
                    "AGAONIDAE",
                    records=80 + i,
                    cells=45,
                    effective=30,
                    extent=900,
                ),
                True,
            )
            for i in range(5)
        )
        result = build_shuffled_partner_null(focal, replacements)
        self.assertTrue(result.passed)
        self.assertEqual(len(result.selected_taxon_ids), SHUFFLE_REPETITIONS)
        self.assertEqual(len(result.seeds), SHUFFLE_REPETITIONS)
        self.assertTrue(set(result.selected_taxon_ids).issubset(set(result.eligible_taxon_ids)))

    def test_four_replacements_stay_unresolved_without_relaxation(self):
        focal = focal_pair()
        replacements = tuple(
            ReplacementCandidate(
                profile(f"YR{i}", "AGAONIDAE", records=80, cells=45, effective=30, extent=900),
                True,
            )
            for i in range(4)
        )
        result = build_shuffled_partner_null(focal, replacements)
        self.assertFalse(result.passed)
        self.assertEqual(result.selected_taxon_ids, ())
        self.assertIn("insufficient_distinct_shuffled_replacements", result.reasons)

    def test_interaction_screen_failure_is_not_shuffle_eligible(self):
        focal = focal_pair()
        replacements = tuple(
            ReplacementCandidate(
                profile(f"YR{i}", "AGAONIDAE", records=80, cells=45, effective=30, extent=900),
                i != 0,
            )
            for i in range(5)
        )
        result = build_shuffled_partner_null(focal, replacements)
        self.assertFalse(result.passed)
        self.assertEqual(len(result.eligible_taxon_ids), 4)


if __name__ == "__main__":
    unittest.main()
