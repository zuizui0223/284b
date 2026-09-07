import ast
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FiniteFrameRepairV03Guards(unittest.TestCase):
    def _contract(self, name):
        return json.loads((ROOT / name).read_text())

    def _source_has_false_dict_entry(self, text, key):
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for k, v in zip(node.keys, node.values):
                if (
                    isinstance(k, ast.Constant)
                    and k.value == key
                    and isinstance(v, ast.Constant)
                    and v.value is False
                ):
                    return True
        return False

    def test_successor_v03_repairs_only_unresolved_cells_and_keeps_outcomes_closed(self):
        c = self._contract('config/product_b_same_target_reference_finite_frame_repair_contract_v0_3.json')
        self.assertEqual(c['contract_version'], 'product_b_same_target_reference_finite_frame_repair_v0.3')
        self.assertEqual(c['finite_frame']['final_background_points_per_taxon_M'], 2000)
        self.assertEqual(c['finite_frame']['candidate_background_points_for_unresolved_cell'],
                         'all_eligible_cells_no_fixed_oversampling_cap')
        self.assertEqual(c['finite_frame']['v0_2_frozen_cells'],
                         'inherit_frame_bytes_and_sha256_without_resampling')
        self.assertTrue(c['selection_invariance']['v0_2_unresolved_cells_only_repaired'])
        self.assertFalse(c['selection_invariance']['v0_2_frozen_frames_reselected'])
        for key in ('model_fit_allowed','prediction_score_computation_allowed',
                    'schoener_d_computation_allowed','reference_ceiling_computation_allowed',
                    'heldout_opening_allowed','process_knockout_allowed'):
            self.assertFalse(c['preflight'][key])
        self.assertFalse(c['empirical_ledger']['this_contract_counts_as_empirical_conclusion'])

    def test_heldout_v03_repairs_only_unresolved_cells_and_keeps_pairing_closed(self):
        c = self._contract('config/product_b_same_target_heldout_finite_frame_repair_contract_v0_3.json')
        self.assertEqual(c['contract_version'], 'product_b_same_target_heldout_finite_frame_repair_v0.3')
        self.assertEqual(c['heldout_taxa'], 12)
        self.assertEqual(c['taxon_M_cells'], 36)
        self.assertEqual(c['final_background_points_per_taxon_M'], 2000)
        self.assertEqual(c['candidate_background_points_for_unresolved_cell'],
                         'all_eligible_cells_no_fixed_oversampling_cap')
        self.assertEqual(c['v0_2_frozen_cells'],
                         'inherit_frame_bytes_and_sha256_without_resampling')
        self.assertTrue(c['selection_invariance']['v0_2_unresolved_cells_only_repaired'])
        self.assertFalse(c['selection_invariance']['v0_2_frozen_frames_reselected'])
        for key in ('model_refit_allowed','prediction_score_computation_allowed',
                    'paired_discordance_computation_allowed','reference_ceiling_read_allowed',
                    'heldout_pairing_allowed','process_knockout_allowed'):
            self.assertFalse(c['preflight'][key])
        self.assertFalse(c['preflight']['counts_as_empirical_conclusion'])

    def test_successor_v03_workflow_requires_exact_completed_v02_parent_summary(self):
        text = (ROOT / '.github/workflows/same_target_successor_finite_frame_preflight_v0_3.yml').read_text()
        self.assertIn('product_b_same_target_reference_finite_frame_preflight_trigger_v0_3.json', text)
        self.assertIn('product-b-successor-finite-frame-v0-2-preflight-summary', text)
        self.assertIn("run.get('status')!='completed'", text)
        self.assertIn("run.get('conclusion')!='success'", text)
        self.assertIn("str(art.get('digest'))", text)
        self.assertIn("taxon_M_cells_unresolved',0)) < 1", text)
        self.assertIn("'model_refit_authorized':False", text)
        self.assertIn("'heldout_opening_authorized':False", text)
        self.assertNotIn('workflow_dispatch:', text)

    def test_heldout_v03_workflow_requires_exact_completed_v02_parent_summary(self):
        text = (ROOT / '.github/workflows/same_target_heldout_finite_frame_preflight_v0_3.yml').read_text()
        self.assertIn('product_b_same_target_heldout_finite_frame_preflight_trigger_v0_3.json', text)
        self.assertIn('product-b-heldout-finite-frame-v0-2-preflight-summary', text)
        self.assertIn("run.get('status')!='completed'", text)
        self.assertIn("run.get('conclusion')!='success'", text)
        self.assertIn("str(art.get('digest'))", text)
        self.assertIn("taxon_M_cells_unresolved',0)) < 1", text)
        self.assertIn("'model_refit_authorized':False", text)
        self.assertIn("'heldout_pairing_authorized':False", text)
        self.assertNotIn('workflow_dispatch:', text)

    def test_v03_scripts_use_exhaustive_parent_preserving_path(self):
        successor = (ROOT / 'scripts/preflight_same_target_successor_finite_frame_v0_3.py').read_text()
        heldout = (ROOT / 'scripts/preflight_same_target_heldout_finite_frame_v0_3.py').read_text()
        for text in (successor, heldout):
            self.assertIn('n_points=max(1, len(target))', text)
            self.assertIn('inherit_v0_2_frozen_frame_byte_identical', text)
            self.assertIn('sha256(path.read_bytes()).hexdigest() != expected', text)
            self.assertIn('finite_comparison_frame_frozen', text)
            self.assertIn('candidate_seeds =', text)
            self.assertIn('final_seeds =', text)
            self.assertTrue(
                self._source_has_false_dict_entry(text, 'counts_as_empirical_conclusion')
            )
            self.assertNotIn('evaluate_same_target_heldout', text)

    def test_v03_refit_adapters_preserve_scientific_body_and_frame_provenance(self):
        paths = (
            'scripts/run_same_target_successor_layer1_fit_taxon_finite_frame_v0_3.py',
            'scripts/run_same_target_heldout_layer1_fit_taxon_finite_frame_v0_3.py',
        )
        for name in paths:
            text = (ROOT / name).read_text()
            self.assertIn('finite_frame_preflight_result_version', text)
            self.assertIn('finite_frame_parent_preflight_result_version', text)
            self.assertIn('v0_3_adapter_changed_frame_bytes', text)
            self.assertIn('v0_3_adapter_changed_model_fit_body', text)
            self.assertIn('base.main()', text)
            self.assertNotIn('schoener_d', text.lower())

    def test_v03_refit_workflows_require_exact_v03_summaries(self):
        successor = (ROOT / '.github/workflows/same_target_successor_finite_frame_refit_v0_3.yml').read_text()
        heldout = (ROOT / '.github/workflows/same_target_heldout_finite_frame_refit_v0_3.yml').read_text()
        self.assertIn('product-b-successor-finite-frame-v0-3-preflight-summary', successor)
        self.assertIn("'taxon_M_cells_frozen':141", successor)
        self.assertIn("'paired_discordance_opened':False", successor)
        self.assertIn('product-b-successor-finite-frame-repair-fit-audit-v0-3', successor)
        self.assertIn('product-b-heldout-finite-frame-v0-3-preflight-summary', heldout)
        self.assertIn("'taxon_M_cells_frozen':36", heldout)
        self.assertIn("'heldout_pairing_opened':False", heldout)
        self.assertIn('product-b-heldout-finite-frame-repair-fit-audit-v0-3', heldout)

    def test_v03_reference_requires_both_closed_refit_audits_before_D(self):
        text = (ROOT / '.github/workflows/same_target_successor_finite_frame_reference_calibration_v0_3.yml').read_text()
        self.assertIn('product-b-successor-finite-frame-repair-fit-audit-v0-3', text)
        self.assertIn('product-b-heldout-finite-frame-repair-fit-audit-v0-3', text)
        self.assertIn('audit_same_target_successor_reference_feasibility_finite_frame_repair_v0_3.py', text)
        self.assertIn('calibrate_same_target_successor_pairing_finite_frame_repair_v0_3.py', text)
        self.assertIn("'heldout_pairing_authorized':False", text)
        self.assertIn("'counts_as_empirical_conclusion':False", text)

    def test_v03_final_is_distinct_one_shot_exact_artifact_endpoint(self):
        workflow = (ROOT / '.github/workflows/same_target_heldout_final_finite_frame_repair_v0_3.yml').read_text()
        evaluator = (ROOT / 'scripts/evaluate_same_target_heldout_final_finite_frame_repair_v0_3.py').read_text()
        self.assertIn("GITHUB_RUN_ATTEMPT')!='1", workflow)
        self.assertIn("'one_shot':True", workflow)
        self.assertIn('heldout_taxon_artifacts', workflow)
        self.assertIn('product-b-successor-finite-frame-repair-reference-v0-3', workflow)
        self.assertIn('product-b-heldout-finite-frame-repair-fit-audit-v0-3', workflow)
        self.assertIn('evaluate_same_target_heldout_final_finite_frame_repair_v0_3.py', workflow)
        self.assertIn("r['counts_as_empirical_conclusion'] is True", workflow)
        self.assertIn('base._load_heldout = _load_heldout_v3', evaluator)
        self.assertIn('base.REFERENCE_RESULT = REFERENCE_RESULT_V3', evaluator)
        self.assertIn('v0_3_adapter_changed_scientific_evaluation_body', evaluator)
        self.assertNotIn('process_knockout_computed(', evaluator)


if __name__ == '__main__':
    unittest.main()
