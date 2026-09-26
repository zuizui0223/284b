import unittest

from product_b_v5.gbif_taxonomy import (
    LEGACY_GBIF_BACKBONE_CHECKLIST_KEY,
    TaxonomyResolutionRequest,
    build_species_match_params,
    parse_direct_taxonomy_resolution,
)


REQUEST = TaxonomyResolutionRequest(
    pair_id="OPM_YUC_002",
    partner="y",
    scientific_name="Tegeticula mojavella",
    kingdom="Animalia",
    expected_key_hint="9143017",
)


def match_payload(**usage_overrides):
    usage = {
        "key": "9143017",
        "name": "Tegeticula mojavella Pellmyr, 1999",
        "canonicalName": "Tegeticula mojavella",
        "rank": "SPECIES",
        "status": "ACCEPTED",
    }
    usage.update(usage_overrides)
    return {
        "usage": usage,
        "diagnostics": {"matchType": "EXACT", "confidence": 99},
        "synonym": False,
    }


def usage_payload(**overrides):
    values = {
        "key": 9143017,
        "scientificName": "Tegeticula mojavella Pellmyr, 1999",
        "canonicalName": "Tegeticula mojavella",
        "rank": "SPECIES",
        "taxonomicStatus": "ACCEPTED",
    }
    values.update(overrides)
    return values


class GBIFTaxonomyResolutionTests(unittest.TestCase):
    def test_match_params_freeze_legacy_backbone_and_species_rank(self):
        params = dict(build_species_match_params(REQUEST))
        self.assertEqual(params["scientificName"], "Tegeticula mojavella")
        self.assertEqual(params["taxonRank"], "SPECIES")
        self.assertEqual(params["kingdom"], "Animalia")
        self.assertEqual(params["checklistKey"], LEGACY_GBIF_BACKBONE_CHECKLIST_KEY)

    def test_direct_exact_match_and_usage_page_pass(self):
        result = parse_direct_taxonomy_resolution(
            request=REQUEST,
            match_payload=match_payload(),
            usage_payload=usage_payload(),
        )
        self.assertEqual(result.usage_key, "9143017")
        self.assertTrue(result.expected_key_hint_agrees)
        self.assertEqual(result.match_type, "EXACT")

    def test_fuzzy_match_is_rejected(self):
        payload = match_payload()
        payload["diagnostics"]["matchType"] = "FUZZY"
        with self.assertRaisesRegex(ValueError, "EXACT"):
            parse_direct_taxonomy_resolution(
                request=REQUEST,
                match_payload=payload,
                usage_payload=usage_payload(),
            )

    def test_higher_rank_match_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "species rank"):
            parse_direct_taxonomy_resolution(
                request=REQUEST,
                match_payload=match_payload(rank="GENUS"),
                usage_payload=usage_payload(),
            )

    def test_synonym_requires_manual_concept_review(self):
        payload = match_payload()
        payload["synonym"] = True
        with self.assertRaisesRegex(ValueError, "synonym"):
            parse_direct_taxonomy_resolution(
                request=REQUEST,
                match_payload=payload,
                usage_payload=usage_payload(),
            )

    def test_secondary_hint_disagreement_is_not_silently_overwritten(self):
        request = TaxonomyResolutionRequest(
            pair_id="OPM_YUC_002",
            partner="y",
            scientific_name="Tegeticula mojavella",
            kingdom="Animalia",
            expected_key_hint="999",
        )
        with self.assertRaisesRegex(ValueError, "secondary key hint"):
            parse_direct_taxonomy_resolution(
                request=request,
                match_payload=match_payload(),
                usage_payload=usage_payload(),
            )

    def test_direct_usage_page_must_agree_with_match(self):
        with self.assertRaisesRegex(ValueError, "key disagrees"):
            parse_direct_taxonomy_resolution(
                request=REQUEST,
                match_payload=match_payload(),
                usage_payload=usage_payload(key=123),
            )


if __name__ == "__main__":
    unittest.main()
