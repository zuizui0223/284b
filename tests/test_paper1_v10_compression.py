import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_9_CANDIDATE.md"
INTRO = ROOT / "manuscript" / "PAPER1_INTRODUCTION_V0_9_1_CANDIDATE.md"
METHODS = ROOT / "manuscript" / "PAPER1_METHODS_V0_10_CANDIDATE.md"
RESULTS = ROOT / "manuscript" / "PAPER1_RESULTS_V0_10_CANDIDATE.md"
REFS = ROOT / "manuscript" / "WORKING_REFERENCES_V0_9_1.md"
SUPP = ROOT / "manuscript" / "PAPER1_SUPPLEMENT_V0_1.md"
BUILDER = ROOT / "scripts" / "build_prefield_flagship_v0_10_candidate.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("v010", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _build() -> str:
    mod = _load_builder()
    return mod.build_candidate(
        SOURCE.read_text(encoding="utf-8"),
        INTRO.read_text(encoding="utf-8"),
        METHODS.read_text(encoding="utf-8"),
        RESULTS.read_text(encoding="utf-8"),
        REFS.read_text(encoding="utf-8"),
    )


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def _main(text: str) -> str:
    return text.split("## 1. Introduction", 1)[1].split("## Data and code availability", 1)[0]


def test_v10_is_materially_shorter_without_changing_submission_limits():
    source = SOURCE.read_text(encoding="utf-8")
    built = _build()
    source_n = _word_count(_main(source))
    built_n = _word_count(_main(built))
    assert built_n < source_n
    assert source_n - built_n >= 200
    assert built_n <= 5000
    abstract = built.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]
    assert _word_count(abstract) <= 150


def test_v10_preserves_core_level_a_numbers_and_replication_boundary():
    built = _build()
    for phrase in [
        "12 held-out taxa",
        "288 repeated diagnostics",
        "283",
        "five remained unresolved",
        "0 of 12 contained an empirical-envelope exceedance",
        "not an independent sample size",
        "empirical source-discordance envelopes",
    ]:
        assert phrase in built
    assert "0.38625" not in _main(built)
    assert "closest opened" not in _main(built).lower()
    assert "Supplement S1" in built


def test_v10_preserves_relation_separation_and_contract_object():
    built = _build()
    for phrase in [
        "opening_rule_reference",
        "deterministic canonical JSON",
        "SHA-256 fingerprint",
        "p_E=p_F=0.5",
        "v=0.5",
        "Blanchet et al. 2020",
        "Galiana et al. 2024",
        "Wilkinson et al. 2021",
    ]:
        assert phrase in built
    assert "not proof of outcome blindness" in built


def test_v10_keeps_exact_unresolved_state_result_but_moves_grid_bulk_to_supplement():
    built = _build()
    main = _main(built)
    assert "FPR_zero - FPR_gated = 1-a1" in main
    assert "TPR_zero - TPR_gated = 1-a0" in main
    assert "a1=a0=a" in main
    for detail in ["4,320", "4,428", "0.776", "1.2 x 10^-16", "0.645"]:
        assert detail not in main
    supp = SUPP.read_text(encoding="utf-8")
    assert "4,320" in supp and "4,428" in supp and "0.776" in supp
    assert "FDF ≈ 0.645" in supp
    assert "Supplement S3" in built


def test_v10_keeps_level_c_as_stopping_rule_only():
    built = _build()
    lower = built.lower()
    assert "CREMV3-007" in built
    assert "BELV3-012" in built
    assert "measurement-boundary results, not biological negatives" in built
    assert "next admissible information is new candidate-specific calibration" in built
    assert "focal hard invariant, soft cross-check and process-knockout outcomes remain sealed" in built
    for phrase in [
        "level c confirmed dependency",
        "level c falsified dependency",
        "level-c confirmed dependency",
        "level-c falsified dependency",
    ]:
        assert phrase not in lower


def test_v10_routes_provenance_and_feasibility_details_to_supplement():
    built = _build()
    main = _main(built)
    assert "Supplement S4" in built
    assert "Supplement S5" in built
    assert "Supplement S6" in built
    for detail in ["Wilson lower bound", "Clopper–Pearson", "28/30", "60/60"]:
        assert detail not in main
    supp = SUPP.read_text(encoding="utf-8")
    assert "Clopper–Pearson" in supp
    assert "28/30" in supp and "60/60" in supp


def test_v10_preserves_frozen_empirical_ledger_and_display_budget():
    built = _build()
    assert "**Empirical ledger:** 1." in built
    assert "Level A closed; Level B unopened; Level C focal biological outcomes sealed" in built
    display = built.split("## Proposed display items", 1)[1]
    assert len(re.findall(r"^\d+\. \*\*", display, flags=re.MULTILINE)) == 6
