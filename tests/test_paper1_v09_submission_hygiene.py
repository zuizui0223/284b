from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIB_AUDIT = ROOT / "manuscript" / "BIBLIOGRAPHY_AUDIT_V0_1.md"
INTRO = ROOT / "manuscript" / "PAPER1_INTRODUCTION_V0_9_1_CANDIDATE.md"
REFS = ROOT / "manuscript" / "WORKING_REFERENCES_V0_9_1.md"
SUPP = ROOT / "manuscript" / "SUPPLEMENT_ROUTING_V0_1.md"


def test_bibliography_audit_contains_direct_and_complementary_antecedents():
    text = BIB_AUDIT.read_text(encoding="utf-8")
    required = [
        "10.1111/ele.13525",
        "10.1111/2041-210X.13518",
        "10.1038/s41559-023-02254-y",
        "10.1111/2041-210X.70311",
        "10.1016/j.tree.2023.10.009",
        "10.1007/0-387-28678-0",
    ]
    for doi in required:
        assert doi in text
    assert "more direct support for the semantic distinction" in text
    assert "Retain as complementary, not primary caution citation" in text
    assert "empirical ledger increment = 0" in text


def test_intro_concedes_joint_modelling_and_uses_both_sides_of_cooccurrence_literature():
    text = INTRO.read_text(encoding="utf-8")
    assert "Wilkinson et al. 2021" in text
    assert "Blanchet et al. 2020" in text
    assert "Galiana et al. 2024" in text
    assert "Gould et al. 2026" in text
    assert "co-occurrence or residual association is not by itself evidence of a biological interaction" in text
    assert "co-occurrence can contain information about interaction-network structure under explicit assumptions" in text
    assert "which biological relation that information is licensed to represent" in text
    assert "Classical Frechet-Hoeffding coupling bounds" in text
    assert "established probability theory" in text
    assert "We do not claim novelty for any of these ingredients" in text


def test_working_references_include_audited_metadata_and_full_gould_entry():
    text = REFS.read_text(encoding="utf-8")
    for ref in [
        "Blanchet FG, Cazelles K, Gravel D. 2020",
        "Wilkinson DP, Golding N, Guillera-Arroita G, Tingley R, McCarthy MA. 2021",
        "Pacifici K, Reich BJ, Miller DAW",
        "Nelsen RB. 2006",
        "Chadwick FJ, Haydon DT, Husmeier D, Ovaskainen O, Matthiopoulos J. 2024",
        "Gould E, Jones CS, Yen JDL, Fraser HS, Wootton HF, Good MK, Duncan DH, Hauser CE, Wintle BC, Rumpff L. 2026",
    ]:
        assert ref in text
    assert "*Methods in Ecology and Evolution* 17(6):1768–1787" in text
    assert "doi:10.1111/2041-210X.70311" in text


def test_supplement_routing_keeps_only_five_claim_spine_in_main():
    text = SUPP.read_text(encoding="utf-8")
    assert "accurate answers do not determine the biological relation" in text
    assert "Level A closes on 12 fresh held-out taxa" in text
    assert "preserving `unresolved` prevents exact class-specific error inflation" in text
    assert "two real systems prospectively stop at the same negative-state measurement boundary" in text
    assert "0/12 taxa with an envelope exceedance" in text
    assert "FPR_zero-FPR_gated=1-a1" in text
    assert "TPR_zero-TPR_gated=1-a0" in text


def test_supplement_routing_moves_provenance_and_bulk_diagnostics_out_of_main():
    text = SUPP.read_text(encoding="utf-8")
    for phrase in [
        "complete 8,748-scenario equal-validity grid",
        "v8 → v8.1 prospective implementation repair",
        "28/30 known-positive success threshold",
        "60/60 known-negative specificity threshold",
        "full candidate-screening ledger",
        "supplementary/raw-source reconstruction attempts",
        "Level B relation-specific soft calibration examples",
    ]:
        assert phrase in text
    assert "Levels B/D/E should not read as missing empirical results in Paper 1" in text
