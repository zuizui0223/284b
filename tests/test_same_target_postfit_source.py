import copy
from pathlib import Path
import unittest
from scripts.verify_same_target_postfit_source import (
    ANALYSIS_SHA, EXECUTION_SHA, PREFIX, REPOSITORY, RUN_ID, WORKFLOW_PATH, verify_source,
)


def fixture():
    run = {'id': RUN_ID, 'head_sha': EXECUTION_SHA,
           'head_branch': 'product-b-v5-obligate-invariant', 'path': WORKFLOW_PATH,
           'event': 'push', 'repository': {'full_name': REPOSITORY},
           'head_repository': {'full_name': REPOSITORY}, 'run_attempt': 1,
           'status': 'completed', 'conclusion': 'success'}
    names = [f'{PREFIX}{i}' for i in range(47)] + ['product-b-successor-layer1-fit-audit']
    artifacts = [{'id': i+1, 'name': name, 'expired': False, 'digest': 'sha256:' + 'a'*64,
                  'workflow_run': {'id': RUN_ID, 'head_sha': EXECUTION_SHA}} for i, name in enumerate(names)]
    return run, {'total_count': len(artifacts), 'artifacts': artifacts}


class PostfitSourceTests(unittest.TestCase):
    def test_complete_fixed_run_passes_but_never_opens_heldout(self):
        decision = verify_source(*fixture())
        self.assertTrue(decision['postfit_authorized'])
        self.assertFalse(decision['heldout_opening_authorized'])
        self.assertEqual(decision['analysis_sha'], ANALYSIS_SHA)

    def test_running_run_is_pending_not_failure(self):
        run, inventory = fixture(); run.update(status='in_progress', conclusion=None)
        inventory['artifacts'] = inventory['artifacts'][:7]; inventory['total_count'] = 7
        result = verify_source(run, inventory)
        self.assertFalse(result['postfit_authorized'])
        self.assertEqual(result['state'], 'source_run_not_complete')

    def test_failed_or_cancelled_source_stays_closed(self):
        for conclusion in ('failure', 'cancelled', 'timed_out'):
            run, inventory = fixture(); run['conclusion'] = conclusion
            self.assertFalse(verify_source(run, inventory)['postfit_authorized'])

    def test_wrong_execution_repository_or_attempt_is_rejected(self):
        for key, bad in [('id', 1), ('head_sha', 'b'*40), ('run_attempt', 2),
                         ('head_repository', {'full_name': 'someone/fork'})]:
            run, inventory = fixture(); run[key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError): verify_source(run, inventory)

    def test_missing_duplicate_or_paginated_artifacts_are_rejected(self):
        for mode in ('missing', 'duplicate', 'paginated'):
            run, inventory = fixture()
            if mode == 'missing': inventory['artifacts'].pop(); inventory['total_count'] -= 1
            if mode == 'duplicate': inventory['artifacts'][-1] = copy.deepcopy(inventory['artifacts'][0])
            if mode == 'paginated': inventory['artifacts'].pop()
            with self.subTest(mode=mode), self.assertRaises(ValueError): verify_source(run, inventory)

    def test_expired_wrong_source_or_missing_digest_is_rejected(self):
        for key, bad in [('expired', True), ('digest', None), ('workflow_run', {'id': 1})]:
            run, inventory = fixture(); inventory['artifacts'][0][key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError): verify_source(run, inventory)

    def test_workflow_does_not_restart_models_or_open_heldout(self):
        text = (Path(__file__).resolve().parents[1] / '.github/workflows/same_target_successor_postfit.yml').read_text()
        self.assertIn('contents: read', text)
        self.assertNotIn('contents: write', text)
        self.assertIn(ANALYSIS_SHA, text)
        self.assertIn('calibrate_same_target_successor_pairing_strict.py', text)
        self.assertNotIn('python scripts/run_same_target_successor_layer1_fit_taxon.py', text)
        self.assertNotIn('evaluate_same_target_heldout_crosscheck', text)
        self.assertNotIn('git push', text)


if __name__ == '__main__':
    unittest.main()
