"""12 heldout repaired-source model audit is 576 cells, with no premature D."""
import ast,copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from aggregate_gbif_repaired_heldout12_source_fits_v1 import check_inputs,aggregate,audit_one

class Heldout12SourceFitAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/"config/gbif_original_heldout12_geometry_manifest_v1.json").read_text())
        cls.source=json.loads((ROOT/"results/gbif_repaired_heldout12_thinning_v1.json").read_text())
    def test_fixed_12_source_denominator(self):
        code=(ROOT/"scripts/aggregate_gbif_repaired_heldout12_source_fits_v1.py").read_text()
        ast.parse(code)
        self.assertIn('"source_fit_cells_expected":576',code)
        self.assertIn('"reference_q95_opened":False',code)
        self.assertIn('"heldout12_paired_discordance_opened":False',code)
        self.assertEqual(len(self.manifest["entries"]),12)
        self.assertEqual(len(self.source["per_taxon_source_mode_result"]),12)
    def test_missing_geometry_cannot_promote_heldout_fits(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):
                aggregate(self.manifest,{},self.source,Path(d))
    def test_fail_closed_changed_taxonomy_or_preopened_q95(self):
        geometry={
          "status":"ALL_12_ORIGINAL_SIGNED_HELDOUT_GEOMETRIES_VERIFIED_NO_REPAIRED_MODELS",
          "original_heldout_geometry_exactly_reproduced":12,
          "historical_source_manifest_sha256":self.manifest["original_source_manifest_sha256"],
          "repaired_source_heldout_model_refits_completed":0,
          "repaired_47_reference_q95_calibrated":False,
          "repaired_12_heldout_paired_outcomes_opened":False,
          "taxa":[{"index":i,"taxon":e["taxon"],"historical_specieskey":e["historical_specieskey"]}
                  for i,e in enumerate(self.manifest["entries"])]
        }
        check_inputs(self.manifest,geometry,self.source)
        g=copy.deepcopy(geometry);g["taxa"][0]["taxon"]="non-original"
        with self.assertRaises(RuntimeError):check_inputs(self.manifest,g,self.source)
        g=copy.deepcopy(geometry);g["repaired_47_reference_q95_calibrated"]=True
        with self.assertRaises(RuntimeError):check_inputs(self.manifest,g,self.source)
    def test_no_incomplete_model_contract_as_success(self):
        e=self.manifest["entries"][0]
        with self.assertRaises(RuntimeError):
            audit_one(e,{},self.source["per_taxon_source_mode_result"][0],
                      {"result_version":"unknown"},[],Path("/nonexistent"))
if __name__=="__main__":unittest.main()
