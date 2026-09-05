import unittest

from product_b_v5.gbif_transport import (
    AuthorizedGBIFSearchTransport,
    GBIFSearchCeilingExceeded,
)
from product_b_v5.occurrence_source import LogicalOccurrenceQuery


QUERY = LogicalOccurrenceQuery(
    pair_id="OPM_FIG_001",
    partner="x",
    taxon_key="5361904",
    checklist_key="d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
    geographic_filter_type="polygon_wkt",
    geographic_filter_value="POLYGON((98 24.67,98.92 18.75,100.42 13.83,101.27 21.9,98.88 24.9,98 24.67))",
)


class FakeTransport(AuthorizedGBIFSearchTransport):
    def __init__(self, payloads):
        super().__init__()
        self.payloads = list(payloads)
        self.calls = []

    def _fetch_payload(self, endpoint, params):
        self.calls.append((endpoint, dict(params)))
        if not self.payloads:
            raise AssertionError("unexpected page request")
        return self.payloads.pop(0)


class AuthorizedGBIFSearchTransportTests(unittest.TestCase):
    def test_single_page_transport_records_audit(self):
        payload = {
            "offset": 0,
            "limit": 300,
            "count": 2,
            "endOfRecords": True,
            "results": [{"key": 1}, {"key": 2}],
        }
        transport = FakeTransport([payload])
        rows = transport(QUERY)
        self.assertEqual(tuple(row["key"] for row in rows), (1, 2))
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.audits[0].declared_count, 2)
        self.assertEqual(transport.audits[0].pages_fetched, 1)

    def test_two_page_transport_uses_frozen_offset_progression(self):
        first = {
            "offset": 0,
            "limit": 300,
            "count": 301,
            "endOfRecords": False,
            "results": [{"key": i} for i in range(300)],
        }
        second = {
            "offset": 300,
            "limit": 300,
            "count": 301,
            "endOfRecords": True,
            "results": [{"key": 300}],
        }
        transport = FakeTransport([first, second])
        rows = transport(QUERY)
        self.assertEqual(len(rows), 301)
        self.assertEqual(transport.calls[1][1]["offset"], "300")
        self.assertEqual(transport.audits[0].pages_fetched, 2)

    def test_opened_count_above_ceiling_stops_on_first_page(self):
        payload = {
            "offset": 0,
            "limit": 300,
            "count": 100001,
            "endOfRecords": False,
            "results": [{"key": i} for i in range(300)],
        }
        transport = FakeTransport([payload])
        with self.assertRaises(GBIFSearchCeilingExceeded):
            transport(QUERY)
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.audits, ())

    def test_declared_count_change_during_paging_is_rejected(self):
        first = {
            "offset": 0,
            "limit": 300,
            "count": 301,
            "endOfRecords": False,
            "results": [{"key": i} for i in range(300)],
        }
        second = {
            "offset": 300,
            "limit": 300,
            "count": 302,
            "endOfRecords": True,
            "results": [{"key": 300}],
        }
        transport = FakeTransport([first, second])
        with self.assertRaisesRegex(ValueError, "declared count changed"):
            transport(QUERY)


if __name__ == "__main__":
    unittest.main()
