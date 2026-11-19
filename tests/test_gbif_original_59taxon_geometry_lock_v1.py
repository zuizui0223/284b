"""Fail-closed original 59-taxon geometry provenance lock."""
import copy,hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from verify_gbif_original_59taxon_geometry_lock_v1 import (
    lock,REFERENCE_RECEIPT_SHA,HELDOUT_RECEIPT_SHA
)

class Original59TaxonGeometryLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r=ROOT/"results/gbif_original_reference47_geometry_complete_v1.json"
        h=ROOT/"results/gbif_original_heldout12_geometry_complete_v1.json"
        cls.r=json.loads(r.read_text())
        cls.h=json.loads(h.read_text())
        assert hashlib.sha256(r.read_bytes()).hexdigest()==REFERENCE_RECEIPT_SHA
        assert hashlib.sha256(h.read_bytes()).hexdigest()==HELDOUT_RECEIPT_SHA

    def test_exact_complete_historical_59_and_no_new_outcome(self):
        d=lock(self.r,self.h,REFERENCE_RECEIPT_SHA,HELDOUT_RECEIPT_SHA)
        self.assertEqual(d["taxa_total"],59)
        self.assertEqual(d["reference_taxa_original_spatial_geometry_complete"],47)
        self.assertEqual(d["heldout_taxa_original_spatial_geometry_complete"],12)
        self.assertEqual(d["unique_spatial_center_hashes"],59)
        self.assertEqual(d["unique_taxon_names"],59)
        self.assertTrue(d["original_reference_and_heldout_no_taxon_overlap"])
        self.assertFalse(d["repaired_reference_q95_recalibrated"])
        self.assertEqual(d["empirical_ledger_increment"],0)

    def test_fail_closed_on_wrong_receipt_sha(self):
        with self.assertRaises(RuntimeError):
            lock(self.r,self.h,"wrong",HELDOUT_RECEIPT_SHA)

    def test_fail_closed_on_panel_overlap_and_missing_original_frames(self):
        h=copy.deepcopy(self.h)
        h["taxa"][0]["taxon"]=self.r["reference_taxa"][0]["taxon"]
        with self.assertRaises(RuntimeError):
            lock(self.r,h,REFERENCE_RECEIPT_SHA,HELDOUT_RECEIPT_SHA)
        h=copy.deepcopy(self.h)
        h["taxa"][0]["original_comparison_frame_sha256_by_M"].pop("500")
        with self.assertRaises(RuntimeError):
            lock(self.r,h,REFERENCE_RECEIPT_SHA,HELDOUT_RECEIPT_SHA)

    def test_fail_closed_on_preopened_repaired_reference_or_heldout(self):
        r=copy.deepcopy(self.r)
        r["calibration_reference_q95_opened"]=True
        with self.assertRaises(RuntimeError):
            lock(r,self.h,REFERENCE_RECEIPT_SHA,HELDOUT_RECEIPT_SHA)
        h=copy.deepcopy(self.h)
        h["repaired_12_heldout_paired_outcomes_opened"]=True
        with self.assertRaises(RuntimeError):
            lock(self.r,h,REFERENCE_RECEIPT_SHA,HELDOUT_RECEIPT_SHA)

if __name__=="__main__":
    unittest.main()
