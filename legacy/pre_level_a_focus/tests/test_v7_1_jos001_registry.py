import csv
import json
from pathlib import Path
import unittest

from product_b_v7.preflight import FrameDeclaration, LiteratureWitness, evaluate_witness_frame_preflight

ROOT = Path(__file__).resolve().parents[1]
PAIR = ROOT / "registry/product_b_v7_1_jos001_pair_registry_v0_1.csv"
WITNESS = ROOT / "registry/product_b_v7_1_jos001_literature_witnesses_v0_1.csv"
FRAME = ROOT / "config/product_b_v7_1_jos001_frame_v0_1.json"
CONTRACT = ROOT / "config/product_b_v7_1_engineering_contract_v0_1.json"


def witnesses():
    with WITNESS.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return tuple(
        LiteratureWitness(
            witness_id=row["witness_id"],
            source_doi=row["source_doi"],
            longitude=float(row["longitude"]),
            latitude=float(row["latitude"]),
            uncertainty_m=float(row["uncertainty_m"]),
            coordinate_source_type=row["coordinate_source_type"],
        )
        for row in rows
        if row["admitted"].lower() == "true"
    )


def frame():
    data = json.loads(FRAME.read_text(encoding="utf-8"))
    return FrameDeclaration(
        frame_id=data["frame_id"],
        source_type=data["source_type"],
        source_authority=data["source_authority"],
        source_version=data["source_version"],
        geometry_type=data["geometry_type"],
        geometry_value=data["geometry_value"],
        witness_coordinates_used_to_derive_geometry=data["witness_coordinates_used_to_derive_geometry"],
        occurrence_information_used_to_derive_geometry=data["occurrence_information_used_to_derive_geometry"],
    )


class JOS001EngineeringAdmissionTests(unittest.TestCase):
    def test_pair_is_engineering_only_and_terminal_after_consumed_transport_run(self):
        with PAIR.open("r", encoding="utf-8", newline="") as handle:
            row = list(csv.DictReader(handle))[0]
        self.assertEqual(row["pair_id"], "JOS001")
        self.assertEqual(row["direction"], "Y_requires_X")
        self.assertEqual(row["engineering_only"], "true")
        self.assertEqual(
            row["taxonomy_state"],
            "resolved_direct_exact_x_plus_manual_direct_synonym_bridge_y",
        )
        self.assertEqual(row["occurrence_reads_performed"], "true")
        self.assertIn("engineering_execution_unresolved", row["known_boundary"])
        self.assertIn("controls were not opened", row["known_boundary"])
        self.assertIn("never confirmatory", row["known_boundary"])

    def test_fourteen_primary_witnesses_pass_v7_floor(self):
        result = evaluate_witness_frame_preflight(
            pair_id="JOS001", witnesses=witnesses(), frame=frame()
        )
        self.assertTrue(result.passed, (result.witness_preflight.reasons, result.frame_errors))
        self.assertEqual(result.witness_preflight.raw_witness_count, 14)
        self.assertEqual(result.witness_preflight.retained_witness_count, 14)
        self.assertEqual(result.witness_preflight.excluded_witness_count, 0)
        self.assertGreaterEqual(len(result.witness_preflight.unique_10km_cells), 3)

    def test_frame_is_independent_USA_adm0(self):
        data = json.loads(FRAME.read_text(encoding="utf-8"))
        self.assertEqual(data["frame_id"], "USA-ADM0-2327393")
        self.assertEqual(data["source_type"], "preexisting_admin_boundary")
        self.assertEqual(data["geometry_value"], "USA")
        self.assertEqual(data["operational_occurrence_country_code_iso2"], "US")
        self.assertIn("9469f09", data["source_version"])
        self.assertFalse(data["witness_coordinates_used_to_derive_geometry"])
        self.assertFalse(data["occurrence_information_used_to_derive_geometry"])

    def test_engineering_contract_does_not_relax_sampling_floors(self):
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(data["host_sampling_floor"]["minimum_independent_records"], 50)
        self.assertEqual(data["host_sampling_floor"]["minimum_unique_10km_cells"], 30)
        self.assertEqual(data["host_sampling_floor"]["minimum_effective_10km_cells"], 10.0)
        self.assertEqual(data["literature_witness_floor"]["minimum_independent_witnesses"], 5)
        self.assertEqual(data["literature_witness_floor"]["minimum_unique_10km_cells"], 3)
        self.assertFalse(
            data["prospective_host_feasibility_screen"][
                "occurrence_counts_maps_or_cell_statistics_allowed_for_candidate_selection"
            ]
        )
        self.assertIn("JOS001", data["firewalled_from_v7_1_confirmation"])


if __name__ == "__main__":
    unittest.main()
