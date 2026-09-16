import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREP = ROOT / "scripts" / "prepare_ecology_letters_stage1_metadata_v2.py"
AUDIT = ROOT / "scripts" / "audit_ecology_letters_stage1_send_readiness.py"
RENDER = ROOT / "scripts" / "render_ecology_letters_stage1_email.py"
TEMPLATE = ROOT / "config" / "ecology_letters_stage1_proposal_metadata_v2.template.json"
POLICY = ROOT / "manuscript" / "PAPER1_STAGE1_ADMIN_POLICY_V2.md"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class Paper1Stage1AdminPolicyV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prep = load("stage1_metadata_v2", PREP)
        cls.audit = load("stage1_audit_v2_test", AUDIT)
        cls.render = load("stage1_render_v2_test", RENDER)
        cls.policy = POLICY.read_text(encoding="utf-8")

    def test_frozen_stage1_package_remains_byte_identical(self):
        rc = self.audit._release_candidate_audit()
        self.assertTrue(rc["receipt_identity_valid"])
        self.assertTrue(rc["byte_identical"])
        self.assertEqual(rc["canonical_file_count"], 20)
        self.assertEqual(rc["matched_file_count"], 20)

    def test_committed_minimal_template_is_blocked(self):
        raw = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            self.prep.prepare(raw)

    def test_single_author_can_reuse_frozen_qualification_sentence(self):
        raw = {
            "provisional_authors": ["Example Author"],
            "affiliations": ["Example Ecology Department"],
            "sender_name": "",
            "sender_email": "author@example.org",
            "author_qualifications": "",
        }
        prepared = self.prep.prepare(raw)
        self.assertEqual(prepared["authors_order"], ["Example Author"])
        self.assertEqual(prepared["corresponding_author_name"], "Example Author")
        self.assertEqual(
            prepared["author_qualifications"],
            self.prep.DEFAULT_SINGLE_AUTHOR_QUALIFICATION,
        )
        self.assertEqual(
            self.audit.audit(prepared)["status"],
            "metadata_complete_package_scientifically_ready",
        )
        email = self.render.render(prepared)
        self.assertIn("Example Author", email)
        self.assertIn("author@example.org", email)
        self.assertIn("exact canonical 295-word body", email)
        self.assertIn("ecology_letters_method_proposal_figure_v0_5.svg", email)

    def test_multi_author_proposal_requires_explicit_group_qualification(self):
        raw = {
            "provisional_authors": ["Author One", "Author Two"],
            "affiliations": ["Example Ecology Department"],
            "sender_email": "one@example.org",
            "author_qualifications": "",
        }
        with self.assertRaisesRegex(ValueError, "multi-author proposal"):
            self.prep.prepare(raw)
        raw["author_qualifications"] = "The authors combine ecological field, modelling and reproducible-method expertise."
        prepared = self.prep.prepare(raw)
        self.assertEqual(prepared["authors_order"], ["Author One", "Author Two"])
        self.assertEqual(prepared["corresponding_author_name"], "Author One")
        self.assertEqual(self.audit.audit(prepared)["status"], "metadata_complete_package_scientifically_ready")

    def test_policy_separates_proposal_authorship_from_full_submission_authorship(self):
        self.assertIn("proposal-stage authorship", self.policy)
        self.assertIn("full-submission authorship", self.policy)
        self.assertIn("final full-manuscript author order", self.policy)
        self.assertIn("Empirical ledger: 1", self.policy)
        self.assertIn("Level C: focal biological outcomes sealed", self.policy)


if __name__ == "__main__":
    unittest.main()
