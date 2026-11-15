"""Test the antirank bound against every permutation of small score vectors."""
import itertools
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_level_a_surface_controls_v1 import antirank_maximum, discordance


class ScorePermutationTests(unittest.TestCase):
    def test_full_permutation_space_is_bounded_by_antirank(self):
        a = np.array([0.3, 2.0, 0.9, 0.15])
        b = np.array([1.5, 0.1, 0.4, 1.0])
        maximum = antirank_maximum(a, b)
        computed = [discordance(a, np.array(p)) for p in itertools.permutations(b)]
        self.assertAlmostEqual(max(computed), maximum, places=12)

    def test_invalid_vectors_fail_closed(self):
        with self.assertRaises(ValueError):
            discordance([0, 0], [1, 2])
        with self.assertRaises(ValueError):
            discordance([1, -1], [1, 2])
        with self.assertRaises(ValueError):
            discordance([1], [1, 2])

    def test_identical_and_permuted_vectors(self):
        v = np.array([1., 2., 3., 4.])
        self.assertAlmostEqual(discordance(v, v), 0.)
        self.assertGreater(discordance(v, v[::-1]), 0.)


if __name__ == "__main__":
    unittest.main()
