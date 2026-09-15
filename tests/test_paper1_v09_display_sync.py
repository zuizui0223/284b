from pathlib import Path
import importlib.util
import re

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "manuscript" / "figures"
FIG1 = FIG_DIR / "figure1_relation_endpoint_contract_v0_2.svg"
FIG2 = FIG_DIR / "figure2_level_a_empirical_anchor_v0_2.svg"
FIG3 = FIG_DIR / "figure3_relation_layer_and_event_function_v0_2.svg"
FIG4 = FIG_DIR / "figure4_parallel_openability_audits_v0_1.svg"
FIG5 = FIG_DIR / "figure5_invalid_state_decomposition_v0_3.svg"
TABLE = ROOT / "manuscript" / "TABLE1_CLAIM_EVIDENCE_MATRIX_V0_2.md"
CAPTIONS = ROOT / "manuscript" / "FULL_SUBMISSION_FIGURE_CAPTIONS_V0_2.md"
MANIFEST = ROOT / "manuscript" / "FULL_SUBMISSION_DISPLAY_MANIFEST_V0_2.md"
LEDGER = ROOT / "manuscript" / "CLAIM_EVIDENCE_LEDGER_V0_5.md"
BUILDER = ROOT / "scripts" / "build_paper1_v09_display_figures.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("v09fig", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_v09_display_route_has_exactly_six_items_and_current_assets():
    text = MANIFEST.read_text(encoding="utf-8")
    items = re.findall(r"^\d+\. \*\*", text, flags=re.MULTILINE)
    assert len(items) == 6
    for path in [FIG1, FIG2, FIG3, FIG4, FIG5, TABLE, CAPTIONS, LEDGER]:
        assert path.exists(), path
    assert "PREFIELD_FLAGSHIP_V0_9_CANDIDATE.md" in text
    assert "CLAIM_EVIDENCE_LEDGER_V0_5.md" in text
    assert "empirical ledger = 1" in text


def test_new_figures_are_deterministically_reproducible():
    mod = _load_builder()
    assert FIG1.read_text(encoding="utf-8") == mod.figure1()
    assert FIG3.read_text(encoding="utf-8") == mod.figure3()


def test_figure1_centers_contract_fingerprint_and_unresolved_state():
    svg = FIG1.read_text(encoding="utf-8")
    for phrase in [
        "Five-part relation-endpoint contract",
        "opening_rule_reference",
        "canonical deterministic JSON",
        "SHA-256 fingerprint",
        "not proof that investigators were outcome-blind",
        "Calibrated soft relation",
        "Directional hard relation",
        "remains unresolved",
    ]:
        assert phrase in svg
    assert "Level D" not in svg
    assert "Level E" not in svg


def test_figure3_integrates_relation_separation_and_event_function_semantics():
    svg = FIG3.read_text(encoding="utf-8")
    for phrase in [
        "same perfect marginals",
        "P(E=1)=0.5",
        "v=0",
        "v=0.5",
        "Fréchet–Hoeffding bounds",
        "Established probability theory",
        "Rejected shortcut",
        "E(k)",
        "F(k)",
        "aggregate function",
        "absence → unresolved",
        "Joint models can estimate coupling",
    ]:
        assert phrase in svg


def test_table_and_ledger_follow_v09_claim_hierarchy_without_opening_level_c():
    table = TABLE.read_text(encoding="utf-8")
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "0/12 taxa with an envelope exceedance" in table
    assert "same exact marginals" in table
    assert "SHA-256 fingerprinting" in table
    assert "FPR_zero-FPR_gated=1-a1" in table
    assert "TPR_zero-TPR_gated=1-a0" in table
    assert "focal hard/soft/process-knockout outcomes remain sealed" in table
    assert "M0" in ledger and "M1" in ledger and "E1" in ledger and "M4" in ledger and "Q1" in ledger
    assert "empirical ledger remains **1**" in ledger
    for forbidden in ["Level C confirmed dependency", "Level C falsified dependency"]:
        assert forbidden in ledger  # only inside prohibited-inference section


def test_captions_lead_with_taxon_replication_and_keep_level_c_as_stopping_rule():
    text = CAPTIONS.read_text(encoding="utf-8")
    assert "0 of 12 taxa contained an envelope exceedance" in text
    assert "283 evaluable cells provide repeated diagnostic stress tests" in text
    assert "established probability theory" in text
    assert "no focal Level-C biological dependency outcome is opened" in text
    assert "empirical ledger remains **1**" in text


def test_stage1_frozen_assets_are_not_repointed_by_v09_manifest():
    text = MANIFEST.read_text(encoding="utf-8")
    assert "noncanonical relative to the frozen Stage-1 package" in text
    # The v0.9 route uses new versioned assets instead of overwriting the frozen ones.
    assert "figure1_relation_endpoint_contract_v0_2.svg" in text
    assert "figure3_relation_layer_and_event_function_v0_2.svg" in text
    assert "TABLE1_CLAIM_EVIDENCE_MATRIX_V0_2.md" in text
    assert "FULL_SUBMISSION_FIGURE_CAPTIONS_V0_2.md" in text
