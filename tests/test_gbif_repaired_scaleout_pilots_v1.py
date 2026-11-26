"""Frozen pilot identity, incompleteness and endpoint-gate tests."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from verify_gbif_repaired_scaleout_pilots_v1 import check

class ScaleoutPilotGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=[json.loads((ROOT/p).read_text()) for p in (
            "results/gbif_repaired_Artemisia_fixedcenters_fit_contract_v1.json",
            "results/gbif_repaired_Artemisia_single_source_drift_v1.json",
            "results/gbif_original_reference_Abies_grandis_centers_v1.json",
            "results/gbif_repaired_heldout12_thinning_v1.json",
            "results/gbif_repaired_reference47_thinning_v1.json")]
    def test_two_completed_pilots_only(self):
        o=check(*self.data)
        self.assertEqual(o["heldout_pilot"]["sealed_cells"],48)
        self.assertEqual(o["reference_geometry_pilot"]["pooled_cells"],7244)
        self.assertEqual(o["source_inputs_audited"]["reference_taxa"],47)
        self.assertFalse(o["full_reference_model_refit_complete"])
        self.assertFalse(o["q95_recalibrated"])
        self.assertEqual(o["submission_status"],"HOLD")
    def test_fail_closed_on_corrupted_model_fit(self):
        d=copy.deepcopy(self.data);d[0]["sealed_fit_cells"]=47
        with self.assertRaises(ValueError):check(*d)
        d=copy.deepcopy(self.data);d[0]["paired_discordance_computed"]=True
        with self.assertRaises(ValueError):check(*d)
    def test_fail_closed_on_reference_geometry_and_source_audit(self):
        d=copy.deepcopy(self.data);d[2]["recomputed_centers_SHA256"]="bad"
        with self.assertRaises(ValueError):check(*d)
        d=copy.deepcopy(self.data);d[4]["completed_and_verified_shards"]=7
        with self.assertRaises(ValueError):check(*d)
    def test_fail_closed_on_prediction_receipt_mismatch(self):
        d=copy.deepcopy(self.data);d[1]["repaired_model_prediction_SHA256"]="bad"
        with self.assertRaises(ValueError):check(*d)

if __name__=="__main__":unittest.main()
