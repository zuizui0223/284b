"""Reference47 repaired model source-fit integrity is a technical, not ecological, endpoint."""
import ast,copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from aggregate_gbif_repaired_reference47_source_fits_v1 import audit_taxon,audit_all

class RepairedReference47ModelAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((ROOT/"config/gbif_original_reference47_geometry_manifest_v1.json").read_text())
        cls.s=json.loads((ROOT/"results/gbif_repaired_reference47_thinning_v1.json").read_text())
    def test_source_inventory_preserves_47_exact_taxa(self):
        self.assertEqual(len(self.m["entries"]),47)
        self.assertEqual(len(self.s["fixed_taxon_input_deltas"]),47)
        self.assertEqual([e["index"] for e in self.m["entries"]],list(range(47)))
        self.assertEqual([e["taxon"] for e in self.m["entries"]],
                         [e["taxon"] for e in self.s["fixed_taxon_input_deltas"]])
        source=(ROOT/"scripts/aggregate_gbif_repaired_reference47_source_fits_v1.py").read_text()
        ast.parse(source)
        self.assertIn('"calibration_24_q95_opened":False',source)
        self.assertIn('"heldout12_paired_discordance_opened":False',source)
    def test_fail_closed_on_unverified_geometry(self):
        g={"status":"ALL_47_ORIGINAL_SIGNED_REFERENCE_GEOMETRIES_VERIFIED_NO_MODELS",
           "reference_taxa_original_geometry_exactly_reproduced":46}
        with self.assertRaises(RuntimeError):
            audit_all(self.m,g,self.s,ROOT/"none")
    def test_fail_closed_on_reference_taxon_substitution(self):
        m=copy.deepcopy(self.m)
        m["entries"][1]["index"]=0
        with self.assertRaises(RuntimeError):
            audit_all(m,{},self.s,ROOT/"none")
    def test_fail_closed_on_wrong_fit_contract_before_scores_read(self):
        e=self.m["entries"][1]
        source=self.s["fixed_taxon_input_deltas"][1]
        g={"original_center_sha256":"0"*64,
           "original_comparison_frame_sha256_by_M":{"150":"1"*64,"300":"2"*64,"500":"3"*64}}
        contract={"result_version":"wrong","taxon_index":1}
        with self.assertRaises(RuntimeError):
            audit_taxon(e,g,source,contract,[],ROOT/"none.parquet")
    def test_no_47_model_outcome_can_be_claimed_from_source_only(self):
        self.assertEqual(self.s["completed_and_verified_shards"],8)
        self.assertEqual(self.s["signed_original_fit_artifact_inputs_verified"],47)
        self.assertIs(self.s["original_24_calibration_q95_refitted"],False)
        self.assertEqual(self.s["empirical_ledger_increment"],0)
if __name__=="__main__":unittest.main()
