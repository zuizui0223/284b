import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_9_CANDIDATE.md"


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def _abstract(text: str) -> str:
    return text.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]


def _main_text(text: str) -> str:
    return text.split("## 1. Introduction", 1)[1].split("## Data and code availability", 1)[0]


def test_v09_candidate_respects_ecology_letters_size_limits():
    text = CANDIDATE.read_text(encoding="utf-8")
    assert _word_count(_abstract(text)) <= 150
    assert _word_count(_main_text(text)) <= 5000


def test_v09_candidate_keeps_frozen_empirical_boundary():
    text = CANDIDATE.read_text(encoding="utf-8")
    lower = text.lower()
    assert "level a closed; level b unopened; level c focal biological outcomes sealed" in lower
    assert "**empirical ledger:** 1" in lower
    for phrase in [
        "level c confirmed dependency",
        "level c falsified dependency",
        "level-c confirmed dependency",
        "level-c falsified dependency",
    ]:
        assert phrase not in lower
    assert "no focal level-c dependency is confirmed or falsified" in lower


def test_v09_candidate_leads_level_a_at_taxon_replication_level():
    text = CANDIDATE.read_text(encoding="utf-8")
    assert "**0 of 12 taxa with an exceedance**" in text
    assert "283/283 cell count is a diagnostic summary rather than an independent sample size" in text
    assert "five remained unresolved" in text
    assert "not as a nominal 95% predictive interval" in text


def test_v09_candidate_keeps_relation_layer_as_nonempirical_separation():
    text = CANDIDATE.read_text(encoding="utf-8")
    assert "Classical Frechet-Hoeffding coupling bounds" in text
    assert "same exact marginals" in text
    assert "v=0.5" in text
    assert "established probability theory" in text
    assert "Joint statistical models may supply coupling information" in text


def test_v09_candidate_preserves_generalized_unresolved_state_result():
    text = CANDIDATE.read_text(encoding="utf-8")
    assert "a1 = P(valid key | F=true)" in text
    assert "a0 = P(valid key | F=false)" in text
    assert "FPR_zero - FPR_gated = 1-a1" in text
    assert "TPR_zero - TPR_gated = 1-a0" in text
    assert "controlled special case `a1=a0=a`" in text
    assert "zero-collapsing ablation" in text


def test_v09_candidate_uses_level_c_only_as_openability_stress_test():
    text = CANDIDATE.read_text(encoding="utf-8")
    assert "CREMV3-007" in text
    assert "BELV3-012" in text
    assert "negative functional state was not independently calibrated" in text
    assert "measurement-boundary results, not biological negatives" in text
    assert "Their focal hard invariant, soft cross-check and process-knockout outcomes remain sealed" in text


def test_v09_candidate_has_exactly_six_display_items():
    text = CANDIDATE.read_text(encoding="utf-8")
    section = text.split("## Proposed display items", 1)[1]
    items = re.findall(r"^\d+\. \*\*", section, flags=re.MULTILINE)
    assert len(items) == 6
