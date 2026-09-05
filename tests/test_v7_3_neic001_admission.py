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
PAIR = ROOT / "registry/product_b_v7_3_neic001_pair_registry_v0_1.csv"
WITNESS = ROOT / "registry/product_b_v7_3_neic001_literature_witnesses_v0_1.csv"
FRAME = ROOT / "config/product_b_v7_3_neic001_frame_v0_1.json"
ADMISSION = ROOT / "config/product_b_v7_3_neic001_admission_v0_1.json"
CURRENT_TAXONOMY = ROOT / "results/product_b_v7_3_neic001_current_taxonomy_v0_1.json"
INTERACTION = ROOT / "config/product_b_v7_3_neic001_control_interaction_evidence_v0_1.json"
CANDIDATE_AUDIT = ROOT / "registry/product_b_v7_3_candidate_audit_v0_1.csv"


def _admission():
    return json.loads(ADMISSION.read_text(encoding="utf-8"))


def _declaration():
    data = _admission()
    return ProspectivePairDeclaration(
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


def _witness_rows():
    with WITNESS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _admitted_witnesses():
    return tuple(
        LiteratureWitness(
            witness_id=row["witness_id"],
            source_doi=row["source_doi"],
            longitude=float(row["longitude"]),
            latitude=float(row["latitude"]),
            uncertainty_m=float(row["uncertainty_m"]),
            coordinate_source_type=row["coordinate_source_type"],
        )
        for row in _witness_rows()
        if row["admitted"].lower() == "true"
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


class NEIC001AdmissionTests(unittest.TestCase):
    def test_response_blind_engineering_admission_still_passes_after_taxonomy_transition(self):
        decision = evaluate_pair_admission(_declaration())
        self.assertTrue(decision.passed, decision.reasons)
        self.assertEqual(decision.direct_witness_site_count, 10)
        self.assertGreaterEqual(decision.independent_host_region_count, 2)
        self.assertEqual(decision.predeclared_control_count, 8)

    def test_exactly_ten_unambiguous_positive_table1_sites_are_admitted(self):
        rows = _witness_rows()
        admitted = [row for row in rows if row["admitted"] == "true"]
        excluded = {row["site_code"]: row for row in rows if row["admitted"] == "false"}
        self.assertEqual(len(admitted), 10)
        self.assertEqual({row["site_code"] for row in admitted}, {"AU","CH","SI","SAG","SAW","SAK","UG","UR","FL","TX"})
        self.assertIn("SAE", excluded)
        self.assertIn("CA", excluded)
        self.assertEqual(excluded["SAE"]["neochetina_eichhorniae_sample_count"], "0")
        self.assertIn("composite_population_row", excluded["CA"]["exclusion_reason"])

    def test_witness_and_world_frame_preflight_pass_without_witness_derived_geometry(self):
        result = evaluate_witness_frame_preflight(pair_id="NEIC001", witnesses=_admitted_witnesses(), frame=_frame())
        self.assertTrue(result.passed, (result.witness_preflight.reasons, result.frame_errors))
        self.assertEqual(result.witness_preflight.retained_witness_count, 10)
        self.assertGreaterEqual(len(result.witness_preflight.unique_10km_cells), 3)
        frame = json.loads(FRAME.read_text(encoding="utf-8"))
        self.assertEqual(frame["frame_id"], "UN-M49-WORLD-001")
        self.assertFalse(frame["witness_coordinates_used_to_derive_geometry"])
        self.assertFalse(frame["occurrence_information_used_to_derive_geometry"])
        self.assertEqual(frame["operational_country_materialization_state"], "deferred_until_separate_sampling_package")

    def test_human_release_and_hybridization_confounds_preclude_confirmatory_promotion(self):
        data = _admission()
        self.assertTrue(data["engineering_only"])
        self.assertFalse(data["confirmatory_promotion_allowed"])
        self.assertTrue(data["human_mediated_release_confounding"])
        self.assertTrue(data["species_identity_hybridization_caveat"])
        self.assertFalse(data["snapshot_occurrence_information_used_for_selection"])
        self.assertFalse(data["snapshot_taxonomy_information_used_for_selection"])

    def test_current_taxonomy_is_opened_only_to_host_synonym_bridge_pending(self):
        data = _admission()
        self.assertEqual(data["host_definition"], "plant_species_supporting_complete_life_cycle_and_reproduction")
        self.assertEqual(data["predeclared_control_interaction_evidence_doi"], "10.52997/jad.2.04.2021")
        self.assertEqual(len(data["predeclared_control_taxa"]), 8)
        self.assertTrue(data["current_taxonomy_access_started"])
        self.assertEqual(data["current_taxonomy_state"], "unresolved_host_synonym_bridge_pending")
        self.assertEqual(data["current_taxonomy_result_path"], "results/product_b_v7_3_neic001_current_taxonomy_v0_1.json")
        self.assertFalse(data["snapshot_taxonomy_identity_access_started"])
        self.assertFalse(data["snapshot_occurrence_row_access_started"])

    def test_partial_current_taxonomy_result_keeps_snapshot_closed(self):
        result = json.loads(CURRENT_TAXONOMY.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "unresolved_current_taxonomy_host_synonym_bridge_pending")
        self.assertEqual(result["resolved_partner"]["partner"], "y")
        self.assertEqual(result["resolved_partner"]["usage_key"], "4290716")
        self.assertEqual(result["unresolved_partner"]["partner"], "x")
        self.assertFalse(result["snapshot_taxonomy_identity_rows_opened"])
        self.assertFalse(result["snapshot_occurrence_rows_opened"])

    def test_frozen_control_interaction_evidence_covers_exact_pool_and_passes_host_definition(self):
        data = json.loads(INTERACTION.read_text(encoding="utf-8"))
        admission = _admission()
        evidence = tuple(
            ReplacementHostInteractionEvidence(
                control_taxon=item["control_taxon"],
                screen_completed=item["screen_completed"],
                dependent_uses_control_as_host=item["dependent_uses_control_as_host"],
            )
            for item in data["controls"]
        )
        decision = evaluate_replacement_host_interaction_screen(
            predeclared_control_taxa=admission["predeclared_control_taxa"],
            evidence=evidence,
        )
        self.assertTrue(decision.passed, decision.reasons)
        self.assertEqual(decision.screened_control_count, 8)
        self.assertEqual(decision.invalid_actual_host_controls, ())
        self.assertEqual(data["source_doi"], "10.52997/jad.2.04.2021")
        self.assertEqual(data["frozen_host_definition"], admission["host_definition"])
        self.assertEqual(data["screen_state"], "evidence_frozen_pending_focal_taxonomy_bridge_completion")
        self.assertFalse(data["snapshot_taxonomy_identity_rows_opened"])
        self.assertFalse(data["snapshot_occurrence_rows_opened"])
        monochoria = next(item for item in data["controls"] if item["control_taxon"] == "Monochoria hastata")
        self.assertFalse(monochoria["dependent_uses_control_as_host"])
        self.assertIn("life cycle not completed", monochoria["reported_interaction"])

    def test_pair_registry_is_bridge_pending_and_snapshot_unopened(self):
        with PAIR.open("r", encoding="utf-8", newline="") as handle:
            row = list(csv.DictReader(handle))[0]
        self.assertEqual(row["pair_id"], "NEIC001")
        self.assertEqual(row["current_taxonomy_state"], "unresolved_host_synonym_bridge_pending")
        self.assertEqual(row["snapshot_taxonomy_identity_state"], "snapshot_taxonomy_identity_unopened")
        self.assertEqual(row["snapshot_occurrence_rows_opened"], "false")

    def test_candidate_audit_records_bridge_pending_without_snapshot_selection(self):
        with CANDIDATE_AUDIT.open("r", encoding="utf-8", newline="") as handle:
            rows = {row["candidate_id"]: row for row in csv.DictReader(handle)}
        row = rows["NEIC001"]
        self.assertEqual(row["screen_state"], "current_taxonomy_host_synonym_bridge_pending")
        self.assertEqual(row["direct_primary_witness_sites_confirmed"], "10")
        self.assertEqual(row["snapshot_occurrence_information_used"], "false")


if __name__ == "__main__":
    unittest.main()
