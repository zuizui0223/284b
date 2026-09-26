from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manuscript" / "ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_6.md"
COMPLIANCE = ROOT / "manuscript" / "ECOLOGY_LETTERS_COMPLIANCE_V0_6.md"
PROPOSAL = ROOT / "manuscript" / "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md"
EMAIL = ROOT / "manuscript" / "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md"


def test_manifest_promotes_current_fingerprinted_stage1_files():
    text = MANIFEST.read_text(encoding="utf-8")
    assert "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md" in text
    assert "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md" in text
    assert "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md" in text
    assert "ECOLOGY_LETTERS_COMPLIANCE_V0_6.md" in text
    assert "RELATION_LAYER_SEPARATION_V0_1.md" in text
    assert "relation_layer_separation_v0_1.json" in text
    assert "freeze_relation_endpoint_contract.py" in text
    assert "relation_endpoint_contract_example_freeze_v0_1.json" in text
    assert "opening_rule_reference" in text
    assert "aeced85ab6708b6d3713e46babbc2c32654dae2d728d5127d1d5c9e05c949da6" in text
    assert "PREFIELD_FLAGSHIP_V0_7.md" in text
    assert "build_prefield_flagship_v0_8_candidate.py" in text


def test_compliance_concedes_prior_art_and_defines_executable_prospectivity():
    text = COMPLIANCE.read_text(encoding="utf-8")
    assert "JSDMs or marginal-versus-joint prediction" in text
    assert "data fusion" in text
    assert "Fréchet-Hoeffding bounds / classical coupling theory" in text
    assert "not a new probability theorem" in text
    assert "opening_rule_reference" in text
    assert "SHA-256 fingerprinted" in text
    assert "Hashing is an audit mechanism, not proof of outcome blindness" in text
    assert "Empirical ledger" in text and "remains **1**" in text


def test_proposal_states_irreducibility_and_fingerprintable_contract():
    text = PROPOSAL.read_text(encoding="utf-8")
    assert "Why this layer is not reducible to better upstream models" in text
    assert "The probability bounds are classical" in text
    assert "A suitable JSDM may estimate the missing joint coupling" in text
    assert "which joint relation is licensed" in text
    assert "### Auditable prospective freezing" in text
    assert "opening_rule_reference" in text
    assert "deterministic canonical JSON and SHA-256 fingerprinted" in text
    assert "Paper 1 contains no Level-C biological dependency result" in text


def test_email_uses_current_pitch_and_preserves_human_placeholders():
    text = EMAIL.read_text(encoding="utf-8")
    assert "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md" in text
    assert "Our 295-word proposal" in text
    assert "SHA-256 fingerprinted" in text
    assert "hard-violation probability from 0 to 0.5" in text
    assert "[Insert final author-qualification sentence(s) here" in text
    assert "[Affiliation]" in text
    assert "[Email]" in text
