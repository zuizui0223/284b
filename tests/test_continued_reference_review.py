import json
from pathlib import Path
import tempfile
import unittest

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None

if pd is not None:
    from scripts.review_same_target_continued_reference import review


@unittest.skipUnless(pd is not None, 'pandas-dependent reference review runs in dedicated CI')
class ContinuedReferenceReviewTests(unittest.TestCase):
    def fixture(self, root: Path):
        procedures = [f'p{i}' for i in range(8)]
        cells = []
        refs = []
        frozen = 0
        for m in (150, 300, 500):
            for i, procedure in enumerate(procedures):
                authorized = i < 4
                n = 31 if authorized else 28
                cells.append({
                    'M_km': m,
                    'procedure': procedure,
                    'eligible_distinct_taxa_pre_discordance': n,
                    'minimum_required_taxa': 30,
                    'discordance_opening_authorized': authorized,
                    'state': 'reference_discordance_opening_authorized' if authorized else 'reference_discordance_opening_unresolved',
                })
                refs.append({
                    'M_km': m,
                    'procedure': procedure,
                    'pre_discordance_eligible_taxa': n,
                    'pre_discordance_opening_authorized': authorized,
                    'authorized_distinct_calibration_taxa': n if authorized else 0,
                    'minimum_required_taxa': 30,
                    'quantile': 0.95,
                    'quantile_method': 'nearest_rank',
                    'nearest_rank_index_1_based': 30 if authorized else None,
                    'one_minus_schoener_d_reference_ceiling': 0.25 if authorized else None,
                    'reference_state': 'reference_ceiling_frozen' if authorized else 'paired_crosscheck_calibration_unresolved',
                })
                frozen += int(authorized)

        continuation = root/'continuation_receipt.json'
        continuation.write_text(json.dumps({
            'completed_taxa': 47,
            'original_artifact_taxa_retained': 45,
            'restored_taxa': ['Alisma plantago-aquatica', 'Populus tremula'],
            'original_run_relabelled_success': False,
            'heldout_opening_authorized': False,
            'predictions_decoded_for_assembly': False,
        }))
        fit = root/'product_b_same_target_successor_layer1_fit_v0_1.json'
        fit.write_text(json.dumps({
            'taxa_expected_from_sampling_pass': 47,
            'taxa_with_prediction_artifacts': 47,
            'expected_fit_cells': 2256,
            'paired_discordance_opened': False,
            'reference_ceiling_opened': False,
            'process_knockout_opened': False,
        }))
        feasibility = root/'product_b_same_target_successor_reference_feasibility_v0_1.json'
        feasibility.write_text(json.dumps({
            'result_version': 'product_b_same_target_successor_reference_feasibility_v0.1',
            'sampling_pass_taxa': 47,
            'candidate_pair_cells': 1128,
            'reference_cells_expected': 24,
            'minimum_eligible_taxa_per_procedure_M': 30,
            'reference_cells': cells,
            'paired_prediction_surfaces_read': False,
            'schoener_d_computed': False,
            'reference_ceiling_computed': False,
            'heldout_12_paired_discordance_read': False,
            'process_knockout_opened': False,
        }))
        reference = root/'product_b_same_target_successor_reference_ceiling_v0_1.csv'
        pd.DataFrame(refs).to_csv(reference, index=False)
        summary = root/'product_b_same_target_successor_pairing_calibration_v0_1.json'
        summary.write_text(json.dumps({
            'result_version': 'product_b_same_target_successor_pairing_calibration_v0.2_strict_opening',
            'sampling_pass_taxa_in_audit': 47,
            'paired_cells_expected': 1128,
            'reference_cells_expected': 24,
            'minimum_distinct_calibration_taxa_per_reference_cell': 30,
            'reference_quantile': 0.95,
            'quantile_method': 'nearest_rank',
            'reference_cells_frozen': frozen,
            'reference_cells_unresolved': 24-frozen,
            'current_12_taxon_paired_discordance_read': False,
            'process_knockout_opened': False,
            'successor_consistent_labels_emitted': 0,
            'successor_attention_required_labels_emitted': 0,
            'unauthorized_prediction_cells_materialized': 0,
        }))
        return continuation, fit, feasibility, reference, summary

    def test_valid_reference_review_keeps_heldout_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.fixture(Path(tmp))
            out = review(*paths)
            self.assertEqual(out['reference_cells_frozen'], 12)
            self.assertEqual(out['reference_cells_unresolved'], 12)
            self.assertFalse(out['heldout_prediction_opened'])
            self.assertFalse(out['process_knockout_opened'])

    def test_reference_count_must_match_preD_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self.fixture(root)
            frame = pd.read_csv(paths[3])
            frame.loc[0, 'pre_discordance_eligible_taxa'] = 30
            frame.to_csv(paths[3], index=False)
            with self.assertRaises(RuntimeError):
                review(*paths)

    def test_unfrozen_cell_cannot_carry_ceiling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self.fixture(root)
            frame = pd.read_csv(paths[3])
            idx = frame.index[frame['reference_state'] != 'reference_ceiling_frozen'][0]
            frame.loc[idx, 'one_minus_schoener_d_reference_ceiling'] = 0.4
            frame.to_csv(paths[3], index=False)
            with self.assertRaises(RuntimeError):
                review(*paths)

    def test_heldout_opening_in_continuation_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self.fixture(root)
            data = json.loads(paths[0].read_text())
            data['heldout_opening_authorized'] = True
            paths[0].write_text(json.dumps(data))
            with self.assertRaises(RuntimeError):
                review(*paths)


if __name__ == '__main__':
    unittest.main()
