"""Guard the metadata-only NEON preflight without fetching biological outcomes."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from neon_external_metadata_preflight_v1 import summarize_metadata
import json

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/"config/neon_external_validation_preflight_v1.json").read_text())


class NeonMetadataTests(unittest.TestCase):
    def test_no_outcome_fields_even_when_site_list_available(self):
        payload={"data":{"productCode":"DP1.10058.001","productName":"Plant presence and percent cover",
                         "siteCodes":[{"siteCode":"ABBY","availableMonths":["2024-06","2024-07"]},
                                      {"siteCode":"BART","availableMonths":["2024-06"]}],
                         "productStatus":"ACTIVE","releases":["RELEASE-2026"]}}
        v=summarize_metadata(payload,"synthetic",b"{}",CFG)
        self.assertEqual(v["unique_site_codes"],2)
        self.assertFalse(v["species_outcomes_read"])
        self.assertFalse(v["taxon_record_counts_read"])
        self.assertEqual(v["empirical_ledger_increment"],0)

    def test_wrong_product_rejected(self):
        with self.assertRaises(ValueError):
            summarize_metadata({"data":{"productCode":"DP1.10059.001"}},
                               "synthetic",b"{}",CFG)

    def test_fixed_focal_taxa_and_stop_rules(self):
        self.assertEqual(len(CFG["focal_taxa_predeclared_from_existing_heldout_for_US_range_only"]),7)
        self.assertEqual(CFG["eligibility_rules_prelabel"]["if_fewer_than_three_taxa_evaluable"],
                         "STOP_EXTERNAL_VALIDATION_UNESTIMABLE")
        self.assertTrue(CFG["eligibility_rules_prelabel"]["no_replacement_after_metadata_or_biological_results"])
        self.assertFalse(CFG["public_source"]["raw_data_download_authorized"])
        self.assertTrue(CFG["success_estimand_if_qualified"]["no_third_source_truth_assumption"])


if __name__=="__main__":
    unittest.main()
