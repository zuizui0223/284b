import csv
import json
import unittest
from pathlib import Path

from product_b_v5.scope import convex_hull_polygon_wkt


class V6PrimaryRegistryTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(
            Path("config/product_b_v6_directed_witness_contract_v0_1.json").read_text(
                encoding="utf-8"
            )
        )
        with Path("registry/product_b_v6_primary_pair_registry_literature_v0_1.csv").open(
            "r", encoding="utf-8", newline=""
        ) as handle:
            self.rows = tuple(csv.DictReader(handle))

    def test_v5_occurrence_opened_pairs_are_firewalled(self):
        self.assertEqual(
            set(self.contract["non_retroactivity"]["confirmatory_v6_excluded_occurrence_opened_pairs"]),
            {"OPM_FIG_001", "OPM_YUC_001", "OPM_YUC_002"},
        )
        for row in self.rows:
            self.assertNotIn(
                row["pair_id"],
                self.contract["non_retroactivity"]["confirmatory_v6_excluded_occurrence_opened_pairs"],
            )

    def test_sen001_is_literature_declared_before_taxonomy_or_occurrence(self):
        self.assertEqual(len(self.rows), 1)
        row = self.rows[0]
        self.assertEqual(row["pair_id"], "SEN001")
        self.assertEqual(row["direction"], "Y_requires_X")
        self.assertEqual(row["x_taxon_key"], "")
        self.assertEqual(row["y_taxon_key"], "")
        self.assertEqual(row["taxonomy_state"], "pending_response_blind_taxonomy_resolution")
        self.assertEqual(row["scope_state"], "operational_scope_resolved")
        self.assertEqual(row["confirmatory_eligible"], "false")

    def test_v6_witness_floors_are_not_v5_sampling_rescue(self):
        self.assertEqual(self.contract["host_x_sampling"]["minimum_independent_records"], 50)
        self.assertEqual(self.contract["host_x_sampling"]["minimum_unique_10km_cells"], 30)
        self.assertEqual(self.contract["host_x_sampling"]["minimum_inverse_simpson_effective_cells"], 10.0)
        self.assertEqual(self.contract["dependent_y_witness_sampling"]["minimum_independent_records"], 5)
        self.assertEqual(self.contract["dependent_y_witness_sampling"]["minimum_unique_10km_cells"], 3)
        self.assertFalse(self.contract["dependent_y_witness_sampling"]["fit_y_niche"])


class SEN001ScopeTests(unittest.TestCase):
    def setUp(self):
        self.scope = json.loads(
            Path("config/product_b_v6_scope_resolution_sen001_v0_1.json").read_text(
                encoding="utf-8"
            )
        )

    def test_all_five_published_sites_recompute_exact_no_buffer_hull(self):
        points = tuple(
            (row["longitude"], row["latitude"])
            for row in self.scope["source_points_lon_lat"]
        )
        self.assertEqual(len(points), 5)
        self.assertEqual(self.scope["buffer_degrees"], 0)
        self.assertFalse(self.scope["occurrence_information_used_in_derivation"])
        self.assertEqual(
            convex_hull_polygon_wkt(points),
            self.scope["filter_value"],
        )


if __name__ == "__main__":
    unittest.main()
