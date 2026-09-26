import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "product_b_level_c_smil001_event_relation_candidate_v0_1.json"


def _load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_smil001_is_directional_candidate_not_mutual_authorization():
    c = _load()
    assert c["contract_version"] == "product_b_level_c_smil001_event_relation_candidate_v0.1"
    assert c["pair_id"] == "SMIL001"
    assert c["x_taxon_name"] == "Smilax insularis"
    assert c["y_taxon_name"] == "Dasineura heterosmilacicola"
    assert c["constraint_class"] == "directional_dependency"
    assert c["authorized_direction"] == "X_requires_Y"
    assert c["mutual_obligacy_authorized"] is False


def test_smil001_relation_space_is_event_level_and_not_raw_range_equality():
    c = _load()
    assert c["declared_biological_event"] == "successful_sexual_reproduction_of_Smilax_insularis"
    assert c["relation_space"]["key_semantics"] == "plant_site_x_flowering_window"
    assert "visitation_or_reachability" in c["candidate_hard_relation"]
    assert c["level_a_same_target_q95_imported_as_cross_role_tolerance"] is False


def test_smil001_stays_closed_until_operational_keys_and_estimators_are_frozen():
    c = _load()
    assert c["operational_scope_state"] == "unresolved_before_focal_occurrence_relation_opening"
    assert c["role_x"]["estimator_contract_frozen"] is False
    assert c["role_y"]["estimator_contract_frozen"] is False
    assert c["relation_space"]["exact_spatial_keys_frozen"] is False
    assert c["relation_space"]["flowering_window_keys_frozen"] is False
    assert c["focal_occurrence_relation_opening_authorized"] is False
    assert c["hard_invariant_opening_authorized"] is False
    assert c["soft_crosscheck_opening_authorized"] is False
    assert c["process_knockout_authorized"] is False
    assert c["counts_as_empirical_evidence"] is False
    assert c["counts_as_empirical_conclusion"] is False


def test_smil001_candidate_selection_is_response_blind():
    c = _load()
    assert c["candidate_selection_used_occurrence_information"] is False
    assert c["candidate_selection_used_fitted_surfaces"] is False
    assert c["candidate_selection_used_relation_outcomes"] is False
