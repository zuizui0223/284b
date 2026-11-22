"""Review ZIP packaging is reproducible, content-addressed and never a submission."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts/build_el_invited_review_bundle_v1.py"
spec = importlib.util.spec_from_file_location("invited_review_bundle", MODULE)
bundle = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = bundle
spec.loader.exec_module(bundle)


class ReviewBundleGateTests(unittest.TestCase):
    def test_signed_hold_reconciles_original_and_restored(self):
        state=bundle.verify_scientific_gate(ROOT)
        self.assertEqual(state["submission_status"],"HOLD_FOR_SENSITIVITY_REVIEW")
        self.assertEqual(state["independent_biological_endpoints"],1)
        self.assertEqual(state["repair_new_independent_endpoints"],0)
        self.assertEqual(state["original_evaluable"],283)
        self.assertEqual(state["repaired_evaluable"],285)
        self.assertEqual(state["original_evaluable_retained"],282)
        self.assertFalse(state["strict_original_coverage_robust"])

    def test_synthetic_figure_files_package_without_publishing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            figures=root/"figures"
            figures.mkdir()
            for number,stem in enumerate(bundle.FIGURES,1):
                for fmt in bundle.FORMATS:
                    (figures/f"{stem}.{fmt}").write_bytes((f"Synthetic local placeholder {number}.{fmt} | "*8).encode())
            (figures/"FIGURE_README.md").write_text("Synthetic local placeholders are not submission artwork.\n")
            payload=bundle.collect_payloads(ROOT,figures)
            self.assertEqual(len([x for x in payload if x.startswith("figures/") and x.endswith((".pdf",".png",".svg"))]),12)
            self.assertIn("BUNDLE_MANIFEST.json",payload)
            self.assertIn("REVIEW_ONLY.txt",payload)
            index=json.loads(payload["BUNDLE_MANIFEST.json"])
            self.assertEqual(index["submission_status"],"HOLD_FOR_SENSITIVITY_REVIEW")
            self.assertEqual(index["strict_original_coverage_robust"],False)
            self.assertEqual(index["figure_files"],12)
            self.assertEqual(index["complete_si_sections"],11)
            self.assertEqual(index["repair_new_independent_endpoints"],0)
            self.assertIn("NOT A JOURNAL SUBMISSION",payload["REVIEW_ONLY.txt"].decode())
            a=root/"one.zip"
            b=root/"two.zip"
            self.assertEqual(bundle.write_bundle(a,payload),bundle.write_bundle(b,payload))
            with zipfile.ZipFile(a) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(set(z.namelist()),set(payload))
                self.assertTrue(all(".." not in Path(i).parts for i in z.namelist()))

    def test_missing_or_empty_figure_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            figures=Path(d)
            for stem in bundle.FIGURES:
                for fmt in bundle.FORMATS:
                    (figures/f"{stem}.{fmt}").write_bytes(b"a"*110)
            (figures/"FIGURE_README.md").write_text("test")
            (figures/"figure3_invalidity.svg").unlink()
            with self.assertRaisesRegex(RuntimeError,"Missing or empty rendered figure"):
                bundle.collect_payloads(ROOT,figures)

if __name__=="__main__":
    unittest.main()
