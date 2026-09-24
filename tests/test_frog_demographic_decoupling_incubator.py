import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "incubator" / "frog_demographic_decoupling"
INPUT_SCRIPT = BASE / "scripts" / "audit_input_contract.py"
JOIN_SCRIPT = BASE / "scripts" / "audit_meetnetten_join.py"
PROTOCOL = BASE / "protocol_v0_4.json"
README = BASE / "README.md"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


input_mod = load_module(INPUT_SCRIPT, "frog_audit_input_contract")
join_mod = load_module(JOIN_SCRIPT, "frog_audit_meetnetten_join")


class FrogDemographicDecouplingIncubatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.readme = README.read_text(encoding="utf-8")

    def _csv(self, fields, rows):
        f = tempfile.NamedTemporaryFile(
            "w", newline="", encoding="utf-8", suffix=".csv", delete=False
        )
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        f.close()
        return Path(f.name)

    def test_outcomes_remain_closed_before_raw_overlap_gate(self):
        self.assertEqual(
            self.protocol["status"],
            "pre-outcome_exact_programme_identity_frozen",
        )
        self.assertEqual(self.protocol["outcome_opening_status"], "closed")
        self.assertEqual(
            self.protocol["focal_candidate"]["raw_overlap_state"],
            "unopened",
        )
        self.assertTrue(
            self.protocol["raw_estimability_gate"][
                "biological_association_must_remain_closed_during_gate"
            ]
        )

    def test_same_species_projects_are_pinned_across_protocols(self):
        species = {
            row["scientificName"]: row["publisher_project_key"]
            for row in self.protocol["focal_candidate"]["species"]
        }
        self.assertEqual(species, {"Hyla arborea": 13, "Pelobates fuscus": 152})
        self.assertEqual(
            self.protocol["focal_candidate"]["chorus_protocol_ids"], [5, 33]
        )
        self.assertEqual(
            self.protocol["focal_candidate"]["downstream_protocol_ids"], [25, 32]
        )
        self.assertIn("same species-specific monitoring projects", self.readme)

    def test_exact_publisher_identity_is_only_authorized_join(self):
        focal = self.protocol["focal_candidate"]
        self.assertEqual(
            focal["analysis_unit_candidate"],
            ["locationID", "scientificName", "calendar_year"],
        )
        self.assertTrue(focal["exact_join_authorized"])
        self.assertTrue(focal["coordinate_or_locality_rescue_forbidden"])
        self.assertEqual(
            focal["common_location_semantics"],
            "INBO:MEETNET:LOCATION:<DimLocation.LocationID>",
        )
        self.assertIn("Nearest-coordinate matching", self.readme)

    def test_claim_language_prevents_demographic_overreach(self):
        forbidden = self.protocol["claim_language"][
            "forbidden_until_additional_data"
        ]
        for phrase in [
            "adult population recruitment",
            "population persistence",
            "demographic ghost population",
            "ecological trap",
            "local extinction early warning",
        ]:
            self.assertIn(phrase, forbidden)
        self.assertFalse(self.protocol["ecological_target"]["recruitment_word_authorized"])

    def test_missing_and_unsurveyed_never_become_absence(self):
        p = self._csv(
            ["site_id", "event_id", "date", "stage", "status", "count"],
            [
                {
                    "site_id": "s1",
                    "event_id": "e1",
                    "date": "2020-04-01",
                    "stage": "juvenile",
                    "status": "missing",
                    "count": "",
                },
                {
                    "site_id": "s1",
                    "event_id": "e2",
                    "date": "2020-05-01",
                    "stage": "juvenile",
                    "status": "unsurveyed",
                    "count": "",
                },
            ],
        )
        out = input_mod.audit(p)
        self.assertEqual(out["stage_status_counts"]["juvenile"]["absent"], 0)
        self.assertFalse(out["biological_failure_classified"])

    def test_present_zero_is_invalid_in_normalized_stage_contract(self):
        p = self._csv(
            ["site_id", "event_id", "date", "stage", "status", "count"],
            [
                {
                    "site_id": "s1",
                    "event_id": "e1",
                    "date": "2020-04-01",
                    "stage": "larva",
                    "status": "present",
                    "count": "0",
                }
            ],
        )
        with self.assertRaises(ValueError):
            input_mod.audit(p)

    def _synthetic_join_inputs(self, include_coordinate=False):
        event_fields = ["eventID", "eventDate", "locationID"]
        if include_coordinate:
            event_fields.append("decimalLatitude")
        chorus_events = []
        chorus_taxa = []
        downstream_events = []
        downstream_taxa = []
        event_num = 1

        for location_num in range(1, 31):
            location_id = f"INBO:MEETNET:LOCATION:{location_num:06d}"
            for month, day in [(4, 15), (5, 15)]:
                event_id = f"INBO:MEETNET:EVENT:{event_num:06d}"
                row = {
                    "eventID": event_id,
                    "eventDate": f"2022-{month:02d}-{day:02d}",
                    "locationID": location_id,
                }
                if include_coordinate:
                    row["decimalLatitude"] = "51.0"
                chorus_events.append(row)
                chorus_taxa.append(
                    {
                        "eventID": event_id,
                        "scientificName": "Hyla arborea",
                        "occurrenceStatus": "present",
                    }
                )
                event_num += 1

            event_id = f"INBO:MEETNET:EVENT:{event_num:06d}"
            downstream_events.append(
                {
                    "eventID": event_id,
                    "eventDate": "2022-06-20",
                    "locationID": location_id,
                }
            )
            downstream_taxa.append(
                {
                    "eventID": event_id,
                    "scientificName": "Hyla arborea",
                    "occurrenceStatus": "present",
                    "lifeStage": "larva",
                }
            )
            event_num += 1

        return (
            self._csv(event_fields, chorus_events),
            self._csv(
                ["eventID", "scientificName", "occurrenceStatus"], chorus_taxa
            ),
            self._csv(["eventID", "eventDate", "locationID"], downstream_events),
            self._csv(
                ["eventID", "scientificName", "occurrenceStatus", "lifeStage"],
                downstream_taxa,
            ),
        )

    def test_structural_join_can_pass_without_opening_ecological_association(self):
        ce, ct, de, dt = self._synthetic_join_inputs()
        out = join_mod.audit(ce, ct, de, dt)
        self.assertEqual(out["shared_location_species_years"], 30)
        self.assertEqual(out["shared_units_with_ge2_chorus_events"], 30)
        self.assertEqual(
            out["shared_units_with_at_least_one_chorus_event_not_after_downstream"],
            30,
        )
        self.assertTrue(out["structural_candidate_pass"])
        self.assertFalse(out["ecological_association_opened"])
        self.assertFalse(out["coordinate_join_used"])

    def test_join_audit_rejects_coordinate_rescue_surface(self):
        ce, ct, de, dt = self._synthetic_join_inputs(include_coordinate=True)
        with self.assertRaisesRegex(ValueError, "spatial rescue columns forbidden"):
            join_mod.audit(ce, ct, de, dt)


if __name__ == "__main__":
    unittest.main()
