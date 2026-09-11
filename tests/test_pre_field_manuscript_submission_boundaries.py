import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_2.md"
PITCH = ROOT / "manuscript" / "ECOLOGY_LETTERS_300WORD_PITCH_V0_2.md"
SUMMARY = ROOT / "results" / "pre_field_identifiability_benchmark_summary_v0_1.json"


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def _main_text(manuscript: str) -> str:
    start = manuscript.index("## 1. Introduction")
    end = manuscript.index("## Data and code availability")
    return manuscript[start:end]


def test_ecology_letters_main_text_stays_within_method_limit():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert _word_count(_main_text(manuscript)) <= 5000


def test_unsolicited_method_pitch_is_at_most_300_words():
    pitch = PITCH.read_text(encoding="utf-8")
    body = pitch.split("\n\n", 1)[1]
    assert _word_count(body) <= 300


def test_manuscript_keeps_level_c_focal_claims_closed():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8").lower()
    forbidden = [
        "level c confirmed dependency",
        "level c falsified dependency",
        "level-c confirmed dependency",
        "level-c falsified dependency",
    ]
    for phrase in forbidden:
        assert phrase not in manuscript


def test_synthetic_receipt_explicitly_reads_no_focal_level_c_values():
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["focal_level_c_values_read"] is False
    assert summary["interpretation_boundary"].startswith(
        "Synthetic inferential benchmark only."
    )


def test_manuscript_has_no_more_than_six_planned_display_items():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    section = manuscript.split("## Proposed display items", 1)[1]
    items = re.findall(r"^\d+\. \*\*", section, flags=re.MULTILINE)
    assert len(items) <= 6
    assert len(items) == 6
