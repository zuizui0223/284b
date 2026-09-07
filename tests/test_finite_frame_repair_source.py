import ast
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPAIR = ROOT / "config/product_b_same_target_reference_finite_frame_repair_contract_v0_1.json"
PREFLIGHT = ROOT / "scripts/preflight_same_target_successor_finite_frame.py"
REFIT = ROOT / "scripts/run_same_target_successor_layer1_fit_taxon_finite_frame.py"
REFIT_WORKFLOW = ROOT / ".github/workflows/same_target_successor_finite_frame_refit.yml"


class FiniteFrameRepairSourceTests(unittest.TestCase):
    def test_repair_contract_keeps_outcome_layers_closed(self):
        c = json.loads(REPAIR.read_text(encoding="utf-8"))
        self.assertFalse(c["preflight"]["model_fit_allowed"])
        self.assertFalse(c["preflight"]["prediction_score_computation_allowed"])
        self.assertFalse(c["preflight"]["schoener_d_computation_allowed"])
        self.assertFalse(c["preflight"]["reference_ceiling_computation_allowed"])
        self.assertFalse(c["preflight"]["heldout_opening_allowed"])
        self.assertFalse(c["preflight"]["process_knockout_allowed"])
        self.assertFalse(c["empirical_ledger"]["this_repair_contract_counts_as_empirical_conclusion"])

    def test_preflight_and_refit_sources_parse(self):
        ast.parse(PREFLIGHT.read_text(encoding="utf-8"))
        ast.parse(REFIT.read_text(encoding="utf-8"))

    def test_refit_workflow_requires_explicit_authorization_file(self):
        text = REFIT_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("product_b_same_target_reference_finite_frame_refit_authorization_v0_1.json", text)
        self.assertIn("all_141_frames_ready_for_review", text)
        self.assertIn("heldout_opening_authorized", text)
        self.assertIn("process_knockout_authorized", text)
        self.assertIn("paired_discordance_opening_authorized", text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_refit_runner_cannot_silently_accept_partial_or_nonfinite_surface(self):
        text = REFIT.read_text(encoding="utf-8")
        self.assertIn("len(scores) != 2000 or not np.isfinite(scores).all()", text)
        self.assertIn("background_rows_resampled_during_refit", text)
        self.assertIn("posthoc_prediction_row_drop_used", text)
        self.assertIn('"heldout_12_paired_discordance_read": False', text)
        self.assertIn('"process_knockout_computed": False', text)


if __name__ == "__main__":
    unittest.main()
