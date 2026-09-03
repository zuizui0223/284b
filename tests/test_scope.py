import unittest

from product_b_v5.scope import (
    GeographicScopeDeclaration,
    ScopeState,
    require_scope_resolved,
    validate_scope_declaration,
    validate_scope_registry,
)


def unresolved_row(**overrides):
    values = dict(
        pair_id="OPM_FIG_001",
        literature_scope_text="continental Southeast Asia; southern China to southern Thailand",
        evidence_doi="10.1111/j.1365-294X.2010.04654.x",
        state=ScopeState.UNRESOLVED,
        filter_type="",
        filter_value="",
        scope_source_type="primary_literature_abstract",
        note="Machine-reconstructable extent not yet available.",
    )
    values.update(overrides)
    return GeographicScopeDeclaration(**values)


def resolved_row(**overrides):
    values = dict(
        pair_id="OPM_TEST_001",
        literature_scope_text="declared study region",
        evidence_doi="10.1234/example",
        state=ScopeState.RESOLVED,
        filter_type="bbox",
        filter_value="95.0,5.0,110.0,25.0",
        scope_source_type="primary_literature_supplement",
        note="Synthetic machine-reconstructable example.",
    )
    values.update(overrides)
    return GeographicScopeDeclaration(**values)


class GeographicScopeGateTests(unittest.TestCase):
    def test_unresolved_literature_scope_is_valid_but_not_execution_eligible(self):
        row = unresolved_row()
        self.assertEqual(validate_scope_declaration(row), ())
        result = validate_scope_registry((row,))
        self.assertTrue(result.passed)
        self.assertEqual(result.execution_eligible_pair_ids, ())

    def test_unresolved_scope_cannot_sneak_in_executable_filter(self):
        row = unresolved_row(filter_type="bbox", filter_value="1,2,3,4")
        errors = validate_scope_declaration(row)
        self.assertIn("unresolved_scope_must_not_carry_executable_filter", errors)

    def test_resolved_scope_requires_machine_reconstructable_filter(self):
        row = resolved_row(filter_value="")
        errors = validate_scope_declaration(row)
        self.assertIn("resolved_scope_requires_filter_value", errors)

    def test_occurrence_derived_scope_is_forbidden_even_if_machine_readable(self):
        row = resolved_row(scope_source_type="occurrence_convex_hull")
        errors = validate_scope_declaration(row)
        self.assertIn("occurrence_derived_scope_source_forbidden", errors)
        self.assertIn(
            "resolved_scope_requires_independent_machine_scope_source",
            errors,
        )

    def test_independent_resolved_scope_becomes_execution_eligible(self):
        row = resolved_row()
        result = validate_scope_registry((row,))
        self.assertTrue(result.passed)
        self.assertEqual(result.execution_eligible_pair_ids, ("OPM_TEST_001",))

    def test_require_scope_resolved_rejects_current_fig_scope(self):
        with self.assertRaisesRegex(ValueError, "operational geographic scope is unresolved"):
            require_scope_resolved((unresolved_row(),), pair_id="OPM_FIG_001")

    def test_duplicate_pair_id_is_rejected(self):
        result = validate_scope_registry(
            (
                unresolved_row(),
                unresolved_row(note="duplicate"),
            )
        )
        self.assertFalse(result.passed)
        self.assertIn("row_1:duplicate_pair_id", result.errors)


if __name__ == "__main__":
    unittest.main()
