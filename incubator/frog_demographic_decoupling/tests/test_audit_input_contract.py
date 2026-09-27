import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_input_contract.py"

spec = importlib.util.spec_from_file_location("audit_input_contract", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


class AuditInputContractTests(unittest.TestCase):
    def write_rows(self, rows):
        tmp = tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", suffix=".csv", delete=False)
        fields = ["site_id", "event_id", "date", "stage", "status", "count"]
        w = csv.DictWriter(tmp, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
        tmp.close()
        return Path(tmp.name)

    def test_missing_is_not_zero(self):
        p = self.write_rows([
            {"site_id":"s1","event_id":"e1","date":"2020-04-01","stage":"juvenile","status":"missing","count":""}
        ])
        out = mod.audit(p)
        self.assertEqual(out["stage_status_counts"]["juvenile"]["missing"], 1)
        self.assertEqual(out["stage_status_counts"]["juvenile"]["absent"], 0)
        self.assertFalse(out["biological_failure_classified"])

    def test_present_requires_positive_count(self):
        p = self.write_rows([
            {"site_id":"s1","event_id":"e1","date":"2020-04-01","stage":"egg","status":"present","count":"0"}
        ])
        with self.assertRaises(ValueError):
            mod.audit(p)

    def test_duplicate_event_stage_fails_full_chain_candidate(self):
        p = self.write_rows([
            {"site_id":"s1","event_id":"e1","date":"2020-04-01","stage":"adult_breeding","status":"present","count":"2"},
            {"site_id":"s1","event_id":"e1","date":"2020-04-01","stage":"adult_breeding","status":"present","count":"3"},
        ])
        out = mod.audit(p)
        self.assertEqual(out["duplicate_event_stage_rows"], 1)
        self.assertFalse(out["full_chain_estimability_candidate"])

    def test_synthetic_complete_panel_can_pass_estimability_candidate(self):
        rows = []
        for site in range(10):
            for year in range(2020, 2023):
                for visit in range(3):
                    event = f"s{site}-{year}-v{visit}"
                    date = f"{year}-0{4+visit}-01"
                    for stage in mod.STAGES:
                        rows.append({
                            "site_id": f"s{site}",
                            "event_id": event,
                            "date": date,
                            "stage": stage,
                            "status": "present",
                            "count": "1",
                        })
        p = self.write_rows(rows)
        out = mod.audit(p)
        self.assertEqual(out["site_years"], 30)
        self.assertEqual(out["repeated_site_years_ge3"], 30)
        self.assertTrue(out["full_chain_estimability_candidate"])
        self.assertFalse(out["biological_failure_classified"])


if __name__ == "__main__":
    unittest.main()
