"""Offline checks for fixed 12-taxon original-vs-restored source-thinning audit."""
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_gbif_repaired_heldout12_thinning_v1 import check_raw_source_row_parity

CFG=json.loads((ROOT/"config/gbif_restored510_heldout12_source_thinning_v1.json").read_text())


class RepairedSourceAdmissionTests(unittest.TestCase):
    def test_twelve_signed_archive_entries_and_original_counts_pinned(self):
        e=CFG["all_12_original_taxa"]
        self.assertEqual(CFG["original_parquet_count"],9705)
        self.assertEqual(CFG["repaired_parquet_count"],10215)
        self.assertEqual(len(e),12)
        self.assertEqual([x["original_index"] for x in e],list(range(12)))
        self.assertEqual(len({x["fit_artifact_id"] for x in e}),12)
        self.assertEqual(CFG["empirical_ledger_increment"],0)
        self.assertFalse(CFG["NEON_plant_plot_outcomes_read"])
        self.assertFalse(CFG["do_not_retrain_models"] is False)

    def test_raw_source_count_additivity_integrity_check(self):
        entry=next(q for q in CFG["all_12_original_taxa"] if q["taxon"]=="Artemisia tridentata")
        expected={
            "PRESERVED_SPECIMEN":entry["original_raw_present_records_by_mode"]["PRESERVED_SPECIMEN"]+
                                   entry["restored_510_raw_present_records_by_mode"]["PRESERVED_SPECIMEN"],
            "HUMAN_OBSERVATION":entry["original_raw_present_records_by_mode"]["HUMAN_OBSERVATION"]+
                                entry["restored_510_raw_present_records_by_mode"]["HUMAN_OBSERVATION"],
        }
        counts={m:{"raw_scanned_records":n} for m,n in expected.items()}
        yes=check_raw_source_row_parity(entry,counts)
        self.assertTrue(all(z["matched"] for z in yes.values()))
        counts["HUMAN_OBSERVATION"]["raw_scanned_records"]-=1
        no=check_raw_source_row_parity(entry,counts)
        self.assertFalse(no["HUMAN_OBSERVATION"]["matched"])


if __name__=="__main__":
    unittest.main()
