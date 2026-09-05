import csv
import json
from pathlib import Path
import unittest

from product_b_v7.preflight import FrameDeclaration, LiteratureWitness, evaluate_witness_frame_preflight
from product_b_v7_3.pair_admission import ProspectivePairDeclaration, evaluate_pair_admission

ROOT = Path(__file__).resolve().parents[1]
PAIR = ROOT / "registry/product_b_v7_3_crot001_pair_registry_v0_1.csv"
WITNESS = ROOT / "registry/product_b_v7_3_crot001_literature_witnesses_v0_1.csv"
FRAME = ROOT / "config/product_b_v7_3_crot001_frame_v0_1.json"
CONTROLS = ROOT / "registry/product_b_v7_3_crot001_control_pool_v0_1.csv"
ADMISSION = ROOT / "config/product_b_v7_3_crot001_admission_v0_1.json"
CURRENT_TAXONOMY = ROOT / "results/product_b_v7_3_crot001_current_taxonomy_v0_1.json"
CANDIDATE_AUDIT = ROOT / "registry/product_b_v7_3_candidate_audit_v0_1.csv"


def _witnesses():
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


def _frame():
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


class CROT001AdmissionTests(unittest.TestCase):
    def test_response_blind_pair_admission_still_passes_after_taxonomy_transition(self):
        data = json.loads(ADMISSION.read_text(encoding="utf-8"))
        declaration = ProspectivePairDeclaration(
            pair_id=data["pair_id"],
            x_biological_name=data["x_biological_name"],
            y_biological_name=data["y_biological_name"],
            direction=data["direction"],
            dependency_class=data["dependency_class"],
            y_obligately_requires_x=data["y_obligately_requires_x"],
            y_host_specificity_supported=data["y_host_specificity_supported"],
            direct_primary_witness_site_ids=tuple(data["direct_primary_witness_site_ids"]),
            independent_host_regions=tuple(data["independent_host_regions"]),
            predeclared_control_taxa=tuple(data["predeclared_control_taxa"]),
            snapshot_occurrence_information_used_for_selection=data["snapshot_occurrence_information_used_for_selection"],
            declaration_frozen=data["declaration_frozen"],
        )
        result = evaluate_pair_admission(declaration)
        self.assertTrue(result.passed, result.reasons)
        self.assertEqual(result.direct_witness_site_count, 12)
        self.assertEqual(result.independent_host_region_count, 2)
        self.assertEqual(result.predeclared_control_count, 8)
        self.assertTrue(data["current_taxonomy_access_started"])
        self.assertEqual(data["current_taxonomy_state"], "resolved_direct_exact_current_taxonomy")
        self.assertFalse(data["snapshot_taxonomy_identity_access_started"])
        self.assertFalse(data["snapshot_occurrence_row_access_started"])

    def test_current_taxonomy_result_is_direct_exact_for_both_partners(self):
        result = json.loads(CURRENT_TAXONOMY.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "resolved_direct_exact_current_taxonomy")
        self.assertEqual(
            [(item["partner"], item["usage_key"]) for item in result["resolutions"]],
            [("x", "3033289"), ("y", "1573228")],
        )
        self.assertFalse(result["snapshot_taxonomy_identity_rows_opened"])
        self.assertFalse(result["snapshot_occurrence_rows_opened"])

    def test_twelve_primary_coordinates_pass_unchanged_v7_witness_gate(self):
        result = evaluate_witness_frame_preflight(pair_id="CROT001", witnesses=_witnesses(), frame=_frame())
        self.assertTrue(result.passed, (result.witness_preflight.reasons, result.frame_errors))
        self.assertEqual(result.witness_preflight.raw_witness_count, 12)
        self.assertEqual(result.witness_preflight.retained_witness_count, 12)
        self.assertGreaterEqual(len(result.witness_preflight.unique_10km_cells), 3)

    def test_un_m49_europe_frame_is_independent_and_broad(self):
        data = json.loads(FRAME.read_text(encoding="utf-8"))
        self.assertEqual(data["frame_id"], "UN-M49-EUROPE-150")
        self.assertEqual(data["geometry_type"], "admin_codes")
        self.assertEqual(data["un_m49_region_code"], "150")
        self.assertEqual(len(data["operational_snapshot_country_codes_iso2"]), 51)
        self.assertIn("RU", data["operational_snapshot_country_codes_iso2"])
        self.assertFalse(data["witness_coordinates_used_to_derive_geometry"])
        self.assertFalse(data["occurrence_information_used_to_derive_geometry"])

    def test_control_pool_is_still_exactly_eight_and_taxonomy_unopened(self):
        with CONTROLS.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row["scientific_name"] for row in rows}), 8)
        self.assertTrue(all(row["current_taxonomy_state"] == "taxonomy_unopened" for row in rows))
        self.assertTrue(all(row["snapshot_occurrence_rows_opened"] == "false" for row in rows))

    def test_pair_registry_is_current_taxonomy_resolved_but_snapshot_unopened(self):
        with PAIR.open("r", encoding="utf-8", newline="") as handle:
            row = list(csv.DictReader(handle))[0]
        self.assertEqual(row["pair_id"], "CROT001")
        self.assertEqual(row["current_taxonomy_state"], "resolved_direct_exact_current_taxonomy")
        self.assertEqual(row["snapshot_taxonomy_identity_state"], "snapshot_taxonomy_identity_unopened")
        self.assertEqual(row["snapshot_occurrence_rows_opened"], "false")

    def test_candidate_audit_records_nonrescued_eight_site_rejection(self):
        with CANDIDATE_AUDIT.open("r", encoding="utf-8", newline="") as handle:
            rows = {row["candidate_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(rows["TMAC001"]["screen_state"], "rejected_before_snapshot_taxonomy")
        self.assertEqual(rows["TMAC001"]["direct_primary_witness_sites_confirmed"], "8")
        self.assertEqual(rows["CROT001"]["screen_state"], "admitted_to_literature_freeze")
        self.assertEqual(rows["CROT001"]["direct_primary_witness_sites_confirmed"], "12")


if __name__ == "__main__":
    unittest.main()
