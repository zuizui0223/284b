"""Synthetic tests for frozen old geometry / repaired single-source fit pilot."""
import unittest
import numpy as np
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_gbif_repaired_Artemisia_single_source_drift_v1 import source_drift

class SourceDriftPilot(unittest.TestCase):
    def test_identical_same_source_score_distributions_have_zero_tv(self):
        a=np.linspace(.1,2.,2000)
        self.assertAlmostEqual(source_drift(a,a),0.)
        self.assertAlmostEqual(source_drift(a,2*a),0.)

    def test_spatial_score_reassignment_is_not_automatically_negligible(self):
        a=np.full(2000,1.)
        b=np.concatenate([np.zeros(1000),np.full(1000,1.)])
        self.assertAlmostEqual(source_drift(a,b),.5)

    def test_nonfinite_allzero_unequal_length_fail_closed(self):
        with self.assertRaises(ValueError):
            source_drift(np.ones(2000),np.zeros(2000))
        with self.assertRaises(ValueError):
            source_drift(np.ones(2000),np.ones(1999))
        with self.assertRaises(ValueError):
            source_drift(np.ones(2000),np.full(2000,float("nan")))

    def test_single_taxon_fitted_arm_does_not_compute_pairing_or_q95(self):
        source=(ROOT/"scripts/fit_gbif_repaired_Artemisia_fixed_original_centers_v1.py").read_text(encoding="utf-8")
        self.assertIn('taxon_index != 0 or name != "Artemisia tridentata"',source)
        self.assertIn('centers = np.load(centers_file, allow_pickle=False)',source)
        self.assertIn('"paired_discordance_computed":False',source)
        self.assertIn('"reference_ceiling_opened_or_read":False',source)
        self.assertIn("repaired_2026-08-01_10215_parquet_files",source)

if __name__=="__main__":
    unittest.main()
