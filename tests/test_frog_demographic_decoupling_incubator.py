import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "incubator" / "frog_demographic_decoupling" / "scripts" / "audit_input_contract.py"
PROTOCOL = ROOT / "incubator" / "frog_demographic_decoupling" / "protocol_v0_2.json"
README = ROOT / "incubator" / "frog_demographic_decoupling" / "README.md"

spec = importlib.util.spec_from_file_location("frog_audit_input_contract", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


class FrogDemographicDecouplingIncubatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.readme = README.read_text(encoding="utf-8")

    def _csv(self, rows):
        f = tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", suffix=".csv", delete=False)
        fields = ["site_id", "event_id", "date", "stage", "status", "count"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
        f.close()
        return Path(f.name)

    def test_primary_selection_remains_unopened(self):
        ps = self.protocol["primary_system_selection"]
        self.assertEqual(ps["state"], "unresolved_pending_raw_estimability_audit")
        self.assertIn("transition coefficient sign", ps["forbidden_selection_information"])
        self.assertIn("model fit favourability", ps["forbidden_selection_information"])
        self.assertFalse(self.protocol["endpoint_policy"]["full_chain_estimands_authorized"])
        self.assertEqual(self.protocol["empirical_outcome_status"], "unopened_for_candidate_selection")

    def test_natterjack_is_not_primary_under_current_snapshot(self):
        rows = {x["name"]: x for x in self.protocol["candidate_systems"]}
        n = rows["Flanders Natterjack sightings"]
        self.assertEqual(n["event_records"], 19)
        self.assertEqual(n["occurrence_records"], 117)
        self.assertFalse(n["primary_authorized"])
        self.assertEqual(n["role"], "small_full_chain_feasibility_or_calibration_candidate")
        self.assertIn("UNRESOLVED", self.readme)
        self.assertNotIn("Primary full-chain system — Flanders Natterjack", self.readme)

    def test_large_flanders_sources_are_recorded_without_authorizing_join(self):
        rows = {x["name"]: x for x in self.protocol["candidate_systems"]}
        chorus = rows["Meetnetten chorus counts"]
        larvae = rows["Meetnetten larvae and metamorph counts"]
        self.assertEqual((chorus["event_records"], chorus["occurrence_records"]), (963, 1436))
        self.assertEqual((larvae["event_records"], larvae["occurrence_records"]), (697, 2995))
        self.assertEqual(larvae["measurement_or_fact_records"], 3741)
        self.assertEqual(chorus["join_status"], "unresolved")
        self.assertEqual(larvae["join_status"], "unresolved")
        self.assertEqual(larvae["shared_target_species_with_chorus"], ["Hyla arborea", "Pelobates fuscus"])
        self.assertTrue(self.protocol["gates"]["coordinate_nearest_join_forbidden"])

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

    def test_synthetic_full_chain_panel_passes_only_structural_screen(self):
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
