import json
import unittest
from pathlib import Path

from product_b_v5.authorization import ExecutionNotAuthorized
from product_b_v5.pipeline import (
    FrozenPairExecutionSpec,
    execute_frozen_pair_sampling_preflight,
    point_in_polygon_wkt,
    validate_returned_rows_against_query,
)
from product_b_v5.sampling import SamplingState
from product_b_v5.scope import GeographicScopeDeclaration, ScopeState
from product_b_v5.occurrence_source import build_logical_occurrence_query


class OneShotPipelineTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(
            Path("config/product_b_v5_sampling_execution_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.scope_contract = json.loads(
            Path("config/product_b_v5_scope_resolution_fig001_v0_2.json").read_text(
                encoding="utf-8"
            )
        )
        self.scope = GeographicScopeDeclaration(
            pair_id="OPM_FIG_001",
            literature_scope_text="published China-Thailand population envelope",
            evidence_doi=self.scope_contract["scope_evidence_doi"],
            state=ScopeState.RESOLVED,
            filter_type="polygon_wkt",
            filter_value=self.scope_contract["filter_value"],
            scope_source_type="primary_literature_methods",
        )

    def _authorized_manifest(self):
        manifest = dict(self.manifest)
        manifest["execution_authorized"] = True
        manifest["occurrence_reads_allowed"] = True
        return manifest

    def _unauthorized_manifest(self):
        manifest = dict(self.manifest)
        manifest["execution_authorized"] = False
        manifest["occurrence_reads_allowed"] = False
        return manifest

    def _inside_points(self, n=50):
        points = []
        for lat_index in range(70):
            lat = 14.0 + 0.16 * lat_index
            for lon_index in range(20):
                lon = 98.0 + 0.16 * lon_index
                if point_in_polygon_wkt(lon, lat, self.scope.filter_value):
                    points.append((lon, lat))
                    if len(points) == n:
                        return tuple(points)
        raise AssertionError("synthetic grid did not produce enough interior points")

    def _rows(self, partner, n=50):
        rows = []
        for index, (lon, lat) in enumerate(self._inside_points(n)):
            rows.append(
                {
                    "key": (100_000 if partner == "x" else 200_000) + index,
                    "datasetKey": f"dataset-{partner}",
                    "occurrenceID": f"{partner}-occ-{index}",
                    "eventID": "",
                    "catalogNumber": "",
                    "otherCatalogNumbers": [],
                    "eventDate": "2020-01-02",
                    "recordedBy": f"collector-{partner}",
                    "decimalLatitude": lat,
                    "decimalLongitude": lon,
                    "coordinateUncertaintyInMeters": 100.0,
                    "occurrenceStatus": "PRESENT",
                }
            )
        return tuple(rows)

    def test_synthetic_unauthorized_manifest_blocks_runner_before_transport(self):
        calls = []

        def transport(query):
            calls.append(query.partner)
            return self._rows(query.partner)

        with self.assertRaises(ExecutionNotAuthorized):
            execute_frozen_pair_sampling_preflight(
                manifest=self._unauthorized_manifest(),
                scope_declarations=(self.scope,),
                transport=transport,
            )
        self.assertEqual(calls, [])

    def test_committed_authorized_run_computes_primary_and_strict_together(self):
        calls = []

        def transport(query):
            calls.append(query.partner)
            return self._rows(query.partner)

        result = execute_frozen_pair_sampling_preflight(
            manifest=self._authorized_manifest(),
            scope_declarations=(self.scope,),
            transport=transport,
        )
        self.assertEqual(calls, ["x", "y"])
        self.assertEqual(result.primary.sampling_result.state, SamplingState.PASSED)
        self.assertEqual(
            result.strict_sensitivity.sampling_result.state,
            SamplingState.UNRESOLVED,
        )
        self.assertIn(
            "x_independent_record_floor_failed",
            result.strict_sensitivity.sampling_result.reasons,
        )
        self.assertIn(
            "y_independent_record_floor_failed",
            result.strict_sensitivity.sampling_result.reasons,
        )
        self.assertEqual(result.primary.audit.retained_records_x, 50)
        self.assertEqual(result.primary.audit.retained_records_y, 50)

    def test_outside_scope_row_stops_before_second_partner_read(self):
        calls = []

        def transport(query):
            calls.append(query.partner)
            if query.partner == "x":
                bad = list(self._rows("x", 1))
                bad[0] = dict(bad[0])
                bad[0]["decimalLongitude"] = 120.0
                bad[0]["decimalLatitude"] = 20.0
                return tuple(bad)
            return self._rows("y")

        with self.assertRaisesRegex(ValueError, "outside frozen query geometry"):
            execute_frozen_pair_sampling_preflight(
                manifest=self._authorized_manifest(),
                scope_declarations=(self.scope,),
                transport=transport,
            )
        self.assertEqual(calls, ["x"])

    def test_absent_row_is_transport_mismatch(self):
        query = build_logical_occurrence_query(
            pair_id="OPM_FIG_001",
            partner="x",
            taxon_key="5361904",
            scope_declarations=(self.scope,),
        )
        row = dict(self._rows("x", 1)[0])
        row["occurrenceStatus"] = "ABSENT"
        with self.assertRaisesRegex(ValueError, "PRESENT"):
            validate_returned_rows_against_query(query, (row,))

    def test_custom_taxon_execution_spec_cannot_bypass_frozen_pair(self):
        custom = FrozenPairExecutionSpec(
            pair_id="OPM_FIG_001",
            x_taxon_key="999",
            y_taxon_key="1359124",
        )
        with self.assertRaisesRegex(ValueError, "differs"):
            execute_frozen_pair_sampling_preflight(
                manifest=self._authorized_manifest(),
                scope_declarations=(self.scope,),
                transport=lambda query: (),
                spec=custom,
            )


if __name__ == "__main__":
    unittest.main()
