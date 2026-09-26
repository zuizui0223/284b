import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "finalize_paper1_human_metadata_v1.py"
TEMPLATE = ROOT / "manuscript" / "PAPER1_HUMAN_METADATA_V1.template.json"


def load_module():
    spec = importlib.util.spec_from_file_location("paper1_human_gate", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def complete_metadata():
    return {
        "schema": "paper1_human_metadata_v1",
        "journal": "Ecology Letters",
        "article_type": "Method",
        "editorial": {
            "full_method_authorized": True,
            "authorization_reference": "EL-METHOD-TEST",
            "authorization_date": "2026-09-15",
        },
        "authors": [
            {
                "author_id": "a1",
                "name": "Author One",
                "order": 1,
                "affiliation_ids": ["aff1"],
                "orcid_status": "confirmed",
                "orcid": "0000-0000-0000-000X",
                "credit_roles": ["Conceptualization", "Writing – original draft"],
            },
            {
                "author_id": "a2",
                "name": "Author Two",
                "order": 2,
                "affiliation_ids": ["aff2"],
                "orcid_status": "not_required",
                "orcid": "",
                "credit_roles": ["Methodology", "Writing – review & editing"],
            },
        ],
        "affiliations": [
            {"affiliation_id": "aff1", "text": "Department One, University One"},
            {"affiliation_id": "aff2", "text": "Department Two, University Two"},
        ],
        "corresponding_author": {"author_id": "a1", "email": "author.one@example.org"},
        "declarations": {
            "author_order_confirmed": True,
            "all_authors_approved": True,
            "not_under_consideration_elsewhere": True,
            "competing_interests_statement": "The authors declare no competing interests.",
            "related_work_disclosure": "No overlapping manuscript is under review or published by this author group.",
        },
        "funding_statement": "No external funding was received for this study.",
        "acknowledgements": "No additional acknowledgements.",
    }


class Paper1HumanMetadataGateV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_committed_template_is_intentionally_blocked(self):
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        errors = self.mod.validate_metadata(data)
        self.assertGreater(len(errors), 8)
        joined = "\n".join(errors)
        self.assertIn("full_method_authorized", joined)
        self.assertIn("authorization_reference", joined)
        self.assertIn("name is required", joined)
        self.assertIn("all_authors_approved", joined)
        self.assertIn("corresponding_author.email", joined)

    def test_synthetic_complete_metadata_passes_all_gates(self):
        self.assertEqual(self.mod.validate_metadata(complete_metadata()), [])

    def test_wrong_author_order_or_affiliation_fails_closed(self):
        data = complete_metadata()
        data["authors"][1]["order"] = 3
        data["authors"][1]["affiliation_ids"] = ["unknown"]
        errors = "\n".join(self.mod.validate_metadata(data))
        self.assertIn("author orders must be unique and contiguous", errors)
        self.assertIn("unknown affiliation_id unknown", errors)

    def test_editorial_and_declaration_false_states_cannot_finalize(self):
        data = complete_metadata()
        data["editorial"]["full_method_authorized"] = False
        data["declarations"]["all_authors_approved"] = False
        data["declarations"]["not_under_consideration_elsewhere"] = False
        errors = "\n".join(self.mod.validate_metadata(data))
        self.assertIn("full_method_authorized must be true", errors)
        self.assertIn("all_authors_approved must be true", errors)
        self.assertIn("not_under_consideration_elsewhere must be true", errors)

    def test_finalizer_renders_exact_submission_identities_only_after_pass(self):
        data = complete_metadata()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            metadata = td / "metadata.json"
            metadata.write_text(json.dumps(data), encoding="utf-8")
            out = td / "out"
            receipt = self.mod.finalize(metadata, out)
            self.assertEqual(receipt["human_metadata_gate"], "passed")
            self.assertEqual(receipt["scientific_source_sha256"], self.mod.SCIENCE_SHA)
            self.assertEqual(receipt["submission_derivative_sha256"], self.mod.SUBMISSION_SHA)
            self.assertEqual(receipt["archive_bundle_sha256"], self.mod.BUNDLE_SHA)
            title = (out / "ECOLOGY_LETTERS_TITLE_PAGE_FINAL.md").read_text(encoding="utf-8")
            cover = (out / "ECOLOGY_LETTERS_COVER_LETTER_FINAL.md").read_text(encoding="utf-8")
            declarations = (out / "PAPER1_DECLARATIONS_FINAL.md").read_text(encoding="utf-8")
            self.assertIn("Author One", title)
            self.assertIn("author.one@example.org", title)
            self.assertIn("EL-METHOD-TEST (2026-09-15)", cover)
            self.assertIn("All authors have explicitly approved", declarations)
            self.assertNotIn("[Insert verified statement", cover)


if __name__ == "__main__":
    unittest.main()
