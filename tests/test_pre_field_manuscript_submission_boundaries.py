import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_3.md"
PITCH = ROOT / "manuscript" / "ECOLOGY_LETTERS_300WORD_PITCH_V0_2.md"
SUMMARY = ROOT / "results" / "pre_field_identifiability_benchmark_summary_v0_1.json"
V81 = ROOT / "results" / "product_b_level_c_operational_package_v8_1.json"


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


def test_manuscript_explicitly_positions_against_prior_imperfect_detection_work():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert "We do not introduce another occupancy model" in manuscript
    assert "MacKenzie et al. (2004)" in manuscript
    assert "Rota et al. 2016" in manuscript
    assert "Weinstein & Graham 2017" in manuscript


def test_synthetic_receipt_explicitly_reads_no_focal_level_c_values():
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert summary["focal_level_c_values_read"] is False
    assert summary["interpretation_boundary"].startswith(
        "Synthetic inferential benchmark only."
    )


def test_v81_repair_is_pre_data_and_nonempirical():
    receipt = json.loads(V81.read_text(encoding="utf-8"))
    assert receipt["field_calibration_data_seen_before_repair"] is False
    assert receipt["scientific_thresholds_changed"] is False
    assert receipt["minimum_sample_counts_changed"] is False
    assert receipt["empirical_ledger_increment"] == 0
    assert receipt["global_284b_empirical_ledger_after_v8_1"] == 1


def test_manuscript_has_exactly_six_planned_display_items():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    section = manuscript.split("## Proposed display items", 1)[1]
    items = re.findall(r"^\d+\. \*\*", section, flags=re.MULTILINE)
    assert len(items) == 6
