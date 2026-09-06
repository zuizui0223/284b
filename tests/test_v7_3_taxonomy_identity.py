import json
from pathlib import Path
import unittest

from product_b_v7_3.taxonomy_identity import (
    ALLOWED_COLUMNS,
    SnapshotIdentityDeclaration,
    SnapshotTaxonomyTuple,
    canonicalize_taxonomy_rows,
    evaluate_snapshot_taxonomy_identity,
    evaluate_v7_3_contract,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_v7_3_snapshot_taxonomy_identity_contract_v0_1.json"


def declaration(**overrides):
    payload = dict(
        pair_id="NEW001",
        taxon_role="x",
        biological_name="Example host",
        current_accepted_name="Example host",
        admissible_species_names=("Example host",),
        declaration_frozen=True,
        snapshot_taxonomy_access_started=False,
    )
    payload.update(overrides)
    return SnapshotIdentityDeclaration(**payload)


def row(*, species="Example host", specieskey="123", taxonkey="123", scientificname="Example host Author", taxonrank="SPECIES"):
    return SnapshotTaxonomyTuple(species, specieskey, taxonkey, scientificname, taxonrank)


class V73ContractTests(unittest.TestCase):
    def test_committed_contract_passes_and_keeps_sampling_closed(self):
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(evaluate_v7_3_contract(data), ())
        self.assertEqual(tuple(data["allowed_snapshot_columns"]), ALLOWED_COLUMNS)
        self.assertFalse(data["sampling_authorization_from_this_gate"])
        self.assertFalse(data["matched_row_counts_may_be_persisted"])

    def test_jos003_is_firewalled(self):
        decision = evaluate_snapshot_taxonomy_identity(
            declaration=declaration(pair_id="JOS003"),
            taxonomy_tuples=(row(),),
        )
        self.assertFalse(decision.passed)
        self.assertIn("pair_is_firewalled", decision.reasons)


class V73SanitizerTests(unittest.TestCase):
    def test_raw_rows_collapse_to_distinct_taxonomy_tuples_without_counts(self):
        rows = [
            {"species":"Example host","specieskey":"123","taxonkey":"123","scientificname":"Example host A","taxonrank":"SPECIES","gbifid":"hidden-1"},
            {"species":"Example host","specieskey":"123","taxonkey":"123","scientificname":"Example host A","taxonrank":"SPECIES","gbifid":"hidden-2"},
        ]
        result = canonicalize_taxonomy_rows(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].specieskey, "123")
        self.assertFalse(hasattr(result[0], "gbifid"))


class V73IdentityDecisionTests(unittest.TestCase):
    def test_one_predeclared_specieskey_passes(self):
        decision = evaluate_snapshot_taxonomy_identity(
            declaration=declaration(),
            taxonomy_tuples=(row(),),
        )
        self.assertTrue(decision.passed, decision.reasons)
        self.assertEqual(decision.resolved_specieskey, "123")
        self.assertEqual(decision.terminal_state, "snapshot_taxonomy_identity_passed")

    def test_zero_tuple_is_terminal_unresolved(self):
        decision = evaluate_snapshot_taxonomy_identity(
            declaration=declaration(), taxonomy_tuples=()
        )
        self.assertFalse(decision.passed)
        self.assertIn("no_snapshot_taxonomy_tuple", decision.reasons)

    def test_multiple_specieskeys_are_not_rescued(self):
        decision = evaluate_snapshot_taxonomy_identity(
            declaration=declaration(),
            taxonomy_tuples=(row(specieskey="123"), row(specieskey="456", taxonkey="456")),
        )
        self.assertFalse(decision.passed)
        self.assertIn("snapshot_specieskey_not_unique", decision.reasons)

    def test_undeclared_species_concept_fails(self):
        decision = evaluate_snapshot_taxonomy_identity(
            declaration=declaration(),
            taxonomy_tuples=(row(species="Other species"),),
        )
        self.assertFalse(decision.passed)
        self.assertIn("undeclared_species_concept_returned", decision.reasons)

    def test_synonym_name_can_pass_only_if_predeclared_before_access(self):
        declared = declaration(
            biological_name="Old host",
            current_accepted_name="Accepted host",
            admissible_species_names=("Old host", "Accepted host"),
        )
        decision = evaluate_snapshot_taxonomy_identity(
            declaration=declared,
            taxonomy_tuples=(row(species="Accepted host", specieskey="789", taxonkey="789"),),
        )
        self.assertTrue(decision.passed, decision.reasons)
        self.assertEqual(decision.resolved_specieskey, "789")

    def test_declaration_after_snapshot_access_is_invalid(self):
        decision = evaluate_snapshot_taxonomy_identity(
            declaration=declaration(snapshot_taxonomy_access_started=True),
            taxonomy_tuples=(row(),),
        )
        self.assertFalse(decision.passed)
        self.assertIn("declaration_created_after_snapshot_access", decision.reasons)


if __name__ == "__main__":
    unittest.main()
