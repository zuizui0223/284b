import csv
import json
from pathlib import Path
import unittest

from product_b_v7.preflight import FrameDeclaration, LiteratureWitness, evaluate_witness_frame_preflight
from product_b_v7_3.pair_admission import (
    ProspectivePairDeclaration,
    ReplacementHostInteractionEvidence,
    evaluate_pair_admission,
    evaluate_replacement_host_interaction_screen,
)

ROOT = Path(__file__).resolve().parents[1]
PAIR = ROOT / "registry/product_b_v7_3_crot001_pair_registry_v0_1.csv"
WITNESS = ROOT / "registry/product_b_v7_3_crot001_literature_witnesses_v0_1.csv"
FRAME = ROOT / "config/product_b_v7_3_crot001_frame_v0_1.json"
CONTROLS = ROOT / "registry/product_b_v7_3_crot001_control_pool_v0_1.csv"
ADMISSION = ROOT / "config/product_b_v7_3_crot001_admission_v0_1.json"
CURRENT_TAXONOMY = ROOT / "results/product_b_v7_3_crot001_current_taxonomy_v0_1.json"
CONTROL_TAXONOMY = ROOT / "results/product_b_v7_3_crot001_control_current_taxonomy_v0_1.json"
TERMINAL = ROOT / "results/product_b_v7_3_crot001_dependency_scope_terminal_v0_1.json"
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


