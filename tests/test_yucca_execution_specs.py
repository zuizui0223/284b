import csv
import json
import unittest
from pathlib import Path

from product_b_v5.authorization import require_execution_authorization
from product_b_v5.pipeline import (
    OPM_YUC_001_SPEC,
    OPM_YUC_002_SPEC,
    FrozenPairExecutionSpec,
    frozen_pair_spec,
)
from product_b_v5.scope import GeographicScopeDeclaration, ScopeState, require_scope_resolved


MANIFEST_PATHS = {
    "OPM_YUC_001": Path("config/product_b_v5_sampling_execution_manifest_yuc001_v0_1.json"),
    "OPM_YUC_002": Path("config/product_b_v5_sampling_execution_manifest_yuc002_v0_1.json"),
}


def load_scopes():
    rows = []
    with Path("registry/obligate_pair_registry_scope_v0_3.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            rows.append(
                GeographicScopeDeclaration(
                    pair_id=row["pair_id"],
                    literature_scope_text=row["literature_scope_text"],
                    evidence_doi=row["evidence_doi"],
                    state=ScopeState(row["operational_scope_state"]),
                    filter_type=row["filter_type"],
                    filter_value=row["filter_value"],
                    scope_source_type=row["scope_source_type"],
                    note=row["note"],
                )
            )
    return tuple(rows)


class YuccaFrozenExecutionSpecTests(unittest.TestCase):
    def test_yuc001_keys_are_exact_direct_taxonomy_result(self):
        self.assertEqual(OPM_YUC_001_SPEC.x_taxon_key, "2775775")
        self.assertEqual(OPM_YUC_001_SPEC.y_taxon_key, "8852308")
        self.assertEqual(frozen_pair_spec("OPM_YUC_001"), OPM_YUC_001_SPEC)

    def test_yuc002_keys_are_exact_direct_taxonomy_result(self):
        self.assertEqual(OPM_YUC_002_SPEC.x_taxon_key, "2775710")
        self.assertEqual(OPM_YUC_002_SPEC.y_taxon_key, "9143017")
        self.assertEqual(frozen_pair_spec("OPM_YUC_002"), OPM_YUC_002_SPEC)

    def test_unknown_pair_cannot_enter_execution_registry(self):
        with self.assertRaisesRegex(ValueError, "absent from frozen"):
            frozen_pair_spec("OPM_UNKNOWN")

    def test_altered_yucca_spec_is_not_the_registered_spec(self):
        altered = FrozenPairExecutionSpec(
            pair_id="OPM_YUC_001",
            x_taxon_key="2775775",
            y_taxon_key="999",
        )
        self.assertNotEqual(altered, frozen_pair_spec(altered.pair_id))

    def test_pair_specific_manifests_are_consumed_and_closed(self):
        for pair_id, path in MANIFEST_PATHS.items():
            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["taxonomy_eligible_pair_ids"], [pair_id])
            self.assertEqual(manifest["scope_eligible_pair_ids"], [pair_id])
            self.assertTrue(manifest["execution_consumed"])
            self.assertFalse(manifest["execution_authorized"])
            self.assertFalse(manifest["occurrence_reads_allowed"])
            self.assertEqual(manifest["terminal_state"], "unresolved_sampling")

    def test_each_yucca_scope_is_independently_resolved(self):
        scopes = load_scopes()
        for pair_id in MANIFEST_PATHS:
            row = require_scope_resolved(scopes, pair_id=pair_id)
            self.assertEqual(row.filter_type, "polygon_wkt")
            self.assertEqual(row.scope_source_type, "primary_literature_methods")

    def test_synthetic_authorization_for_each_pair_is_independent(self):
        for pair_id, path in MANIFEST_PATHS.items():
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["execution_consumed"] = False
            manifest["execution_authorized"] = True
            manifest["occurrence_reads_allowed"] = True
            decision = require_execution_authorization(
                manifest, requested_pair_ids=[pair_id]
            )
            self.assertTrue(decision.authorized)
            other = "OPM_YUC_002" if pair_id == "OPM_YUC_001" else "OPM_YUC_001"
            with self.assertRaises(Exception):
                require_execution_authorization(manifest, requested_pair_ids=[other])


if __name__ == "__main__":
    unittest.main()
