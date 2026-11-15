"""Dependency-free audit guards for frozen target-swap climate-support summaries."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_target_swap_transport_strata_v1 import aggregate, correlation, summarize


class TransportSummaryTests(unittest.TestCase):
    def test_aggregate_counts_only_validated_boolean_flags(self):
        r=[{"target":"A","flag":True},{"target":"A","flag":False},{"target":"B","flag":False}]
        x=aggregate(r)
        self.assertEqual((x["cells"],x["flagged"],x["silent"],x["target_taxa"]),(3,1,2,2))
        self.assertAlmostEqual(x["silence_fraction"],2/3)

    def test_correlate_descriptive_blocks(self):
        self.assertAlmostEqual(correlation([(0.1,1),(0.2,0.5),(0.3,0)]),-1.)
        with self.assertRaises(ValueError):
            correlation([(0.1,0.5),(0.2,0.6)])

    def test_pinned_input_sources_and_key_result_accounting(self):
        x=summarize()
        self.assertEqual(x["schema"],"284b.target_identity_climate_stratification_v1")
        self.assertEqual(x["empirical_ledger_increment"],0)
        self.assertEqual((x["overall"]["cells"],x["overall"]["silent"],x["unresolved"]),(280,115,8))
        self.assertEqual((x["all19_row_support_minimum"]["0.80"]["cells"],
                          x["all19_row_support_minimum"]["0.80"]["silent"]),(102,62))
        self.assertEqual(len(x["taxon_table"]),12)
        self.assertEqual(len(x["target_M_table"]),36)


if __name__=="__main__":
    unittest.main()
