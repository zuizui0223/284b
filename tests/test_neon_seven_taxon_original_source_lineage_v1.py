"""Offline seven-taxon original-source lineage audit guards."""
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_neon_seven_taxon_original_source_lineage_v1 import classify_source_replay

CFG=json.loads((ROOT/"config/neon_seven_taxon_gbif_lineage_v1.json").read_text())
V1=json.loads((ROOT/"config/neon_external_validation_preflight_v1.json").read_text())


class SevenTaxonSourceTests(unittest.TestCase):
    def test_predeclared_seven_tariff_and_signed_origins(self):
        e=CFG["taxon_inventory"]
        self.assertEqual(len(e),7)
        self.assertEqual([x["taxon"] for x in e],
                         V1["focal_taxa_predeclared_from_existing_heldout_for_US_range_only"])
        self.assertEqual(len({x["specieskey"] for x in e}),7)
        self.assertEqual(len({x["fit_artifact_id"] for x in e}),7)
        for x in e:
            self.assertEqual(len(x["fit_artifact_digest"]),71)
            self.assertTrue(x["fit_artifact_digest"].startswith("sha256:"))
        self.assertEqual(CFG["empirical_ledger_increment"],0)
        self.assertTrue(CFG["no_NEON_plant_outcomes_read"])

    def test_exact_parity_allows_known_data_source_incidence(self):
        x=CFG["taxon_inventory"][0]
        expected={"PRESERVED_SPECIMEN":3285,"HUMAN_OBSERVATION":4516}
        counts={"PRESERVED_SPECIMEN":{
                    "source_thinned_model_presence_rows":3285,
                    "source_thinned_known_NEON_dataset_rows":2},
                "HUMAN_OBSERVATION":{
                    "source_thinned_model_presence_rows":4516,
                    "source_thinned_known_NEON_dataset_rows":0}}
        r=classify_source_replay(x,expected,counts)
        self.assertEqual(r["state"],"known_NEON_voucher_dataset_in_historical_training")
        self.assertEqual(r["known_NEON_datasetkey_model_input_rows"],2)
        self.assertTrue(all(r["source_count_reproduced"].values()))
        self.assertFalse(r["full_independence_of_NEON_plots_verified"])

    def test_source_parity_failure_must_not_license_independence_claim(self):
        x=CFG["taxon_inventory"][0]
        expected={"PRESERVED_SPECIMEN":3285,"HUMAN_OBSERVATION":4516}
        counts={"PRESERVED_SPECIMEN":{
                    "source_thinned_model_presence_rows":3286,
                    "source_thinned_known_NEON_dataset_rows":2},
                "HUMAN_OBSERVATION":{
                    "source_thinned_model_presence_rows":4516,
                    "source_thinned_known_NEON_dataset_rows":0}}
        r=classify_source_replay(x,expected,counts)
        self.assertEqual(r["state"],"historical_model_input_count_parity_FAILED")
        self.assertIsNone(r["known_NEON_datasetkey_model_input_rows"])
        self.assertFalse(r["full_independence_of_NEON_plots_verified"])


if __name__=="__main__":
    unittest.main()
