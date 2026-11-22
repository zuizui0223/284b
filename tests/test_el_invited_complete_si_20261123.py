"""Source-matched tests for invited complete M1+M2 Supporting Information.

No model fitting, new endpoint opening, q95 recalibration or data retrieval.
Run: python -m unittest discover -s tests -p test_el_invited_complete_si_20261123.py
"""
import csv
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md"
SI = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COMPLETE_SI_V1.md"
HIST = ROOT / "results/product_b_same_target_core19_v0_4_heldout_final_receipt.json"
REPAIRED = ROOT / "results/gbif_repaired_heldout12_sensitivity_v1.json"
AUDIT = ROOT / "results/reviewer2_level_a_structure_audit_v0_1.json"
COVERAGE = ROOT / "results/gbif_repaired_heldout12_postterminal_coverage_audit_v1.json"
BENCH = ROOT / "results/pre_field_identifiability_benchmark_summary_v0_1.json"
INVALID = ROOT / "results/pre_field_state_dependent_invalidity_v0_2.json"
CELLS = ROOT / "results/gbif_repaired_heldout12_sensitivity_cells_v1.csv"
Q95 = ROOT / "results/gbif_repaired_reference47_q95_ceiling_v1.csv"
MANIFEST = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_MANIFEST_V1.json"
FIGCAP = ROOT / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_CAPTIONS_V1.md"

def jsonfile(path):
    return json.loads(path.read_text(encoding="utf-8"))

