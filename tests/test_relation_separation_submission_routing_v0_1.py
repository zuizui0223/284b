from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manuscript" / "ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_4.md"
COMPLIANCE = ROOT / "manuscript" / "ECOLOGY_LETTERS_COMPLIANCE_V0_4.md"
PROPOSAL = ROOT / "manuscript" / "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_7.md"
EMAIL = ROOT / "manuscript" / "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_4.md"


def test_manifest_promotes_relation_separation_stage1_files():
    text = MANIFEST.read_text(encoding="utf-8")
    assert "ECOLOGY_LETTERS_300WORD_PITCH_V0_7.md" in text
    assert "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_7.md" in text
    assert "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_4.md" in text
    assert "ECOLOGY_LETTERS_COMPLIANCE_V0_4.md" in text
    assert "RELATION_LAYER_SEPARATION_V0_1.md" in text
    assert "relation_layer_separation_v0_1.json" in text
    assert "PREFIELD_FLAGSHIP_V0_7.md" in text
    assert "full manuscript remains v0.7 until invitation" in text.lower()


def test_compliance_concedes_jsdm_and_classical_coupling_prior_art():
    text = COMPLIANCE.read_text(encoding="utf-8")
    assert "JSDMs or the distinction between marginal and joint prediction" in text
    assert "data fusion" in text
    assert "Fréchet-Hoeffding bounds or classical coupling theory" in text
    assert "not a new probability theorem" in text
    assert "Empirical ledger" in text and "remains **1**" in text


def test_proposal_states_irreducibility_without_attacking_jsdms():
    text = PROPOSAL.read_text(encoding="utf-8")
    assert "Why this layer is not reducible to better upstream models" in text
    assert "The probability bounds are classical" in text
    assert "A suitable JSDM may estimate the missing joint coupling" in text
    assert "which joint relation is licensed" in text
    assert "Paper 1 contains no Level-C biological dependency result" in text


def test_email_uses_new_pitch_and_preserves_human_placeholders():
    text = EMAIL.read_text(encoding="utf-8")
    assert "ECOLOGY_LETTERS_300WORD_PITCH_V0_7.md" in text
    assert "JSDM" in text
    assert "hard-violation probability from 0 to 0.5" in text
    assert "[Insert final author-qualification sentence(s) here" in text
    assert "[Affiliation]" in text
    assert "[Email]" in text
