import csv
import json
from pathlib import Path
import unittest

from product_b_v7.preflight import (
    FrameDeclaration,
    LiteratureWitness,
    evaluate_witness_frame_preflight,
)


ROOT = Path(__file__).resolve().parents[1]
WITNESS_PATH = ROOT / "registry/product_b_v7_kim001_literature_witnesses_v0_1.csv"
FRAME_PATH = ROOT / "config/product_b_v7_kim001_frame_v0_1.json"
PAIR_PATH = ROOT / "registry/product_b_v7_kim001_pair_registry_v0_1.csv"


def load_witnesses():
    with WITNESS_PATH.open("r", encoding="utf-8", newline="") as handle:
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


def load_frame():
    data = json.loads(FRAME_PATH.read_text(encoding="utf-8"))
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


class KIM001LiteratureWitnessTests(unittest.TestCase):
    def test_pair_is_new_and_occurrence_blind_across_taxonomy_transition(self):
        with PAIR_PATH.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["pair_id"], "KIM001")
        self.assertEqual(row["direction"], "Y_requires_X")
        self.assertEqual(row["occurrence_reads_performed"], "false")
        self.assertIn(
            row["taxonomy_state"],
            {
                "taxonomy_unopened",
                "resolved_manual_homotypic_synonym_bridge_x_plus_direct_exact_y",
            },
        )
        self.assertEqual(row["confirmatory_eligible"], "false")

    def test_thirteen_positive_rearing_sites_pass_unchanged_witness_floor(self):
        result = evaluate_witness_frame_preflight(
            pair_id="KIM001",
            witnesses=load_witnesses(),
            frame=load_frame(),
        )
        self.assertTrue(result.passed, (result.witness_preflight.reasons, result.frame_errors))
        self.assertEqual(result.witness_preflight.raw_witness_count, 13)
        self.assertEqual(result.witness_preflight.retained_witness_count, 13)
        self.assertEqual(result.witness_preflight.excluded_witness_count, 0)
        self.assertEqual(result.witness_preflight.duplicate_collapsed_count, 0)
        self.assertEqual(len(result.witness_preflight.unique_10km_cells), 13)

    def test_frame_is_independent_china_adm0_not_a_witness_hull(self):
        data = json.loads(FRAME_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["frame_id"], "CHN-ADM0-351020")
        self.assertEqual(data["source_type"], "preexisting_admin_boundary")
        self.assertEqual(data["geometry_type"], "admin_codes")
        self.assertEqual(data["geometry_value"], "CHN")
        self.assertIn("9469f09", data["source_version"])
        self.assertFalse(data["witness_coordinates_used_to_derive_geometry"])
        self.assertFalse(data["occurrence_information_used_to_derive_geometry"])


if __name__ == "__main__":
    unittest.main()
