import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "incubator" / "frog_demographic_decoupling" / "scripts" / "audit_input_contract.py"

spec = importlib.util.spec_from_file_location("frog_audit_input_contract", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


class FrogDemographicDecouplingIncubatorTests(unittest.TestCase):
    def _csv(self, rows):
        f = tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", suffix=".csv", delete=False)
        fields = ["site_id", "event_id", "date", "stage", "status", "count"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
        f.close()
        return Path(f.name)

    def test_missing_and_unsurveyed_never_become_absence(self):
        p = self._csv([
            {"site_id":"s1","event_id":"e1","date":"2020-04-01","stage":"juvenile","status":"missing","count":""},
            {"site_id":"s1","event_id":"e2","date":"2020-05-01","stage":"juvenile","status":"unsurveyed","count":""},
        ])
        out = mod.audit(p)
        self.assertEqual(out["stage_status_counts"]["juvenile"]["absent"], 0)
        self.assertEqual(out["stage_status_counts"]["juvenile"]["missing"], 1)
        self.assertEqual(out["stage_status_counts"]["juvenile"]["unsurveyed"], 1)
        self.assertFalse(out["biological_failure_classified"])

    def test_present_zero_is_invalid(self):
        p = self._csv([
            {"site_id":"s1","event_id":"e1","date":"2020-04-01","stage":"larva","status":"present","count":"0"},
        ])
        with self.assertRaises(ValueError):
            mod.audit(p)

    def test_synthetic_full_chain_panel_passes_only_estimability(self):
        rows=[]
        for site in range(10):
            for year in range(2020,2023):
                for visit in range(3):
                    for stage in mod.STAGES:
                        rows.append({
                            "site_id":f"s{site}",
                            "event_id":f"s{site}-{year}-v{visit}",
                            "date":f"{year}-0{4+visit}-01",
                            "stage":stage,
                            "status":"present",
                            "count":"1",
                        })
        out=mod.audit(self._csv(rows))
        self.assertTrue(out["full_chain_estimability_candidate"])
        self.assertFalse(out["biological_failure_classified"])


if __name__ == "__main__":
    unittest.main()
