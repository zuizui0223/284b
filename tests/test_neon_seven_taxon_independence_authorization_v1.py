"""No-label regression tests for all-seven NEON source-independence gate."""
import json
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from authorize_neon_seven_taxon_source_independence_v1 import classify

DATA=json.loads((ROOT/"results/neon_seven_taxon_original_source_lineage_v1.json").read_text())
DESIGN=json.loads((ROOT/"config/neon_external_validation_preflight_v1.json").read_text())
PILOT=json.loads((ROOT/"results/neon_original_gbif_historical_replay_v2.json").read_text())


class SevenSourceIndependenceTests(unittest.TestCase):
    def test_verifiable_six_training_rows_in_three_predeclared_taxa(self):
        a=classify(DATA,DESIGN,PILOT)
        self.assertEqual(a["status"],"SOURCE_LEVEL_INDEPENDENCE_NOT_ESTABLISHED__LABEL_GATE_CLOSED")
        self.assertEqual(a["predeclared_taxa"],7)
        self.assertEqual(a["taxa_with_known_NEON_voucher_datasetkey_inputs"],3)
        self.assertEqual(a["known_NEON_voucher_datasetkey_total_input_rows"],6)
        self.assertEqual(a["known_NEON_voucher_model_inputs_by_mode"]["PRESERVED_SPECIMEN"],6)
        self.assertEqual(a["known_NEON_voucher_model_inputs_by_mode"]["HUMAN_OBSERVATION"],0)
        self.assertEqual(a["known_NEON_voucher_raw_records_by_mode"]["PRESERVED_SPECIMEN"],41)
        self.assertFalse(a["authorized_to_open_NEON_taxon_plot_labels"])
        self.assertFalse(a["actual_identity_overlap_with_NEON_DP1_plot_events_verified"])
        self.assertEqual(a["empirical_ledger_increment"],0)

    def test_zero_voucher_datasetkey_does_not_claim_external_truth(self):
        a=classify(DATA,DESIGN,PILOT)
        for x in a["taxon_results"]:
            if x["known_NEON_datasetkey_thinned_source_input_rows"]==0:
                self.assertFalse(x["eligible_for_unqualified_NEON_external_accuracy_claim"])
                self.assertFalse(x["all_NEON_publications_absent_from_training_proven"])
                self.assertEqual(x["state"],"NO_KNOWN_DATASETKEY_IN_MODEL_INPUT__OTHER_LEAKAGE_UNRESOLVED")

    def test_original_source_parity_break_stops(self):
        invalid=json.loads(json.dumps(DATA))
        invalid["taxon_level_source_provenance"][2]["source_count_reproduced"]["PRESERVED_SPECIMEN"]=False
        with self.assertRaises(ValueError):
            classify(invalid,DESIGN,PILOT)

    def test_taxon_selection_changes_stop(self):
        invalid=json.loads(json.dumps(DATA))
        invalid["taxon_level_source_provenance"].reverse()
        with self.assertRaises(ValueError):
            classify(invalid,DESIGN,PILOT)


if __name__=="__main__":
    unittest.main()
