"""Exact 2000-row within-source TV pilot: no source-paired discordance."""
import importlib.util,unittest
from pathlib import Path
import numpy as np
SRC=Path(__file__).resolve().parents[1]/"scripts"/"audit_gbif_repaired_Abies_reference_single_source_drift_v1.py"
spec=importlib.util.spec_from_file_location("abies_source_drift",SRC)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class AbiesSignedSourceDrift(unittest.TestCase):
    def test_identical_vectors_zero(self):
        v=np.linspace(1,2,2000)
        self.assertAlmostEqual(mod.source_drift(v,v),0.0)
    def test_normalized_mass_shift_positive(self):
        a=np.ones(2000)
        b=np.ones(2000);b[0]=20
        self.assertGreater(mod.source_drift(a,b),0.0)
    def test_source_score_denominator_and_nonnegativity(self):
        for a,b in [(np.ones(1999),np.ones(2000)),
                    (-np.ones(2000),np.ones(2000)),
                    (np.zeros(2000),np.ones(2000))]:
            with self.assertRaises(ValueError):mod.source_drift(a,b)
    def test_frozen_original_reference_artifact(self):
        self.assertEqual(mod.SIGNATURE,
                         "sha256:9a817480d8f023246fe3dc9fedee01a6bf4e95a05418d854937610d78e58c99b")
        self.assertEqual(mod.ORIGINAL_RESULT,"product_b_same_target_successor_core19_layer1_fit_taxon_v0.4")
        self.assertEqual(mod.REPAIRED_RESULT,"284b.gbif_repaired_Abies_reference_fixed_old_centers_fit_v1")
    def test_no_cross_source_scoring_or_q95(self):
        s=SRC.read_text()
        self.assertIn('"cross_source_paired_discordance_computed":False',s)
        self.assertIn('"repaired_47taxon_q95_calibrated":False',s)
        self.assertIn('"empirical_ledger_increment":0',s)
        self.assertNotIn("schoener_d_if_both_answers_adequate",s)
if __name__=="__main__":unittest.main()
