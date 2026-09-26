from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG1 = ROOT / "manuscript" / "figures" / "figure1_relation_endpoint_contract_v0_1.svg"
FIG3 = ROOT / "manuscript" / "figures" / "figure3_event_function_dependency_v0_1.svg"
FIG4 = ROOT / "manuscript" / "figures" / "figure4_parallel_openability_audits_v0_1.svg"
TABLE1 = ROOT / "manuscript" / "TABLE1_CLAIM_EVIDENCE_MATRIX_V0_1.md"
LEDGER = ROOT / "manuscript" / "CLAIM_EVIDENCE_LEDGER_V0_4.md"
MANIFEST = ROOT / "manuscript" / "FULL_SUBMISSION_DISPLAY_MANIFEST_V0_1.md"


def test_all_static_display_files_exist():
    for path in [FIG1, FIG3, FIG4, TABLE1, LEDGER, MANIFEST]:
        assert path.exists()


def test_figure1_matches_executable_endpoint_engine_states():
    svg = FIG1.read_text(encoding="utf-8")
    assert "Five objects are frozen before focal comparison" in svg
    assert "consistent" in svg
    assert "attention_required" in svg
    assert "hard_violation_" in svg
    assert "no_observed_" in svg
    assert "noninformative_for_" in svg
    assert "focal values sealed" in svg
    assert "Levels D" not in svg  # do not imply D/E are directly implemented as named code paths


def test_figure3_keeps_provider_completeness_and_function_absence_separate():
    svg = FIG3.read_text(encoding="utf-8")
    assert "Adult plant occupancy" in svg
    assert "event-key implication" in svg
    assert "complete provider set" in svg
    assert "direct aggregate function" in svg
    assert "provider universe incomplete" in svg
    assert "unresolved" in svg
    assert "Close the alternative-provider universe" in svg


def test_figure4_is_openability_audit_not_biological_result():
    svg = FIG4.read_text(encoding="utf-8")
    assert "Cremastra" in svg
    assert "Belonocnema" in svg
    assert "functional absence uncalibrated" in svg
    assert "usable-resource absence uncalibrated" in svg
    assert "Hard endpoint opening = false" in svg
    assert "no focal biological outcome is opened" in svg
    assert "confirmed dependency" not in svg.lower()
    assert "falsified dependency" not in svg.lower()


def test_table1_preserves_reviewer_hardened_claim_boundaries():
    table = TABLE1.read_text(encoding="utf-8")
    assert "12 fresh held-out taxa" in table
    assert "283 evaluable" in table
    assert "not independent replicates" in table
    assert "empirical source-discordance envelope" in table
    assert "Level C — focal hard endpoint" in table
    assert "Unopened" in table
    assert "No record = no function" in table
    assert "Empirical ledger remains **1**" in table


def test_ledger_uses_state_dependent_validity_generalization():
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "a1=P(valid|F=true)" in ledger
    assert "a0=P(valid|F=false)" in ledger
    assert "FPR_zero-FPR_gated=1-a1" in ledger
    assert "TPR_zero-TPR_gated=1-a0" in ledger
    assert "old `1-a` equality is only the equal-validity special case" in ledger
    assert "283 Level-A cells are independent replicates" in ledger


def test_manifest_has_exactly_six_canonical_display_items():
    text = MANIFEST.read_text(encoding="utf-8")
    for i in range(1, 7):
        assert f"{i}. **" in text
    assert "figure2_level_a_empirical_anchor_v0_2.svg" in text
    assert "figure5_invalid_state_decomposition_v0_3.svg" in text
    assert "CLAIM_EVIDENCE_LEDGER_V0_4.md" in text
