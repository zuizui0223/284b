import csv
import json
from pathlib import Path
import unittest

from product_b_v7.preflight import FrameDeclaration, LiteratureWitness, evaluate_witness_frame_preflight

ROOT = Path(__file__).resolve().parents[1]
PAIR = ROOT / "registry/product_b_v7_2_jos002_pair_registry_v0_1.csv"
WITNESS = ROOT / "registry/product_b_v7_2_jos002_literature_witnesses_v0_1.csv"
FRAME = ROOT / "config/product_b_v7_2_jos002_frame_v0_1.json"
SNAPSHOT_CONTRACT = ROOT / "config/product_b_v7_2_snapshot_transport_contract_v0_1.json"
TERMINAL = ROOT / "results/product_b_v7_2_jos002_taxonomy_terminal_v0_1.json"


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


class JOS002HeldOutEngineeringAdmissionTests(unittest.TestCase):
    def test_pair_is_engineering_only_and_terminal_before_occurrence(self):
        with PAIR.open("r", encoding="utf-8", newline="") as handle:
            row = list(csv.DictReader(handle))[0]
        self.assertEqual(row["pair_id"], "JOS002")
        self.assertEqual(row["direction"], "Y_requires_X")
        self.assertEqual(row["engineering_only"], "true")
        self.assertEqual(row["taxonomy_state"], "unresolved_snapshot_taxonomy_concept")
        self.assertEqual(row["occurrence_reads_performed"], "false")
        self.assertIn("SYNONYM", row["known_boundary"])
        self.assertIn("Yucca brevifolia", row["known_boundary"])
        self.assertIn("permanently firewalled", row["known_boundary"])

    def test_terminal_result_records_concept_collapse_not_sampling_failure(self):
        result = json.loads(TERMINAL.read_text(encoding="utf-8"))
        self.assertEqual(result["terminal_state"], "unresolved_snapshot_taxonomy_concept")
        self.assertEqual(result["terminal_gate"], "snapshot_native_taxonomy_concept")
        self.assertFalse(result["host_taxon"]["snapshot_native_species_concept_separable"])
        self.assertEqual(result["host_taxon"]["current_gbif_accepted_name"], "Yucca brevifolia")
        self.assertFalse(result["snapshot_occurrence_rows_opened"])
        self.assertFalse(result["snapshot_occurrence_counts_opened"])
        self.assertIn(
            "filter_snapshot_rows_by_scientificname_to_split_the_collapsed_concept",
            result["forbidden_rescues"],
        )

    def test_seventeen_primary_eastern_sites_pass_unchanged_witness_floor(self):
        result = evaluate_witness_frame_preflight(pair_id="JOS002", witnesses=witnesses(), frame=frame())
        self.assertTrue(result.passed, (result.witness_preflight.reasons, result.frame_errors))
        self.assertEqual(result.witness_preflight.raw_witness_count, 17)
        self.assertEqual(result.witness_preflight.retained_witness_count, 17)
        self.assertEqual(result.witness_preflight.excluded_witness_count, 0)
        self.assertGreaterEqual(len(result.witness_preflight.unique_10km_cells), 3)

    def test_frame_is_independent_USA_adm0(self):
        data = json.loads(FRAME.read_text(encoding="utf-8"))
        self.assertEqual(data["frame_id"], "USA-ADM0-2327393")
        self.assertEqual(data["source_type"], "preexisting_admin_boundary")
        self.assertEqual(data["geometry_value"], "USA")
        self.assertEqual(data["operational_snapshot_country_code_iso2"], "US")
        self.assertIn("9469f09", data["source_version"])
        self.assertFalse(data["witness_coordinates_used_to_derive_geometry"])
        self.assertFalse(data["occurrence_information_used_to_derive_geometry"])

    def test_snapshot_transport_remains_open_only_for_new_pair_selection(self):
        contract = json.loads(SNAPSHOT_CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["snapshot"]["schema_audit_state"], "completed_frozen")
        self.assertTrue(contract["new_pair_selection_allowed"])
        self.assertFalse(contract["occurrence_row_reads_allowed"])
        self.assertIn("JOS001", contract["firewalled_consumed_pairs"])
        self.assertIn("JOS002", contract["firewalled_consumed_pairs"])


if __name__ == "__main__":
    unittest.main()
