"""One-shot repaired-source heldout sensitivity: preserve the historical 283 opened cells."""
import copy,hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from evaluate_gbif_repaired_heldout12_source_completeness_v1 import (
    verify_preopening,assess_original_cell_coverage
)

def valid():
    original={
     "endpoint_id":"same_target_cross_source_reproducibility_heldout12_core19_v0_4",
     "result_version":"product_b_same_target_heldout_final_core19_v0.4",
     "heldout":{"taxa":12,"cells_expected":288,"paired_crosscheck_attention_required":0,
                "paired_prediction_surfaces_opened_cells":283},
     "counts_as_empirical_conclusion":True,"empirical_ledger_increment":1,
     "do_not_recount_same_endpoint":True
    }
    rf={
     "schema":"284b.gbif_repaired_reference47_source_fit_audit.v1",
     "status":"ALL_47_REPAIRED_REFERENCE_SOURCE_FITS_INTEGRITY_VERIFIED_NO_Q95",
     "reference_taxa_verified":47,"fit_cells_expected":2256,
     "calibration_24_q95_opened":False,"heldout12_paired_discordance_opened":False,
     "empirical_ledger_increment":0
    }
    hf={
     "schema":"284b.gbif_repaired_heldout12_source_fit_audit.v1",
     "status":"ALL_12_REPAIRED_HELDOUT_SOURCE_MODELS_INTEGRITY_VERIFIED_PAIRING_CLOSED",
     "heldout_taxa_verified":12,"source_fit_cells_expected":576,
     "source_fit_cells_sealed":574,"source_fit_cells_unresolved":2,
     "reference_q95_opened":False,"heldout12_paired_discordance_opened":False,
     "empirical_ledger_increment":0
    }
    rs={
     "result_version":"284b.gbif_repaired_reference47_q95_calibration.v1",
     "source_arm":"repaired_2026-08-01_10215_parquet_files",
     "reference_cells_expected":24,"reference_cells_frozen":24,
     "reference_cells_unresolved":0,"full_reference_matrix_available":True,
     "minimum_distinct_calibration_taxa_per_reference_cell":30,
     "reference_quantile":0.95,"quantile_method":"nearest_rank",
     "heldout12_repaired_source_outcomes_opened":False,
     "heldout_12_paired_discordance_read":False,"process_knockout_opened":False,
     "empirical_ledger_increment":0
    }
    return rs,rf,hf,original

class RestoreSourceHeldoutSensitivity(unittest.TestCase):
    def test_signatures_and_24_q95_gate(self):
        v=valid()
        self.assertTrue(verify_preopening(*v,"1"*64))
    def test_reference_underqualified_stops_before_heldout(self):
        v=list(valid());v[0]["reference_cells_frozen"]=23
        with self.assertRaises(RuntimeError):verify_preopening(*v,"1"*64)
        v=list(valid());v[0]["heldout12_repaired_source_outcomes_opened"]=True
        with self.assertRaises(RuntimeError):verify_preopening(*v,"1"*64)
        v=list(valid());v[1]["reference_taxa_verified"]=46
        with self.assertRaises(RuntimeError):verify_preopening(*v,"1"*64)
    def test_missing_heldout_or_altered_history_stops(self):
        v=list(valid());v[2]["source_fit_cells_unresolved"]=3
        with self.assertRaises(RuntimeError):verify_preopening(*v,"1"*64)
        v=list(valid());v[3]["heldout"]["paired_prediction_surfaces_opened_cells"]=282
        with self.assertRaises(RuntimeError):verify_preopening(*v,"1"*64)
        v=list(valid());v[3]["do_not_recount_same_endpoint"]=False
        with self.assertRaises(RuntimeError):verify_preopening(*v,"1"*64)
    def test_repaired_source_robust_requires_coverage_of_all_283(self):
        old={("x",i,"method") for i in range(283)}
        stable=assess_original_cell_coverage(old,old,set())
        self.assertTrue(stable["robust"])
        self.assertEqual(stable["status"],"historical_0of12_robust_to_repaired_source")
        reduced=assess_original_cell_coverage(old,old-{("x",0,"method")},set())
        self.assertFalse(reduced["robust"])
        self.assertEqual(len(reduced["lost"]),1)
        self.assertEqual(reduced["status"],"repaired_source_no_attention_but_original_283_cell_coverage_decreased")
        attention=assess_original_cell_coverage(old,old,{"x"})
        self.assertFalse(attention["robust"])
        self.assertEqual(attention["status"],"historical_0of12_not_robust_to_repaired_source")
    def test_historical_0_of12_not_double_counted_as_independent_endpoint(self):
        c=(ROOT/"scripts/evaluate_gbif_repaired_heldout12_source_completeness_v1.py").read_text()
        for expected in (
            '"terminal_class":"postfreeze_source_completeness_sensitivity"',
            '"counts_as_empirical_conclusion":False',
            '"counts_as_empirical_evidence":False',
            '"empirical_ledger_increment":0',
            '"historical_result_replaced":False',
            '"historical_signed_288_cells_sha256"',
            'reviewed.main()',
        ):self.assertIn(expected,c)

if __name__=="__main__":unittest.main()
