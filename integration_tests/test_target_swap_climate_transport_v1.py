"""Climate-frame coverage proxy tests; separate from root dependency-free CI."""
import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_target_swap_climate_transport_v1 import per_feature_overlap


class ClimateCoverageTests(unittest.TestCase):
    def test_identical_reference_frame_high_average_coverage(self):
        d=np.repeat(np.linspace(0,1,2000)[:,None],19,axis=1)
        r=per_feature_overlap(d,d)
        self.assertGreater(r["mean_feature_coverage_1_99"],0.975)
        self.assertLess(r["mean_feature_coverage_1_99"],0.985)

    def test_shifted_frame_has_zero_donor_coverage(self):
        d=np.repeat(np.linspace(0,1,2000)[:,None],19,axis=1)
        r=per_feature_overlap(d+2,d)
        self.assertEqual(r["mean_feature_coverage_1_99"],0)

    def test_bad_frames_rejected(self):
        with self.assertRaises(ValueError):
            per_feature_overlap(np.ones((2,19)),np.ones((2000,19)))


if __name__=="__main__":
    unittest.main()
