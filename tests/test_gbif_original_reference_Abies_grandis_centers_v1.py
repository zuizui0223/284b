"""Guard original two-historical-key reference source geometry replay."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/"config/gbif_original_reference_centers_Abies_grandis_v1.json").read_text())
SCRIPT=(ROOT/"scripts/reconstruct_original_reference_Abies_grandis_centers_v1.py").read_text()


class OriginalRefCenterPilotTest(unittest.TestCase):
    def test_pinned_taxon_concept_and_original_ref_geometry(self):
        self.assertEqual(CFG["original_taxon"],"Abies grandis")
        self.assertEqual(CFG["original_index"],1)
        self.assertEqual(CFG["original_historical_specieskeys"],["2685361","8KCY"])
        self.assertEqual(CFG["original_common_pooled_cells"],7244)
        self.assertEqual(CFG["original_model_thinned_presence"],
                         {"PRESERVED_SPECIMEN":958,"HUMAN_OBSERVATION":6566})
        self.assertEqual(CFG["original_12block_centers_sha256"],
                         "9eb19bf125fdd06c5e2b9ef901c869c23db6cd9aa88feb1305dffed79ff37f7e")
        self.assertEqual(CFG["original_parquet_object_count"],9705)

    def test_two_historical_keys_same_target_and_no_model_fit(self):
        self.assertIn('from scripts.run_same_target_successor_layer1_fit_taxon import',SCRIPT)
        self.assertIn('ds.field("specieskey").isin(list(cfg["original_historical_specieskeys"]))',SCRIPT)
        self.assertIn('receipt.get("historical_specieskeys") != cfg["original_historical_specieskeys"]',SCRIPT)
        self.assertIn('"model_training_or_refitting_performed":False',SCRIPT)
        self.assertEqual(CFG["new_empirical_endpoint_count"],0)


if __name__=="__main__":
    unittest.main()
