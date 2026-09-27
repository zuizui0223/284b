import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"incubator"/"frog_demographic_decoupling"/"scripts"/"run_rmnp_eligibility_audit.py"
spec=importlib.util.spec_from_file_location("rmnp_eligibility",SCRIPT)
mod=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


class RMNPEligibilityRuleTests(unittest.TestCase):
    def row(self, **kw):
        base={
            "date":"6/15/2010","site_name":"S1","psma":"1","psma_stage":"A",
            "perc_surveyed":"100","max_depth":"< or = 1","fish":"N",
            "site_length_m":"10","site_width_m":"5",
        }
        base.update(kw)
        return base

    def test_stage_token_compounds(self):
        self.assertEqual(mod.stage_tokens("A, E"),{"A","E"})
        self.assertEqual(mod.stage_tokens("J/L"),{"J","L"})

    def test_visit_classification_contract(self):
        self.assertEqual(mod.classify_visit(self.row(psma="0",psma_stage="NA")),0)
        self.assertEqual(mod.classify_visit(self.row(psma="1",psma_stage="E")),1)
        self.assertEqual(mod.classify_visit(self.row(psma="1",psma_stage="A")),0)
        self.assertIsNone(mod.classify_visit(self.row(psma="1",psma_stage="J")))
        self.assertIsNone(mod.classify_visit(self.row(perc_surveyed="NA")))

    def test_adult_confirmation_requires_detection_and_A(self):
        self.assertTrue(mod.adult_detected(self.row(psma="1",psma_stage="A")))
        self.assertFalse(mod.adult_detected(self.row(psma="0",psma_stage="A")))
        self.assertFalse(mod.adult_detected(self.row(psma="1",psma_stage="E")))

    def test_depth_and_fish_rules(self):
        rs=[
            self.row(date="5/1/2010",max_depth="",fish="N"),
            self.row(date="6/1/2010",max_depth=">1 - <2",fish="Y"),
        ]
        for r in rs:
            r["_date"]=mod.parse_date(r["date"])
        depth,fish,area=mod.annual_covariates(rs)
        self.assertEqual(depth,"deeper")
        self.assertEqual(fish,"Y")
        self.assertIsNotNone(area)

    def test_synthetic_eligibility_can_pass_without_fitting_effects(self):
        rows=[]
        for s in range(60):
            depth="< or = 1" if s<30 else ">1 - <2"
            fish="Y" if s<20 else "N"
            # adult confirmed
            rows.append(self.row(site_name=f"S{s}",date="5/1/2010",psma="1",psma_stage="A",max_depth=depth,fish=fish))
            # reproductive positive for first 20, valid negatives otherwise
            rows.append(self.row(site_name=f"S{s}",date="6/1/2010",psma="1" if s<20 else "0",psma_stage="L" if s<20 else "NA",max_depth=depth,fish=fish))
        out=mod.audit_rows(rows)
        self.assertTrue(out["endpoint_gate_pass"])
        self.assertTrue(out["primary_depth_gate_pass"])
        self.assertTrue(out["secondary_fish_gate_pass"])
        self.assertTrue(out["confirmatory_primary_model_authorized"])
        self.assertFalse(out["effect_model_fitted"])
        self.assertFalse(out["effect_direction_opened"])


if __name__=="__main__":
    unittest.main()
