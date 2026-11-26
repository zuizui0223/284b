"""Heldout source adequacy flip diagnostic: original 4-fold gate remains unchanged."""
import csv,io,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_gbif_repaired_heldout12_postterminal_cv_switch_v1 import load_folds,adequacy

class SignedAdequacyFlip(unittest.TestCase):
    def test_original_four_fold_adequacy_floor_reused(self):
        cfg=json.loads((ROOT/"config/product_b_same_target_source_model_fit_contract_v0_1.json").read_text())
        a=cfg["prediction_adequacy"]
        self.assertEqual((a["outer_folds"],a["chance_auc"],a["minimum_auc_margin"],a["auc_sem_multiplier"]),
                         (4,0.5,0.01,1))
        passed=adequacy([{"presence_rank":str(x)} for x in (0.70,0.75,0.72,0.73)],a)
        failed=adequacy([{"presence_rank":str(x)} for x in (0.49,0.48,0.5,0.48)],a)
        self.assertTrue(passed.adequate)
        self.assertFalse(failed.adequate)
    def test_incomplete_fold_cannot_beadequate(self):
        cfg=json.loads((ROOT/"config/product_b_same_target_source_model_fit_contract_v0_1.json").read_text())["prediction_adequacy"]
        v=adequacy([{"presence_rank":"0.99"}],cfg)
        self.assertFalse(v.adequate)
        self.assertIn("outer_fold_evidence_incomplete",v.reasons)
    def test_duplicate_original_fold_stops(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"folds.csv"
            p.write_text("source,M_km,procedure,fold,presence_rank\nPRESERVED_SPECIMEN,150,p,0,0.7\nPRESERVED_SPECIMEN,150,p,0,0.8\n")
            with self.assertRaisesRegex(RuntimeError,"Duplicate outer-fold"):load_folds(p)
    def test_four_transition_keys_fixed_from_signed_postterminal_coverage(self):
        f=ROOT/"results/gbif_repaired_heldout12_postterminal_coverage_audit_v1.json"
        rows=json.loads(f.read_text())["transition_cells"]
        self.assertEqual(len(rows),4)
        self.assertEqual(sum(r["transition"]=="original_open_lost" for r in rows),1)
        self.assertEqual(sum(r["transition"]=="restored_newly_open" for r in rows),3)
        self.assertEqual({r["taxon"] for r in rows},
                         {"Nothofagus antarctica","Eucalyptus globulus","Larix laricina"})
if __name__=="__main__":unittest.main()
