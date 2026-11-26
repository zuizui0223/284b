"""Independent post-terminal audit, with fail-closed mutation tests.

No model fitting or new source-paired Schoener D is run. Reads only already
committed one-shot sensitivity output and original signed terminal receipt.
"""
import copy,csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_gbif_repaired_heldout12_postterminal_coverage_v1 import audit

class PostterminalOriginal283Coverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/"results/product_b_same_target_core19_v0_4_heldout_final_receipt.json").read_text())
        cls.final=json.loads((ROOT/"results/gbif_repaired_heldout12_sensitivity_v1.json").read_text())
        cls.ref=json.loads((ROOT/"results/gbif_repaired_reference47_q95_summary_v1.json").read_text())
        cls.raw=(ROOT/"results/gbif_repaired_heldout12_sensitivity_cells_v1.csv").read_bytes()
        cls.rows=list(csv.DictReader(cls.raw.decode("utf-8").splitlines()))

    def test_observed_one_shot_288_keys_and_283_cell_coverage(self):
        r=audit(self.old,self.final,self.rows,self.raw,self.ref)
        self.assertEqual(r["historical_opened_cells"],283)
        self.assertEqual(r["restored_opened_cells"],285)
        self.assertEqual(r["original_opened_retained"],282)
        self.assertEqual(r["original_opened_lost"],1)
        self.assertEqual(r["newly_opened_restored_cells"],3)
        self.assertEqual(r["q95_exceeding_restored_opened_cells"],0)
        self.assertFalse(r["historical_0_of_12_source_completeness_fully_robust"])
        self.assertEqual(r["submission_status"],"HOLD_FOR_SENSITIVITY_REVIEW")
        self.assertEqual(r["empirical_ledger_increment"],0)
        lost=[x for x in r["transition_cells"] if x["transition"]=="original_open_lost"]
        self.assertEqual(len(lost),1)
        self.assertEqual((lost[0]["taxon"],lost[0]["M_km"],lost[0]["procedure"]),
                         ("Nothofagus antarctica",150,"niche_forward|logit_l2_C0.1_degree1"))
        self.assertFalse(lost[0]["preserved_specimen_adequate"])

    def test_tampered_opening_flag_fails_exact_count(self):
        rows=copy.deepcopy(self.rows)
        changed=next(x for x in rows if x["paired_prediction_surface_opened"]=="True")
        changed["paired_prediction_surface_opened"]="False"
        with self.assertRaises(RuntimeError):audit(self.old,self.final,rows,self.raw,self.ref)

    def test_wrong_source_pdf_threshold_gate_rejected(self):
        f=copy.deepcopy(self.final)
        f["reference_cells_frozen"]=23
        with self.assertRaises(RuntimeError):audit(self.old,f,self.rows,self.raw,self.ref)
        ref=copy.deepcopy(self.ref)
        ref["reference_cells_frozen"]=23
        with self.assertRaises(RuntimeError):audit(self.old,self.final,self.rows,self.raw,ref)

    def test_tampered_historical_original_283_or_fingerprint_rejected(self):
        old=copy.deepcopy(self.old)
        old["heldout"]["paired_prediction_surfaces_opened_cells"]=282
        with self.assertRaises(RuntimeError):audit(old,self.final,self.rows,self.raw,self.ref)
        new=copy.deepcopy(self.final)
        new["historical_endpoint_fingerprint"]="changed"
        with self.assertRaises(RuntimeError):audit(self.old,new,self.rows,self.raw,self.ref)

    def test_no_premature_robustness_promotion_or_evidence_recount(self):
        new=copy.deepcopy(self.final)
        new["source_completeness_0_of_12_robust"]=True
        with self.assertRaises(RuntimeError):audit(self.old,new,self.rows,self.raw,self.ref)
        new=copy.deepcopy(self.final)
        new["empirical_ledger_increment"]=1
        with self.assertRaises(RuntimeError):audit(self.old,new,self.rows,self.raw,self.ref)

if __name__=="__main__":unittest.main()
