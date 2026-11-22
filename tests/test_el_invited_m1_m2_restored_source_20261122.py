"""Invited M1+M2 manuscript cannot silently upgrade restored-GBIF Level A source sensitivity.

This gate verifies manuscript, claim ledger, cover letter, Figure 2, readiness
and submission manifest against the original signed 283/288 Level A result
and the independently audited repaired-source one-shot terminal receipt.
It does not alter data, open models, refit q95, or recount empirical evidence.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md"
LEDGER = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_CLAIM_LEDGER_V1.md"
FIGURE = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_PLAN_V1.md"
COVER = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COVER_LETTER_V1.md"
READINESS = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_READINESS_V1.md"
MANIFEST = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_MANIFEST_V1.json"
HISTORICAL = ROOT / "results/product_b_same_target_core19_v0_4_heldout_final_receipt.json"
RESTORED = ROOT / "results/gbif_repaired_heldout12_sensitivity_v1.json"
REFERENCE = ROOT / "results/gbif_repaired_reference47_q95_summary_v1.json"
CV_AUDIT = ROOT / "results/gbif_repaired_heldout12_postterminal_cv_switch_v1.json"


class InvitedManuscriptRestoredSourceGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manuscript=MANUSCRIPT.read_text(encoding="utf-8")
        cls.ledger=LEDGER.read_text(encoding="utf-8")
        cls.figure=FIGURE.read_text(encoding="utf-8")
        cls.cover=COVER.read_text(encoding="utf-8")
        cls.readiness=READINESS.read_text(encoding="utf-8")
        cls.manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.historical=json.loads(HISTORICAL.read_text(encoding="utf-8"))
        cls.restored=json.loads(RESTORED.read_text(encoding="utf-8"))
        cls.reference=json.loads(REFERENCE.read_text(encoding="utf-8"))
        cls.cv=json.loads(CV_AUDIT.read_text(encoding="utf-8"))

    def test_primary_original_heldout_endpoint_is_not_replaced(self):
        old=self.historical
        core=self.manifest["scientific_core"]
        self.assertEqual(old["heldout"]["taxa"],core["level_a_independent_taxa"])
        self.assertEqual(old["heldout"]["cells_expected"],core["diagnostics_prespecified"])
        self.assertEqual(old["heldout"]["paired_prediction_surfaces_opened_cells"],
                         core["diagnostics_evaluable"])
        self.assertEqual(old["heldout"]["paired_crosscheck_attention_required"],
                         core["taxa_with_envelope_exceedance"])
        self.assertEqual(core["diagnostics_evaluable"],283)
        self.assertEqual(core["diagnostics_unresolved"],5)
        self.assertEqual(core["historical_endpoint_fingerprint"],old["final_endpoint_fingerprint"])
        self.assertIn("283 of 288",self.manuscript)
        self.assertIn("five remained unresolved",self.manuscript)
        self.assertIn("0 of 12 taxa with an exceedance",self.manuscript)

    def test_repaired_source_no_exceedance_but_original_cell_loss_is_explicit(self):
        x=self.restored
        p=self.manifest["postfreeze_repaired_GBIF_source_sensitivity"]
        self.assertEqual(p["classification"],x["status"])
        self.assertEqual(p["repaired_sensitivity_endpoint_fingerprint"],x["final_endpoint_fingerprint"])
        self.assertEqual(x["paired_prediction_surfaces_opened_cells"],285)
        self.assertEqual(x["paired_crosscheck_attention_required"],0)
        self.assertEqual(x["historical_original_opened_cells_retained"],282)
        self.assertEqual(x["historical_original_opened_cells_lost"],1)
        self.assertEqual(x["newly_evaluable_repaired_cells"],3)
        self.assertFalse(x["source_completeness_0_of_12_robust"])
        self.assertFalse(p["strict_full_historical_283_cell_retention_robust"])
        self.assertFalse(x["counts_as_empirical_conclusion"])
        self.assertFalse(x["counts_as_empirical_evidence"])
        self.assertEqual(x["empirical_ledger_increment"],0)
        self.assertEqual(p["additional_independent_biological_endpoints"],0)
        for phrase in (
            "### 3.4 Post-freeze GBIF source-completeness sensitivity",
            "10,215 objects",
            "2,832 source-specific fit cells",
            "1,033 of 1,128",
            "285 of 288 held-out cells",
            "282 of the original 283 evaluable cells",
            "was not met",
            "does **not** constitute a new independent biological replication",
        ):
            self.assertIn(phrase,self.manuscript,phrase)

    def test_24_recalibrated_reference_cells_and_cv_mechanism_are_not_overstated(self):
        ref=self.reference
        p=self.manifest["postfreeze_repaired_GBIF_source_sensitivity"]
        self.assertEqual(ref["reference_cells_frozen"],24)
        self.assertEqual(ref["paired_surfaces_opened_authorized_cells"],1033)
        self.assertEqual(ref["reference_cells_unresolved"],0)
        self.assertEqual(p["recalibrated_q95_reference_cells_frozen"],24)
        self.assertEqual(p["eligible_reference_paired_cells"],1033)
        self.assertEqual(self.cv["source_specific_adequacy_state_flips"],4)
        self.assertEqual(self.cv["frozen_adequacy_science"],{
            "outer_folds":4,"chance_auc":0.5,"minimum_auc_margin":0.01,
            "auc_sem_multiplier":1
        })
        self.assertIn("0.5070 to 0.4945",self.manuscript)
        self.assertIn("full original-283-cell retention condition failed",self.manuscript)
        self.assertIn("individual source-paired discordance or q95 values sometimes shifted appreciably",
                      self.manuscript)

    def test_abstract_stays_invited_method_length_safe(self):
        match=re.search(r"## Abstract\n\n(.*?)\n\n## 1\.",self.manuscript,re.S)
        self.assertIsNotNone(match)
        abstract=match.group(1)
        words=re.findall(r"\b[\w=-]+\b",abstract)
        self.assertLessEqual(len(words),150)
        self.assertIn("strict full-coverage robustness was not established",abstract)
        self.assertIn("1-a1",abstract)
        self.assertIn("1-a0",abstract)

    def test_submission_assets_disclose_source_limited_claim(self):
        p=self.manifest
        self.assertEqual(p["status"],"HOLD_FOR_SENSITIVITY_REVIEW")
        self.assertTrue(p["postfreeze_repaired_GBIF_source_sensitivity"]["manuscript_human_scientific_signoff_required"])
        for label,text in (("claim ledger",self.ledger),("cover letter",self.cover),
                           ("figure plan",self.figure),("readiness",self.readiness)):
            self.assertIn("283",text,label)
            self.assertIn("0/12",text,label)
            self.assertTrue(("282" in text or "one" in text),label)
        self.assertIn("full cell-coverage robustness",self.cover)
        self.assertIn("full original-283-cell retention condition",self.manuscript)
        self.assertIn("coauthors",self.readiness)
        self.assertIn("24",self.figure)
        self.assertIn("282",self.figure)
        for forbidden in ("Cremastra","Belonocnema","SMIL001"):
            self.assertNotIn(forbidden,self.manuscript)
            self.assertNotIn(forbidden,self.cover)

if __name__=="__main__":
    unittest.main()
