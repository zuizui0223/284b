import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_v7_2_jos003_snapshot_sampling.py"


class JOS003RunnerSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = RUNNER.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source, filename=str(RUNNER))

    def test_runner_is_valid_python(self):
        self.assertIsInstance(self.tree, ast.Module)

    def test_runner_rechecks_frozen_object_manifest_before_dataset_creation(self):
        self.assertIn("_verify_frozen_snapshot_objects", self.source)
        self.assertIn("EXPECTED_OBJECT_MANIFEST_SHA256", self.source)
        verify_pos = self.source.index("self.object_manifest_recheck = _verify_frozen_snapshot_objects()")
        dataset_pos = self.source.index("self._dataset = ds.dataset(")
        self.assertLess(verify_pos, dataset_pos)

    def test_runner_uses_snapshot_specieskey_country_and_present_filters(self):
        self.assertIn('ds.field("specieskey")', self.source)
        self.assertIn('ds.field("countrycode")', self.source)
        self.assertIn('ds.field("occurrencestatus")', self.source)
        self.assertNotIn("api.gbif.org/v1/occurrence/search", self.source)

    def test_runner_never_persists_raw_rows(self):
        self.assertIn('"raw_snapshot_rows_persisted": False', self.source)
        self.assertNotIn("write_parquet", self.source)
        self.assertNotIn("write_csv", self.source)

    def test_runner_records_row_boundary_and_transport_failure_state(self):
        self.assertIn("self.row_access_started = True", self.source)
        self.assertIn('"engineering_execution_unresolved"', self.source)
        self.assertIn('"pre_row_execution_failure"', self.source)

    def test_runner_keeps_invariant_layers_closed(self):
        self.assertIn('"model_fit_reads_opened": False', self.source)
        self.assertIn('"invariant_reads_opened": False', self.source)
        self.assertIn('"process_knockout_reads_opened": False', self.source)


if __name__ == "__main__":
    unittest.main()
