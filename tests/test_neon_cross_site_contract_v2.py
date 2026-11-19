"""Keep external NEON validation cross-site and unlaunched until source integrity."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V1=json.loads((ROOT/"config/neon_external_validation_preflight_v1.json").read_text())
V2=json.loads((ROOT/"config/neon_cross_site_evaluation_contract_v2.json").read_text())


class SiteScaleContractTests(unittest.TestCase):
    def test_frozen_taxa_and_original_gates_preserved(self):
        self.assertEqual(V2["fixed_taxa_from_v1"],
                         V1["focal_taxa_predeclared_from_existing_heldout_for_US_range_only"])
        self.assertEqual(V2["unchanged_v1_eligibility"]["min_sites_per_taxon"],
                         V1["eligibility_rules_prelabel"]["minimum_independent_sites_per_evaluable_taxon"])
        self.assertEqual(V2["unchanged_v1_eligibility"]["min_evaluable_taxa"],3)
        self.assertEqual(V2["empirical_ledger_increment"],0)
        self.assertFalse(V2["independent_field_result_obtained"])

    def test_score_target_is_site_not_pseudoreplicated_plot(self):
        d=V2["planned_computation"]
        self.assertIn("site-level Kendall",d["primary_statistic"])
        self.assertIn("site",V2["planned_unit"])
        self.assertIn("site",d["avoid_pseudoreplication"])
        self.assertNotIn("within-site",d["primary_statistic"])
        self.assertIn("non-detection",d["species_label"])

    def test_no_label_opening_before_source_independence(self):
        self.assertIn("NOT_AUTHORIZED",V2["status"])
        self.assertEqual(V2["source_overlap_barrier"]["status"],"unresolved")
        self.assertTrue(any("before source-lineage" in x for x in V2["forbidden"]))
        self.assertTrue(any("q95" in x for x in V2["forbidden"]))


if __name__=="__main__":
    unittest.main()
