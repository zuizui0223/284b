import csv
import unittest
from pathlib import Path

from product_b_v5.registry import (
    LiteraturePairDeclaration,
    validate_literature_pair,
    validate_literature_registry,
)


def make_row(**overrides):
    values = dict(
        pair_id="OPM_TEST_001",
        x_taxon_name="Plantus example",
        y_taxon_name="Mothus example",
        x_taxon_key="",
        y_taxon_key="",
        taxon_key_status="pending_response_blind_taxonomy_resolution",
        obligacy_class="obligate_pollination_mutualism",
        direction="Y_requires_X",
        literature_doi="10.1234/example.1",
        evidence_type="primary_host_specificity_study",
        association_scale="reproductive_host_dependence",
        declared_geographic_scope="declared test region",
        registry_state="eligible_literature_only",
        known_boundary="Direction is no stronger than the literature evidence.",
    )
    values.update(overrides)
    return LiteraturePairDeclaration(**values)


class LiteraturePairValidationTests(unittest.TestCase):
    def test_valid_phase1_directional_pair_passes(self):
        self.assertEqual(validate_literature_pair(make_row()), ())

    def test_bidirectional_pair_is_rejected_in_phase1(self):
        errors = validate_literature_pair(make_row(direction="bidirectional"))
        self.assertIn("phase1_direction_must_be_Y_requires_X", errors)

    def test_taxon_keys_cannot_be_prepopulated_during_literature_step(self):
        errors = validate_literature_pair(make_row(x_taxon_key="12345"))
        self.assertIn("literature_step_must_not_prepopulate_taxon_keys", errors)

    def test_missing_geographic_scope_is_rejected(self):
        errors = validate_literature_pair(make_row(declared_geographic_scope=""))
        self.assertIn("missing_required_field:declared_geographic_scope", errors)

    def test_known_boundary_is_mandatory(self):
        errors = validate_literature_pair(make_row(known_boundary=""))
        self.assertIn("missing_required_field:known_boundary", errors)

    def test_non_phase1_obligacy_class_is_rejected(self):
        errors = validate_literature_pair(
            make_row(obligacy_class="obligate_host_specific_parasitoid")
        )
        self.assertIn("phase1_obligacy_class_not_allowed", errors)


class LiteratureRegistryValidationTests(unittest.TestCase):
    def test_same_host_can_have_two_dependent_pollinators(self):
        rows = (
            make_row(
                pair_id="OPM_TEST_001",
                x_taxon_name="Plantus shared",
                y_taxon_name="Mothus alpha",
            ),
            make_row(
                pair_id="OPM_TEST_002",
                x_taxon_name="Plantus shared",
                y_taxon_name="Mothus beta",
            ),
        )
        result = validate_literature_registry(rows)
        self.assertTrue(result.passed)

    def test_duplicate_directed_pair_is_rejected(self):
        rows = (
            make_row(pair_id="OPM_TEST_001"),
            make_row(pair_id="OPM_TEST_002"),
        )
        result = validate_literature_registry(rows)
        self.assertFalse(result.passed)
        self.assertIn("row_1:duplicate_directed_pair", result.errors)

    def test_duplicate_pair_id_is_rejected(self):
        rows = (
            make_row(pair_id="OPM_TEST_DUP", y_taxon_name="Mothus alpha"),
            make_row(pair_id="OPM_TEST_DUP", y_taxon_name="Mothus beta"),
        )
        result = validate_literature_registry(rows)
        self.assertFalse(result.passed)
        self.assertIn("row_1:duplicate_pair_id", result.errors)

    def test_empty_registry_is_rejected(self):
        result = validate_literature_registry(())
        self.assertFalse(result.passed)
        self.assertIn("registry_must_not_be_empty", result.errors)

    def test_committed_literature_registry_passes_validator(self):
        path = Path("registry/obligate_pair_registry_literature_v0_1.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = tuple(
                LiteraturePairDeclaration(**row)
                for row in csv.DictReader(handle)
            )

        self.assertEqual(len(rows), 7)
        result = validate_literature_registry(rows)
        self.assertTrue(result.passed, result.errors)


if __name__ == "__main__":
    unittest.main()
