"""Site geometry preflight uses only available NEON site metadata."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from neon_site_geometry_metadata_v1 import great_circle_km, summarize


def fixture():
    coords=[
        {"siteCode":f"ST{i:02d}","siteLatitude":32+i*.05,
         "siteLongitude":-110-i*.07,"domainCode":"D14","stateCode":"AZ"}
        for i in range(47)
    ]
    return {"data":coords}, {"site_metadata_url":"https://example.invalid/"},
           {"site_month_by_site":{x["siteCode"]:{} for x in coords}}


class TestSiteGeometry(unittest.TestCase):
    def test_distance_symmetry_and_scale(self):
        self.assertAlmostEqual(great_circle_km(0,0,0,0),0.)
        self.assertAlmostEqual(great_circle_km(0,0,0,1),111.195,places=2)
        self.assertAlmostEqual(great_circle_km(1,2,3,4),great_circle_km(3,4,1,2),places=11)

    def test_47_metadata_locations_does_not_authorize_ecological_inference(self):
        p,c,i=fixture()
        r=summarize(p,c,i,b"fake-raw")
        self.assertEqual(r["product_site_count"],47)
        self.assertEqual(r["pairwise_site_distances_count"],1081)
        self.assertFalse(r["external_validation_authorized"])
        self.assertFalse(r["raw_data_and_plant_labels_opened"])
        self.assertFalse(r["NEON_plot_coordinates_opened"])
        self.assertEqual(r["empirical_ledger_increment"],0)

    def test_missing_code_fails_closed(self):
        p,c,i=fixture()
        p["data"].pop()
        with self.assertRaises(ValueError):
            summarize(p,c,i,b"fake-raw")

    def test_duplicate_site_code_fails_closed(self):
        p,c,i=fixture()
        p["data"].append(p["data"][0])
        with self.assertRaises(ValueError):
            summarize(p,c,i,b"fake-raw")


if __name__=="__main__":
    unittest.main()
