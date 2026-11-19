"""All 12 repaired-source heldout model loops must preserve original methods."""
import ast,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=(ROOT/"scripts/fit_gbif_repaired_Artemisia_fixed_original_centers_v1.py").read_text()
REPAIRED=(ROOT/"scripts/fit_gbif_repaired_heldout12_fixed_original_centers_v1.py").read_text()
MANIFEST=json.loads((ROOT/"config/gbif_original_heldout12_geometry_manifest_v1.json").read_text())

def science_body(text):
    a="    for m in (150,300,500):\n        background = backgrounds[m]"
    b="    predictions=pd.DataFrame(prediction_rows)"
    assert text.count(a)==text.count(b)==1
    return text[text.index(a):text.index(b)]

class RepairedHeldout12Model(unittest.TestCase):
    def test_model_method_cv_and_fitting_loop_unchanged(self):
        self.assertEqual(science_body(ORIGINAL),science_body(REPAIRED))
        ast.parse(REPAIRED)
    def test_no_selected_or_substituted_heldout_taxon(self):
        self.assertEqual(MANIFEST["frozen_taxon_count"],12)
        self.assertEqual(len(MANIFEST["entries"]),12)
        self.assertIn('panel != "heldout" or not 0 <= taxon_index < 12',REPAIRED)
        self.assertIn('entry["index"] != taxon_index',REPAIRED)
        self.assertIn('prior_taxon["original_specieskey"] != entry["historical_specieskey"]',REPAIRED)
    def test_fixed_original_frames_centers_and_source(self):
        for word in ('ORIGINAL_SIGNED_HELDOUT_GEOMETRY_EXACTLY_REPRODUCED',
                     'original_qualification_artifact_id',
                     'original_fit_artifact_id','center_npy_sha256',
                     'reconstructed_center_sha256','original_comparison_frame_sha256_by_M',
                     'observed_manifest != recovered["current_manifest_sha256"]'):
            self.assertIn(word,REPAIRED)
    def test_no_reference_q95_or_repaired_12_paired_outcomes(self):
        for text in ('"paired_discordance_computed":False',
                     '"reference_ceiling_opened_or_read":False',
                     '"heldout_pairing_opened":False',
                     '"process_knockout_computed":False',
                     '"counts_as_empirical_conclusion":False'):
            self.assertIn(text,REPAIRED)
        self.assertEqual(MANIFEST["empirical_ledger_increment"],0)
if __name__=="__main__":unittest.main()
