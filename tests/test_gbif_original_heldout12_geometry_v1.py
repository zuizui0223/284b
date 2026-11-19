"""Original fixed 12-heldout spatial geometry identity and no-outcome gates."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from reconstruct_original_heldout12_centers_v1 import frozen_entry

class Heldout12OriginalGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((ROOT/"config/gbif_original_heldout12_geometry_manifest_v1.json").read_text())
        cls.a=json.loads((ROOT/"results/gbif_repaired_heldout12_thinning_v1.json").read_text())
    def test_exact_original_12_heldout_selection(self):
        self.assertEqual(len(self.m["entries"]),12)
        for i in range(12):
            e,r=frozen_entry(self.m,self.a,i)
            self.assertEqual(e["index"],i)
            self.assertEqual(e["historical_specieskey"],r["original_specieskey"])
            self.assertEqual(e["original_source_thinned_counts"],r["original_signed_source_thinned_model_presence"])
        self.assertEqual(len({e["taxon"] for e in self.m["entries"]}),12)
        self.assertEqual(len({e["historical_specieskey"] for e in self.m["entries"]}),12)
    def test_original_Artemisia_pilot_provenance(self):
        e,r=frozen_entry(self.m,self.a,0)
        self.assertEqual(e["taxon"],"Artemisia tridentata")
        self.assertEqual(e["historical_specieskey"],"GX2B")
        self.assertEqual(e["original_qualification_artifact_id"],10065445666)
        self.assertEqual(e["original_fit_artifact_id"],10089523542)
        self.assertEqual(e["original_source_thinned_counts"],{
             "PRESERVED_SPECIMEN":3285,"HUMAN_OBSERVATION":4516})
    def test_fail_closed_taxon_key_change(self):
        m=copy.deepcopy(self.m);m["entries"][0]["historical_specieskey"]="wrong"
        with self.assertRaises(RuntimeError):frozen_entry(m,self.a,0)
        m=copy.deepcopy(self.m);m["entries"][0]["original_fit_artifact_digest"]="bad"
        with self.assertRaises(RuntimeError):frozen_entry(m,self.a,0)
    def test_fail_closed_incomplete_and_opened_outcomes(self):
        m=copy.deepcopy(self.m);m["frozen_taxon_count"]=11
        with self.assertRaises(RuntimeError):frozen_entry(m,self.a,0)
        a=copy.deepcopy(self.a);a["repaired_reference_q95_opened"]=True
        with self.assertRaises(RuntimeError):frozen_entry(self.m,a,0)
        with self.assertRaises(ValueError):frozen_entry(self.m,self.a,12)
    def test_geometry_only_not_premature_predictive_result(self):
        self.assertIs(self.m["full_repaired_model_refit"],False)
        self.assertIs(self.m["q95_computed"],False)
        self.assertIs(self.m["heldout_scores_opened"],False)
        self.assertEqual(self.m["empirical_ledger_increment"],0)

if __name__=="__main__":unittest.main()
