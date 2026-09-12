import importlib.util
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_ecology_letters_stage1_release_candidate.py"
RECEIPT = ROOT / "results" / "ecology_letters_stage1_release_candidate_v0_2.json"

SPEC = importlib.util.spec_from_file_location("stage1_rc_v02_audit", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

EXPECTED_PACKAGE_ID = "2787b4462850458dbbb01f975ef71d7171f553e2f4f7898c851a43a1548fea87"
EXPECTED_SOURCE_COMMIT = "8a1dbfb2bc4d03e3ade39e9b6b20173ab71aac4e"


def test_v02_receipt_identity_is_self_consistent():
    receipt = MOD.load_receipt(RECEIPT)
    assert receipt["package_identity_sha256"] == EXPECTED_PACKAGE_ID
    assert receipt["source_tree_commit"] == EXPECTED_SOURCE_COMMIT
    assert receipt["canonical_file_count"] == 20
    assert len(receipt["canonical_blob_sha1"]) == 20
    assert MOD.recompute_package_identity(receipt) == EXPECTED_PACKAGE_ID


def test_current_tree_is_byte_identical_to_frozen_rc():
    audit = MOD.audit_current_tree(root=ROOT, receipt_path=RECEIPT)
    assert audit["status"] == "matches_frozen_release_candidate"
    assert audit["byte_identical_to_frozen_release_candidate"] is True
    assert audit["matched_file_count"] == 20
    assert audit["missing_paths"] == []
    assert audit["changed_files"] == []
    assert audit["focal_level_c_values_read"] is False
    assert audit["empirical_ledger_increment"] == 0
    assert audit["global_284b_empirical_ledger"] == 1


def test_one_byte_drift_is_detected(tmp_path):
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    for relpath in receipt["canonical_blob_sha1"]:
        src = ROOT / relpath
        dst = tmp_path / relpath
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    target_rel = "manuscript/ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md"
    target = tmp_path / target_rel
    target.write_bytes(target.read_bytes() + b"\n")

    audit = MOD.audit_current_tree(root=tmp_path, receipt_path=RECEIPT)
    assert audit["status"] == "release_candidate_drift_detected"
    assert audit["byte_identical_to_frozen_release_candidate"] is False
    assert audit["missing_paths"] == []
    assert [item["path"] for item in audit["changed_files"]] == [target_rel]


def test_git_blob_hash_is_content_sensitive_and_matches_known_empty_blob():
    assert MOD.git_blob_sha1_bytes(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    assert MOD.git_blob_sha1_bytes(b"a") != MOD.git_blob_sha1_bytes(b"b")


def test_receipt_keeps_human_and_empirical_layers_outside_rc():
    receipt = MOD.load_receipt(RECEIPT)
    assert receipt["human_metadata_embedded"] is False
    assert receipt["email_sent"] is False
    assert receipt["focal_level_c_values_read"] is False
    assert receipt["empirical_ledger_increment"] == 0
    assert receipt["global_284b_empirical_ledger"] == 1
