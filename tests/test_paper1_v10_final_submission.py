import hashlib
import importlib.util
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_BUILDER = ROOT / "scripts" / "build_prefield_flagship_v0_10_candidate.py"
SOURCE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_9_CANDIDATE.md"
INTRO = ROOT / "manuscript" / "PAPER1_INTRODUCTION_V0_9_1_CANDIDATE.md"
METHODS = ROOT / "manuscript" / "PAPER1_METHODS_V0_10_CANDIDATE.md"
RESULTS = ROOT / "manuscript" / "PAPER1_RESULTS_V0_10_CANDIDATE.md"
REFS = ROOT / "manuscript" / "WORKING_REFERENCES_V0_9_1.md"
SUPP = ROOT / "manuscript" / "PAPER1_SUPPLEMENT_V0_1.md"
SURFACE = ROOT / "manuscript" / "PAPER1_V0_10_SUBMISSION_SURFACE.md"
TITLE = ROOT / "manuscript" / "ECOLOGY_LETTERS_TITLE_PAGE_V0_3.md"
COVER = ROOT / "manuscript" / "ECOLOGY_LETTERS_FULL_COVER_LETTER_V0_2.md"
COMMITTED = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_10_CANDIDATE.md"
SHA_FILE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_10_CANDIDATE.sha256"
IDENTITY = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_10_IDENTITY.txt"
SUBMISSION_IDENTITY = ROOT / "manuscript" / "PAPER1_SUBMISSION_IDENTITY_V0_1.md"
READINESS = ROOT / "manuscript" / "PAPER1_FULL_SUBMISSION_READINESS_V0_1.md"
EXPECTED_SHA256 = "66ad208f2a922800cb7f1d14f96b28295de13af4cdbdbec2f8b698b8fa320cc5"
FIG_DIR = ROOT / "manuscript" / "figures"
FIGURES = [
    FIG_DIR / "figure1_relation_endpoint_contract_v0_2.svg",
    FIG_DIR / "figure2_level_a_empirical_anchor_v0_2.svg",
    FIG_DIR / "figure3_relation_layer_and_event_function_v0_2.svg",
    FIG_DIR / "figure4_parallel_openability_audits_v0_1.svg",
    FIG_DIR / "figure5_invalid_state_decomposition_v0_3.svg",
]


def _load_builder():
    spec = importlib.util.spec_from_file_location("v010", MANUSCRIPT_BUILDER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _build():
    mod = _load_builder()
    return mod.build_candidate(
        SOURCE.read_text(encoding="utf-8"),
        INTRO.read_text(encoding="utf-8"),
        METHODS.read_text(encoding="utf-8"),
        RESULTS.read_text(encoding="utf-8"),
        REFS.read_text(encoding="utf-8"),
    )


def _word_count(text):
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def _num(value):
    if value is None:
        return None
    m = re.match(r"^-?\d+(?:\.\d+)?", value)
    return float(m.group(0)) if m else None


def test_submission_surface_routes_v010_and_frozen_claim_boundary():
    text = SURFACE.read_text(encoding="utf-8")
    for phrase in [
        "PREFIELD_FLAGSHIP_V0_10_CANDIDATE.md",
        "PAPER1_SUPPLEMENT_V0_1.md",
        "FULL_SUBMISSION_DISPLAY_MANIFEST_V0_2.md",
        "CLAIM_EVIDENCE_LEDGER_V0_5.md",
        "0/12 taxa with an envelope exceedance",
        "FPR_zero-FPR_gated=1-a1",
        "TPR_zero-TPR_gated=1-a0",
        "Empirical ledger: **1**",
    ]:
        assert phrase in text


def test_exact_v010_build_respects_limits_and_core_claims():
    text = _build()
    abstract = text.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]
    main = text.split("## 1. Introduction", 1)[1].split("## Data and code availability", 1)[0]
    assert _word_count(abstract) <= 150
    assert _word_count(main) <= 5000
    for phrase in [
        "0 of 12 contained an empirical-envelope exceedance",
        "FPR_zero - FPR_gated = 1-a1",
        "TPR_zero - TPR_gated = 1-a0",
        "CREMV3-007",
        "BELV3-012",
        "measurement-boundary results, not biological negatives",
    ]:
        assert phrase in text
    lower = text.lower()
    for forbidden in [
        "level c confirmed dependency",
        "level c falsified dependency",
        "level-c confirmed dependency",
        "level-c falsified dependency",
    ]:
        assert forbidden not in lower


