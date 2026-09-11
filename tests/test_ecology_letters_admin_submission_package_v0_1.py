from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = ROOT / "manuscript" / "ECOLOGY_LETTERS_TITLE_PAGE_V0_2.md"
COVER = ROOT / "manuscript" / "ECOLOGY_LETTERS_FULL_COVER_LETTER_V0_1.md"
COMPLIANCE = ROOT / "manuscript" / "ECOLOGY_LETTERS_COMPLIANCE_V0_3.md"
MANIFEST = ROOT / "manuscript" / "ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_3.md"


def test_admin_files_exist():
    for path in [TITLE, COVER, COMPLIANCE, MANIFEST]:
        assert path.exists(), path


def test_title_page_points_only_to_reviewer_hardened_scientific_package():
    text = TITLE.read_text(encoding="utf-8")
    assert "PREFIELD_FLAGSHIP_V0_7.md" in text
    assert "FULL_SUBMISSION_DISPLAY_MANIFEST_V0_1.md" in text
    assert "CLAIM_EVIDENCE_LEDGER_V0_4.md" in text
    assert "Display items:** 6" in text
    assert "empirical ledger = 1" in text.lower()
    assert "PREFIELD_FLAGSHIP_V0_6.md" not in text
    assert "[insert final corresponding-author email]" in text.lower()


def test_cover_letter_does_not_claim_unverified_human_or_level_c_facts():
    text = COVER.read_text(encoding="utf-8")
    assert "12 independently held-out taxa" in text
    assert "283 were evaluable" in text
    assert "rather than independent replication" in text
    assert "a1=P(valid|F=true)" in text
    assert "a0=P(valid|F=false)" in text
    assert "No focal Level-C biological outcome is opened" in text
    assert "[Insert statement confirming that the manuscript is not under consideration elsewhere" in text
    assert "[Insert one concise sentence explaining any recent related work" in text
    assert "all authors approve" not in text.lower().split("[insert statement", 1)[0]


def test_compliance_routes_current_proposal_and_full_packages():
    text = COMPLIANCE.read_text(encoding="utf-8")
    assert "ECOLOGY_LETTERS_300WORD_PITCH_V0_6.md" in text
    assert "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_6.md" in text
    assert "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_3.md" in text
    assert "ecology_letters_method_proposal_figure_v0_5.svg" in text
    assert "PREFIELD_FLAGSHIP_V0_7.md" in text
    assert "ECOLOGY_LETTERS_TITLE_PAGE_V0_2.md" in text
    assert "CLAIM_EVIDENCE_LEDGER_V0_4.md" in text
    assert "FULL_SUBMISSION_DISPLAY_MANIFEST_V0_1.md" in text
    assert "main text maximum: **5,000 words**" in text
    assert "maximum: **6** figures/tables/text boxes" in text
    assert "abstract maximum: **150 words**" in text
    assert "Empirical ledger:** remains 1" in text


def test_manifest_separates_proposal_from_invited_full_submission():
    text = MANIFEST.read_text(encoding="utf-8")
    assert "Stage 1 — unsolicited Method proposal" in text
    assert "Stage 2 — invited full Method manuscript" in text
    assert "Use only after an invitation/approved proposal" in text
    assert "Do not send until all four are human-confirmed" in text
    assert "No new Level-C field data are required for Stage 1" in text
    assert "PREFIELD_FLAGSHIP_V0_7.md" in text
    assert "ECOLOGY_LETTERS_TITLE_PAGE_V0_2.md" in text
    assert "CLAIM_EVIDENCE_LEDGER_V0_4.md" in text
    assert "figure5_invalid_state_decomposition_v0_3.svg" in text
    assert "Empirical ledger remains **1**" in text


def test_manifest_explicitly_supersedes_old_submission_versions():
    text = MANIFEST.read_text(encoding="utf-8")
    section = text.split("## Files explicitly superseded for submission routing", 1)[1]
    assert "PREFIELD_FLAGSHIP_V0_6.md" in section
    assert "ECOLOGY_LETTERS_TITLE_PAGE_V0_1.md" in section
    assert "ECOLOGY_LETTERS_COMPLIANCE_V0_2.md" in section
    assert "CLAIM_EVIDENCE_LEDGER_V0_2.md" in section
    assert "proposal figures before v0.5" in section


def test_admin_package_preserves_reviewer_hardened_scientific_boundary():
    combined = "\n".join(
        p.read_text(encoding="utf-8") for p in [TITLE, COVER, COMPLIANCE, MANIFEST]
    )
    assert "283 is not an independent sample size" in combined
    assert "source-discordance envelope" in combined
    assert "1-a1" in combined
    assert "1-a0" in combined
    assert "zero collapsing" in combined
    assert "pre-outcome endpoint-openability" in combined
    assert "empirical ledger remains **1**" in combined.lower()
