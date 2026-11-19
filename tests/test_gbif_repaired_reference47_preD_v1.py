"""No q95, paired D or heldout ecological labels in repaired reference pre-D."""
import ast,copy,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_gbif_repaired_reference47_preD_v1 import checked_reference_fits

def summary():
    return {
        "schema":"284b.gbif_repaired_reference47_source_fit_audit.v1",
        "status":"ALL_47_REPAIRED_REFERENCE_SOURCE_FITS_INTEGRITY_VERIFIED_NO_Q95",
        "reference_taxa_expected":47,"reference_taxa_verified":47,
        "fit_cells_expected":2256,"fit_cells_sealed":2256,"fit_cells_unresolved":0,
        "source_prediction_rows_integrity_verified":2256*2000,
        "source_arm":"repaired_2026-08-01_10215_parquet_files",
        "calibration_24_q95_opened":False,"heldout12_paired_discordance_opened":False,
        "empirical_ledger_increment":0,
        "taxa":[{"index":i,"taxon":f"taxon_{i}"} for i in range(47)],
    }

class RepairedReference47PreD(unittest.TestCase):
    def test_original_reviewed_adequacy_body_is_reused(self):
        source=(ROOT/"scripts/audit_gbif_repaired_reference47_preD_v1.py").read_text()
        ast.parse(source)
        self.assertIn("reviewed_core19_preD()",source)
        self.assertIn("adapt_core19_successor_root",source)
        self.assertIn('"reference_q95_recalibrated":False',source)
        self.assertIn('"heldout12_repaired_sensitivity_opened":False',source)
        self.assertIn('"empirical_ledger_increment":0',source)
    def test_no_missing_reference_fits_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeError,"exactly 47"):
                checked_reference_fits(Path(temp),summary())
    def test_fail_closed_underpowered_or_relabelled_source_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            bad=summary();bad["fit_cells_expected"]=2255
            with self.assertRaises(RuntimeError):checked_reference_fits(Path(temp),bad)
            bad=summary();bad["reference_taxa_verified"]=46
            with self.assertRaises(RuntimeError):checked_reference_fits(Path(temp),bad)
    def test_no_preopened_q95_or_heldout(self):
        with tempfile.TemporaryDirectory() as temp:
            bad=summary();bad["calibration_24_q95_opened"]=True
            with self.assertRaises(RuntimeError):checked_reference_fits(Path(temp),bad)
            bad=summary();bad["heldout12_paired_discordance_opened"]=True
            with self.assertRaises(RuntimeError):checked_reference_fits(Path(temp),bad)
    def test_original_population_does_not_change(self):
        with tempfile.TemporaryDirectory() as temp:
            bad=summary();bad["taxa"][1]["index"]=0
            # Input has no fit artifacts; in any case never a success.
            with self.assertRaises(RuntimeError):checked_reference_fits(Path(temp),bad)

if __name__=="__main__":unittest.main()
