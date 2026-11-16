"""No-network sanity checks for recovering old GBIF file set."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from recover_gbif_aug_snapshot_missing20_v1 import partition_historical
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"legacy/pre_level_a_focus"))
from product_b_v7_2.snapshot_transport import SnapshotObject, object_manifest_sha256


def obj(key):
    return SnapshotObject(key=key,size=200,etag='"abc"',last_modified='2026-08-01T00:00:00Z')


class Missing20RecoveryTests(unittest.TestCase):
    def test_only_numbered_multiples_of_twenty_excluded(self):
        prefix="occurrence/2026-08-01/occurrence.parquet/"
        entries=[obj("occurrence/2026-08-01/citation.txt")] + [
            obj(prefix+f"{i:06d}") for i in [1,19,20,21,39,40,41,60,61]
        ]
        kept,added,unknown=partition_historical(entries)
        self.assertEqual(len(kept),7)
        self.assertEqual([x.key[len(prefix):] for x in added],["000020","000040","000060"])
        self.assertFalse(unknown)
        self.assertEqual(object_manifest_sha256(kept),object_manifest_sha256(
            list(reversed(kept))))

    def test_nonstandard_object_name_fails_identification(self):
        prefix="occurrence/2026-08-01/occurrence.parquet/"
        preserved,added,unknown=partition_historical([obj(prefix+"unknown")])
        self.assertEqual(len(preserved),0)
        self.assertEqual(len(added),0)
        self.assertEqual(len(unknown),1)


if __name__=="__main__":
    unittest.main()
