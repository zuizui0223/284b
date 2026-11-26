"""Test the NEON site-month metadata barrier with synthetic product responses."""
import hashlib
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from neon_release_site_month_inventory_v2 import summarize_public_metadata

DATA=b'{"no_species_outcomes": true}'
P={"sites_sorted":["ABBY","BART"],"schema":"284b.neon_external_source_metadata_receipt.v1"}
C={"fixed_release":{
    "product_code":"DP1.10058.001","label":"RELEASE-2026","doi":"10.48443/9g4s-hq52",
    "publication_date":"2026-01-23","original_metadata_sha256":hashlib.sha256(DATA).hexdigest(),
    "expected_site_count":2,"expected_date_range":["2013-06","2024-12"],
}}


class MetadataTests(unittest.TestCase):
    def test_metadata_only_counts_site_months_without_species(self):
        payload={"data":{"productCode":"DP1.10058.001","siteCodes":[
            {"siteCode":"ABBY","availableMonths":["2013-06","2020-08","2020-08"]},
            {"siteCode":"BART","availableMonths":["2024-12","2024-11"]}
        ]}}
        r=summarize_public_metadata(payload,DATA,P,C)
        self.assertEqual(r["status"],"metadata_site_months_confirmed")
        self.assertEqual(r["site_month_memberships"],4)
        self.assertEqual(r["unique_site_count"],2)
        self.assertEqual(r["year_site_month_memberships"]["2020"],1)
        self.assertEqual(r["actual_site_month_span"],["2013-06","2024-12"])
        self.assertFalse(r["species_outcomes_read"])
        self.assertFalse(r["external_validation_authorized"])

    def test_metadata_drift_is_blocker(self):
        p={"data":{"productCode":"DP1.10058.001","siteCodes":[
            {"siteCode":"ABBY","availableMonths":["2025-08"]},
            {"siteCode":"BART","availableMonths":["2024-12"]}]}}
        r=summarize_public_metadata(p,DATA,P,C)
        self.assertEqual(r["status"],"metadata_drift_or_incomplete_STOP")
        self.assertFalse(r["all_site_months_within_official_range"])

    def test_bad_product_and_missing_months_fail(self):
        with self.assertRaises(ValueError):
            summarize_public_metadata({"data":{"productCode":"OTHER","siteCodes":[]}},DATA,P,C)
        with self.assertRaises(ValueError):
            summarize_public_metadata({"data":{"productCode":"DP1.10058.001","siteCodes":[
                {"siteCode":"ABBY"}]}},DATA,P,C)


if __name__=="__main__":
    unittest.main()
