import json
import unittest
from pathlib import Path

from product_b_v5.authorization import ExecutionNotAuthorized
from product_b_v5.occurrence_source import (
    FIXED_REQUIRED_FIELDS,
    LogicalOccurrenceQuery,
    build_logical_occurrence_query,
    execute_guarded_occurrence_read,
)
from product_b_v5.scope import GeographicScopeDeclaration, ScopeState


class OccurrenceSourceBoundaryTests(unittest.TestCase):
    def setUp(self):
        path = Path("config/product_b_v5_sampling_execution_manifest.json")
        self.manifest = json.loads(path.read_text(encoding="utf-8"))
        self.unresolved_scope = GeographicScopeDeclaration(
            pair_id="OPM_FIG_001",
            literature_scope_text="continental Southeast Asia; southern China to southern Thailand",
            evidence_doi="10.1111/j.1365-294X.2010.04654.x",
            state=ScopeState.UNRESOLVED,
            scope_source_type="primary_literature_abstract",
        )
        self.resolved_scope = GeographicScopeDeclaration(
            pair_id="OPM_FIG_001",
            literature_scope_text="synthetic resolved study envelope",
            evidence_doi="10.1111/j.1365-294X.2010.04654.x",
            state=ScopeState.RESOLVED,
            filter_type="bbox",
            filter_value="95.0,5.0,110.0,25.0",
            scope_source_type="primary_literature_supplement",
        )

    def test_query_cannot_be_built_from_unresolved_scope(self):
        with self.assertRaisesRegex(ValueError, "operational geographic scope is unresolved"):
            build_logical_occurrence_query(
                pair_id="OPM_FIG_001",
                partner="x",
                taxon_key="5361904",
                scope_declarations=(self.unresolved_scope,),
            )

    def test_resolved_scope_builds_fixed_logical_query(self):
        query = build_logical_occurrence_query(
            pair_id="OPM_FIG_001",
            partner="y",
            taxon_key="1359124",
            scope_declarations=(self.resolved_scope,),
        )
        self.assertEqual(query.geographic_filter_type, "bbox")
        self.assertEqual(query.geographic_filter_value, "95.0,5.0,110.0,25.0")
        self.assertTrue(query.has_coordinate)
        self.assertEqual(query.occurrence_status, "PRESENT")
        for required in (
            "occurrenceID",
            "eventID",
            "catalogNumber",
            "datasetKey",
            "eventDate",
            "recordedBy",
            "decimalLatitude",
            "decimalLongitude",
            "coordinateUncertaintyInMeters",
        ):
            self.assertIn(required, FIXED_REQUIRED_FIELDS)

    def test_committed_manifest_blocks_transport_before_it_is_called(self):
        query = build_logical_occurrence_query(
            pair_id="OPM_FIG_001",
            partner="x",
            taxon_key="5361904",
            scope_declarations=(self.resolved_scope,),
        )
        calls = []

        def transport(value):
            calls.append(value)
            return ({"key": 1},)

        with self.assertRaises(ExecutionNotAuthorized):
            execute_guarded_occurrence_read(
                manifest=self.manifest,
                query=query,
                transport=transport,
            )
        self.assertEqual(calls, [])

    def test_synthetic_fully_authorized_manifest_invokes_transport_once(self):
        query = build_logical_occurrence_query(
            pair_id="OPM_FIG_001",
            partner="x",
            taxon_key="5361904",
            scope_declarations=(self.resolved_scope,),
        )
        authorized = dict(self.manifest)
        authorized["scope_eligible_pair_ids"] = ["OPM_FIG_001"]
        authorized["execution_authorized"] = True
        authorized["occurrence_reads_allowed"] = True
        calls = []

        def transport(value):
            calls.append(value)
            return ({"key": 101}, {"key": 102})

        decision, rows = execute_guarded_occurrence_read(
            manifest=authorized,
            query=query,
            transport=transport,
        )
        self.assertTrue(decision.authorized)
        self.assertEqual(len(calls), 1)
        self.assertEqual(tuple(row["key"] for row in rows), (101, 102))

    def test_transport_boundary_rejects_mutated_query_semantics(self):
        query = LogicalOccurrenceQuery(
            pair_id="OPM_FIG_001",
            partner="x",
            taxon_key="5361904",
            checklist_key=self.manifest["checklist_key"],
            geographic_filter_type="bbox",
            geographic_filter_value="1,2,3,4",
            has_coordinate=False,
        )
        calls = []

        def transport(value):
            calls.append(value)
            return ()

        with self.assertRaisesRegex(ValueError, "requires coordinates"):
            execute_guarded_occurrence_read(
                manifest=self.manifest,
                query=query,
                transport=transport,
            )
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
