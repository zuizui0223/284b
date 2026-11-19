"""Repaired source 47-reference q95 gate: outcomes open only after n>=30 pre-D."""
import ast,copy,hashlib,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from calibrate_gbif_repaired_reference47_q95_v1 import check_calibration_gate

def adequate():
    fit_raw=b"signed-frozen-fit-audit"
    fit={"schema":"284b.gbif_repaired_reference47_source_fit_audit.v1",
         "status":"ALL_47_REPAIRED_REFERENCE_SOURCE_FITS_INTEGRITY_VERIFIED_NO_Q95",
         "reference_taxa_verified":47,"fit_cells_expected":2256,
         "calibration_24_q95_opened":False,"heldout12_paired_discordance_opened":False}
    rows=[{"M_km":m,"procedure":f"p_{i}","discordance_opening_authorized":True,
           "eligible_distinct_taxa_pre_discordance":40}
          for m in [150,300,500] for i in range(8)]
    feas={
         "result_version":"284b.gbif_repaired_reference47_preD_feasibility.v1",
         "core19_contract_version":"product_b_same_target_core19_requalification_v0.4",
         "repaired_GBIF_source_arm":"repaired_2026-08-01_10215_parquet_files",
         "repaired_source_fit_audit_sha256":hashlib.sha256(fit_raw).hexdigest(),
         "repaired_source_fit_taxa":47,"repaired_source_fit_cells":2256,
         "sampling_pass_taxa":47,"candidate_pair_cells":1128,"reference_cells_expected":24,
         "minimum_eligible_taxa_per_procedure_M":30,
         "reference_cells_authorized_to_open_discordance":24,
         "reference_cells_unresolved_pre_discordance":0,
         "paired_prediction_surfaces_read":False,"schoener_d_computed":False,
         "reference_ceiling_computed":False,"reference_q95_recalibrated":False,
         "heldout_12_paired_discordance_read":False,
         "heldout12_repaired_sensitivity_opened":False,
         "empirical_ledger_increment":0,"reference_cells":rows}
    return feas,fit,fit_raw

class RepairedReferenceQ95Gate(unittest.TestCase):
    def test_all_24_are_predeclared_authorized(self):
        f,g,raw=adequate()
        s=check_calibration_gate(f,b"feasibility",g,raw)
        self.assertEqual(s,hashlib.sha256(b"feasibility").hexdigest())
        source=(ROOT/"scripts/calibrate_gbif_repaired_reference47_q95_v1.py").read_text()
        ast.parse(source)
        self.assertIn("reviewed_calibrate()",source)
        self.assertIn('"heldout12_repaired_source_outcomes_opened":False',source)
    def test_one_underpowered_reference_stops_before_d(self):
        f,g,raw=adequate()
        f["reference_cells"][0]["eligible_distinct_taxa_pre_discordance"]=29
        with self.assertRaises(RuntimeError):check_calibration_gate(f,b"feasibility",g,raw)
        f,g,raw=adequate()
        f["reference_cells_authorized_to_open_discordance"]=23
        with self.assertRaises(RuntimeError):check_calibration_gate(f,b"feasibility",g,raw)
    def test_preopened_source_or_heldout_stops(self):
        for field in ("schoener_d_computed","reference_ceiling_computed","heldout12_repaired_sensitivity_opened"):
            f,g,raw=adequate();f[field]=True
            with self.assertRaises(RuntimeError):check_calibration_gate(f,b"feasibility",g,raw)
    def test_reference_manifest_and_integrity_stops(self):
        f,g,raw=adequate();g["fit_cells_expected"]=2255
        with self.assertRaises(RuntimeError):check_calibration_gate(f,b"feasibility",g,raw)
        f,g,raw=adequate();f["repaired_source_fit_audit_sha256"]="bad"
        with self.assertRaises(RuntimeError):check_calibration_gate(f,b"feasibility",g,raw)
    def test_no_posthoc_procedure_or_taxon_selection(self):
        f,g,raw=adequate();f["reference_cells"][3]["procedure"]=f["reference_cells"][2]["procedure"]
        with self.assertRaises(RuntimeError):check_calibration_gate(f,b"feasibility",g,raw)
if __name__=="__main__":unittest.main()
