import unittest

from product_b_v7_3.pair_admission import (
    MIN_DIRECT_WITNESS_SITES,
    MIN_PREDECLARED_CONTROLS,
    ProspectivePairDeclaration,
    ReplacementHostInteractionEvidence,
    evaluate_pair_admission,
    evaluate_replacement_host_interaction_screen,
)


def declaration(**overrides):
    payload = dict(
        pair_id="NEW001",
        x_biological_name="Host species",
        y_biological_name="Dependent species",
        direction="Y_requires_X",
        dependency_class="obligate_nursery_pollination",
        y_obligately_requires_x=True,
        y_host_specificity_supported=True,
        direct_primary_witness_site_ids=tuple(f"W{i:02d}" for i in range(1, 11)),
        independent_host_regions=("region_a", "region_b"),
        predeclared_control_taxa=tuple(f"Control species {i}" for i in range(1, 9)),
        snapshot_occurrence_information_used_for_selection=False,
        declaration_frozen=True,
    )
    payload.update(overrides)
    return ProspectivePairDeclaration(**payload)


def clean_interaction_evidence():
    return tuple(
        ReplacementHostInteractionEvidence(
            control_taxon=f"Control species {i}",
            screen_completed=True,
            dependent_uses_control_as_host=False,
        )
        for i in range(1, 9)
    )


class V73PairAdmissionTests(unittest.TestCase):
    def test_complete_response_blind_declaration_passes(self):
        result = evaluate_pair_admission(declaration())
        self.assertTrue(result.passed, result.reasons)
        self.assertEqual(result.direct_witness_site_count, MIN_DIRECT_WITNESS_SITES)
        self.assertEqual(result.predeclared_control_count, MIN_PREDECLARED_CONTROLS)

    def test_nine_direct_sites_do_not_pass(self):
        result = evaluate_pair_admission(
            declaration(direct_primary_witness_site_ids=tuple(f"W{i:02d}" for i in range(1, 10)))
        )
        self.assertFalse(result.passed)
        self.assertIn("direct_primary_witness_site_floor_failed", result.reasons)

    def test_one_host_region_does_not_pass(self):
        result = evaluate_pair_admission(declaration(independent_host_regions=("region_a",)))
        self.assertFalse(result.passed)
        self.assertIn("independent_host_region_floor_failed", result.reasons)

    def test_seven_controls_are_not_rescued(self):
        result = evaluate_pair_admission(
            declaration(predeclared_control_taxa=tuple(f"Control species {i}" for i in range(1, 8)))
        )
        self.assertFalse(result.passed)
        self.assertIn("predeclared_control_floor_failed", result.reasons)

    def test_snapshot_occurrence_informed_selection_is_forbidden(self):
        result = evaluate_pair_admission(
            declaration(snapshot_occurrence_information_used_for_selection=True)
        )
        self.assertFalse(result.passed)
        self.assertIn("snapshot_occurrence_selection_forbidden", result.reasons)

    def test_firewalled_jos003_cannot_reenter(self):
        result = evaluate_pair_admission(declaration(pair_id="JOS003"))
        self.assertFalse(result.passed)
        self.assertIn("pair_is_firewalled", result.reasons)

    def test_firewalled_crot001_cannot_reenter_after_dependency_conflict(self):
        result = evaluate_pair_admission(declaration(pair_id="CROT001"))
        self.assertFalse(result.passed)
        self.assertIn("pair_is_firewalled", result.reasons)

    def test_duplicates_do_not_inflate_witness_or_control_floors(self):
        result = evaluate_pair_admission(
            declaration(
                direct_primary_witness_site_ids=("W01",) * 10,
                predeclared_control_taxa=("Control one",) * 8,
            )
        )
        self.assertFalse(result.passed)
        self.assertIn("direct_primary_witness_site_floor_failed", result.reasons)
        self.assertIn("predeclared_control_floor_failed", result.reasons)

    def test_complete_adversarial_interaction_screen_passes_only_clean_frozen_pool(self):
        result = evaluate_replacement_host_interaction_screen(
            predeclared_control_taxa=declaration().predeclared_control_taxa,
            evidence=clean_interaction_evidence(),
        )
        self.assertTrue(result.passed, result.reasons)
        self.assertEqual(result.invalid_actual_host_controls, ())
        self.assertEqual(result.screened_control_count, 8)

    def test_actual_host_in_predeclared_control_pool_fails_without_rescue_path(self):
        evidence = list(clean_interaction_evidence())
        evidence[2] = ReplacementHostInteractionEvidence(
            control_taxon="Control species 3",
            screen_completed=True,
            dependent_uses_control_as_host=True,
        )
        result = evaluate_replacement_host_interaction_screen(
            predeclared_control_taxa=declaration().predeclared_control_taxa,
            evidence=tuple(evidence),
        )
        self.assertFalse(result.passed)
        self.assertIn("predeclared_control_is_actual_host", result.reasons)
        self.assertEqual(result.invalid_actual_host_controls, ("Control species 3",))

    def test_incomplete_or_changed_interaction_pool_fails_closed(self):
        evidence = clean_interaction_evidence()[:-1]
        result = evaluate_replacement_host_interaction_screen(
            predeclared_control_taxa=declaration().predeclared_control_taxa,
            evidence=evidence,
        )
        self.assertFalse(result.passed)
        self.assertIn("interaction_screen_not_exactly_frozen_control_pool", result.reasons)


if __name__ == "__main__":
    unittest.main()
