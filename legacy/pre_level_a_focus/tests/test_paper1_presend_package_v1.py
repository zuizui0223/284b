import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
TITLE = MANUSCRIPT / "ECOLOGY_LETTERS_TITLE_PAGE_V0_4.md"
READINESS = MANUSCRIPT / "PAPER1_FULL_SUBMISSION_READINESS_V0_2.md"
PACKAGE = MANUSCRIPT / "PAPER1_PRESEND_PACKAGE_V1.md"

SCIENCE_SHA = "66ad208f2a922800cb7f1d14f96b28295de13af4cdbdbec2f8b698b8fa320cc5"
SUBMISSION_SHA = "a2f45e2b91953b47f24682e95667533a923680ec65a9b0fef2c88a423b75cf84"
BUNDLE_SHA = "ebf1d848ac2eaa99f7e15b5f8a95e33262f1f76a768b1f4f8944331b177ff680"


class Paper1PresendPackageV1Tests(unittest.TestCase):
    def test_all_surfaces_share_exact_identities(self):
        texts = [p.read_text(encoding="utf-8") for p in [TITLE, READINESS, PACKAGE]]
        for text in texts:
            self.assertIn(SCIENCE_SHA, text)
            self.assertIn(SUBMISSION_SHA, text)
            self.assertIn(BUNDLE_SHA, text)

    def test_submission_counts_are_consistent(self):
        title = TITLE.read_text(encoding="utf-8")
        readiness = READINESS.read_text(encoding="utf-8")
        package = PACKAGE.read_text(encoding="utf-8")
        for text in [title, readiness, package]:
            self.assertIn("146", text)
            self.assertIn("3,437", text)
            self.assertIn("16", text)
            self.assertIn("6", text)

    def test_archive_candidate_is_not_misrepresented_as_release_or_doi(self):
        title = TITLE.read_text(encoding="utf-8").lower()
        readiness = READINESS.read_text(encoding="utf-8").lower()
        package = PACKAGE.read_text(encoding="utf-8").lower()
        self.assertIn("not", title)
        self.assertIn("archive-candidate/paper1-ecology-letters-v1", title)
        self.assertIn("archive-candidate/paper1-ecology-letters-v1", readiness)
        self.assertIn("not a public release or doi", package)
        self.assertIn("create/record the external archive deposit and doi", readiness)

    def test_scientific_boundary_and_sending_gate_remain_closed(self):
        readiness = READINESS.read_text(encoding="utf-8")
        package = PACKAGE.read_text(encoding="utf-8")
        for text in [readiness, package]:
            self.assertIn("Level A", text)
            self.assertIn("Level B", text)
            self.assertIn("Level C", text)
            self.assertIn("Empirical ledger", text)
        self.assertIn("Do **not** send", readiness)
        self.assertIn("12 held-out taxa", package)
        self.assertIn("not 283 repeated diagnostic cells", package)
        self.assertIn("focal hard/soft/process-knockout outcomes sealed", package)

    def test_no_new_ecological_analysis_is_required_by_remaining_blockers(self):
        text = PACKAGE.read_text(encoding="utf-8")
        self.assertIn("No remaining blocker requires a new ecological analysis.", text)
        readiness = READINESS.read_text(encoding="utf-8")
        self.assertIn("Ecology Letters has invited/approved the full Method submission", readiness)
        self.assertIn("Final author list and order confirmed by all authors", readiness)


if __name__ == "__main__":
    unittest.main()
