"""Original signed 47-reference geometry reconstruction stays frozen and pre-model."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from reconstruct_original_reference47_centers_v1 import select_signed_entry
class OriginalReference47Geometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((ROOT/"config/gbif_original_reference47_geometry_manifest_v1.json").read_text())
        cls.a=json.loads((ROOT/"results/gbif_repaired_reference47_thinning_v1.json").read_text())
    def test_all_47_signed_identity_mappings(self):
        self.assertEqual(len(self.m["entries"]),47)
        for i in range(47):
            e,a=select_signed_entry(self.m,self.a,i)
            self.assertEqual(e["historical_specieskeys"],a["historical_specieskeys"])
            self.assertTrue(e["original_fit_artifact_digest"].startswith("sha256:"))
        self.assertEqual(len({x["taxon"] for x in self.m["entries"]}),47)
        self.assertEqual(len({k for x in self.m["entries"] for k in x["historical_specieskeys"]}),
                         sum(len(x["historical_specieskeys"]) for x in self.m["entries"]))
    def test_original_Abies_reference_example_pinned(self):
        e,a=select_signed_entry(self.m,self.a,1)
        self.assertEqual(e["taxon"],"Abies grandis")
        self.assertEqual(e["historical_specieskeys"],["2685361","8KCY"])
        self.assertEqual(e["original_qualification_artifact_id"],10066646765)
        self.assertEqual(e["original_fit_artifact_id"],10090599087)
        self.assertEqual(e["original_fit_artifact_digest"],
                         "sha256:9a817480d8f023246fe3dc9fedee01a6bf4e95a05418d854937610d78e58c99b")
        self.assertEqual(a["original_signed_thinned_n"],{
            "PRESERVED_SPECIMEN":958,"HUMAN_OBSERVATION":6566})
    def test_fail_closed_on_entry_relabel_and_invalid_digest(self):
        m=copy.deepcopy(self.m);m["entries"][1]["taxon"]="not Abies"
        with self.assertRaises(RuntimeError):select_signed_entry(m,self.a,1)
        m=copy.deepcopy(self.m);m["entries"][1]["original_qualification_artifact_digest"]="bad"
        with self.assertRaises(RuntimeError):select_signed_entry(m,self.a,1)
    def test_reference_population_and_endpoint_guards(self):
        a=copy.deepcopy(self.a);a["original_24_calibration_q95_refitted"]=True
        with self.assertRaises(RuntimeError):select_signed_entry(self.m,a,1)
        a=copy.deepcopy(self.a);a["completed_and_verified_shards"]=7
        with self.assertRaises(RuntimeError):select_signed_entry(self.m,a,1)
        with self.assertRaises(ValueError):select_signed_entry(self.m,self.a,47)
        for field in ("full_model_refit","q95_computed","heldout_scores_opened","neon_field_outcomes_opened"):
            self.assertIs(self.m[field],False)
        self.assertEqual(self.m["empirical_ledger_increment"],0)
if __name__=="__main__":unittest.main()
