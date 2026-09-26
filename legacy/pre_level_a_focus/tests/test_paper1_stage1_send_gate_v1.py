import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "scripts" / "audit_ecology_letters_stage1_send_readiness.py"
RENDER_PATH = ROOT / "scripts" / "render_ecology_letters_stage1_email.py"
TEMPLATE = ROOT / "config" / "ecology_letters_stage1_human_metadata_template.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def synthetic_metadata():
    return {
        "authors_order": ["Author One", "Author Two"],
        "affiliations": ["Department One, University One", "Department Two, University Two"],
        "corresponding_author_name": "Author One",
        "corresponding_email": "author.one@example.org",
        "author_qualifications": "The author group combines ecological modelling, observation-process analysis and empirical field expertise relevant to the proposed Method.",
    }


class Paper1Stage1SendGateV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit_mod = load(AUDIT_PATH, "paper1_stage1_audit")
        cls.render_mod = load(RENDER_PATH, "paper1_stage1_renderer")

    def test_frozen_release_candidate_is_still_byte_identical(self):
        rc = self.audit_mod._release_candidate_audit()
        self.assertTrue(rc["receipt_exists"])
        self.assertTrue(rc["receipt_identity_valid"])
        self.assertTrue(rc["byte_identical"])
        self.assertEqual(rc["canonical_file_count"], 20)
        self.assertEqual(rc["matched_file_count"], 20)
        self.assertEqual(rc["missing_paths"], [])
        self.assertEqual(rc["changed_files"], [])
        self.assertEqual(rc["package_identity_sha256"], "2787b4462850458dbbb01f975ef71d7171f553e2f4f7898c851a43a1548fea87")

    def test_without_human_metadata_package_is_blocked_only_on_five_human_fields(self):
        result = self.audit_mod.audit(None)
        self.assertEqual(result["status"], "blocked_human_metadata")
        self.assertTrue(all(result["package_checks"].values()))
        self.assertEqual(
            result["missing_human_metadata"],
            ["authors_order", "affiliations", "corresponding_author_name", "corresponding_email", "author_qualifications"],
        )
        self.assertTrue(result["does_not_send_email"])
        self.assertFalse(result["focal_level_c_values_read"])
        self.assertEqual(result["empirical_ledger_increment"], 0)

    def test_committed_human_metadata_template_remains_empty_and_cannot_send(self):
        import json
        metadata = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        result = self.audit_mod.audit(metadata)
        self.assertEqual(result["status"], "blocked_human_metadata")
        self.assertEqual(len(result["missing_human_metadata"]), 5)

    def test_synthetic_complete_metadata_opens_only_admin_rendering_gate(self):
        metadata = synthetic_metadata()
        result = self.audit_mod.audit(metadata)
        self.assertEqual(result["status"], "metadata_complete_package_scientifically_ready")
        self.assertTrue(all(result["package_checks"].values()))
        self.assertTrue(all(result["human_metadata_checks"].values()))
        self.assertEqual(result["missing_human_metadata"], [])
        self.assertEqual(result["empirical_ledger_increment"], 0)
        rendered = self.render_mod.render(metadata)
        self.assertIn("ecolets@cefe.cnrs.fr; ecolets2@cefe.cnrs.fr", rendered)
        self.assertIn("exact canonical 295-word body", rendered)
        self.assertIn("Author One; Author Two", rendered)
        self.assertIn("author.one@example.org", rendered)
        self.assertIn("ecology_letters_method_proposal_figure_v0_5.svg", rendered)
        self.assertNotIn("[Affiliation]", rendered)
        self.assertNotIn("[Email]", rendered)


if __name__ == "__main__":
    unittest.main()
