import json
from pathlib import Path
import tempfile
import unittest
from scripts.audit_same_target_reference_surfaces import diagnose, checked_zip


class SurfacePreconditionTests(unittest.TestCase):
    def test_finite_equal_domain_does_not_require_equal_scores(self):
        r = diagnose(['a','b'], [0.9,0.1], ['b','a'], [0.8,0.2])
        self.assertEqual(r['integrity_state'], 'strict_surface_complete')
        self.assertEqual(r['joint_finite_rows'], 2)
        self.assertNotIn('schoener_d', r)

    def test_nonfinite_is_not_zero_or_disagreement(self):
        for x in (float('nan'), float('inf')):
            r = diagnose(['a','b'], [x,1], ['b','a'], [1,1])
            self.assertEqual(r['integrity_state'], 'nonfinite_prediction_scores')
            self.assertEqual(r['joint_finite_rows'], 1)

    def test_duplicate_and_different_domains_fail(self):
        self.assertEqual(diagnose(['a','a'], [1,1], ['a','b'], [1,1])['integrity_state'], 'duplicate_row_ids')
        self.assertEqual(diagnose(['a'], [1], ['b'], [1])['integrity_state'], 'row_set_mismatch')

    def test_empty_negative_and_zero_mass_fail(self):
        cases = [([], [], 'empty_vector'), (['a'], [-1], 'negative_prediction_scores'), (['a'], [0], 'nonpositive_prediction_mass')]
        for ids, scores, state in cases:
            self.assertEqual(diagnose(ids, scores, ids, scores)['integrity_state'], state)

    def test_alignment_checked_before_support(self):
        self.assertEqual(diagnose(['a'], [1,2], ['a'], [1])['integrity_state'], 'row_score_alignment_failure')

    def test_wrong_archive_digest_is_rejected_before_decode(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'x.zip'; p.write_bytes(b'not an archive')
            with self.assertRaises(ValueError): checked_zip(p, '0'*64)


try:
    import pandas as pd
except ImportError:
    pd = None


@unittest.skipUnless(pd is not None, 'pandas review is exercised in dedicated CI')
class ReviewAvailabilityTests(unittest.TestCase):
    def fixture(self, root):
        from scripts.review_same_target_continued_reference import EXPECTED_RESTORED
        gates=[]; refs=[]
        for m in (150,300,500):
            for i in range(8):
                gates.append(dict(M_km=m,procedure=f'p{i}',eligible_distinct_taxa_pre_discordance=31,
                                  minimum_required_taxa=30,discordance_opening_authorized=True))
                refs.append(dict(M_km=m,procedure=f'p{i}',pre_discordance_eligible_taxa=31,
                    pre_discordance_opening_authorized=True,authorized_distinct_calibration_taxa=0,
                    minimum_required_taxa=30,quantile=0.95,quantile_method='nearest_rank',
                    nearest_rank_index_1_based=None,one_minus_schoener_d_reference_ceiling=None,
                    reference_state='reference_ceiling_unresolved'))
        values=[dict(completed_taxa=47,original_artifact_taxa_retained=45,restored_taxa=sorted(EXPECTED_RESTORED),
                     original_run_relabelled_success=False,heldout_opening_authorized=False,predictions_decoded_for_assembly=False),
                dict(taxa_expected_from_sampling_pass=47,taxa_with_prediction_artifacts=47,expected_fit_cells=2256,
                     paired_discordance_opened=False,reference_ceiling_opened=False,process_knockout_opened=False),
                dict(result_version='product_b_same_target_successor_reference_feasibility_v0.1',sampling_pass_taxa=47,
                     candidate_pair_cells=1128,reference_cells_expected=24,minimum_eligible_taxa_per_procedure_M=30,
                     paired_prediction_surfaces_read=False,schoener_d_computed=False,reference_ceiling_computed=False,
                     heldout_12_paired_discordance_read=False,process_knockout_opened=False,reference_cells=gates)]
        paths=[]
        for i,v in enumerate(values):
            p=root/f'{i}.json';p.write_text(json.dumps(v));paths.append(p)
        p=root/'reference.csv';pd.DataFrame(refs).to_csv(p,index=False);paths.append(p)
        v=dict(result_version='product_b_same_target_successor_pairing_calibration_v0.2_strict_opening',
               sampling_pass_taxa_in_audit=47,paired_cells_expected=1128,reference_cells_expected=24,
               minimum_distinct_calibration_taxa_per_reference_cell=30,reference_quantile=0.95,quantile_method='nearest_rank',
               reference_cells_frozen=0,reference_cells_unresolved=24,current_12_taxon_paired_discordance_read=False,
               process_knockout_opened=False,successor_consistent_labels_emitted=0,successor_attention_required_labels_emitted=0,
               unauthorized_prediction_cells_materialized=0)
        p=root/'summary.json';p.write_text(json.dumps(v));paths.append(p)
        return paths

    def test_authorized_but_unavailable_is_a_valid_terminal_review(self):
        from scripts.review_same_target_continued_reference import review
        with tempfile.TemporaryDirectory() as temp:
            r=review(*self.fixture(Path(temp)))
            self.assertEqual(r['review_state'],'reference_unavailable')
            self.assertEqual(r['authorized_but_reference_unavailable_cells'],24)
            self.assertFalse(r['heldout_opening_authorized'])

    def test_unavailable_does_not_allow_ceiling_or_sufficient_valid_n(self):
        from scripts.review_same_target_continued_reference import review
        for column,value in [('one_minus_schoener_d_reference_ceiling',0.2),('authorized_distinct_calibration_taxa',30)]:
            with self.subTest(column=column), tempfile.TemporaryDirectory() as temp:
                p=self.fixture(Path(temp));f=pd.read_csv(p[3]);f.loc[0,column]=value;f.to_csv(p[3],index=False)
                with self.assertRaises(RuntimeError):review(*p)

    def test_string_false_not_treated_as_true(self):
        from scripts.review_same_target_continued_reference import _boolean
        self.assertFalse(_boolean('False'))
        with self.assertRaises(RuntimeError): _boolean('not-a-bool')

if __name__ == '__main__':
    unittest.main()
