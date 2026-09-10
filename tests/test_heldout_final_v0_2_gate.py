import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class HeldoutFinalV02GateTests(unittest.TestCase):
    def test_legacy_final_path_is_fail_closed(self):
        text=(ROOT/'.github/workflows/same_target_heldout_final_finite_frame_repair.yml').read_text(encoding='utf-8')
        self.assertIn('legacy-deprecated', text)
        self.assertIn('exit 1', text)
        self.assertNotIn('evaluate_same_target_heldout_final_finite_frame_repair.py', text)

    def test_v02_final_requires_v02_reference_and_new_authorization(self):
        text=(ROOT/'.github/workflows/same_target_heldout_final_finite_frame_repair_v0_2.yml').read_text(encoding='utf-8')
        self.assertIn('product_b_same_target_heldout_final_authorization_v0_2.json', text)
        self.assertIn('product-b-successor-finite-frame-repair-reference-v0-2', text)
        self.assertIn('product_b_same_target_successor_pairing_calibration_finite_frame_repair_v0.2', text)
        self.assertIn('product_b_same_target_heldout_finite_frame_repair_fit_audit_v0.2', text)
        self.assertIn("GITHUB_RUN_ATTEMPT", text)
        self.assertIn("heldout_taxon_artifact_count':12", text)
        self.assertIn('evaluate_same_target_heldout_final_finite_frame_repair_v0_2.py', text)

    def test_v02_evaluator_changes_only_provenance_identity(self):
        text=(ROOT/'scripts/evaluate_same_target_heldout_final_finite_frame_repair_v0_2.py').read_text(encoding='utf-8')
        self.assertIn('base.REFERENCE_RESULT = REFERENCE_RESULT_V0_2', text)
        self.assertIn('product_b_same_target_successor_pairing_calibration_finite_frame_repair_v0.2', text)
        self.assertIn('product_b_same_target_heldout_final_finite_frame_repair_v0.2', text)
        self.assertIn('same_target_cross_source_reproducibility_heldout12_finite_frame_v0_2', text)
        self.assertIn('base.main()', text)


if __name__ == '__main__':
    unittest.main()
