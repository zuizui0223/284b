import csv
import json
from pathlib import Path
import unittest

from product_b_v7.preflight import FrameDeclaration, LiteratureWitness, evaluate_witness_frame_preflight

ROOT = Path(__file__).resolve().parents[1]
PAIR = ROOT / "registry/product_b_v7_2_jos003_pair_registry_v0_1.csv"
WITNESS = ROOT / "registry/product_b_v7_2_jos003_literature_witnesses_v0_1.csv"
FRAME = ROOT / "config/product_b_v7_2_jos003_frame_v0_1.json"
SNAPSHOT_CONTRACT = ROOT / "config/product_b_v7_2_snapshot_transport_contract_v0_1.json"


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
        for row in rows if row["admitted"].lower() == "true"
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


class JOS003HeldOutEngineeringAdmissionTests(unittest.TestCase):
    def test_pair_is_new_engineering_only_and_occurrence_blind(self):
        with PAIR.open("r", encoding="utf-8", newline="") as handle:
            row = list(csv.DictReader(handle))[0]
        self.assertEqual(row["pair_id"], "JOS003")
        self.assertEqual(row["direction"], "Y_requires_X")
        self.assertEqual(row["taxonomy_state"], "taxonomy_unopened")
        self.assertEqual(row["occurrence_reads_performed"], "false")
        self.assertIn("No snapshot occurrence row", row["known_boundary"])

    def test_twelve_primary_positive_sites_pass_unchanged_witness_floor(self):
        result = evaluate_witness_frame_preflight(pair_id="JOS003", witnesses=witnesses(), frame=frame())
        self.assertTrue(result.passed, (result.witness_preflight.reasons, result.frame_errors))
        self.assertEqual(result.witness_preflight.raw_witness_count, 12)
        self.assertEqual(result.witness_preflight.retained_witness_count, 12)
        self.assertGreaterEqual(len(result.witness_preflight.unique_10km_cells), 3)

    def test_frame_is_independent_USA_adm0(self):
        data = json.loads(FRAME.read_text(encoding="utf-8"))
        self.assertEqual(data["frame_id"], "USA-ADM0-2327393")
        self.assertFalse(data["witness_coordinates_used_to_derive_geometry"])
        self.assertFalse(data["occurrence_information_used_to_derive_geometry"])

    def test_snapshot_contract_is_frozen_and_occurrence_closed(self):
        contract = json.loads(SNAPSHOT_CONTRACT.read_text(encoding="utf-8"))
        self.assertTrue(contract["new_pair_selection_allowed"])
        self.assertFalse(contract["occurrence_row_reads_allowed"])
        self.assertIn("JOS002", contract["firewalled_consumed_pairs"])
        self.assertNotIn("JOS003", contract["firewalled_consumed_pairs"])


if __name__ == "__main__":
    unittest.main()
