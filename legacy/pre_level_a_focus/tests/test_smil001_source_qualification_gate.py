import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "results" / "product_b_smil001_independent_source_scan_v0_1.json"


class Smil001SourceQualificationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(RECEIPT.read_text(encoding="utf-8"))

    def test_scan_is_not_empirical(self):
        self.assertFalse(self.r["counts_as_empirical_evidence"])
        self.assertFalse(self.r["counts_as_empirical_conclusion"])
        self.assertEqual(self.r["empirical_ledger_increment"], 0)
        self.assertEqual(self.r["global_284b_empirical_ledger_after_this_scan"], 1)

    def test_relation_defining_sources_cannot_double_as_confirmatory_answers(self):
        for source in self.r["relation_defining_sources"]:
            self.assertFalse(source["eligible_as_confirmatory_focal_role_answer"])

    def test_no_occurrence_availability_or_overlap_was_inspected(self):
        for was_not_inspected in self.r["information_not_inspected"].values():
            self.assertTrue(was_not_inspected)

    def test_execution_remains_hard_stopped(self):
        d = self.r["operational_decision"]
        self.assertFalse(d["SMIL001_confirmatory_execution_authorized"])
        self.assertFalse(d["SMIL001_sampling_feasibility_authorized"])
        self.assertFalse(d["SMIL001_hard_invariant_opening_authorized"])
        self.assertFalse(d["SMIL001_soft_crosscheck_opening_authorized"])
        self.assertFalse(d["SMIL001_process_knockout_authorized"])
        self.assertTrue(
            d["SMIL001_execution_hard_stop_until_new_external_metadata_or_independent_source"]
        )

    def test_no_false_claim_that_independent_sources_do_not_exist(self):
        self.assertIn("bounded source-discovery scan", self.r["scan_interpretation"])
        self.assertIn("not a proof", self.r["scan_interpretation"])


if __name__ == "__main__":
    unittest.main()
