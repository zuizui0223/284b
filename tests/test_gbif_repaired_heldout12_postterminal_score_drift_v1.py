"""Signed source-version model-score and q95 comparison is postterminal-only."""
import ast,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_gbif_repaired_heldout12_postterminal_score_drift_v1 import summary_delta,keyed,cell_key,opened

class SignedPostterminalSourceScoreDrift(unittest.TestCase):
    def test_delta_summary_has_explicit_counts_and_direction(self):
        s=summary_delta([-0.5,-0.2,0,0.1,0.4])
        self.assertEqual((s["n"],s["positive_count"],s["negative_count"],s["zero_with_tolerance_1e_12_count"]),(5,2,2,1))
        self.assertEqual(s["median"],0)
        self.assertEqual(s["minimum"],-0.5)
        self.assertEqual(s["maximum"],0.4)
    def test_nonfinite_or_empty_shift_fails(self):
        for x in ([],[float("nan")],[float("inf")]):
            with self.assertRaises(RuntimeError):summary_delta(x)
    def test_duplicate_cell_rejected(self):
        rows=[{"taxon":"x","M_km":"150","procedure":"p"}]*2
        with self.assertRaises(RuntimeError):keyed(rows,cell_key)
    def test_only_explicit_booleans_can_open(self):
        self.assertTrue(opened({"paired_prediction_surface_opened":"True"}))
        self.assertFalse(opened({"paired_prediction_surface_opened":"False"}))
        with self.assertRaises(RuntimeError):opened({"paired_prediction_surface_opened":""})
    def test_only_descriptive_no_new_endpoint_is_authored(self):
        s=(ROOT/"scripts/audit_gbif_repaired_heldout12_postterminal_score_drift_v1.py").read_text()
        ast.parse(s)
        self.assertIn('"scientific_model_or_q95_recalculated_in_this_audit":False',s)
        self.assertIn('"postfreeze_source_repair_is_independent_replication":False',s)
        self.assertIn('"empirical_ledger_increment":0',s)
        self.assertIn('"robustness_does_not_pass_full_283_cell_coverage_rule":True',s)

if __name__=="__main__":unittest.main()
