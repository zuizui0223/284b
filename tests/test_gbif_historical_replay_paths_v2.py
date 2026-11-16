"""Offline tests for selecting the exact frozen 9705 GBIF parquet files."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_original_gbif_neon_historical_replay_v2 import frozen_parquet_paths


class HistoricalPathTests(unittest.TestCase):
    def test_excludes_exact_510_backfilled_multiples(self):
        prefix="gbif-open-data-us-east-1/occurrence/2026-08-01/occurrence.parquet/"
        paths=[prefix+f"{i:06d}" for i in range(1,10216)]
        recovered=frozen_parquet_paths(paths)
        self.assertEqual(len(recovered),9705)
        self.assertIn(prefix+"000019",recovered)
        self.assertNotIn(prefix+"000020",recovered)
        self.assertNotIn(prefix+"010200",recovered)
        self.assertIn(prefix+"010201",recovered)

    def test_fail_closed_on_missing_or_duplicate_parquet(self):
        prefix="gbif-open-data-us-east-1/occurrence/2026-08-01/occurrence.parquet/"
        paths=[prefix+f"{i:06d}" for i in range(1,10216)]
        with self.assertRaises(RuntimeError):
            frozen_parquet_paths(paths[:-1])
        with self.assertRaises(RuntimeError):
            frozen_parquet_paths(paths[:-1]+paths[-2:])

    def test_fail_closed_on_unexpected_object_name(self):
        prefix="gbif-open-data-us-east-1/occurrence/2026-08-01/occurrence.parquet/"
        paths=[prefix+f"{i:06d}" for i in range(1,10215)]
        paths.append(prefix+"no_name")
        with self.assertRaises(RuntimeError):
            frozen_parquet_paths(paths)


if __name__=="__main__":
    unittest.main()
