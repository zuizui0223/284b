from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPP = ROOT / "manuscript" / "PAPER1_SUPPLEMENT_V0_1.md"
MANIFEST = ROOT / "manuscript" / "PAPER1_SUPPLEMENT_MANIFEST_V0_1.md"


def test_supplement_materializes_all_seven_routed_sections():
    text = SUPP.read_text(encoding="utf-8")
    for i in range(1, 8):
        assert f"## Supplement S{i}." in text
    assert "empirical ledger = **1**" in text
    assert "Nothing here opens a new focal biological endpoint" in text


def test_s1_keeps_taxa_as_independent_units_and_q95_as_empirical_envelope():
    text = SUPP.read_text(encoding="utf-8")
    assert "independent held-out biological units are **12 taxa**" in text
    assert "283 cells; five stayed unresolved" in text
    assert "0 of 12 held-out taxa contained an envelope exceedance" in text
    assert "not a nominal 95% predictive interval" in text
    assert "not an independent binomial sample size" in text


def test_s2_fingerprint_is_audit_not_outcome_blindness_proof():
    text = SUPP.read_text(encoding="utf-8")
    assert "`opening_rule_reference`" in text
    assert "deterministic canonical JSON" in text
    assert "SHA-256" in text
    assert "not proof of outcome blindness" in text
    assert "results/relation_endpoint_contract_example_freeze_v0_1.json" in text


def test_s3_preserves_generalized_invalidity_and_benchmark_scope():
    text = SUPP.read_text(encoding="utf-8")
    assert "FPR_zero - FPR_gated = 1-a1" in text
    assert "TPR_zero - TPR_gated = 1-a0" in text
    assert "8,748 scenarios" in text
    assert "4,320" in text and "4,428" in text
    assert "not** an estimate of how common these observation regimes are in nature" in text
    assert "FDF ≈ 0.645" in text


def test_s4_s5_preserve_predata_repair_and_no_adaptive_rescue():
    text = SUPP.read_text(encoding="utf-8")
    assert "before field calibration data were entered" in text
    assert "one-sided exact Clopper–Pearson" in text
    assert "candidate identities, biological thresholds, minimum sample counts" in text
    assert "28/30" in text
    assert "60/60" in text
    assert "do not authorize outcome-dependent sample-size extension" in text


def test_s6_uses_real_systems_only_as_measurement_boundary_evidence():
    text = SUPP.read_text(encoding="utf-8")
    assert "CREMV3-007" in text
    assert "BELV3-012" in text
    assert "measurement-boundary results, not biological negatives" in text
    assert "focal hard invariant, soft cross-check and process-knockout outcomes remain sealed" in text
    assert "product_b_level_c_candidate_specific_calibration_audit_v5.json" in text
    assert "product_b_level_c_raw_calibration_reconstruction_v6.json" in text


def test_s7_does_not_turn_scope_classes_into_missing_results():
    text = SUPP.read_text(encoding="utf-8")
    assert "no fresh Level-B empirical reference endpoint is opened" in text
    assert "not missing empirical results required for the present paper" in text
    assert "Level-A source-discordance q95 must not be imported" in text


def test_manifest_routes_each_section_to_repository_evidence():
    text = MANIFEST.read_text(encoding="utf-8")
    for label in ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]:
        assert f"| {label} |" in text
    for path in [
        "results/reviewer2_level_a_structure_audit_v0_1.json",
        "results/relation_endpoint_contract_example_freeze_v0_1.json",
        "results/pre_field_state_dependent_invalidity_v0_2.json",
        "results/product_b_level_c_operational_package_v8_1.json",
        "results/product_b_level_c_source_qualification_v3.json",
        "results/product_b_level_c_raw_calibration_reconstruction_v6.json",
    ]:
        assert path in text


def test_supplement_prohibited_inferences_are_explicit():
    text = SUPP.read_text(encoding="utf-8")
    prohibited = [
        "Level C confirmed dependency",
        "Level C falsified dependency",
        "no record = no function",
        "five unresolved Level-A cells = failures",
        "283 Level-A diagnostics = independent replicates",
        "fingerprinting = proof of outcome blindness",
    ]
    for phrase in prohibited:
        assert phrase in text