def csvfile(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

class CompleteSupportingInformationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.si = SI.read_text(encoding="utf-8")
        cls.ms = MS.read_text(encoding="utf-8")
        cls.historical = jsonfile(HIST)
        cls.repaired = jsonfile(REPAIRED)
        cls.original_audit = jsonfile(AUDIT)
        cls.coverage = jsonfile(COVERAGE)
        cls.benchmark = jsonfile(BENCH)
        cls.invalid = jsonfile(INVALID)
        cls.cells = csvfile(CELLS)
        cls.references = csvfile(Q95)
        cls.manifest = jsonfile(MANIFEST)

    def test_eleven_sections_and_four_figures(self):
        headings = re.findall(r"^## S(\d+)\. ", self.si, flags=re.MULTILINE)
        self.assertEqual(headings, [str(i) for i in range(1,12)])
        self.assertIn("Integrated Supporting Information", self.si)
        for number in range(1,5):
            self.assertIn(f"Fig. {number}", self.ms)
            self.assertIn(f"## Figure {number}.", FIGCAP.read_text(encoding="utf-8"))
        for banned in ("Cremastra","Belonocnema","SMIL001"):
            self.assertNotIn(banned, self.si)

    def test_original_not_overwritten_and_source_repair_not_promoted(self):
        self.assertEqual(self.historical["heldout"]["taxa"],12)
        self.assertEqual(self.historical["heldout"]["paired_prediction_surfaces_opened_cells"],283)
        self.assertEqual(self.historical["heldout"]["paired_prediction_surfaces_kept_closed_cells"],5)
        self.assertTrue(self.historical["counts_as_empirical_conclusion"])
        self.assertEqual(self.repaired["heldout_cells_expected"],288)
        self.assertEqual(self.repaired["paired_prediction_surfaces_opened_cells"],285)
        self.assertEqual(self.repaired["paired_prediction_surfaces_kept_closed_cells"],3)
        self.assertEqual(self.repaired["repaired_heldout_taxa_with_attention"],0)
        self.assertEqual(self.coverage["original_opened_retained"],282)
        self.assertEqual(self.coverage["original_opened_lost"],1)
        self.assertEqual(self.coverage["newly_opened_restored_cells"],3)
        self.assertFalse(self.repaired["source_completeness_0_of_12_robust"])
        self.assertEqual(self.repaired["empirical_ledger_increment"],0)
        self.assertEqual(self.manifest["status"],"HOLD_FOR_SENSITIVITY_REVIEW")
        self.assertIn("**282/283**",self.si)
        self.assertIn("**0/12 taxa with any exceedance**",self.si)
        self.assertIn(self.historical["final_endpoint_fingerprint"],self.si)
        self.assertIn(self.repaired["final_endpoint_fingerprint"],self.si)
        self.assertIn("not independent biological replications",self.si)

    def test_twelve_species_table_matches_source_specific_maxima(self):
        audited = self.original_audit["taxon_level_max_observed_to_ceiling_ratio"]
        self.assertEqual(len(audited),12)
        cells = self.cells
        self.assertEqual(len(cells),288)
        keys={(x["taxon"],x["M_km"],x["procedure"]) for x in cells}
        self.assertEqual(len(keys),288)
        start=self.si.index("## S3. ")
        end=self.si.index("## S4. ", start)
        table=self.si[start:end]
        pattern=r"^\| \*([A-Za-z]+ [a-z]+)\* \| (\d+\.\d{3}) \| (\d+\.\d{3}) \| (\d+)/24 \|$"
        lines=re.findall(pattern,table,flags=re.MULTILINE)
        self.assertEqual(len(lines),12)
        self.assertEqual({x[0] for x in lines},set(audited))
        limits={(x["M_km"],x["procedure"]):float(x["one_minus_schoener_d_reference_ceiling"]) for x in self.references}
        self.assertEqual(len(limits),24)
        opened_total=0
        for name,old_ratio,new_ratio,eligible in lines:
            taxon=[x for x in cells if x["taxon"]==name]
            self.assertEqual(len(taxon),24)
            opened=[x for x in taxon if x["paired_prediction_surface_opened"]=="True"]
            opened_total+=len(opened)
            maximum=0.0
            for x in opened:
                ceiling=limits[(x["M_km"],x["procedure"])]
                discordance=float(x["one_minus_schoener_d"])
                self.assertAlmostEqual(float(x["frozen_reference_ceiling"]),ceiling,places=10)
                self.assertLessEqual(discordance,ceiling)
                maximum=max(maximum,discordance/ceiling)
            self.assertEqual(int(eligible),len(opened))
            self.assertEqual(old_ratio,f"{audited[name]:.3f}")
            self.assertEqual(new_ratio,f"{maximum:.3f}")
        self.assertEqual(opened_total,285)

    def test_twentyfour_restored_reference_ceiling_table(self):
        table=self.si[self.si.index("### Table S2."):self.si.index("## S8.")]
        pattern=r"^\| (150|300|500) \| \x60([^\x60]+)\x60 \| (\d+) \| (\d+\.\d{5}) \|$"
        rows=re.findall(pattern,table,flags=re.MULTILINE)
        self.assertEqual(len(rows),24)
        refs={(x["M_km"],x["procedure"]):(int(x["authorized_distinct_calibration_taxa"]),
                float(x["one_minus_schoener_d_reference_ceiling"])) for x in self.references}
        self.assertEqual(len(refs),24)
        for M,procedure,n,q95 in rows:
            actual_n,actual_q95=refs[(M,procedure)]
            self.assertGreaterEqual(actual_n,30)
            self.assertEqual(int(n),actual_n)
            self.assertEqual(q95,f"{actual_q95:.5f}")

    def test_theorem_fdf_conditioning_and_zero_call(self):
        for label in ("FPR_zero − FPR_gated = 1 − a1","TPR_zero − TPR_gated = 1 − a0",
                      "FDF_qualified = (1-pi)a1(1-q)","undefined if the denominator is zero",
                      "pi_valid",".585774",".700389"):
            self.assertIn(label,self.si)
        for a1,a0,expected in ((1,1,.6451612903225806),(.7,.9,.5857740585774057),(.9,.7,.7003891050583658)):
            fp=.9*a1*.2
            tp=.1*a0*.99
            self.assertAlmostEqual(fp/(fp+tp),expected,places=12)
        self.assertEqual(self.invalid["empirical_ledger_increment"],0)
        self.assertEqual(self.invalid["general_result"]["false_violation_inflation"],"1-a1")

    def test_analytic_benchmark_and_required_hold(self):
        self.assertEqual(self.benchmark["scenario_count"],8748)
        self.assertEqual(self.benchmark["calibration_pass_count"],4320)
        self.assertEqual(self.benchmark["calibration_fail_count"],4428)
        self.assertTrue(self.benchmark["analytic_not_monte_carlo"])
        self.assertFalse(self.benchmark["focal_level_c_values_read"])
        for marker in ("**8,748 parameter scenarios**","**4,320**","**4,428**",
                       "not real observed key-level data","HOLD_FOR_SENSITIVITY_REVIEW",
                       "results/gbif_repaired_heldout12_sensitivity_cells_v1.csv",
                       "results/pre_field_identifiability_benchmark_summary_v0_1.json"):
            self.assertIn(marker,self.si)
        self.assertTrue(self.manifest["postfreeze_repaired_GBIF_source_sensitivity"]["manuscript_human_scientific_signoff_required"])
        self.assertFalse(self.manifest["postfreeze_repaired_GBIF_source_sensitivity"]["strict_full_historical_283_cell_retention_robust"])

if __name__=="__main__":
    unittest.main()
