import unittest

from product_b_v5.projection import wgs84_to_epsg6933


class EPSG6933ProjectionTests(unittest.TestCase):
    def test_origin_projects_to_origin(self):
        easting, northing = wgs84_to_epsg6933(0.0, 0.0)
        self.assertAlmostEqual(easting, 0.0, places=9)
        self.assertAlmostEqual(northing, 0.0, places=9)

    def test_epsg_documented_northeast_bound_control_point(self):
        easting, northing = wgs84_to_epsg6933(180.0, 86.0)
        self.assertAlmostEqual(easting, 17_367_530.45, places=2)
        self.assertAlmostEqual(northing, 7_324_184.56, places=2)

    def test_bangkok_scope_point_has_frozen_projection(self):
        easting, northing = wgs84_to_epsg6933(100.42, 13.83)
        self.assertAlmostEqual(easting, 9_689_152.262795, places=6)
        self.assertAlmostEqual(northing, 1_747_701.298764, places=6)

    def test_outside_epsg_area_of_use_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "area of use"):
            wgs84_to_epsg6933(0.0, 86.0001)

    def test_invalid_longitude_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "longitude"):
            wgs84_to_epsg6933(180.1, 0.0)


if __name__ == "__main__":
    unittest.main()
