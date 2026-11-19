"""No-network source-mode raw restoration imbalance and holdout contrast guards."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from summarize_gbif_restored510_source_imbalance_v1 import audit, fraction


class RawMissing20Tests(unittest.TestCase):
    def test_retro_source_only_denominators(self):
        out=audit()
        held=out["panels"]["heldout12"]
        ref=out["panels"]["reference47"]
        self.assertEqual(held["newly_restored_raw_present_records_by_mode"]["HUMAN_OBSERVATION"],15329)
        self.assertEqual(held["newly_restored_raw_present_records_by_mode"]["PRESERVED_SPECIMEN"],2688)
        self.assertEqual(ref["newly_restored_raw_present_records_by_mode"]["HUMAN_OBSERVATION"],335772)
        self.assertEqual(ref["newly_restored_raw_present_records_by_mode"]["PRESERVED_SPECIMEN"],19058)
        self.assertEqual(len(out["heldout12_taxon_source_contrasts"]),12)
        self.assertTrue(out["frozen_original_Level_A_unchanged"])
        self.assertEqual(out["empirical_ledger_increment"],0)

    def test_source_restoration_not_uniform_across_taxa(self):
        out=audit()
        self.assertEqual(out["notable_heldout"]["largest_human_restoration_fraction_taxon"],"Artemisia tridentata")
        self.assertEqual(out["notable_heldout"]["largest_preserved_restoration_fraction_taxon"],"Abies lasiocarpa")
        x={z["taxon"]:z for z in out["heldout12_taxon_source_contrasts"]}
        self.assertGreater(x["Artemisia tridentata"]["human_minus_preserved_fraction_pp"],10)
        self.assertLess(x["Abies lasiocarpa"]["human_minus_preserved_fraction_pp"],-5)

    def test_invalid_undefined_raw_counts_fail_closed(self):
        with self.assertRaises(ValueError):
            fraction(0,5)
        with self.assertRaises(ValueError):
            fraction(100,-1)


if __name__=="__main__":
    unittest.main()
