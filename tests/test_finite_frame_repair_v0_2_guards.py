import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FiniteFrameRepairV02Guards(unittest.TestCase):
    def test_successor_v02_widens_only_candidate_pool_and_keeps_outcomes_closed(self):
        c = json.loads((ROOT / 'config/product_b_same_target_reference_finite_frame_repair_contract_v0_2.json').read_text())
        self.assertEqual(c['contract_version'], 'product_b_same_target_reference_finite_frame_repair_v0.2')
        self.assertEqual(c['finite_frame']['candidate_background_points_per_taxon_M'], 32000)
        self.assertEqual(c['finite_frame']['final_background_points_per_taxon_M'], 2000)
        self.assertEqual(c['unchanged_scientific_rules']['minimum_complete_calibration_taxa_per_procedure_M'], 30)
        self.assertEqual(c['unchanged_scientific_rules']['reference_quantile'], 0.95)
        self.assertEqual(c['unchanged_scientific_rules']['quantile_method'], 'nearest_rank')
        for key in ('model_fit_allowed','prediction_score_computation_allowed','schoener_d_computation_allowed','reference_ceiling_computation_allowed','heldout_opening_allowed','process_knockout_allowed'):
            self.assertFalse(c['preflight'][key])
        self.assertFalse(c['empirical_ledger']['this_contract_counts_as_empirical_conclusion'])

    def test_heldout_v02_is_frozen_before_reference_and_pairing(self):
        c = json.loads((ROOT / 'config/product_b_same_target_heldout_finite_frame_repair_contract_v0_2.json').read_text())
        self.assertEqual(c['candidate_background_points_per_taxon_M'], 32000)
        self.assertEqual(c['final_background_points_per_taxon_M'], 2000)
        self.assertEqual(c['taxon_M_cells'], 36)
        for key in ('model_refit_allowed','prediction_score_computation_allowed','paired_discordance_computation_allowed','reference_ceiling_read_allowed','heldout_pairing_allowed','process_knockout_allowed'):
            self.assertFalse(c['preflight'][key])
        self.assertFalse(c['preflight']['counts_as_empirical_conclusion'])

    def test_successor_v02_refit_accepts_only_v02_summary_and_keeps_pairing_closed(self):
        text = (ROOT / '.github/workflows/same_target_successor_finite_frame_refit_v0_2.yml').read_text()
        self.assertIn("product_b_same_target_successor_finite_frame_preflight_v0.2", text)
        self.assertIn("product-b-successor-finite-frame-v0-2-preflight-summary", text)
        self.assertIn("taxon_M_cells_frozen':141", text)
        self.assertIn("'paired_discordance_opened':False", text)
        self.assertIn("'heldout_12_paired_discordance_read':False", text)
        self.assertNotIn('same_target_heldout_crosscheck_strict.py', text)

    def test_heldout_v02_refit_requires_36_of_36_and_never_reads_reference(self):
        text = (ROOT / '.github/workflows/same_target_heldout_finite_frame_refit_v0_2.yml').read_text()
        self.assertIn("product_b_same_target_heldout_finite_frame_preflight_v0.2", text)
        self.assertIn("taxon_M_cells_frozen':36", text)
        self.assertIn("'reference_ceiling_read':False", text)
        self.assertIn("'heldout_pairing_opened':False", text)
        self.assertNotIn('repaired_reference_ceiling', text)
        self.assertNotIn('evaluate_same_target_heldout_crosscheck', text)

    def test_reference_D_waits_for_both_repaired_fit_audits(self):
        text = (ROOT / '.github/workflows/same_target_successor_finite_frame_reference_calibration.yml').read_text()
        self.assertIn('product-b-successor-finite-frame-repair-fit-audit', text)
        self.assertIn('product-b-heldout-finite-frame-repair-fit-audit', text)
        self.assertIn("'heldout_pairing_authorized':False", text)
        self.assertIn("assert s['heldout_12_paired_discordance_read'] is False", text)


if __name__ == '__main__':
    unittest.main()
