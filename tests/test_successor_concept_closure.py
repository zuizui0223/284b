import unittest

from product_b_v7_3.concept_closure import CurrentConceptResolution
from product_b_v7_3.successor_concept_closure import evaluate_successor_snapshot_species_concept_closure
from product_b_v7_3.taxonomy_identity import SnapshotTaxonomyTuple


class SuccessorConceptClosureTests(unittest.TestCase):
    def row(self, name: str, key: str, rank: str = "SUBVARIETY") -> SnapshotTaxonomyTuple:
        return SnapshotTaxonomyTuple(
            species="Example species",
            specieskey=key,
            taxonkey=key + "0",
            scientificname=name,
            taxonrank=rank,
        )

    def review(self, name: str, accepted: str | None, *, complete: bool = True) -> CurrentConceptResolution:
        return CurrentConceptResolution(
            snapshot_scientific_name=name,
            review_complete=complete,
            resolved=accepted is not None,
            accepted_species_name=accepted,
            accepted_usage_key="1" if accepted is not None else None,
            match_type="EXACT" if accepted is not None else None,
            reason=None,
        )

    def test_rank_is_audited_not_exclusion_gate(self):
        rows = (self.row("Historical name", "11", "SUBVARIETY"),)
        d = evaluate_successor_snapshot_species_concept_closure(
            current_accepted_species="Example species",
            taxonomy_tuples=rows,
            current_name_resolutions={"Historical name": self.review("Historical name", "Example species")},
        )
        self.assertTrue(d.passed)
        self.assertEqual(d.frozen_historical_specieskeys, ("11",))
        self.assertEqual(d.observed_taxonranks, ("SUBVARIETY",))

    def test_different_current_species_fails(self):
        rows = (self.row("Historical name", "11", "SPECIES"),)
        d = evaluate_successor_snapshot_species_concept_closure(
            current_accepted_species="Example species",
            taxonomy_tuples=rows,
            current_name_resolutions={"Historical name": self.review("Historical name", "Different species")},
        )
        self.assertFalse(d.passed)
        self.assertIn("snapshot_name_resolves_to_different_current_species", d.reasons)
        self.assertEqual(d.frozen_historical_specieskeys, ())

    def test_completed_current_no_match_is_audited_not_conflict(self):
        rows = (self.row("Historical name", "11", "FORM"),)
        d = evaluate_successor_snapshot_species_concept_closure(
            current_accepted_species="Example species",
            taxonomy_tuples=rows,
            current_name_resolutions={"Historical name": self.review("Historical name", None)},
        )
        self.assertTrue(d.passed)
        self.assertEqual(d.current_unresolved_historical_names, ("Historical name",))

    def test_incomplete_review_fails_closed(self):
        rows = (self.row("Historical name", "11", "VARIETY"),)
        d = evaluate_successor_snapshot_species_concept_closure(
            current_accepted_species="Example species",
            taxonomy_tuples=rows,
            current_name_resolutions={"Historical name": self.review("Historical name", None, complete=False)},
        )
        self.assertFalse(d.passed)
        self.assertIn("current_taxonomy_closure_review_incomplete", d.reasons)

    def test_all_historical_keys_freeze_together(self):
        rows = (
            self.row("Historical name A", "11", "SPECIES"),
            self.row("Historical name B", "22", "SUBSPECIES"),
        )
        d = evaluate_successor_snapshot_species_concept_closure(
            current_accepted_species="Example species",
            taxonomy_tuples=rows,
            current_name_resolutions={
                "Historical name A": self.review("Historical name A", "Example species"),
                "Historical name B": self.review("Historical name B", "Example species"),
            },
        )
        self.assertTrue(d.passed)
        self.assertEqual(d.frozen_historical_specieskeys, ("11", "22"))


if __name__ == "__main__":
    unittest.main()
