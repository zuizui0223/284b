"""59 fixed-taxon GBIF source-repair metadata and fail-closed endpoint tests."""
from pathlib import Path
import copy,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_gbif_repaired_59taxa_source_balance_v1 import extract,build,summarize

class Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h=json.loads((ROOT/"results/gbif_repaired_heldout12_thinning_v1.json").read_text())
        cls.r=json.loads((ROOT/"results/gbif_repaired_reference47_thinning_v1.json").read_text())
    def test_reproduce_original_source_only_59_taxa(self):
        o,rows=build(self.h,self.r,{"heldout":"test","reference":"test"})
        total=o["panels"]["combined"]
        self.assertEqual(len(rows),59)
        self.assertEqual(total["taxa"],59)
        self.assertEqual(total["per_mode"]["specimen"]["original"],103633)
        self.assertEqual(total["per_mode"]["specimen"]["repaired"],107357)
        self.assertEqual(total["per_mode"]["human"]["original"],1010173)
        self.assertEqual(total["per_mode"]["human"]["repaired"],1033261)
        self.assertEqual(total["taxa_with_any_source_increment_at_least_5pct"],13)
        self.assertEqual(total["human_to_specimen_ratio_up"],34)
        self.assertEqual(total["human_to_specimen_ratio_down"],25)
        self.assertEqual(total["max_specimen_gain_taxon"],"Artemisia filifolia")
        self.assertIs(o["repaired_model_predictions_read"],False)
        self.assertEqual(o["empirical_ledger_increment"],0)
    def test_rejects_status_or_source_parity_mismatch(self):
        a=copy.deepcopy(self.h);a["status"]="not_verified"
        with self.assertRaises(ValueError):extract("heldout",a)
        a=copy.deepcopy(self.r);a["completed_and_verified_shards"]=7
        with self.assertRaises(ValueError):extract("reference",a)
        a=copy.deepcopy(self.h);a["per_taxon_source_mode_result"][0]["repaired_source_thinned_presence"]["HUMAN_OBSERVATION"]+=1
        with self.assertRaises(ValueError):extract("heldout",a)
    def test_rejects_wrong_scientific_boundary_or_taxon_duplicates(self):
        a=copy.deepcopy(self.h);a["NEON_plot_species_outcomes_read"]=True
        with self.assertRaises(ValueError):extract("heldout",a)
        a=copy.deepcopy(self.r);a["original_24_calibration_q95_refitted"]=True
        with self.assertRaises(ValueError):extract("reference",a)
        a=copy.deepcopy(self.h);a["per_taxon_source_mode_result"][1]["taxon"]=a["per_taxon_source_mode_result"][0]["taxon"]
        with self.assertRaises(ValueError):extract("heldout",a)
    def test_weighted_and_equal_taxon_weight_distinct(self):
        rows=[
            dict(old_specimen=10,new_specimen=11,old_human=20,new_human=21,
                 specimen_fraction=.1,human_fraction=.05,balance_multiplier=21/22,taxon="a"),
            dict(old_specimen=10,new_specimen=10,old_human=20,new_human=24,
                 specimen_fraction=0.,human_fraction=.2,balance_multiplier=24/20,taxon="b")]
        v=summarize(rows)
        self.assertEqual(v["taxa_with_any_source_increment_at_least_5pct"],2)
        self.assertEqual(v["human_to_specimen_ratio_up"],1)
        self.assertEqual(v["human_to_specimen_ratio_down"],1)
        self.assertAlmostEqual(v["per_mode"]["specimen"]["weighted_increment_pct"],5)
        self.assertAlmostEqual(v["per_mode"]["human"]["weighted_increment_pct"],12.5)

if __name__=="__main__":unittest.main()
