import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_paper1_ecology_letters_submission_v1.py"
SOURCE = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_10_CANDIDATE.md"
INTRO = ROOT / "manuscript" / "PAPER1_INTRODUCTION_V0_9_2_CANDIDATE.md"
REFS = ROOT / "manuscript" / "ECOLOGY_LETTERS_REFERENCES_V1.md"


def _load_builder():
    spec = importlib.util.spec_from_file_location("paper1_el_v1", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _build():
    mod = _load_builder()
    return mod.build_submission(
        SOURCE.read_text(encoding="utf-8"),
        INTRO.read_text(encoding="utf-8"),
        REFS.read_text(encoding="utf-8"),
    )


def _word_count(text):
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


class EcologyLettersSubmissionV1Tests(unittest.TestCase):
    def test_only_introduction_reference_style_and_status_change(self):
        source = SOURCE.read_text(encoding="utf-8")
        built = _build()
        source_abstract = source.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]
        built_abstract = built.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]
        self.assertEqual(built_abstract, source_abstract)

        source_science = source.split("## 2. Methods", 1)[1].split("## Working references", 1)[0]
        built_science = built.split("## 2. Methods", 1)[1].split("## References", 1)[0]
        self.assertEqual(built_science, source_science)

    def test_submission_size_and_empirical_boundaries_remain_valid(self):
        built = _build()
        abstract = built.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]
        main = built.split("## 1. Introduction", 1)[1].split("## Data and code availability", 1)[0]
        self.assertEqual(_word_count(abstract), 146)
        self.assertLessEqual(_word_count(main), 5000)
        for phrase in [
            "0 of 12 contained an empirical-envelope exceedance",
            "FPR_zero - FPR_gated = 1-a1",
            "TPR_zero - TPR_gated = 1-a0",
            "CREMV3-007",
            "BELV3-012",
            "measurement-boundary results, not biological negatives",
            "**Empirical ledger:** 1.",
        ]:
            self.assertIn(phrase, built)
        lower = built.lower()
        self.assertNotIn("level-c confirmed dependency", lower)
        self.assertNotIn("level-c falsified dependency", lower)

    def test_all_sixteen_styled_references_are_cited(self):
        built = _build()
        intro = built.split("## 1. Introduction", 1)[1].split("## 2. Methods", 1)[0]
        citations = [
            "Blanchet et al. 2020",
            "Chadwick et al. 2024",
            "Erickson & Smith 2021",
            "Gaier & Resasco 2023",
            "Galiana et al. 2024",
            "Getz et al. 2018",
            "Gould et al. 2026",
            "Guillera-Arroita 2017",
            "Guillera-Arroita et al. 2017",
            "MacKenzie et al. 2004",
            "Matutini et al. 2021",
            "Nelsen 2006",
            "Pacifici et al. 2017",
            "Rota et al. 2016",
            "Weinstein & Graham 2017",
            "Wilkinson et al. 2021",
        ]
        for citation in citations:
            self.assertIn(citation, intro, citation)

        ref_block = built.split("## References", 1)[1].split("## Proposed display items", 1)[0]
        entries = re.findall(r"^[A-ZÀ-Ž][^\n]*\(\d{4}\)\.", ref_block, flags=re.MULTILINE)
        self.assertEqual(len(entries), 16)
        self.assertNotIn("doi:", ref_block.lower())
        self.assertFalse(any(line.startswith("- ") for line in ref_block.splitlines()))

    def test_parenthetical_citation_clusters_follow_alphabetical_order(self):
        intro = _build().split("## 1. Introduction", 1)[1].split("## 2. Methods", 1)[0]
        expected = [
            "(Guillera-Arroita 2017; Guillera-Arroita et al. 2017; MacKenzie et al. 2004)",
            "(Rota et al. 2016; Wilkinson et al. 2021)",
            "(Erickson & Smith 2021; Gaier & Resasco 2023; Matutini et al. 2021)",
            "(Chadwick et al. 2024; Getz et al. 2018; Weinstein & Graham 2017)",
        ]
        for cluster in expected:
            self.assertIn(cluster, intro)
        self.assertNotIn("(MacKenzie et al. 2004; Guillera-Arroita 2017)", intro)
        self.assertNotIn("(Weinstein & Graham 2017; Getz et al. 2018; Chadwick et al. 2024)", intro)

    def test_reference_style_uses_six_author_cutoff_and_standard_abbreviations(self):
        refs = REFS.read_text(encoding="utf-8")
        for phrase in [
            "Getz, W.M., Marshall, C.R., Carlson, C.J., Giuggioli, L., Ryan, S.J., Romañach, S.S. et al. (2018)",
            "Gould, E., Jones, C.S., Yen, J.D.L., Fraser, H.S., Wootton, H.F., Good, M.K. et al. (2026)",
            "Pacifici, K., Reich, B.J., Miller, D.A.W., Gardner, B., Stauffer, G.E., Singh, S. et al. (2017)",
            "Rota, C.T., Ferreira, M.A.R., Kays, R.W., Forrester, T.D., Kalies, E.L., McShea, W.J. et al. (2016)",
            "Ecol. Lett.",
            "Methods Ecol. Evol.",
            "J. Anim. Ecol.",
            "Nat. Ecol. Evol.",
        ]:
            self.assertIn(phrase, refs)


if __name__ == "__main__":
    unittest.main()
