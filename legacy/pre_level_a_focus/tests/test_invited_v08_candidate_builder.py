import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_prefield_flagship_v0_8_candidate.py"
SOURCE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_7.md"

SPEC = importlib.util.spec_from_file_location("v08_builder", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def _abstract(text: str) -> str:
    start = text.index("## Abstract") + len("## Abstract")
    end = text.index("## 1. Introduction")
    return text[start:end]


def _main_text(text: str) -> str:
    start = text.index("## 1. Introduction")
    end = text.index("## Data and code availability")
    return text[start:end]


def candidate() -> str:
    return MOD.build_candidate(SOURCE.read_text(encoding="utf-8"))


def test_builder_promotes_title_but_not_source_file():
    source = SOURCE.read_text(encoding="utf-8")
    out = candidate()
    assert source.startswith("# " + MOD.OLD_TITLE)
    assert out.startswith("# " + MOD.NEW_TITLE)
    assert "invited-manuscript candidate v0.8 — not canonical until invitation/promotion audit" in out
    assert MOD.NEW_TITLE not in source


def test_relation_layer_separation_is_inserted_once_and_classical():
    out = candidate()
    assert out.count("### 2.2 Why accurate answers do not eliminate the relation layer") == 1
    assert out.count("### 2.3 Soft coherence and hard dependency") == 1
    assert "max(0,p_E-p_F) <= v <= min(p_E,1-p_F)" in out
    assert "p_E=p_F=0.5" in out
    assert "same perfect marginal answers admit both `v=0`" in out
    assert "separation argument using established probability theory, not a new coupling theorem" in out
    assert "A JSDM can estimate joint rather than marginal structure" in out


def test_prior_work_boundary_expands_without_overclaiming():
    out = candidate()
    assert "Data-fusion methods combine heterogeneous observation sources" in out
    assert "joint species distribution models distinguish marginal from joint prediction" in out
    assert "do **not** claim novelty for imperfect detection, joint-distribution modelling, data fusion" in out
    for ref in ["Nelsen RB. 2006", "Wilkinson DP", "Galiana N", "Pacifici K"]:
        assert ref in out


def test_frozen_empirical_boundary_is_preserved():
    out = candidate()
    required = [
        "independent held-out biological units were 12 taxa",
        "283/283",
        "five stayed closed",
        "No focal Level-C cross-role value",
        "FPR_zero - FPR_gated = 1-a1",
        "TPR_zero - TPR_gated = 1-a0",
        "0.38625",
        "0.39085",
    ]
    for phrase in required:
        assert phrase in out
    forbidden = [
        "Level C confirmed dependency",
        "Level C falsified dependency",
        "Level-C confirmed dependency",
        "Level-C falsified dependency",
    ]
    for phrase in forbidden:
        assert phrase not in out


def test_candidate_remains_within_method_limits():
    out = candidate()
    assert _word_count(_abstract(out)) <= 150
    assert _word_count(_main_text(out)) <= 5000
    display_section = out.split("## Proposed display items", 1)[1]
    items = re.findall(r"^\d+\. \*\*", display_section, flags=re.MULTILINE)
    assert len(items) == 6


def test_candidate_builder_is_deterministic():
    source = SOURCE.read_text(encoding="utf-8")
    assert MOD.build_candidate(source) == MOD.build_candidate(source)
