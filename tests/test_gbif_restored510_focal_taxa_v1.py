"""Synthetic regression checks for raw 510-file restoration exposure."""
from collections import Counter
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_gbif_restored510_focal_taxa_v1 import aggregate_batch,NEON_VOUCHER


class RestoredSourceAccounting(unittest.TestCase):
    def test_counts_only_declared_modes_and_specieskeys(self):
        out=Counter()
        a={
           "specieskey":["GX2B","GX2B","JLB9"],
           "basisofrecord":["PRESERVED_SPECIMEN","HUMAN_OBSERVATION","HUMAN_OBSERVATION"],
           "occurrencestatus":["PRESENT","PRESENT","PRESENT"],
           "datasetkey":[NEON_VOUCHER,"other",None]
        }
        aggregate_batch(a,{"GX2B","JLB9"},out)
        self.assertEqual(out[("GX2B","PRESERVED_SPECIMEN","known_NEON_voucher_datasetkey")],1)
        self.assertEqual(out[("GX2B","HUMAN_OBSERVATION","raw_present")],1)
        self.assertEqual(out[("JLB9","HUMAN_OBSERVATION","missing_datasetkey")],1)

    def test_unlisted_species_or_basis_raises(self):
        bad={"specieskey":["other"],"basisofrecord":["PRESERVED_SPECIMEN"],
             "occurrencestatus":["PRESENT"],"datasetkey":["foo"]}
        with self.assertRaises(RuntimeError):
            aggregate_batch(bad,{"GX2B"},Counter())

    def test_unmatched_batch_fields_raise(self):
        bad={"specieskey":["GX2B"],"basisofrecord":["PRESERVED_SPECIMEN"],
             "occurrencestatus":[],"datasetkey":["foo"]}
        with self.assertRaises(ValueError):
            aggregate_batch(bad,{"GX2B"},Counter())


if __name__=="__main__":
    unittest.main()
