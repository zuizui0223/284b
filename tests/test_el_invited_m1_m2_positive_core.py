import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "manuscript" / "ECOLOGY_LETTERS_INVITED_M1_M2_V1.md"
LEDGER = ROOT / "manuscript" / "ECOLOGY_LETTERS_INVITED_M1_M2_CLAIM_LEDGER_V1.md"

def _abstract(text: str) -> str:
    m = re.search(r"## Abstract\\n\\n(.*?)\\n\\n## 1\\.", text, flags=re.S)
    assert m
    return m.group(1)

def test_positive_core_only():
    text = PAPER.read_text(encoding="utf-8")
    assert "0 of 12 taxa with an exceedance" in text
    assert "FPR_zero - FPR_gated = 1-a1" in text
    assert "TPR_zero - TPR_gated = 1-a0" in text
    assert "approximately 0.645" in text
    for forbidden in ("Cremastra", "Belonocnema", "SMIL001"):
        assert forbidden not in text

def test_replication_boundary():
    text = PAPER.read_text(encoding="utf-8")
    assert "not 288 independent biological replicates" in text
    assert "five remained unresolved" in text

def test_abstract_is_method_length_safe():
    words = re.findall(r"\\b[\\w=-]+\\b", _abstract(PAPER.read_text(encoding="utf-8")))
    assert len(words) <= 150

def test_claim_ledger_prohibits_pseudoreplication_and_level_c():
    text = LEDGER.read_text(encoding="utf-8")
    assert "283 independent biological replicates" in text
    assert "Level-C dependency confirmation or falsification" in text
