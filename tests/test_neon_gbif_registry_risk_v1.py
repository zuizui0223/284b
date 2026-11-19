"""NEON voucher publisher linkage audit without reading GBIF occurrence rows."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_neon_gbif_registry_risk_v1 import check_dataset_metadata

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/"config/neon_external_metadata_dependency_gate_v2.json").read_text())
KEY="3fed506c-d04f-4cd4-b373-bd602572f39b"


class SourceRegistryTests(unittest.TestCase):
    def test_publisher_link_confirms_risk_not_training_contamination(self):
        d={"key":KEY,
           "title":"NEON Biorepository Terrestrial Plant Collection (Herbarium Vouchers)",
           "created":"2020-05-22T10:22:13.000+0000","type":"OCCURRENCE",
           "doi":"10.15468/bmmg36"}
        a=check_dataset_metadata(d,b"{}",CFG)
        self.assertTrue(a["registered_on_or_before_source_snapshot"])
        self.assertFalse(a["confirmed_NEON_voucher_used_in_focal_model"])
        self.assertFalse(a["independence_from_NEON_data_verified"])
        self.assertFalse(a["gbif_occurrence_records_read"])
        self.assertEqual(a["empirical_ledger_increment"],0)

    def test_wrong_dataset_rejected(self):
        with self.assertRaises(ValueError):
            check_dataset_metadata({"key":"wrong","title":"NEON vouchers"},b"{}",CFG)
        with self.assertRaises(ValueError):
            check_dataset_metadata({"key":KEY,"title":"Other dataset"},b"{}",CFG)


if __name__=="__main__":
    unittest.main()
