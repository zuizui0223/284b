import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "manuscript" / "PAPER1_ARCHIVE_IDENTITY_V1.json"
EXPECTED_SCIENCE_SHA = "66ad208f2a922800cb7f1d14f96b28295de13af4cdbdbec2f8b698b8fa320cc5"
EXPECTED_SUBMISSION_SHA = "a2f45e2b91953b47f24682e95667533a923680ec65a9b0fef2c88a423b75cf84"
EXPECTED_BUNDLE_SHA = "788ffe715ee12831022e286887b960201bb04af63fda568d421708233d124a84"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Paper1ArchiveIdentityV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(RECEIPT.read_text(encoding="utf-8"))

    def test_archive_identity_preserves_scientific_boundary(self):
        p = self.data
        self.assertEqual(p["scientific_source_sha256"], EXPECTED_SCIENCE_SHA)
        self.assertEqual(p["submission_derivative_sha256"], EXPECTED_SUBMISSION_SHA)
        self.assertEqual(p["bundle_identity_sha256"], EXPECTED_BUNDLE_SHA)
        self.assertEqual(p["scientific_boundary"]["level_a"], "sole_completed_empirical_endpoint")
        self.assertEqual(p["scientific_boundary"]["level_b"], "unopened")
        self.assertEqual(p["scientific_boundary"]["level_c"], "focal_outcomes_sealed")
        self.assertEqual(p["scientific_boundary"]["empirical_ledger"], 1)
        self.assertIsNone(p["doi"])
        self.assertIsNone(p["release_tag"])

    def test_all_25_archive_files_exist_and_match_recorded_hashes(self):
        files = self.data["files"]
        self.assertEqual(len(files), 25)
        paths = [row["path"] for row in files]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertIn("scripts/build_paper1_archive_identity_v1.py", paths)
        for row in files:
            path = ROOT / row["path"]
            self.assertTrue(path.exists(), row["path"])
            self.assertEqual(path.stat().st_size, row["bytes"], row["path"])
            self.assertEqual(sha256(path), row["sha256"], row["path"])

    def test_known_manuscript_hash_files_match_archive_receipt(self):
        science = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_10_CANDIDATE.md"
        submission = ROOT / "manuscript" / "PAPER1_ECOLOGY_LETTERS_SUBMISSION_V1.md"
        self.assertEqual(sha256(science), EXPECTED_SCIENCE_SHA)
        self.assertEqual(sha256(submission), EXPECTED_SUBMISSION_SHA)
        self.assertEqual(
            (ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_10_CANDIDATE.sha256").read_text().split()[0],
            EXPECTED_SCIENCE_SHA,
        )
        self.assertEqual(
            (ROOT / "manuscript" / "PAPER1_ECOLOGY_LETTERS_SUBMISSION_V1.sha256").read_text().split()[0],
            EXPECTED_SUBMISSION_SHA,
        )


if __name__ == "__main__":
    unittest.main()
