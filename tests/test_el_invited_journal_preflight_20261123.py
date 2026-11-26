"""Provisional Method source-text preflight; not publisher proof."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MS=ROOT/"manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md"
SI=ROOT/"manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COMPLETE_SI_V1.md"
TITLE=ROOT/"manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_TITLE_PAGE_V1.md"
PREFLIGHT=ROOT/"docs/EL_METHOD_JOURNAL_PREFLIGHT_20261123.md"
MANIFEST=ROOT/"manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_MANIFEST_V1.json"

def count_source_words(t):
    t=re.sub(r"\x60([^\x60]+)\x60",r"\1",t)
    t=t.replace("**","").replace("*","").replace("#","").replace("|","")
    return len(t.split())

class MethodPreflightTests(unittest.TestCase):
    def test_counts_recomputed_on_current_main_and_si(self):
        main=MS.read_text(encoding="utf-8")
        si=SI.read_text(encoding="utf-8")
        title=TITLE.read_text(encoding="utf-8")
        m=json.loads(MANIFEST.read_text(encoding="utf-8"))
        p=m["journal_source_preflight_20261123"]
        abstract=main.split("## Abstract\n\n",1)[1].split("\n\n## 1.",1)[0]
        body="## 1."+main.split("## 1.",1)[1].split("## References",1)[0]
        n_abstract=count_source_words(abstract)
        n_body=count_source_words(body)
        refs=[r for r in main.split("## References",1)[1].strip().split("\n\n") if r.strip()]
        self.assertEqual(n_abstract,p["source_abstract_words"])
        self.assertEqual(n_body,p["source_main_text_words_approx"])
        self.assertLessEqual(n_abstract,p["abstract_limit"])
        self.assertLessEqual(n_body,p["method_main_word_limit"])
        self.assertEqual(len(refs),p["reference_entries"])
        self.assertIn("**Provisional abstract word count:** 135",title)
        self.assertIn("**Provisional main-text word count (sections 1–7):** 2,392",title)
        self.assertEqual(len(re.findall(r"^## S\d+\.",si,flags=re.M)),p["complete_SI_sections"])
        for i in (1,2,3,4):
            self.assertIn(f"Fig. {i}",main)
        self.assertEqual(p["main_figures"],4)
        self.assertEqual(p["complete_SI_tables"],2)
        self.assertEqual(p["main_figures"]+p["main_tables"]+p["main_boxes"],4)
        self.assertLessEqual(p["main_figures"]+p["main_tables"]+p["main_boxes"],p["main_display_limit"])

    def test_journal_limit_claims_and_human_requirements_not_marked_ready(self):
        title=TITLE.read_text(encoding="utf-8")
        txt=PREFLIGHT.read_text(encoding="utf-8")
        m=json.loads(MANIFEST.read_text(encoding="utf-8"))
        p=m["journal_source_preflight_20261123"]
        running=re.search(r"^\*\*Running title:\*\* (.+)$",title,flags=re.M).group(1)
        keywords=re.search(r"^\*\*Keywords:\*\* (.+)$",title,flags=re.M).group(1).split(";")
        self.assertEqual(len(running),29)
        self.assertLess(len(running),p["running_title_limit_exclusive"])
        self.assertEqual(len(keywords),p["keywords"])
        self.assertLessEqual(len(keywords),10)
        self.assertEqual(m["status"],"HOLD_FOR_SENSITIVITY_REVIEW")
        self.assertFalse(p["publisher_format_approved"])
        self.assertFalse(p["doi_present"])
        self.assertFalse(p["author_approval_received"])
        self.assertFalse(p["corrected_source_coverage_strictly_robust"])
        self.assertIn("source-text limits",txt)
        self.assertIn("published as supplied",txt)
        self.assertIn("ForAuthors.html",txt)
        self.assertIn("[INSERT FINAL AUTHOR LIST AND ORDER]",title)

if __name__=="__main__":
    unittest.main()
