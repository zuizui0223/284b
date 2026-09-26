import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PITCH = ROOT / "manuscript" / "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md"


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def test_pitch_v08_is_within_300_words_and_frozen_at_295():
    text = PITCH.read_text(encoding="utf-8")
    body = text.split("\n\n", 1)[1]
    assert _word_count(body) == 295
    assert _word_count(body) <= 300


def test_pitch_v08_makes_relation_layer_irreducibility_explicit():
    text = PITCH.read_text(encoding="utf-8")
    assert "not reducible to better marginal models" in text
    assert "exact `p_E=p_F=0.5`" in text
    assert "`P(E=1,F=0)` can range from 0 to 0.5" in text
    assert "Classical coupling bounds" in text


def test_pitch_v08_makes_prospective_contract_fingerprint_explicit():
    text = PITCH.read_text(encoding="utf-8")
    assert "calibration/protocol reference" in text
    assert "canonically serialized" in text
    assert "SHA-256 fingerprinted before focal opening" in text


def test_pitch_v08_preserves_empirical_and_level_c_boundaries():
    text = PITCH.read_text(encoding="utf-8")
    assert "12 fresh held-out taxa" in text
    assert "The cell count is diagnostic rather than independent replication" in text
    assert "five stayed unresolved" in text
    assert "functional absence lacked calibration" in text
    assert "Level C confirmed" not in text
    assert "Level C falsified" not in text
