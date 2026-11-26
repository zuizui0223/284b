"""Guard post-freeze source-completeness sensitivity estimands before SDM outcomes."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DESIGN=json.loads((ROOT/"config/gbif_missing20_fixed_vs_rebuilt_geometry_v1.json").read_text())
ORIG=json.loads((ROOT/"config/gbif_missing20_restoration_sensitivity_v1.json").read_text())


class FixedFrameRestorationTests(unittest.TestCase):
    def test_panel_M_and_quantile_are_original_and_immutable(self):
        self.assertEqual(DESIGN["original_target_taxa"],12)
        self.assertEqual(DESIGN["original_reference_taxa"],47)
        self.assertEqual(DESIGN["same_M_km"],[150,300,500])
        self.assertEqual(DESIGN["same_procedure_count"],8)
        self.assertEqual(len(DESIGN["same_covariates"]),19)
        self.assertEqual(DESIGN["same_reference_quantile"]["q"],.95)
        self.assertEqual(DESIGN["same_reference_quantile"]["minimum_calibration_taxa"],30)
        self.assertEqual(ORIG["original_reference_taxa"],47) if "original_reference_taxa" in ORIG else self.assertEqual(ORIG["independent_frozen_panels"]["calibration_taxa"],47)

    def test_original_frozen_geo_and_repaired_new_geo_are_not_mixed(self):
        self.assertEqual(DESIGN["primary"],"fixed_original_geometry_source_restoration")
        self.assertEqual(DESIGN["secondary"],"fully_rebuilt_geometry_source_restoration")
        self.assertEqual(DESIGN["secondary_status"],"SEPARATE_VERSIONED_EXPERIMENT_NOT_YET_AUTHORIZED")
        self.assertTrue(DESIGN["stop_if_original_centers_hash_not_reproduced"])
        self.assertTrue(DESIGN["stop_if_frozen_original_model_predictions_not_reproduced"])
        self.assertIn("2000-row frame",DESIGN["primary_gates"][4])
        self.assertTrue(any("47" in s and "30" in s for s in DESIGN["primary_gates"]))

    def test_not_new_biological_endpoint_or_NEON_result(self):
        self.assertTrue(DESIGN["original_Level_A_historical_endpoint_unchanged"])
        self.assertTrue(DESIGN["original_M1_mathematical_identity_unchanged"])
        self.assertTrue(DESIGN["no_upstream_NEON_field_outcomes_access"])
        self.assertEqual(DESIGN["empirical_ledger_increment"],0)
        self.assertIn("not a new independent",DESIGN["explicit_claim_boundary"])


if __name__=="__main__":
    unittest.main()
