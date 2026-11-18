"""Repaired-reference47 fits preserve the frozen ecological modeling loop."""
import ast,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=(ROOT/"scripts/fit_gbif_repaired_Artemisia_fixed_original_centers_v1.py").read_text()
NEW=(ROOT/"scripts/fit_gbif_repaired_reference47_fixed_original_centers_v1.py").read_text()
MANIFEST=json.loads((ROOT/"config/gbif_original_reference47_geometry_manifest_v1.json").read_text())
def fit_science_loop(s):
    a="    for m in (150,300,500):\n        background = backgrounds[m]"
    b="    predictions=pd.DataFrame(prediction_rows)"
    assert s.count(a)==1 and s.count(b)==1
    return s[s.index(a):s.index(b)]

class Reference47FixedCentersModel(unittest.TestCase):
    def test_model_cv_fit_scoring_loop_unchanged(self):
        self.assertEqual(fit_science_loop(BASE),fit_science_loop(NEW))
        ast.parse(NEW)
    def test_all_frozen_reference_taxa_supported_without_selection(self):
        self.assertEqual(len(MANIFEST["entries"]),47)
        self.assertIn('panel != "successor" or not 0 <= taxon_index < 47',NEW)
        self.assertIn('"results/gbif_repaired_reference47_thinning_v1.json"',NEW)
        self.assertIn('reference_entry["index"] != taxon_index',NEW)
        self.assertIn('prior_taxon["original_signed_fit_artifact_id"] != reference_entry["original_fit_artifact_id"]',NEW)
    def test_geometry_and_m_frame_identifiers_required(self):
        for x in (
            'ORIGINAL_SIGNED_REFERENCE_GEOMETRY_EXACTLY_REPRODUCED',
            'original_qualification_artifact_id',
            'original_fit_artifact_id',
            'center_npy_sha256',
            'reconstructed_center_sha256',
            'original_comparison_frame_sha256_by_M',
            'observed_manifest != recovered["current_manifest_sha256"]',
        ):self.assertIn(x,NEW)
    def test_no_q95_or_biological_outcomes_open(self):
        for x in (
            '"paired_discordance_computed":False',
            '"reference_ceiling_opened_or_read":False',
            '"heldout_pairing_opened":False',
            '"process_knockout_computed":False',
            '"counts_as_empirical_conclusion":False',
        ):self.assertIn(x,NEW)
if __name__=="__main__":unittest.main()
