"""Small unit tests for the fixed cross-target identity benchmark."""
import unittest
from pathlib import Path
import sys
# The default repo unittest job intentionally has no numerical dependencies.
# Run these tests in the dedicated target-identity workflow when numpy is present.
try:
    import numpy as np
except ModuleNotFoundError:
    np = None

if np is not None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from audit_target_identity_controls_v1 import discordance, nearest_rank_q95


@unittest.skipIf(np is None, "numpy is provided by the dedicated model-control workflow")
class TestIdentityControls(unittest.TestCase):
    def test_discordance(self):
        x = np.ones(2000)
        self.assertAlmostEqual(discordance(x,x),0.0)
        y=np.ones(2000)
        y[:1000]=0
        self.assertAlmostEqual(discordance(x,y),0.5)

    def test_fail_closed_invalid_vectors(self):
        with self.assertRaises(ValueError):
            discordance(np.ones(1999),np.ones(2000))
        with self.assertRaises(ValueError):
            discordance(np.zeros(2000),np.ones(2000))
        with self.assertRaises(ValueError):
            discordance(np.ones(2000),np.full(2000,float("nan")))

    def test_reference_nearest_rank_and_no_threshold_retune(self):
        self.assertEqual(nearest_rank_q95(list(range(1,41))),38)


if __name__ == "__main__":
    unittest.main()
