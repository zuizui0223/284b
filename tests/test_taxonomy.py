import csv
import unittest
from pathlib import Path

from product_b_v5.taxonomy import (
    DIRECT_PROVENANCE,
    LEGACY_GBIF_BACKBONE,
    LEGACY_GBIF_CHECKLIST_KEY,
    PAIR_ELIGIBLE,
    PAIR_UNRESOLVED,
    RESOLVED,
    SECONDARY_PROVENANCE,
    UNRESOLVED_CONCEPT,
    UNRESOLVED_MISSING_KEY,
    TaxonomyOverlayRow,
    validate_taxonomy_registry,
    validate_taxonomy_row,
)


def make_row(**overrides):
    values = dict(
        pair_id="OPM_TEST_001",
        x_literature_name="Plantus example",
        y_literature_name="Mothus example",
        matching_checklist=LEGACY_GBIF_BACKBONE,
        checklist_key=LEGACY_GBIF_CHECKLIST_KEY,
        x_resolved_name="Plantus example",
        x_legacy_gbif_key="123",
        x_key_provenance=DIRECT_PROVENANCE,
        x_taxonomy_state=RESOLVED,
        y_resolved_name="Mothus example",
        y_legacy_gbif_key="456",
        y_key_provenance=DIRECT_PROVENANCE,
        y_taxonomy_state=RESOLVED,
        pair_taxonomy_state=PAIR_ELIGIBLE,
        sampling_preflight_eligible="true",
        taxonomy_note="Synthetic direct exact-key case.",
    )
    values.update(overrides)
    return TaxonomyOverlayRow(**values)


class TaxonomyRowTests(unittest.TestCase):
    def test_two_direct_exact_keys_can_be_sampling_preflight_eligible(self):
        self.assertEqual(validate_taxonomy_row(make_row()), ())

    def test_secondary_key_cannot_silently_authorize_sampling(self):
        row = make_row(
            y_key_provenance=SECONDARY_PROVENANCE,
            pair_taxonomy_state=PAIR_UNRESOLVED,
            sampling_preflight_eligible="false",
        )
        self.assertEqual(validate_taxonomy_row(row), ())

        bad = make_row(y_key_provenance=SECONDARY_PROVENANCE)
        errors = validate_taxonomy_row(bad)
        self.assertIn("sampling_eligibility_requires_two_direct_exact_keys", errors)

    def test_concept_conflict_cannot_be_sampling_eligible(self):
        row = make_row(
            x_legacy_gbif_key="",
            x_key_provenance="",
            x_taxonomy_state=UNRESOLVED_CONCEPT,
            pair_taxonomy_state=PAIR_UNRESOLVED,
            sampling_preflight_eligible="false",
        )
        self.assertEqual(validate_taxonomy_row(row), ())

    def test_missing_key_state_cannot_carry_a_key(self):
        row = make_row(
            y_taxonomy_state=UNRESOLVED_MISSING_KEY,
            y_legacy_gbif_key="456",
            y_key_provenance=DIRECT_PROVENANCE,
            pair_taxonomy_state=PAIR_UNRESOLVED,
            sampling_preflight_eligible="false",
        )
        errors = validate_taxonomy_row(row)
        self.assertIn("y:missing_key_state_must_not_have_key", errors)

    def test_checklist_cannot_change_silently(self):
        errors = validate_taxonomy_row(make_row(checklist_key="different-checklist"))
        self.assertIn("checklist_key_not_frozen", errors)


class CommittedTaxonomyRegistryTests(unittest.TestCase):
    def _taxonomy_rows(self):
        path = Path("registry/obligate_pair_registry_taxonomy_v0_1.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            return tuple(TaxonomyOverlayRow(**row) for row in csv.DictReader(handle))

    def test_committed_taxonomy_overlay_passes(self):
        rows = self._taxonomy_rows()
        self.assertEqual(len(rows), 7)
        result = validate_taxonomy_registry(rows)
        self.assertTrue(result.passed, result.errors)

    def test_only_directly_verified_pair_is_sampling_preflight_eligible(self):
        rows = self._taxonomy_rows()
        eligible = [row.pair_id for row in rows if row.eligible_bool]
        self.assertEqual(eligible, ["OPM_FIG_001"])

    def test_taxonomy_overlay_is_nonretroactive_to_literature_registry(self):
        literature_path = Path("registry/obligate_pair_registry_literature_v0_1.csv")
        with literature_path.open(newline="", encoding="utf-8") as handle:
            literature = {
                row["pair_id"]: (row["x_taxon_name"], row["y_taxon_name"])
                for row in csv.DictReader(handle)
            }

        taxonomy = {
            row.pair_id: (row.x_literature_name, row.y_literature_name)
            for row in self._taxonomy_rows()
        }
        self.assertEqual(taxonomy, literature)


if __name__ == "__main__":
    unittest.main()
