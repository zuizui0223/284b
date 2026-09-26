import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "manuscript" / "CLOSER_ANTECEDENT_AUDIT_V0_3.md"
GA_MD = ROOT / "manuscript" / "ECOLOGY_LETTERS_GRAPHICAL_ABSTRACT_V0_2.md"
GA_SVG = ROOT / "manuscript" / "figures" / "ecology_letters_graphical_abstract_v0_2.svg"


def test_2026_antecedent_audit_concedes_adjacent_literatures():
    text = AUDIT.read_text(encoding="utf-8")
    assert "Chadwick et al. (2024)" in text
    assert "Pacifici et al. (2017)" in text
    assert "Gelfand & Schliep (2026)" in text
    assert "Non-detection by citizen scientists" in text
    assert "eLTER Framework of Standard Observations" in text
    assert "A short guide for effective field data collection" in text
    assert "No searched antecedent was found" in text
    assert "No automatic manuscript rewrite is authorized" in text
    assert "Empirical ledger increment: **0**" in text


def test_antecedent_audit_preserves_upstream_downstream_distinction():
    text = AUDIT.read_text(encoding="utf-8")
    assert "data fusion combines multiple sources" in text
    assert "common latent process/quantity" in text
    assert "what biological relation may the resulting answers jointly test" in text
    assert "Observation-process identifiability is not a novelty claim" in text
    assert "relation-endpoint contract" in text


def test_graphical_abstract_canvas_and_scientific_boundary():
    svg = GA_SVG.read_text(encoding="utf-8")
    assert 'width="50mm" height="60mm"' in svg
    assert 'viewBox="0 0 500 600"' in svg
    assert "relation-endpoint contract" in svg
    assert "12 held-out taxa" in svg
    assert "0 / 12 with envelope" in svg
    assert "invalid / missing ≠ absent" in svg
    assert "→ unresolved" in svg
    assert "new measurement is required" in svg
    assert "283" not in svg
    assert "Cremastra" not in svg
    assert "Belonocnema" not in svg
    assert "confirmed dependency" not in svg.lower()
    assert "falsified dependency" not in svg.lower()


def test_graphical_abstract_short_text_is_within_500_characters():
    text = GA_MD.read_text(encoding="utf-8")
    body = text.split("## Short graphical-abstract text — 431 characters including spaces", 1)[1]
    body = body.split("## Scientific boundary", 1)[0].strip()
    assert len(body) == 431
    assert len(body) <= 500
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", body) if s]
    assert len(sentences) == 3


def test_graphical_abstract_package_is_revision_stage_not_proposal_blocker():
    text = GA_MD.read_text(encoding="utf-8")
    assert "post-invite / revision-stage asset" in text
    assert "not required for the unsolicited Method proposal" in text
    assert "Empirical ledger remains 1" in text
    assert "Do not show a Cremastra or Belonocnema focal biological outcome" in text
