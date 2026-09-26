import importlib.util
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "manuscript" / "figures"
BUILDER = ROOT / "scripts" / "build_paper1_submission_figures_v1.py"
MANIFEST = ROOT / "manuscript" / "FULL_SUBMISSION_DISPLAY_MANIFEST_V0_3.md"
CAPTIONS = ROOT / "manuscript" / "FULL_SUBMISSION_FIGURE_CAPTIONS_V0_3.md"

FILES = {
    1: FIG / "figure1_relation_endpoint_contract_v1_0.svg",
    2: FIG / "figure2_level_a_empirical_anchor_v1_0.svg",
    3: FIG / "figure3_relation_layer_and_event_function_v1_0.svg",
    4: FIG / "figure4_parallel_openability_audits_v1_0.svg",
    5: FIG / "figure5_invalid_state_decomposition_v1_0.svg",
}

PHYSICAL_WIDTH_MM = 173.0
PHYSICAL_WIDTH_PT = PHYSICAL_WIDTH_MM / 25.4 * 72.0


def _load_builder():
    spec = importlib.util.spec_from_file_location("paper1_fig_v1", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _num(value):
    if value is None:
        return None
    m = re.match(r"^-?\d+(?:\.\d+)?", value)
    return float(m.group(0)) if m else None


class Paper1SubmissionFigureV1Tests(unittest.TestCase):
    def test_committed_v1_svgs_are_exact_builder_outputs(self):
        mod = _load_builder()
        for num, path in FILES.items():
            source = mod.SOURCES[num].read_text(encoding="utf-8")
            expected = mod.TRANSFORMS[num](source)
            self.assertEqual(path.read_text(encoding="utf-8"), expected, path.name)

    def test_all_v1_svgs_parse_and_geometry_stays_inside_canvas(self):
        for path in FILES.values():
            root = ET.fromstring(path.read_text(encoding="utf-8"))
            self.assertTrue(root.tag.endswith("svg"))
            width = _num(root.attrib.get("width"))
            height = _num(root.attrib.get("height"))
            self.assertTrue(width and height)
            for elem in root.iter():
                tag = elem.tag.rsplit("}", 1)[-1]
                if tag == "rect":
                    x = _num(elem.attrib.get("x")) or 0.0
                    y = _num(elem.attrib.get("y")) or 0.0
                    w = _num(elem.attrib.get("width")) or 0.0
                    h = _num(elem.attrib.get("height")) or 0.0
                    self.assertGreaterEqual(x, 0)
                    self.assertGreaterEqual(y, 0)
                    self.assertLessEqual(x + w, width + 1e-6, path.name)
                    self.assertLessEqual(y + h, height + 1e-6, path.name)
                elif tag == "text":
                    x = _num(elem.attrib.get("x"))
                    y = _num(elem.attrib.get("y"))
                    if x is not None:
                        self.assertTrue(0 <= x <= width, (path.name, x, width))
                    if y is not None:
                        self.assertTrue(0 <= y <= height, (path.name, y, height))

    def test_minimum_text_is_at_least_six_points_at_173mm(self):
        for path in FILES.values():
            text = path.read_text(encoding="utf-8")
            root = ET.fromstring(text)
            viewbox_width = float(root.attrib["viewBox"].split()[2])
            sizes = [float(x) for x in re.findall(r"font-size:([0-9.]+)px", text)]
            self.assertTrue(sizes, path.name)
            min_pt = min(sizes) * PHYSICAL_WIDTH_PT / viewbox_width
            self.assertGreaterEqual(min_pt, 6.0, (path.name, min_pt))
            self.assertAlmostEqual(min_pt, 6.13, places=2)

    def test_scientific_boundary_survives_v1_typography_edit(self):
        f1 = FILES[1].read_text(encoding="utf-8")
        f2 = FILES[2].read_text(encoding="utf-8")
        f3 = FILES[3].read_text(encoding="utf-8")
        f4 = FILES[4].read_text(encoding="utf-8")
        f5 = FILES[5].read_text(encoding="utf-8")

        for phrase in ["opening_rule_reference", "SHA-256 fingerprint", "unresolved"]:
            self.assertIn(phrase, f1)
        self.assertIn("0 / 12", f2)
        self.assertIn("not 283 independent successes", f2)
        self.assertIn("Fréchet–Hoeffding bounds", f3)
        self.assertIn("v=0.5", f3)
        self.assertIn("absence → unresolved", f3)
        self.assertIn("No focal biological outcome is opened.", f4)
        self.assertNotIn("confirmed dependency", f4.lower())
        self.assertNotIn("falsified dependency", f4.lower())
        self.assertIn("FPRzero − FPRgated = 1 − a₁", f5)
        self.assertIn("TPRzero − TPRgated = 1 − a₀", f5)

    def test_scientific_names_are_italicized_where_plotted(self):
        f2 = FILES[2].read_text(encoding="utf-8")
        f4 = FILES[4].read_text(encoding="utf-8")
        self.assertIn('font-style="italic"', f2)
        self.assertIn('<tspan font-style="italic">Cremastra appendiculata</tspan>', f4)
        self.assertIn('<tspan font-style="italic">Belonocnema treatae</tspan>', f4)

    def test_v03_manifest_has_exactly_six_items_and_routes_v1(self):
        text = MANIFEST.read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^\d+\. \*\*", text, flags=re.MULTILINE)), 6)
        for path in FILES.values():
            self.assertIn(path.name, text)
        self.assertIn("6.13 pt", text)
        self.assertIn("173 mm", text)
        self.assertIn("empirical ledger = 1", text)

    def test_v03_captions_preserve_level_a_and_level_c_boundaries(self):
        text = CAPTIONS.read_text(encoding="utf-8")
        self.assertIn("0 of 12 taxa contained an envelope exceedance", text)
        self.assertIn("no focal Level-C biological dependency outcome is opened", text)
        self.assertIn("empirical ledger remains **1**", text)


if __name__ == "__main__":
    unittest.main()
