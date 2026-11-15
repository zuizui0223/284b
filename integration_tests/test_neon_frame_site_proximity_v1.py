"""Synthetic geometry-only tests; no plant records or species labels."""
import unittest
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_neon_frame_site_proximity_v1 import closest_haversine_km


class SiteProxyTests(unittest.TestCase):
    def test_identical_location_zero_distance(self):
        c=np.array([[45.0,-110.0],[46.0,-110.0]])
        self.assertAlmostEqual(closest_haversine_km(45,-110,c),0.,places=10)

    def test_known_one_degree_longitudinal_arc(self):
        c=np.array([[0.,1.]])
        self.assertAlmostEqual(closest_haversine_km(0.,0.,c),111.195,places=2)

    def test_min_of_two_locations(self):
        c=np.array([[0,10],[0,.01]])
        self.assertLess(closest_haversine_km(0,0,c),2.)

    def test_bad_shapes_fail_closed(self):
        with self.assertRaises(ValueError):
            closest_haversine_km(0,0,np.zeros((1,3)))
        with self.assertRaises(ValueError):
            closest_haversine_km(0,0,np.zeros((0,2)))


if __name__=="__main__":
    unittest.main()
