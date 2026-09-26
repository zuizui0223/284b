import unittest

from product_b_v5.calibration import (
    CalibrationState,
    CalibrationTaxonResult,
    calibrate_reference_ceiling,
)


class PairedCalibrationTests(unittest.TestCase):
    def test_95_percent_nearest_rank_uses_all_complete_taxa(self):
        results = tuple(
            CalibrationTaxonResult(
                taxon_name=f"taxon_{index:02d}",
                mode_a_adequate=True,
                mode_b_adequate=True,
                discordance=index / 100.0,
            )
            for index in range(30)
        )
        decision = calibrate_reference_ceiling(results)
        self.assertEqual(decision.state, CalibrationState.READY)
        self.assertAlmostEqual(decision.reference_ceiling, 0.28)
        self.assertEqual(decision.complete_taxa, 30)
        self.assertEqual(len(decision.included_taxa), 30)
        self.assertEqual(decision.quantile_method, "nearest_rank")

    def test_high_discordance_complete_taxon_cannot_be_dropped(self):
        results = [
            CalibrationTaxonResult(
                taxon_name=f"taxon_{index:02d}",
                mode_a_adequate=True,
                mode_b_adequate=True,
                discordance=0.10,
            )
            for index in range(29)
        ]
        results.append(
            CalibrationTaxonResult(
                taxon_name="high_discordance_taxon",
                mode_a_adequate=True,
                mode_b_adequate=True,
                discordance=0.95,
            )
        )
        decision = calibrate_reference_ceiling(tuple(results))
        self.assertEqual(decision.state, CalibrationState.READY)
        self.assertIn("high_discordance_taxon", decision.included_taxa)
        self.assertAlmostEqual(decision.reference_ceiling, 0.10)

    def test_fewer_than_30_complete_taxa_is_unresolved(self):
        results = tuple(
            CalibrationTaxonResult(
                taxon_name=f"taxon_{index:02d}",
                mode_a_adequate=True,
                mode_b_adequate=index < 29,
                discordance=0.10 if index < 29 else None,
            )
            for index in range(30)
        )
        decision = calibrate_reference_ceiling(results)
        self.assertEqual(decision.state, CalibrationState.UNRESOLVED)
        self.assertIsNone(decision.reference_ceiling)
        self.assertEqual(decision.complete_taxa, 29)
        self.assertIn("insufficient_complete_calibration_taxa", decision.reasons)

    def test_missing_discordance_is_unresolved_not_zero(self):
        results = tuple(
            CalibrationTaxonResult(
                taxon_name=f"taxon_{index:02d}",
                mode_a_adequate=True,
                mode_b_adequate=True,
                discordance=None if index == 0 else 0.10,
            )
            for index in range(31)
        )
        decision = calibrate_reference_ceiling(results)
        self.assertEqual(decision.state, CalibrationState.READY)
        self.assertEqual(decision.complete_taxa, 30)
        self.assertIn("taxon_00", decision.unresolved_taxon_names)


if __name__ == "__main__":
    unittest.main()
