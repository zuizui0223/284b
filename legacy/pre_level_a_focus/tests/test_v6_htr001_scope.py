import json
from pathlib import Path
import unittest

from product_b_v5.scope import (
    GeographicScopeDeclaration,
    ScopeState,
    convex_hull_polygon_wkt,
    validate_scope_declaration,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config/product_b_v6_scope_resolution_htr001_v0_1.json"


class HTR001ScopeTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_all_five_revision_points_recompute_exact_no_buffer_hull(self):
        points = [
            (row["longitude"], row["latitude"])
            for row in self.contract["source_points_lon_lat"]
        ]
        self.assertEqual(
            convex_hull_polygon_wkt(points),
            self.contract["filter_value"],
        )
        self.assertEqual(self.contract["buffer_degrees"], 0)
        self.assertFalse(self.contract["occurrence_information_used_in_derivation"])

    def test_scope_uses_existing_allowed_literature_source_class(self):
        declaration = GeographicScopeDeclaration(
            pair_id=self.contract["pair_id"],
            literature_scope_text=(
                "Five explicitly georeferenced Hydnora triceps revision specimens "
                "in Namibia and Northern Cape, South Africa"
            ),
            evidence_doi=self.contract["scope_evidence_doi"],
            state=ScopeState(self.contract["operational_scope_state"]),
            filter_type=self.contract["filter_type"],
            filter_value=self.contract["filter_value"],
            scope_source_type=self.contract["scope_source_type"],
            note=self.contract["interpretation_boundary"],
        )
        self.assertEqual(validate_scope_declaration(declaration), ())

    def test_host_specificity_conflict_is_frozen_before_occurrence_access(self):
        review = self.contract["host_specificity_review"]
        self.assertEqual(review["state"], "resolved_under_2024_revision")
        self.assertIn("only known host", review["current_revision_statement"].lower())
        self.assertIn("2021", review["older_secondary_conflict"])
        self.assertIn("do not reopen", review["execution_rule"].lower())


if __name__ == "__main__":
    unittest.main()
