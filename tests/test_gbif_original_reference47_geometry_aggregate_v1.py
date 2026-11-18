"""Synthetic complete/incomplete 47-reference original geometry aggregation tests."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from aggregate_gbif_original_reference47_geometry_v1 import aggregate

class Reference47GeometryAggregation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/"config/gbif_original_reference47_geometry_manifest_v1.json").read_text())
        SHA="1"*64
        cls.receipts=[{
            "schema":"284b.gbif_original_reference47_center_reconstruction.v1",
            "status":"ORIGINAL_SIGNED_REFERENCE_GEOMETRY_EXACTLY_REPRODUCED",
            "taxon_index":e["index"],"taxon":e["taxon"],
            "historical_specieskeys":e["historical_specieskeys"],
            "original_qualification_artifact_id":e["original_qualification_artifact_id"],
            "original_fit_artifact_id":e["original_fit_artifact_id"],
            "historical_source_manifest_sha256":cls.manifest["original_source_manifest_sha256"],
            "historical_source_parquet_count":9705,
            "original_center_sha256":SHA,
            "reconstructed_center_sha256":SHA,
            "original_common_pooled_geometry_cells":100,
            "center_npy_sha256":SHA,
            "original_comparison_frame_sha256_by_M":{"150":SHA,"300":SHA,"500":SHA},
            "original_source_thinned_counts":{"PRESERVED_SPECIMEN":100,"HUMAN_OBSERVATION":100},
            "source_rows_or_coordinates_exported":False,
            "model_refit_performed":False,"paired_discordance_computed":False,
            "reference_q95_computed":False,"heldout12_opened":False,
            "neon_field_outcomes_read":False,"empirical_ledger_increment":0,
        } for e in cls.manifest["entries"]]
    def test_47_frozen_receipts_only(self):
        o=aggregate(self.manifest,self.receipts)
        self.assertEqual(o["reference_taxa_original_geometry_exactly_reproduced"],47)
        self.assertEqual(o["repaired_source_reference_model_refits_completed"],0)
        self.assertFalse(o["calibration_reference_q95_opened"])
        self.assertEqual(o["submission_status"],"HOLD")
    def test_fail_closed_missing_duplicate_and_changed_taxon(self):
        with self.assertRaises(RuntimeError):aggregate(self.manifest,self.receipts[:-1])
        r=copy.deepcopy(self.receipts);r[-1]["taxon_index"]=0
        with self.assertRaises(RuntimeError):aggregate(self.manifest,r)
        r=copy.deepcopy(self.receipts);r[-1]["taxon"]="not taxon"
        with self.assertRaises(RuntimeError):aggregate(self.manifest,r)
    def test_fail_closed_changed_center_and_opened_q95(self):
        r=copy.deepcopy(self.receipts);r[1]["reconstructed_center_sha256"]="2"*64
        with self.assertRaises(RuntimeError):aggregate(self.manifest,r)
        r=copy.deepcopy(self.receipts);r[1]["reference_q95_computed"]=True
        with self.assertRaises(RuntimeError):aggregate(self.manifest,r)
if __name__=="__main__":unittest.main()
