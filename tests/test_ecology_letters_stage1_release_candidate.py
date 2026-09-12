import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SPEC = importlib.util.spec_from_file_location(
    "freeze_ecology_letters_stage1_release_candidate",
    SCRIPTS / "freeze_ecology_letters_stage1_release_candidate.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

RECEIPT = ROOT / "results" / "ecology_letters_stage1_release_candidate_v0_1.json"
SOURCE_COMMIT = "36d3d3c414b1ae18ccd27f57c4f109997bdab64e"
EXPECTED_PACKAGE_ID = "c39f94e81f27183ce3d298dee2206242934baee3b7b036741fe6c80c6a08dbad"


def test_committed_release_candidate_matches_freeze_utility_exactly():
    committed = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert committed == MOD.build_receipt(SOURCE_COMMIT)
    assert committed["package_identity_sha256"] == EXPECTED_PACKAGE_ID


def test_release_candidate_freezes_current_stage1_surface_not_human_metadata():
    receipt = MOD.build_receipt(SOURCE_COMMIT)
    paths = receipt["package_identity_material"]["canonical_paths"]
    assert "manuscript/ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md" in paths
    assert "manuscript/ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md" in paths
    assert "manuscript/ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md" in paths
    assert "manuscript/ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_6.md" in paths
    assert "scripts/audit_ecology_letters_stage1_send_readiness.py" in paths
    assert "scripts/render_ecology_letters_stage1_email.py" in paths
    assert receipt["human_metadata_embedded"] is False
    assert receipt["email_sent"] is False


def test_release_candidate_preserves_empirical_boundary():
    receipt = MOD.build_receipt(SOURCE_COMMIT)
    assert receipt["focal_level_c_values_read"] is False
    assert receipt["empirical_ledger_increment"] == 0
    assert receipt["global_284b_empirical_ledger"] == 1
    assert receipt["status"] == "scientific_package_frozen_human_metadata_external"


def test_package_identity_changes_if_source_commit_or_file_set_changes():
    original = MOD.build_receipt(SOURCE_COMMIT)["package_identity_sha256"]
    other_commit = "0" * 40
    mutated = MOD.build_receipt(other_commit)["package_identity_sha256"]
    assert original != mutated


def test_invalid_source_commit_is_rejected():
    try:
        MOD.build_receipt("not-a-sha")
    except ValueError as exc:
        assert "40-character lowercase Git SHA" in str(exc)
    else:
        raise AssertionError("invalid source commit should fail")
