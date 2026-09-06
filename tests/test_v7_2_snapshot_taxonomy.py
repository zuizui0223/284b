import unittest

from product_b_v7_2.snapshot_taxonomy import (
    SnapshotTaxonomyRequest,
    build_current_species_match_params,
    parse_current_direct_taxonomy_resolution,
)


class SnapshotNativeTaxonomyTests(unittest.TestCase):
    def test_match_params_do_not_pin_legacy_checklist(self):
        request = SnapshotTaxonomyRequest("JOS002", "x", "Yucca jaegeriana", "Plantae")
        params = dict(build_current_species_match_params(request))
        self.assertEqual(params["scientificName"], "Yucca jaegeriana")
        self.assertEqual(params["taxonRank"], "SPECIES")
        self.assertEqual(params["kingdom"], "Plantae")
        self.assertNotIn("checklistKey", params)

    def test_exact_accepted_current_match_and_usage_pass(self):
        request = SnapshotTaxonomyRequest("JOS002", "x", "Yucca jaegeriana", "Plantae")
        match = {
            "usage": {
                "key": "123",
                "canonicalName": "Yucca jaegeriana",
                "name": "Yucca jaegeriana (McKelvey) L.W.Lenz",
                "rank": "SPECIES",
                "status": "ACCEPTED",
            },
            "diagnostics": {"matchType": "EXACT", "confidence": 100},
            "synonym": False,
        }
        usage = {
            "key": 123,
            "canonicalName": "Yucca jaegeriana",
            "rank": "SPECIES",
            "taxonomicStatus": "ACCEPTED",
        }
        result = parse_current_direct_taxonomy_resolution(
            request=request, match_payload=match, usage_payload=usage
        )
        self.assertEqual(result.usage_key, "123")
        self.assertEqual(result.status, "ACCEPTED")
        self.assertEqual(result.match_type, "EXACT")

    def test_synonym_stops_for_manual_review(self):
        request = SnapshotTaxonomyRequest("JOS002", "y", "Tegeticula antithetica", "Animalia")
        match = {
            "usage": {
                "key": "456",
                "canonicalName": "Tegeticula antithetica",
                "name": "Tegeticula antithetica Pellmyr",
                "rank": "SPECIES",
                "status": "SYNONYM",
            },
            "diagnostics": {"matchType": "EXACT", "confidence": 100},
            "synonym": True,
        }
        usage = {
            "key": 456,
            "canonicalName": "Tegeticula antithetica",
            "rank": "SPECIES",
            "taxonomicStatus": "SYNONYM",
        }
        with self.assertRaisesRegex(ValueError, "must be ACCEPTED|manual concept review"):
            parse_current_direct_taxonomy_resolution(
                request=request, match_payload=match, usage_payload=usage
            )

    def test_usage_key_or_name_disagreement_fails(self):
        request = SnapshotTaxonomyRequest("JOS002", "x", "Yucca jaegeriana", "Plantae")
        match = {
            "usage": {
                "key": "123",
                "canonicalName": "Yucca jaegeriana",
                "name": "Yucca jaegeriana",
                "rank": "SPECIES",
                "status": "ACCEPTED",
            },
            "diagnostics": {"matchType": "EXACT", "confidence": 100},
            "synonym": False,
        }
        usage = {
            "key": 124,
            "canonicalName": "Yucca jaegeriana",
            "rank": "SPECIES",
            "taxonomicStatus": "ACCEPTED",
        }
        with self.assertRaisesRegex(ValueError, "key disagrees"):
            parse_current_direct_taxonomy_resolution(
                request=request, match_payload=match, usage_payload=usage
            )


if __name__ == "__main__":
    unittest.main()
