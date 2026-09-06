import unittest

from product_b_v7_3.concept_closure import (
    CurrentConceptResolution,
    evaluate_snapshot_species_concept_closure,
)
from product_b_v7_3.taxonomy_identity import SnapshotTaxonomyTuple


class SnapshotSpeciesConceptClosureTests(unittest.TestCase):
    def test_multiple_historical_specieskeys_can_close_to_one_current_species(self):
        rows = [
            SnapshotTaxonomyTuple(
                species="Example alpha",
                specieskey="100",
                taxonkey="100",
                scientificname="Example alpha Author",
                taxonrank="SPECIES",
            ),
            SnapshotTaxonomyTuple(
                species="Example alpha",
                specieskey="XR1",
                taxonkey="XR2",
                scientificname="Oldexample alpha Author",
                taxonrank="SPECIES",
            ),
            SnapshotTaxonomyTuple(
                species="Example alpha",
                specieskey="XR1",
                taxonkey="XR3",
                scientificname="Example alpha subsp. minor Author",
                taxonrank="SUBSPECIES",
            ),
        ]
        reviews = {
            "Example alpha Author": CurrentConceptResolution(
                "Example alpha Author", True, True, "Example alpha", "100", "EXACT"
            ),
            "Oldexample alpha Author": CurrentConceptResolution(
                "Oldexample alpha Author", True, True, "Example alpha", "100", "EXACT"
            ),
            "Example alpha subsp. minor Author": CurrentConceptResolution(
                "Example alpha subsp. minor Author", True, True, "Example alpha", "200", "EXACT"
            ),
        }
        decision = evaluate_snapshot_species_concept_closure(
            current_accepted_species="Example alpha",
            taxonomy_tuples=rows,
            current_name_resolutions=reviews,
        )
        self.assertTrue(decision.passed)
        self.assertEqual(decision.frozen_historical_specieskeys, ("100", "XR1"))
        self.assertEqual(decision.current_unresolved_historical_names, ())
        self.assertEqual(decision.reasons, ())

    def test_one_name_resolving_to_different_species_fails_whole_key_set(self):
        rows = [
            SnapshotTaxonomyTuple("Example alpha", "100", "100", "Example alpha", "SPECIES"),
            SnapshotTaxonomyTuple("Example alpha", "XR1", "XR2", "Example beta", "SPECIES"),
        ]
        reviews = {
            "Example alpha": CurrentConceptResolution("Example alpha", True, True, "Example alpha"),
            "Example beta": CurrentConceptResolution("Example beta", True, True, "Example beta"),
        }
        decision = evaluate_snapshot_species_concept_closure(
            current_accepted_species="Example alpha",
            taxonomy_tuples=rows,
            current_name_resolutions=reviews,
        )
        self.assertFalse(decision.passed)
        self.assertIn("snapshot_name_resolves_to_different_current_species", decision.reasons)
        self.assertEqual(decision.frozen_historical_specieskeys, ())

    def test_missing_review_fails_but_completed_historical_no_match_is_audited_not_conflict(self):
        rows = [SnapshotTaxonomyTuple("Example alpha", "100", "100", "Old alpha", "SPECIES")]
        missing = evaluate_snapshot_species_concept_closure(
            current_accepted_species="Example alpha",
            taxonomy_tuples=rows,
            current_name_resolutions={},
        )
        self.assertFalse(missing.passed)
        self.assertIn("current_taxonomy_closure_review_missing", missing.reasons)

        historical_no_match = evaluate_snapshot_species_concept_closure(
            current_accepted_species="Example alpha",
            taxonomy_tuples=rows,
            current_name_resolutions={
                "Old alpha": CurrentConceptResolution(
                    "Old alpha", True, False, None, reason="completed_no_current_exact_match"
                )
            },
        )
        self.assertTrue(historical_no_match.passed)
        self.assertEqual(historical_no_match.current_unresolved_historical_names, ("Old alpha",))
        self.assertEqual(historical_no_match.frozen_historical_specieskeys, ("100",))

    def test_incomplete_review_fails_closed(self):
        rows = [SnapshotTaxonomyTuple("Example alpha", "100", "100", "Old alpha", "SPECIES")]
        decision = evaluate_snapshot_species_concept_closure(
            current_accepted_species="Example alpha",
            taxonomy_tuples=rows,
            current_name_resolutions={
                "Old alpha": CurrentConceptResolution(
                    "Old alpha", False, False, None, reason="taxonomy_transport_failure"
                )
            },
        )
        self.assertFalse(decision.passed)
        self.assertIn("current_taxonomy_closure_review_incomplete", decision.reasons)

    def test_snapshot_species_field_must_equal_frozen_current_species(self):
        rows = [SnapshotTaxonomyTuple("Example beta", "100", "100", "Example beta", "SPECIES")]
        decision = evaluate_snapshot_species_concept_closure(
            current_accepted_species="Example alpha",
            taxonomy_tuples=rows,
            current_name_resolutions={
                "Example beta": CurrentConceptResolution("Example beta", True, True, "Example alpha")
            },
        )
        self.assertFalse(decision.passed)
        self.assertIn("snapshot_species_field_conflicts_with_frozen_current_species", decision.reasons)

    def test_invalid_rank_or_blank_specieskey_fails(self):
        rows = [SnapshotTaxonomyTuple("Example alpha", "", "x", "Example alpha", "GENUS")]
        decision = evaluate_snapshot_species_concept_closure(
            current_accepted_species="Example alpha",
            taxonomy_tuples=rows,
            current_name_resolutions={
                "Example alpha": CurrentConceptResolution("Example alpha", True, True, "Example alpha")
            },
        )
        self.assertFalse(decision.passed)
        self.assertIn("snapshot_specieskey_blank", decision.reasons)
        self.assertIn("snapshot_taxonrank_outside_species_concept", decision.reasons)


if __name__ == "__main__":
    unittest.main()
