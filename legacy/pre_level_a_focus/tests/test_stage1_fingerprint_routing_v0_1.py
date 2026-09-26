from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"

PITCH = MANUSCRIPT / "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md"
PROPOSAL = MANUSCRIPT / "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md"
EMAIL = MANUSCRIPT / "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md"
COMPLIANCE = MANUSCRIPT / "ECOLOGY_LETTERS_COMPLIANCE_V0_6.md"
MANIFEST = MANUSCRIPT / "ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_6.md"
SNAPSHOT = MANUSCRIPT / "ECOLOGY_LETTERS_SUBMISSION_READY_SNAPSHOT_V0_4.md"
ENGINE = ROOT / "scripts" / "relation_endpoint_contract.py"
FREEZER = ROOT / "scripts" / "freeze_relation_endpoint_contract.py"
EXAMPLE = ROOT / "config" / "relation_endpoint_contract_example.json"
RECEIPT = ROOT / "results" / "relation_endpoint_contract_example_freeze_v0_1.json"

CURRENT = [PITCH, PROPOSAL, EMAIL, COMPLIANCE, MANIFEST, SNAPSHOT]
FINGERPRINT = "aeced85ab6708b6d3713e46babbc2c32654dae2d728d5127d1d5c9e05c949da6"


def test_current_stage1_files_exist():
    for path in CURRENT + [ENGINE, FREEZER, EXAMPLE, RECEIPT]:
        assert path.exists(), path


def test_manifest_is_the_single_current_stage1_routing_surface():
    text = MANIFEST.read_text(encoding="utf-8")
    assert text.startswith("# Ecology Letters submission manifest v0.6")
    assert "This is the single Stage-1 routing surface" in text
    assert "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md" in text
    assert "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md" in text
    assert "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md" in text
    assert "ECOLOGY_LETTERS_COMPLIANCE_V0_6.md" in text
    assert "proposal pitches before v0.8" in text
    assert "proposal rationales before v0.9" in text
    assert "proposal email wrappers before v0.6" in text
    assert "compliance checklists before v0.6" in text
    assert "submission manifests before v0.6" in text


def test_current_stage1_surfaces_expose_fingerprintable_prospectivity():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in CURRENT)
    assert "opening_rule_reference" in combined
    assert "SHA-256" in combined
    assert "canonical" in combined.lower()
    assert "fingerprint" in combined.lower()
    assert FINGERPRINT in combined


def test_engine_schema_binds_opening_rule_reference():
    text = ENGINE.read_text(encoding="utf-8")
    assert '"opening_rule_reference"' in text
    assert "opening_rule_reference: str" in text
    assert '("opening_rule_reference", self.opening_rule_reference)' in text
    assert "def fingerprint_sha256" in text


def test_fingerprint_promotion_does_not_open_new_empirical_endpoint():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in [COMPLIANCE, MANIFEST, SNAPSHOT])
    assert "Empirical ledger remains **1**" in combined or "Empirical ledger: **1**" in combined
    assert "Level B" in combined
    assert "Level C" in combined
    assert "focal" in combined.lower() and "sealed" in combined.lower()
