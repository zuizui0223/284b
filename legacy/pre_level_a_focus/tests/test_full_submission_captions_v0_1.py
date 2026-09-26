from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTIONS = ROOT / "manuscript" / "FULL_SUBMISSION_FIGURE_CAPTIONS_V0_1.md"


def test_captions_preserve_level_a_replication_boundary():
    text = CAPTIONS.read_text(encoding="utf-8")
    assert "independent held-out biological units were 12 taxa" in text
    assert "rather than treating 283 cells as independent n" in text
    assert "empirical envelope, not a nominal 95% predictive interval" in text


def test_captions_use_generalized_hard_endpoint_notation():
    text = CAPTIONS.read_text(encoding="utf-8")
    assert "a1=P(valid key | F=true)" in text
    assert "a0=P(valid key | F=false)" in text
    assert "adds exactly `1-a1`" in text
    assert "and `1-a0`" in text
    assert "special case `a1=a0=a`" in text
    assert "ablation of the endpoint's unresolved-state guard" in text


def test_captions_keep_level_c_preoutcome():
    text = CAPTIONS.read_text(encoding="utf-8")
    assert "no focal Level-C biological outcome is opened" in text
    assert "no focal biological dependency result" in text
    assert "empirical ledger remains 1" in text
