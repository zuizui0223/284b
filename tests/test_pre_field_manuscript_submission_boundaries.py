import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_4.md"
PITCH = ROOT / "manuscript" / "ECOLOGY_LETTERS_300WORD_PITCH_V0_5.md"
PROPOSAL = ROOT / "manuscript" / "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_5.md"
PROPOSAL_FIGURE = ROOT / "manuscript" / "figures" / "ecology_letters_method_proposal_figure_v0_2.svg"
ANTECEDENT_AUDIT = ROOT / "manuscript" / "CLOSER_ANTECEDENT_AUDIT_V0_2.md"
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


def test_unsolicited_method_pitch_is_at_most_300_words_and_has_qualification():
    pitch = PITCH.read_text(encoding="utf-8")
    body = pitch.split("\n\n", 1)[1]
    assert _word_count(body) <= 300
    assert "The lead author works across" in body


def test_canonical_proposal_and_attachment_exist():
    assert PROPOSAL.exists()
    assert PROPOSAL_FIGURE.exists()
    assert ANTECEDENT_AUDIT.exists()
    proposal = PROPOSAL.read_text(encoding="utf-8")
    figure = PROPOSAL_FIGURE.read_text(encoding="utf-8")
    assert "prospective relation endpoint" in proposal.lower()
    assert "relation-endpoint" in proposal.lower()
    assert "Chadwick et al. (2024)" in proposal
    assert "Latency, Identifiability, Effort and Scale" in proposal
    assert "1-a" in proposal
    assert "30% missingness" in figure
    assert "3 accessible areas" in figure


def test_lies_audit_explicitly_concedes_observation_process_identifiability():
    audit = ANTECEDENT_AUDIT.read_text(encoding="utf-8")
    assert "LIES of omission" in audit
    assert "observation-process identifiability is not the novelty claim" in audit
    assert "relation endpoint between independently generated ecological answers" in audit


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


def test_manuscript_explicitly_positions_against_prior_work():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert "Imperfect detection is not a new problem" in manuscript
    assert "Getz et al. (2018)" in manuscript
    assert "MacKenzie et al. 2004" in manuscript
    assert "Rota et al. 2016" in manuscript
    assert "Weinstein & Graham 2017" in manuscript
    assert "prospectivity itself is not the novelty claim" in manuscript


def test_manuscript_uses_unambiguous_benchmark_notation():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert "Let `a` be the probability that an event key is valid" in manuscript
    assert "true violation prevalence `π`" in manuscript
    assert "`FPR_zero - FPR_gated = 1-a`" in manuscript
    assert "Let `v` be the probability that an event key is valid" not in manuscript


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
