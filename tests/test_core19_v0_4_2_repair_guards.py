from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Core19V042RepairGuards(unittest.TestCase):
    def test_serialization_repair_is_successor_only_and_outcome_blind(self):
        w = (ROOT / '.github/workflows/same_target_core19_successor_serialization_repair_v0_4_2.yml').read_text()
        self.assertIn("'successor_sealed_fit_cells':0", w)
        self.assertIn("'heldout_sealed_fit_cells':576", w)
        self.assertIn("'failed_fit_cells':2256", w)
        self.assertIn('pandas_list_length_assignment_mismatch', w)
        self.assertIn("'heldout_artifact_inheritance_authorized':True", w)
        self.assertIn("'heldout_refit_authorized':False", w)
        self.assertIn("'paired_discordance_authorized':False", w)
        self.assertIn("'reference_ceiling_authorized':False", w)
        self.assertIn("'heldout_pairing_authorized':False", w)
        self.assertIn("'process_knockout_authorized':False", w)
        self.assertIn("'result_version':'product_b_same_target_core19_fit_audit_v0.4'", w)
        self.assertIn("'successor_serialization_repair_version':'v0.4.2'", w)
        self.assertIn("'successor_sealed_fit_cells':ss", w)
        self.assertIn("'heldout_fit_artifacts_inherited_from_parent':True", w)

    def test_reference_requires_repaired_exact_audit_not_parent_failed_audit(self):
        w = (ROOT / '.github/workflows/same_target_core19_reference_calibration_v0_4_2.yml').read_text()
        self.assertIn('product-b-core19-v0-4-fit-audit', w)
        self.assertIn("'result_version':'product_b_same_target_core19_fit_audit_v0.4'", w)
        self.assertIn("'successor_serialization_repair_version':'v0.4.2'", w)
        self.assertIn("'successor_sealed_fit_cells':2256", w)
        self.assertIn("'successor_unresolved_fit_cells':0", w)
        self.assertIn("'heldout_sealed_fit_cells':576", w)
        self.assertIn("'heldout_unresolved_fit_cells':0", w)
        self.assertIn("'heldout_fit_artifacts_inherited_from_parent':True", w)
        self.assertNotIn("'successor_sealed_fit_cells':0", w)
        self.assertIn('product-b-core19-v0-4-2-reference', w)
        self.assertIn("s['heldout_12_paired_discordance_read'] is False", w)
        self.assertIn("s['quantile_method']=='nearest_rank'", w)

    def test_final_keeps_scientific_v04_endpoint_and_is_one_shot(self):
        w = (ROOT / '.github/workflows/same_target_core19_heldout_final_v0_4_2.yml').read_text()
        self.assertIn("GITHUB_RUN_ATTEMPT')!='1", w)
        self.assertIn("'endpoint_id':'same_target_cross_source_reproducibility_heldout12_core19_v0_4'", w)
        self.assertIn("'reference_result_version':'product_b_same_target_successor_pairing_calibration_core19_v0.4'", w)
        self.assertIn("'heldout_fit_result_version':'product_b_same_target_heldout_core19_layer1_fit_taxon_v0.4'", w)
        self.assertIn('product-b-core19-v0-4-2-reference', w)
        self.assertIn('product-b-core19-v0-4-fit-audit', w)
        self.assertIn("'successor_serialization_repair_version':'v0.4.2'", w)
        self.assertIn("'heldout_fit_artifacts_inherited_from_parent':True", w)
        self.assertIn("'procedure_selection_authorized':False", w)
        self.assertIn("'M_selection_authorized':False", w)
        self.assertIn("'taxon_replacement_authorized':False", w)
        self.assertIn("'process_knockout_authorized':False", w)
        self.assertIn("r['terminal_class']=='empirical_result'", w)
        self.assertIn("r['counts_as_empirical_conclusion'] is True", w)


if __name__ == '__main__':
    unittest.main()