def _historical_declaration():
    data = json.loads(ADMISSION.read_text(encoding="utf-8"))
    return data, ProspectivePairDeclaration(
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


class CROT001AdmissionTests(unittest.TestCase):
    def test_original_declaration_is_preserved_but_firewall_now_blocks_reentry(self):
        data, declaration = _historical_declaration()
        self.assertTrue(data["y_host_specificity_supported"])
        overlay = data["nonretroactive_terminal_overlay"]
        self.assertTrue(overlay["original_host_specificity_declaration_preserved_as_historical"])
        self.assertTrue(overlay["dependent_host_specificity_declaration_invalidated_for_downstream_use"])
        self.assertEqual(overlay["terminal_state"], "unresolved_dependency_scope")
        self.assertFalse(overlay["downstream_use_allowed"])
        result = evaluate_pair_admission(declaration)
        self.assertFalse(result.passed)
        self.assertIn("pair_is_firewalled", result.reasons)

    def test_current_taxonomy_result_remains_valid_historical_audit(self):
        result = json.loads(CURRENT_TAXONOMY.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "resolved_direct_exact_current_taxonomy")
        self.assertEqual(
            [(item["partner"], item["usage_key"]) for item in result["resolutions"]],
            [("x", "3033289"), ("y", "1573228")],
        )
        self.assertFalse(result["snapshot_taxonomy_identity_rows_opened"])
        self.assertFalse(result["snapshot_occurrence_rows_opened"])

    def test_twelve_primary_coordinates_remain_valid_historical_witnesses(self):
        result = evaluate_witness_frame_preflight(pair_id="CROT001", witnesses=_witnesses(), frame=_frame())
        self.assertTrue(result.passed, (result.witness_preflight.reasons, result.frame_errors))
        self.assertEqual(result.witness_preflight.raw_witness_count, 12)
        self.assertEqual(result.witness_preflight.retained_witness_count, 12)

    def test_un_m49_europe_frame_remains_independent_and_unopened(self):
        data = json.loads(FRAME.read_text(encoding="utf-8"))
        self.assertEqual(data["frame_id"], "UN-M49-EUROPE-150")
        self.assertEqual(data["geometry_type"], "admin_codes")
        self.assertEqual(data["un_m49_region_code"], "150")
        self.assertEqual(len(data["operational_snapshot_country_codes_iso2"]), 51)
        self.assertFalse(data["witness_coordinates_used_to_derive_geometry"])
        self.assertFalse(data["occurrence_information_used_to_derive_geometry"])

    def test_control_pool_records_taxonomy_history_and_actual_host_conflict(self):
        with CONTROLS.open("r", encoding="utf-8", newline="") as handle:
            rows = {row["control_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows["CROT_C02"]["current_taxonomy_state"], "rejected_current_taxonomy_not_accepted")
        admitted = [row for row in rows.values() if row["current_taxonomy_state"] == "resolved_exact_accepted"]
        self.assertEqual(len(admitted), 7)
        self.assertEqual(rows["CROT_C03"]["interaction_screen"], "invalid_actual_host_C_rotundiventris")
        self.assertEqual(rows["CROT_C04"]["interaction_screen"], "invalid_actual_host_C_rotundiventris")
        self.assertTrue(all(row["snapshot_occurrence_rows_opened"] == "false" for row in rows.values()))
        self.assertTrue(all(row["downstream_use_allowed"] == "false" for row in rows.values()))

        evidence = tuple(
            ReplacementHostInteractionEvidence(
                control_taxon=row["scientific_name"],
                screen_completed=row["current_taxonomy_state"] != "rejected_current_taxonomy_not_accepted",
                dependent_uses_control_as_host=row["interaction_screen"] == "invalid_actual_host_C_rotundiventris",
            )
            for row in rows.values()
        )
        decision = evaluate_replacement_host_interaction_screen(
            predeclared_control_taxa=tuple(row["scientific_name"] for row in rows.values()),
            evidence=evidence,
        )
        self.assertFalse(decision.passed)
        self.assertIn("predeclared_control_is_actual_host", decision.reasons)
        self.assertIn("interaction_screen_incomplete", decision.reasons)
        self.assertEqual(
            decision.invalid_actual_host_controls,
            ("Trollius altaicus", "Trollius asiaticus"),
        )

    def test_control_taxonomy_result_is_historical_and_downstream_invalidated(self):
        result = json.loads(CONTROL_TAXONOMY.read_text(encoding="utf-8"))
        self.assertEqual(result["admitted_count"], 7)
        self.assertEqual(result["interaction_screen_invalidated_controls"], ["CROT_C03", "CROT_C04"])
        self.assertFalse(result["downstream_use_allowed"])
        self.assertFalse(result["snapshot_taxonomy_identity_rows_opened"])

    def test_pair_registry_is_terminal_before_snapshot_identity(self):
        with PAIR.open("r", encoding="utf-8", newline="") as handle:
            row = list(csv.DictReader(handle))[0]
        self.assertEqual(row["pair_id"], "CROT001")
        self.assertEqual(row["terminal_state"], "unresolved_dependency_scope")
        self.assertEqual(row["snapshot_taxonomy_identity_state"], "not_opened_pair_terminal_dependency_scope")
        self.assertEqual(row["snapshot_occurrence_rows_opened"], "false")
        self.assertEqual(row["downstream_use_allowed"], "false")

    def test_candidate_audit_records_terminal_without_snapshot_rescue(self):
        with CANDIDATE_AUDIT.open("r", encoding="utf-8", newline="") as handle:
            rows = {row["candidate_id"]: row for row in csv.DictReader(handle)}
        self.assertEqual(rows["TMAC001"]["screen_state"], "rejected_before_snapshot_taxonomy")
        self.assertEqual(rows["TMAC001"]["direct_primary_witness_sites_confirmed"], "8")
        self.assertEqual(rows["CROT001"]["screen_state"], "terminal_dependency_scope_conflict_before_snapshot_identity")
        self.assertEqual(rows["CROT001"]["snapshot_occurrence_information_used"], "false")

    def test_terminal_result_forbids_control_or_scope_rescue_and_keeps_downstream_closed(self):
        result = json.loads(TERMINAL.read_text(encoding="utf-8"))
        self.assertEqual(result["terminal_state"], "unresolved_dependency_scope")
        self.assertEqual(result["invalidated_predeclared_controls"], ["CROT_C03", "CROT_C04"])
        self.assertFalse(result["replacement_or_rescue_controls_added"])
        self.assertFalse(result["dependency_scope_narrowed_after_conflict"])
        self.assertFalse(result["snapshot_taxonomy_identity_rows_opened"])
        self.assertFalse(result["snapshot_occurrence_rows_opened"])
        self.assertFalse(result["model_fit_reads_opened"])
        self.assertFalse(result["invariant_reads_opened"])
        self.assertFalse(result["process_knockout_reads_opened"])
        self.assertFalse(result["downstream_use_allowed"])


if __name__ == "__main__":
    unittest.main()
