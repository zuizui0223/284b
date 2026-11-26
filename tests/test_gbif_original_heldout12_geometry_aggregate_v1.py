"""Require exactly original 12 spatial geometry receipts, never repaired outcome."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from aggregate_gbif_original_heldout12_geometry_v1 import aggregate

class OriginalHeldout12Aggregation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/"config/gbif_original_heldout12_geometry_manifest_v1.json").read_text())
        h="1"*64
        cls.receipts=[{
           "schema":"284b.gbif_original_heldout12_center_reconstruction.v1",
           "status":"ORIGINAL_SIGNED_HELDOUT_GEOMETRY_EXACTLY_REPRODUCED",
           "taxon_index":e["index"],"taxon":e["taxon"],
           "historical_specieskey":e["historical_specieskey"],
           "original_qualification_artifact_id":e["original_qualification_artifact_id"],
           "original_fit_artifact_id":e["original_fit_artifact_id"],
           "historical_source_manifest_sha256":cls.manifest["original_source_manifest_sha256"],
           "historical_source_parquet_count":9705,
           "original_center_sha256":h,"reconstructed_center_sha256":h,
           "original_pooled_geometry_cells":100,
           "original_source_thinned_counts":e["original_source_thinned_counts"],
           "original_comparison_frame_sha256_by_M":{"150":h,"300":h,"500":h},
           "center_npy_sha256":h,
           "source_rows_or_coordinates_exported":False,"repaired_model_fit_performed":False,
           "paired_discordance_computed":False,"reference_q95_opened":False,
           "repaired_heldout_endpoint_opened":False,"neon_field_outcomes_read":False,
           "empirical_ledger_increment":0
        } for e in cls.manifest["entries"]]
    def test_all_12_only_source(self):
        x=aggregate(self.manifest,self.receipts)
        self.assertEqual(x["original_heldout_geometry_exactly_reproduced"],12)
        self.assertEqual(x["repaired_source_heldout_model_refits_completed"],0)
        self.assertEqual(x["submission_status"],"HOLD")
        self.assertEqual(set(x["taxa"][0]["original_comparison_frame_sha256_by_M"]),{"150","300","500"})
    def test_missing_duplicate_and_taxon_substitution_stop(self):
        with self.assertRaises(RuntimeError):aggregate(self.manifest,self.receipts[:-1])
        r=copy.deepcopy(self.receipts);r[1]["taxon_index"]=0
        with self.assertRaises(RuntimeError):aggregate(self.manifest,r)
        r=copy.deepcopy(self.receipts);r[1]["taxon"]="invented"
        with self.assertRaises(RuntimeError):aggregate(self.manifest,r)
    def test_center_changed_or_q95_preopened_stop(self):
        r=copy.deepcopy(self.receipts);r[0]["reconstructed_center_sha256"]="2"*64
        with self.assertRaises(RuntimeError):aggregate(self.manifest,r)
        r=copy.deepcopy(self.receipts);r[0]["reference_q95_opened"]=True
        with self.assertRaises(RuntimeError):aggregate(self.manifest,r)
if __name__=="__main__":unittest.main()
