import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = [f"bio{i}" for i in range(1, 20)]


class Core19V04Guards(unittest.TestCase):
    def test_contract_preserves_all43_terminal_and_defines_distinct_uniform_endpoint(self):
        c = json.loads((ROOT / 'config/product_b_same_target_core19_requalification_contract_v0_4.json').read_text())
        self.assertEqual(c['contract_version'], 'product_b_same_target_core19_requalification_v0.4')
        self.assertTrue(c['endpoint_versioning']['all43_v0_3_endpoint_is_not_redefined'])
        self.assertTrue(c['endpoint_versioning']['all43_v0_3_structural_unresolved_state_is_preserved'])
        self.assertEqual(c['endpoint_versioning']['future_endpoint_id'], 'same_target_cross_source_reproducibility_heldout12_core19_v0_4')
        self.assertEqual(c['predictor_universe']['expected_predictors_in_manifest_order'], CORE)
        self.assertTrue(c['predictor_universe']['alternate_subset_selection_after_diagnostic_forbidden'])
        self.assertTrue(c['predictor_universe']['raw_zero_reinterpretation_without_separate_encoding_proof_forbidden'])
        q = c['uniform_requalification']
        self.assertEqual((q['successor_taxa'], q['heldout_taxa']), (47, 12))
        self.assertTrue(q['all_taxa_are_requalified_from_coordinates_not_only_v0_3_unresolved_taxa'])
        self.assertTrue(q['all43_v0_3_frame_bytes_are_not_reused_as_core19_frames'])
        self.assertEqual(q['final_background_points_per_taxon_M'], 2000)
        for key, value in c['information_boundary'].items():
            if key.startswith('qualification_'):
                self.assertFalse(value)
        self.assertFalse(c['information_boundary']['counts_as_empirical_conclusion'])

    def test_all43_structural_unresolved_receipt_cannot_be_recast_empirical(self):
        r = json.loads((ROOT / 'results/product_b_same_target_all43_v0_3_structural_unresolved_receipt.json').read_text())
        self.assertEqual(r['successor_preflight']['taxon_M_cells_unresolved'], 10)
        self.assertEqual(r['heldout_preflight']['taxon_M_cells_unresolved'], 4)
        self.assertTrue(r['all43_endpoint_disposition']['endpoint_redefinition_forbidden'])
        self.assertFalse(r['all43_endpoint_disposition']['model_refit_authorized'])
        self.assertFalse(r['all43_endpoint_disposition']['paired_discordance_opened'])
        self.assertFalse(r['all43_endpoint_disposition']['heldout_pairing_opened'])
        self.assertFalse(r['counts_as_empirical_conclusion'])
        self.assertFalse(r['counts_as_empirical_evidence'])

    def test_core19_qualification_is_uniform_outcome_blind_and_exact_diagnostic_gated(self):
        workflow = (ROOT / '.github/workflows/same_target_core19_qualification_v0_4.yml').read_text()
        script = (ROOT / 'scripts/preflight_same_target_core19_taxon_v0_4.py').read_text()
        self.assertIn('product-b-v0-4-predictor-availability-diagnostic-summary', workflow)
        self.assertIn("'core19_cells_ready_for_2000':14", workflow)
        self.assertIn("'core19_cells_not_ready_for_2000':0", workflow)
        self.assertIn("'all_14_unresolved_cells_core19_ready_for_2000':True", workflow)
        self.assertIn('taxon_index: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46]', workflow)
        self.assertIn('taxon_index: [0,1,2,3,4,5,6,7,8,9,10,11]', workflow)
        self.assertIn('candidate_class', script)
        self.assertIn('core_climate', script)
        self.assertIn('n_points=max(1, len(target))', script)
        self.assertIn('parent_v0_3_frame_bytes_reused', script)
        self.assertIn('"parent_v0_3_frame_bytes_reused": False', script)
        self.assertIn('"model_fit_opened": False', script)
        self.assertIn('"paired_discordance_opened": False', script)
        self.assertIn('"heldout_pairing_opened": False', script)
        self.assertNotIn('evaluate_same_target_heldout_final', script)

    def test_core19_refit_requires_177_qualified_frames_and_keeps_pairing_closed(self):
        workflow = (ROOT / '.github/workflows/same_target_core19_refit_v0_4.yml').read_text()
        script = (ROOT / 'scripts/run_same_target_core19_layer1_fit_taxon_v0_4.py').read_text()
        self.assertIn('product-b-core19-v0-4-qualification-summary', workflow)
        self.assertIn("'successor_cells_frozen':141", workflow)
        self.assertIn("'heldout_cells_frozen':36", workflow)
        self.assertIn("'all_177_core19_frames_ready_for_review':True", workflow)
        self.assertIn("'paired_discordance_opened':False", workflow)
        self.assertIn("'heldout_pairing_opened':False", workflow)
        self.assertIn('product-b-core19-v0-4-fit-audit', workflow)
        self.assertIn('core19_layer1_model_fit_sealed', script)
        self.assertIn('all_prediction_scores_finite_for_sealed_cells', script)
        self.assertIn('"paired_discordance_computed":False', script)
        self.assertIn('"heldout_pairing_opened":False', script)

    def test_core19_reference_opens_only_successor_D_and_keeps_heldout_closed(self):
        workflow = (ROOT / '.github/workflows/same_target_core19_reference_calibration_v0_4.yml').read_text()
        self.assertIn('product-b-core19-v0-4-fit-audit', workflow)
        self.assertIn('audit_same_target_successor_reference_feasibility_core19_v0_4.py', workflow)
        self.assertIn('calibrate_same_target_successor_pairing_core19_v0_4.py', workflow)
        self.assertIn("s['minimum_eligible_taxa_per_procedure_M']==30", workflow)
        self.assertIn("s['reference_quantile']==0.95", workflow)
        self.assertIn("s['quantile_method']=='nearest_rank'", workflow)
        self.assertIn("s['heldout_12_paired_discordance_read'] is False", workflow)
        self.assertIn("'heldout_pairing_authorized':False", workflow)
        self.assertIn("'counts_as_empirical_conclusion':False", workflow)

    def test_only_core19_final_is_one_shot_empirical_opening_surface(self):
        workflow = (ROOT / '.github/workflows/same_target_core19_heldout_final_v0_4.yml').read_text()
        evaluator = (ROOT / 'scripts/evaluate_same_target_heldout_final_core19_v0_4.py').read_text()
        self.assertIn("GITHUB_RUN_ATTEMPT')!='1", workflow)
        self.assertIn("'one_shot':True", workflow)
        self.assertIn("'procedure_selection_authorized':False", workflow)
        self.assertIn("'M_selection_authorized':False", workflow)
        self.assertIn("'taxon_replacement_authorized':False", workflow)
        self.assertIn('heldout_taxon_artifacts', workflow)
        self.assertIn("r['terminal_class']=='empirical_result'", workflow)
        self.assertIn("r['counts_as_empirical_conclusion'] is True", workflow)
        self.assertIn("r['process_knockout_opened'] is False", workflow)
        self.assertIn('provenance_adapter_changed_scientific_evaluation_body', evaluator)
        self.assertNotIn('process_knockout_computed(', evaluator)


if __name__ == '__main__':
    unittest.main()
