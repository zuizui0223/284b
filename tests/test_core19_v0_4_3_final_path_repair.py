from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Core19V043FinalPathRepairGuards(unittest.TestCase):
    def test_path_repair_requires_proof_prior_opening_never_ran(self):
        w=(ROOT/'.github/workflows/same_target_core19_heldout_final_v0_4_3.yml').read_text()
        self.assertIn("'execution_repair_scope':'artifact_relative_path_only'", w)
        self.assertIn("parent.get('conclusion')!='failure'", w)
        self.assertIn("Recheck core19 information boundary before first held-out D", w)
        self.assertIn("Open only prospectively authorized core19 held-out paired cells", w)
        self.assertIn("('completed','skipped')", w)
        self.assertIn("GITHUB_RUN_ATTEMPT')!='1", w)

    def test_only_reference_artifact_relative_path_changes_before_same_evaluator(self):
        w=(ROOT/'.github/workflows/same_target_core19_heldout_final_v0_4_3.yml').read_text()
        self.assertIn("reference/final/core19_reference_summary.json", w)
        self.assertIn("reference/final/core19_reference_ceiling.csv", w)
        self.assertIn("scripts/evaluate_same_target_heldout_final_core19_v0_4.py", w)
        self.assertIn("'endpoint_id':'same_target_cross_source_reproducibility_heldout12_core19_v0_4'", w)
        self.assertIn("'process_knockout_authorized':False", w)
        self.assertIn("'procedure_selection_authorized':False", w)
        self.assertIn("'M_selection_authorized':False", w)
        self.assertIn("'taxon_replacement_authorized':False", w)


if __name__=='__main__':
    unittest.main()
