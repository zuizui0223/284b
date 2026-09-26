import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "finalize_ecology_letters_stage1_package.py"

SPEC = importlib.util.spec_from_file_location("stage1_finalizer", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def synthetic_metadata():
    return {
        "authors_order": ["Author A", "Author B"],
        "affiliations": ["Department A, University B"],
        "corresponding_author_name": "Author A",
        "corresponding_email": "author@example.org",
        "author_qualifications": "Author A works across empirical ecology and reproducible computational inference.",
        "orcid_ids": [],
        "funding_notes": "",
        "coi_notes": "",
    }


def test_finalizer_blocks_incomplete_metadata():
    try:
        MOD.build_finalization({}, write_outputs=False)
    except ValueError as exc:
        assert "blocked_human_metadata" in str(exc)
    else:
        raise AssertionError("incomplete metadata should block finalization")


def test_finalizer_builds_non_sensitive_receipt_without_sending():
    metadata = synthetic_metadata()
    rendered, receipt = MOD.build_finalization(metadata, write_outputs=False)

    assert receipt["status"] == "finalized_not_sent"
    assert receipt["release_candidate_byte_identical"] is True
    assert receipt["required_human_metadata_complete"] is True
    assert receipt["raw_human_metadata_embedded_in_receipt"] is False
    assert receipt["does_not_send_email"] is True
    assert receipt["does_not_infer_human_metadata"] is True
    assert receipt["focal_level_c_values_read"] is False
    assert receipt["empirical_ledger_increment"] == 0
    assert receipt["global_284b_empirical_ledger"] == 1
    assert receipt["rendered_email_sha256"] == MOD._sha256_text(rendered)

    receipt_text = json.dumps(receipt, ensure_ascii=False)
    assert metadata["corresponding_email"] not in receipt_text
    assert metadata["corresponding_author_name"] not in receipt_text
    assert metadata["author_qualifications"] not in receipt_text


def test_finalizer_writes_email_and_receipt_only_outside_repo(tmp_path):
    metadata = synthetic_metadata()
    _, receipt = MOD.build_finalization(metadata, out_dir=tmp_path, write_outputs=True)

    email_path = tmp_path / MOD.EMAIL_FILENAME
    receipt_path = tmp_path / MOD.RECEIPT_FILENAME
    assert email_path.exists()
    assert receipt_path.exists()
    assert receipt["rendered_email_sha256"] == MOD._sha256_text(email_path.read_text(encoding="utf-8"))

    stored_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert stored_receipt == receipt
    assert metadata["corresponding_email"] in email_path.read_text(encoding="utf-8")
    assert metadata["corresponding_email"] not in receipt_path.read_text(encoding="utf-8")


def test_finalizer_refuses_repository_output():
    metadata = synthetic_metadata()
    repo_output = ROOT / "tmp-stage1-output"
    try:
        MOD.build_finalization(metadata, out_dir=repo_output, write_outputs=True)
    except ValueError as exc:
        assert "inside the repository" in str(exc)
    else:
        raise AssertionError("repository output should be refused")


def test_finalizer_binds_current_release_candidate_identity():
    _, receipt = MOD.build_finalization(synthetic_metadata(), write_outputs=False)
    assert receipt["release_candidate_package_identity_sha256"] == (
        "2787b4462850458dbbb01f975ef71d7171f553e2f4f7898c851a43a1548fea87"
    )
    assert receipt["release_candidate_source_tree_commit"] == (
        "8a1dbfb2bc4d03e3ade39e9b6b20173ab71aac4e"
    )
