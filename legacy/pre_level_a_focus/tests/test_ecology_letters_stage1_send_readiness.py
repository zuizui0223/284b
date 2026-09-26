import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_ecology_letters_stage1_send_readiness.py"
TEMPLATE = ROOT / "config" / "ecology_letters_stage1_human_metadata_template.json"

SPEC = importlib.util.spec_from_file_location("stage1_send_readiness", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_package_is_scientifically_ready_before_human_metadata():
    result = MOD.audit(None)
    assert result["status"] == "blocked_human_metadata"
    assert all(result["package_checks"].values())
    assert set(result["missing_human_metadata"]) == set(MOD.REQUIRED_METADATA)
    assert result["focal_level_c_values_read"] is False
    assert result["empirical_ledger_increment"] == 0


def test_empty_template_is_deliberately_blocked():
    metadata = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    result = MOD.audit(metadata)
    assert result["status"] == "blocked_human_metadata"
    assert all(not result["human_metadata_checks"][key] for key in MOD.REQUIRED_METADATA)


def test_complete_synthetic_metadata_clears_only_human_gate():
    metadata = {
        "authors_order": ["Author A", "Author B"],
        "affiliations": ["Department A, University B"],
        "corresponding_author_name": "Author A",
        "corresponding_email": "author@example.org",
        "author_qualifications": "Author A works across empirical ecology and reproducible computational inference.",
        "orcid_ids": [],
        "funding_notes": "",
        "coi_notes": "",
    }
    result = MOD.audit(metadata)
    assert result["status"] == "metadata_complete_package_scientifically_ready"
    assert all(result["package_checks"].values())
    assert all(result["human_metadata_checks"].values())
    assert result["missing_human_metadata"] == []
    assert result["does_not_send_email"] is True
    assert result["does_not_infer_human_metadata"] is True
    assert result["focal_level_c_values_read"] is False
    assert result["empirical_ledger_increment"] == 0


def test_invalid_corresponding_email_remains_blocking():
    metadata = {
        "authors_order": ["Author A"],
        "affiliations": ["Department A, University B"],
        "corresponding_author_name": "Author A",
        "corresponding_email": "not-an-email",
        "author_qualifications": "Relevant qualification statement.",
    }
    result = MOD.audit(metadata)
    assert result["status"] == "blocked_human_metadata"
    assert result["human_metadata_checks"]["corresponding_email"] is False
    assert "corresponding_email" in result["missing_human_metadata"]


def test_gate_routes_only_current_manifest():
    result = MOD.audit(None)
    assert result["canonical_manifest"] == "manuscript/ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_6.md"
    assert result["stage1_title"] == (
        "Relation endpoints for ecological inference: when independent answers can support joint biological claims"
    )
