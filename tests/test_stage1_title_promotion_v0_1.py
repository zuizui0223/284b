from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = "Relation endpoints for ecological inference: when independent answers can support joint biological claims"
OLD = "Prospective validation of ecological answers: from cross-source reproducibility to identifiable biological absence"

AUDIT = ROOT / "manuscript" / "TITLE_AUDIT_V0_1.md"
PITCH = ROOT / "manuscript" / "ECOLOGY_LETTERS_300WORD_PITCH_V0_7.md"
PROPOSAL = ROOT / "manuscript" / "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_8.md"
EMAIL = ROOT / "manuscript" / "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_5.md"
COMPLIANCE = ROOT / "manuscript" / "ECOLOGY_LETTERS_COMPLIANCE_V0_5.md"
MANIFEST = ROOT / "manuscript" / "ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_5.md"
SNAPSHOT = ROOT / "manuscript" / "ECOLOGY_LETTERS_SUBMISSION_READY_SNAPSHOT_V0_3.md"
FULL = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_7.md"


def test_selected_title_is_explicitly_audited():
    text = AUDIT.read_text(encoding="utf-8")
    assert TITLE in text
    assert "### A — selected" in text
    assert "Promote Candidate A" in text
    assert "Stage-1 working title" in text
    assert "empirical ledger remains 1" in text.lower()


def test_stage1_surfaces_use_promoted_title():
    for path in [PROPOSAL, EMAIL, COMPLIANCE, MANIFEST, SNAPSHOT]:
        text = path.read_text(encoding="utf-8")
        assert TITLE in text, path


def test_stage1_routing_promotes_only_current_files():
    manifest = MANIFEST.read_text(encoding="utf-8")
    compliance = COMPLIANCE.read_text(encoding="utf-8")
    assert "ECOLOGY_LETTERS_300WORD_PITCH_V0_7.md" in manifest
    assert "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_8.md" in manifest
    assert "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_5.md" in manifest
    assert "ECOLOGY_LETTERS_COMPLIANCE_V0_5.md" in manifest
    assert "TITLE_AUDIT_V0_1.md" in manifest
    assert "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_8.md" in compliance
    assert "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_5.md" in compliance


def test_pitch_content_remains_relation_layer_strengthened_and_under_same_version():
    pitch = PITCH.read_text(encoding="utf-8")
    assert "Classical coupling bounds show why this layer is not reducible to better marginal models" in pitch
    assert "12 fresh held-out taxa" in pitch
    assert "cell count is diagnostic rather than independent replication" in pitch
    assert "Unqualified negatives remain unresolved" in pitch


def test_full_manuscript_is_intentionally_not_silently_retitled_before_invitation():
    full = FULL.read_text(encoding="utf-8")
    manifest = MANIFEST.read_text(encoding="utf-8")
    snapshot = SNAPSHOT.read_text(encoding="utf-8")
    assert full.startswith(f"# {OLD}")
    assert "canonical **scientific** manuscript remains `manuscript/PREFIELD_FLAGSHIP_V0_7.md` until invitation" in manifest
    assert "not the promoted Stage-1 working title" in snapshot
    assert "Do not silently edit v0.7" in snapshot


def test_title_promotion_changes_no_empirical_state():
    combined = "\n".join(
        p.read_text(encoding="utf-8") for p in [AUDIT, COMPLIANCE, MANIFEST, SNAPSHOT]
    )
    assert "Level B" in combined
    assert "Level C" in combined
    assert "Empirical ledger remains **1**" in combined or "Empirical ledger: **1**" in combined
    assert "Title promotion increment = 0" in manifest
    assert "no threshold, candidate, relation or endpoint-opening rule changes" in AUDIT.read_text(encoding="utf-8")
