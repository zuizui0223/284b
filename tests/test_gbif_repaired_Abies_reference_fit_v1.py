"""Abies reference repaired refit changes identity/source provenance, never model science."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=(ROOT/"scripts/fit_gbif_repaired_Artemisia_fixed_original_centers_v1.py").read_text()
REFERENCE=(ROOT/"scripts/fit_gbif_repaired_Abies_reference_fixed_original_centers_v1.py").read_text()
CFG=json.loads((ROOT/"config/gbif_repaired_Abies_reference_fixed_geometry_launch_v1.json").read_text())

def science_body(source):
    marker="    for m in (150,300,500):\n        background = backgrounds[m]"
    end="    predictions=pd.DataFrame(prediction_rows)"
    assert source.count(marker)==source.count(end)==1
    return source.split(marker)[1].split(end)[0]

class FixedAbiesReferenceModelScience(unittest.TestCase):
    def test_frozen_fit_and_adequacy_loop_byte_identical(self):
        self.assertEqual(science_body(ORIGINAL),science_body(REFERENCE))
    def test_predeclared_reference_identity(self):
        self.assertEqual((CFG["panel"],CFG["original_reference_index"],CFG["taxon"]),
                         ("successor",1,"Abies grandis"))
        self.assertEqual(CFG["historical_specieskeys"],["2685361","8KCY"])
        self.assertEqual(CFG["expected_repaired_source_thinned_counts"],{
            "PRESERVED_SPECIMEN":990,"HUMAN_OBSERVATION":6710})
        self.assertEqual(CFG["expected_fit_cells"],48)
        self.assertEqual(CFG["historical_center_sha256"],
                         "9eb19bf125fdd06c5e2b9ef901c869c23db6cd9aa88feb1305dffed79ff37f7e")
    def test_reference_prefit_requires_exact_source_and_center(self):
        for expected in (
            'panel != "successor" or taxon_index != 1 or name != "Abies grandis"',
            '"results/gbif_repaired_reference47_thinning_v1.json"',
            '"repaired_thinned_n"',
            'observed_manifest != recovered["current_manifest_sha256"]',
            'centers_receipt["recomputed_centers_SHA256"]',
            'original_signed_comparison_frames_unchanged',
        ):
            self.assertIn(expected,REFERENCE)
        self.assertIn("original_signed_comparison_frames_unchanged",REFERENCE)
    def test_no_heldout_or_reference_calibration_unsealed(self):
        self.assertIn('"reference_ceiling_opened_or_read":False',REFERENCE)
        self.assertIn('"heldout_pairing_opened":False',REFERENCE)
        self.assertIn('"counts_as_empirical_conclusion":False',REFERENCE)
        self.assertEqual(CFG["reference47_q95_opened"],False)
        self.assertEqual(CFG["heldout12_endpoint_opened"],False)
        self.assertEqual(CFG["empirical_ledger_increment"],0)

if __name__=="__main__":unittest.main()
