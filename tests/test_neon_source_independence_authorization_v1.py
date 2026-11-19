"""Prelabel source-lineage gate must not launder known NEON inputs into independence."""
import json
import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from authorize_neon_source_independence_v1 import assess_source_eligibility
P=json.loads((ROOT/"results/neon_original_gbif_historical_replay_v2.json").read_text())
V1=json.loads((ROOT/"config/neon_external_validation_preflight_v1.json").read_text())
R=json.loads((ROOT/"results/neon_release_site_month_inventory_v2.json").read_text())


class NEONSourceIndependenceTests(unittest.TestCase):
    def test_verified_2_voucher_rows_block_unqualified_independence(self):
        result=assess_source_eligibility(P,V1,R)
        self.assertEqual(result["verified_known_NEON_voucher_dataset_model_inputs"],2)
        self.assertEqual(result["state"],"CONFIRMED_NEON_VOUCHER_DATASET_IN_FROZEN_MODEL_SOURCE")
        self.assertFalse(result["authorization_to_open_NEON_plant_outcomes"])
        self.assertFalse(result["blanket_independence_from_all_NEON_derived_biological_materials"])
        self.assertFalse(result["exact_overlap_with_proposed_NEON_plot_bout_labels_established"])
        self.assertEqual(result["empirical_ledger_increment"],0)

    def test_zero_known_key_still_not_prove_independence(self):
        changed=json.loads(json.dumps(P))
        changed["known_NEON_training_rows_in_thinned_sources"]=0
        changed["source_counts"]["PRESERVED_SPECIMEN"]["source_thinned_known_NEON_dataset_rows"]=0
        result=assess_source_eligibility(changed,V1,R)
        self.assertIsNone(result["blanket_independence_from_all_NEON_derived_biological_materials"])
        self.assertFalse(result["authorization_to_open_NEON_plant_outcomes"])

    def test_wrong_input_counts_raise(self):
        changed=json.loads(json.dumps(P))
        changed["original_model_counts_recovered"]["PRESERVED_SPECIMEN"]=False
        with self.assertRaises(ValueError):
            assess_source_eligibility(changed,V1,R)


if __name__=="__main__":
    unittest.main()
