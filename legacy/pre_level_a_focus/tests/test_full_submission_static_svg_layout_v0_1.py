import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "manuscript" / "figures"
FIGURES = [
    FIG_DIR / "figure1_relation_endpoint_contract_v0_1.svg",
    FIG_DIR / "figure2_level_a_empirical_anchor_v0_2.svg",
    FIG_DIR / "figure3_event_function_dependency_v0_1.svg",
    FIG_DIR / "figure4_parallel_openability_audits_v0_1.svg",
    FIG_DIR / "figure5_invalid_state_decomposition_v0_3.svg",
]


def _num(value: str | None) -> float | None:
    if value is None:
        return None
    m = re.match(r"^-?\d+(?:\.\d+)?", value)
    return float(m.group(0)) if m else None


def test_all_five_canonical_svg_figures_exist_and_parse():
    for path in FIGURES:
        assert path.exists(), path
        root = ET.fromstring(path.read_text(encoding="utf-8"))
        assert root.tag.endswith("svg")


def test_svg_rectangles_and_text_anchors_stay_inside_canvas():
    for path in FIGURES:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
        width = _num(root.attrib["width"])
        height = _num(root.attrib["height"])
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


def test_figure2_layout_repair_keeps_margin_diagnostics_on_canvas():
    svg = (FIG_DIR / "figure2_level_a_empirical_anchor_v0_2.svg").read_text(encoding="utf-8")
    assert 'height="970" viewBox="0 0 1200 970"' in svg
    assert 'y="927"' in svg
    assert "not 283 independent successes" in svg


def test_figure3_long_surface_warning_is_split_across_lines():
    svg = (FIG_DIR / "figure3_event_function_dependency_v0_1.svg").read_text(encoding="utf-8")
    assert "Adult plant occupancy need not be contained in current pollinator occupancy." in svg
    assert "That mismatch alone is not a hard biological contradiction." in svg
    assert "Adult plant occupancy ⊄ current pollinator occupancy is not a hard contradiction." not in svg


def test_figure4_stop_messages_are_multiline_and_preoutcome():
    svg = (FIG_DIR / "figure4_parallel_openability_audits_v0_1.svg").read_text(encoding="utf-8")
    assert "STOP: functional absence" in svg
    assert "is not calibrated" in svg
    assert "STOP: usable-resource absence" in svg
    assert "No focal biological outcome is opened." in svg
    assert "STOP: functional absence uncalibrated" not in svg


def test_figure5_layout_and_generalized_claims_are_frozen():
    svg = (FIG_DIR / "figure5_invalid_state_decomposition_v0_3.svg").read_text(encoding="utf-8")
    assert 'x="315" y="371"' in svg
    assert "FPRzero − FPRgated = 1 − a₁" in svg
    assert "TPRzero − TPRgated = 1 − a₀" in svg
    assert "Equal-validity corollary" in svg
    assert "ablation of the unresolved-state guard" in svg
