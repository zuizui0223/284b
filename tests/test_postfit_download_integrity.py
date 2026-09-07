"""Keep post-fit downloads fail-closed without changing any scientific rule.

These are workflow-wiring tests, not a simulation of corrupted GitHub storage.
The separate synthetic-artifact-transfer CI job checks v4 upload compatibility
and the v8 authenticated pattern/single-artifact download paths with real ZIPs.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PIN = 'actions/download-artifact@70fc10c6e5e1ce46ad2ea6f2b72d43f7d47b13c3'


def download_steps(text):
    """Select downloader step blocks; base unit tests need no YAML dependency."""
    return [part for part in re.split(r'(?m)^      - ', text)
            if re.search(r'(?m)^        uses: actions/download-artifact@', part)]


def validate_download_steps(text):
    steps = download_steps(text)
    if len(steps) != 2:
        raise ValueError('expected taxon and aggregate download steps')
    for step in steps:
        if f'uses: {PIN} # v8.0.0\n' not in step:
            raise ValueError('download implementation is not pinned')
        if not re.search(r'(?m)^          digest-mismatch: error$', step):
            raise ValueError('digest mismatch must fail the action')
        if 'continue-on-error:' in step:
            raise ValueError('download failure must not be ignored')
        if "if: steps.source.outputs.authorized == 'true'" not in step:
            raise ValueError('source authorization must precede download')
        if 'run-id: 34032659571\n' not in step:
            raise ValueError('frozen fit run must remain unchanged')
    return steps


def validate_heldout_download(text):
    steps = download_steps(text)
    if len(steps) != 1:
        raise ValueError('expected exactly one held-out artifact download')
    step = steps[0]
    if f'uses: {PIN} # v8.0.0\n' not in step:
        raise ValueError('held-out download implementation is not pinned')
    if not re.search(r'(?m)^          digest-mismatch: error$', step):
        raise ValueError('held-out digest mismatch must fail the action')
    if 'continue-on-error:' in step:
        raise ValueError('held-out download failure must not be ignored')
    if 'run-id: ${{ steps.trigger.outputs.heldout_fit_run_id }}' not in step:
        raise ValueError('held-out download must use the frozen trigger run id')
    if 'pattern: product-b-layer1-baseline-fit-taxon-*' not in step:
        raise ValueError('held-out artifact selector changed')
    return step


class PostfitDownloadIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT/'.github/workflows/same_target_successor_postfit.yml').read_text()
        cls.integration = (ROOT/'.github/workflows/same_target_postfit_integration.yml').read_text()
        cls.heldout = (ROOT/'.github/workflows/same_target_heldout_crosscheck_strict.yml').read_text()

    def test_both_production_downloads_pin_error_behavior(self):
        steps = validate_download_steps(self.workflow)
        self.assertIn('pattern: product-b-successor-layer1-fit-taxon-*', steps[0])
        self.assertIn('name: product-b-successor-layer1-fit-audit', steps[1])
        self.assertIn('path: analysis/fit_artifacts', steps[0])
        self.assertIn('path: analysis/source_audit', steps[1])

    def test_regression_to_warning_missing_setting_or_mutable_tag_fails(self):
        for before,after in [('digest-mismatch: error', 'digest-mismatch: warn'),
                             ('digest-mismatch: error', ''),
                             (PIN, 'actions/download-artifact@v8')]:
            with self.subTest(after=after), self.assertRaises(ValueError):
                validate_download_steps(self.workflow.replace(before,after,1))

    def test_ignored_failure_or_missing_authorization_fails(self):
        old=f'uses: {PIN} # v8.0.0'
        weakened=self.workflow.replace(old, 'continue-on-error: true\n        '+old, 1)
        with self.assertRaises(ValueError):
            validate_download_steps(weakened)
        steps=download_steps(self.workflow)
        weakened=self.workflow.replace(steps[0],steps[0].replace("if: steps.source.outputs.authorized == 'true'",''),1)
        with self.assertRaises(ValueError):
            validate_download_steps(weakened)

    def test_analysis_remains_pinned_and_follows_downloads(self):
        text=self.workflow
        self.assertIn('ref: 89f1a01386d5906420cb625dbf87ee18d60672e5', text)
        self.assertLess(text.index('name: Download source-run aggregate'),
                        text.index('name: Run existing pre-discordance reference-feasibility audit'))
        self.assertNotIn('continue-on-error:', text)
        self.assertNotIn('contents: write', text)
        self.assertNotIn('evaluate_same_target_heldout_crosscheck', text)
        self.assertNotIn('python scripts/run_same_target_successor_layer1_fit_taxon.py', text)

    def test_real_smoke_job_is_synthetic_and_uses_same_download_implementation(self):
        text=self.integration.split('  synthetic-artifact-transfer:\n',1)[1]
        self.assertEqual(text.count(PIN),2)
        self.assertEqual(text.count('digest-mismatch: error'),2)
        self.assertEqual(text.count('run-id: ${{ github.run_id }}'),2)
        self.assertIn('pattern: postfit-synthetic-taxon-',text)
        self.assertIn('name: postfit-synthetic-aggregate-',text)
        self.assertNotIn('34032659571',text)
        self.assertNotIn('sealed_prediction',text)
        self.assertEqual(self.integration.count("      - '.github/workflows/same_target_successor_postfit.yml'"),2)

    def test_strict_heldout_download_is_fail_closed(self):
        step = validate_heldout_download(self.heldout)
        self.assertIn('path: heldout_fit_artifacts', step)
        self.assertNotIn('continue-on-error:', self.heldout)
        self.assertIn('reference_ceiling_must_be_frozen_before_heldout_prediction_surfaces_are_opened', self.heldout)

    def test_heldout_regression_to_warning_or_mutable_tag_fails(self):
        for before,after in [('digest-mismatch: error', 'digest-mismatch: warn'),
                             (PIN, 'actions/download-artifact@v8')]:
            with self.subTest(after=after), self.assertRaises(ValueError):
                validate_heldout_download(self.heldout.replace(before,after,1))


if __name__ == '__main__':
    unittest.main()