def test_committed_v010_is_exact_builder_output_and_identity_is_frozen():
    built = _build()
    committed = COMMITTED.read_text(encoding="utf-8")
    assert committed == built
    digest = hashlib.sha256(COMMITTED.read_bytes()).hexdigest()
    assert digest == EXPECTED_SHA256
    assert SHA_FILE.read_text(encoding="utf-8").split()[0] == EXPECTED_SHA256

    abstract = committed.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]
    main = committed.split("## 1. Introduction", 1)[1].split("## Data and code availability", 1)[0]
    refs = committed.split("## Working references", 1)[1].split("## Proposed display items", 1)[0]
    displays = committed.split("## Proposed display items", 1)[1]
    assert _word_count(abstract) == 146
    assert _word_count(main) == 3408
    assert sum(1 for line in refs.splitlines() if line.startswith("- ")) == 16
    assert len(re.findall(r"^\d+\. \*\*", displays, flags=re.MULTILINE)) == 6

    identity = IDENTITY.read_text(encoding="utf-8")
    assert "abstract_words=146" in identity
    assert "main_words=3408" in identity
    assert "reference_entries=16" in identity
    assert "display_items=6" in identity

    receipt = SUBMISSION_IDENTITY.read_text(encoding="utf-8")
    assert EXPECTED_SHA256 in receipt
    assert "abstract words: **146**" in receipt
    assert "main-text words: **3,408**" in receipt
    assert "working reference entries: **16**" in receipt
    assert "display items: **6**" in receipt


def test_title_page_and_cover_letter_are_v010_aligned_but_human_metadata_remain_blocked():
    title = TITLE.read_text(encoding="utf-8")
    cover = COVER.read_text(encoding="utf-8")
    promoted = "Relation endpoints for ecological inference: when independent answers can support joint biological claims"
    assert promoted in title and promoted in cover
    assert EXPECTED_SHA256 in title
    assert "**Abstract word count:** 146." in title
    assert "**Main-text word count:** 3,408." in title
    assert "16 audited references" in title
    assert "editor invitation/approved Method proposal details" in title
    assert "Do not send until" in cover
    assert "0 of 12 taxa" in cover
    assert "No focal Level-C biological dependency outcome is opened" in cover
    assert "[Insert verified statement" in cover
    assert "[Insert the Ecology Letters Method invitation" in cover


def test_readiness_marks_science_green_but_send_remains_blocked():
    text = READINESS.read_text(encoding="utf-8")
    assert EXPECTED_SHA256 in text
    assert "Abstract word count fixed at **146**" in text
    assert "Main-text word count fixed at **3,408**" in text
    assert "Working reference entries fixed at **16**" in text
    assert "Display items fixed at **6**" in text
    assert "Do **not** send the full manuscript while any RED item remains unresolved" in text
    assert "Ecology Letters has invited/approved the full Method submission" in text
    assert "Final author list and order confirmed by all authors" in text


def test_all_submission_figures_parse_and_geometry_stays_inside_canvas():
    for path in FIGURES:
        assert path.exists(), path
        root = ET.fromstring(path.read_text(encoding="utf-8"))
        assert root.tag.endswith("svg")
        width = _num(root.attrib.get("width"))
        height = _num(root.attrib.get("height"))
        assert width and height
        for elem in root.iter():
            tag = elem.tag.rsplit("}", 1)[-1]
            if tag == "rect":
                x = _num(elem.attrib.get("x")) or 0.0
                y = _num(elem.attrib.get("y")) or 0.0
                w = _num(elem.attrib.get("width")) or 0.0
                h = _num(elem.attrib.get("height")) or 0.0
                assert x >= 0 and y >= 0
                assert x + w <= width + 1e-6, (path.name, x, w, width)
                assert y + h <= height + 1e-6, (path.name, y, h, height)
            elif tag == "text":
                x = _num(elem.attrib.get("x"))
                y = _num(elem.attrib.get("y"))
                if x is not None:
                    assert 0 <= x <= width, (path.name, x, width)
                if y is not None:
                    assert 0 <= y <= height, (path.name, y, height)


def test_figure_specific_submission_messages_are_preserved():
    fig1, fig2, fig3, fig4, fig5 = [p.read_text(encoding="utf-8") for p in FIGURES]
    assert "opening_rule_reference" in fig1
    assert "SHA-256 fingerprint" in fig1
    assert "remains unresolved" in fig1
    assert "not 283 independent successes" in fig2
    assert "0 / 12" in fig2 or "0 of 12" in fig2
    assert "Fréchet–Hoeffding bounds" in fig3
    assert "v=0.5" in fig3 and "aggregate function" in fig3
    assert "No focal biological outcome is opened." in fig4
    assert "confirmed dependency" not in fig4.lower()
    assert "falsified dependency" not in fig4.lower()
    assert "FPRzero − FPRgated = 1 − a₁" in fig5
    assert "TPRzero − TPRgated = 1 − a₀" in fig5
    assert "ablation of the unresolved-state guard" in fig5


def test_supplement_preserves_detail_removed_from_main():
    supp = SUPP.read_text(encoding="utf-8")
    for detail in ["4,320", "4,428", "0.776", "28/30", "60/60", "Clopper–Pearson"]:
        assert detail in supp
