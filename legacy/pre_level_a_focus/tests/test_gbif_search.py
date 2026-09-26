import json
import unittest
from pathlib import Path

from product_b_v5.gbif_search import (
    GBIF_MAX_PAGE_SIZE,
    GBIF_OCCURRENCE_SEARCH_ENDPOINT,
    GBIFSearchEnvelope,
    next_search_request,
    parse_search_envelope,
    polygon_signed_area,
    require_gbif_anticlockwise_polygon,
    serialize_gbif_search_request,
)
from product_b_v5.occurrence_source import build_logical_occurrence_query
from product_b_v5.scope import GeographicScopeDeclaration, ScopeState


class GBIFSearchPlanningTests(unittest.TestCase):
    def setUp(self):
        path = Path("config/product_b_v5_scope_resolution_fig001_v0_2.json")
        self.scope_contract = json.loads(path.read_text(encoding="utf-8"))
        self.scope = GeographicScopeDeclaration(
            pair_id="OPM_FIG_001",
            literature_scope_text="published China-Thailand population envelope",
            evidence_doi=self.scope_contract["scope_evidence_doi"],
            state=ScopeState.RESOLVED,
            filter_type=self.scope_contract["filter_type"],
            filter_value=self.scope_contract["filter_value"],
            scope_source_type=self.scope_contract["scope_source_type"],
        )
        self.query = build_logical_occurrence_query(
            pair_id="OPM_FIG_001",
            partner="x",
            taxon_key="5361904",
            scope_declarations=(self.scope,),
        )

    def test_frozen_fig_polygon_is_anticlockwise_for_gbif(self):
        area = polygon_signed_area(self.scope_contract["filter_value"])
        self.assertGreater(area, 0.0)
        self.assertEqual(
            require_gbif_anticlockwise_polygon(self.scope_contract["filter_value"]),
            self.scope_contract["filter_value"],
        )

    def test_clockwise_polygon_is_rejected(self):
        clockwise = "POLYGON((98 24.67,98.88 24.9,101.27 21.9,100.42 13.83,98.92 18.75,98 24.67))"
        self.assertLess(polygon_signed_area(clockwise), 0.0)
        with self.assertRaisesRegex(ValueError, "anticlockwise"):
            require_gbif_anticlockwise_polygon(clockwise)

    def test_search_request_has_only_predeclared_filters_and_paging(self):
        request = serialize_gbif_search_request(self.query)
        self.assertEqual(request.endpoint, GBIF_OCCURRENCE_SEARCH_ENDPOINT)
        self.assertEqual(request.limit, GBIF_MAX_PAGE_SIZE)
        params = request.as_mapping()
        self.assertEqual(params["taxonKey"], "5361904")
        self.assertEqual(
            params["checklistKey"],
            "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
        )
        self.assertEqual(params["geometry"], self.scope_contract["filter_value"])
        self.assertEqual(params["hasCoordinate"], "true")
        self.assertEqual(params["occurrenceStatus"], "PRESENT")
        self.assertEqual(params["offset"], "0")
        self.assertEqual(params["limit"], "300")
        self.assertEqual(
            set(params),
            {
                "taxonKey",
                "checklistKey",
                "geometry",
                "hasCoordinate",
                "occurrenceStatus",
                "offset",
                "limit",
            },
        )

    def test_page_size_above_documented_maximum_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "\[1, 300\]"):
            serialize_gbif_search_request(self.query, limit=301)

    def test_offset_plus_limit_above_search_ceiling_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "100000"):
            serialize_gbif_search_request(self.query, offset=99_900, limit=101)

    def test_synthetic_page_metadata_plans_next_page_deterministically(self):
        payload = {
            "offset": 0,
            "limit": 300,
            "count": 725,
            "endOfRecords": False,
            "results": [{"key": value} for value in range(300)],
        }
        envelope = parse_search_envelope(payload)
        request = next_search_request(self.query, envelope)
        self.assertIsNotNone(request)
        self.assertEqual(request.offset, 300)
        self.assertEqual(request.limit, 300)

    def test_terminal_synthetic_page_has_no_next_request(self):
        envelope = GBIFSearchEnvelope(
            offset=600,
            limit=300,
            count=725,
            end_of_records=True,
            result_count=125,
        )
        self.assertIsNone(next_search_request(self.query, envelope))

    def test_nonterminal_empty_page_fails_closed(self):
        envelope = GBIFSearchEnvelope(
            offset=0,
            limit=300,
            count=1,
            end_of_records=False,
            result_count=0,
        )
        with self.assertRaisesRegex(ValueError, "advance"):
            next_search_request(self.query, envelope)

    def test_search_ceiling_does_not_adaptively_switch_to_download(self):
        envelope = GBIFSearchEnvelope(
            offset=99_700,
            limit=300,
            count=120_000,
            end_of_records=False,
            result_count=300,
        )
        with self.assertRaisesRegex(ValueError, "100000-record ceiling"):
            next_search_request(self.query, envelope)


if __name__ == "__main__":
    unittest.main()
