import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location(
    "relation_endpoint_quickstart", SCRIPTS / "relation_endpoint_quickstart.py"
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

DOC = ROOT / "docs" / "relation_endpoint_quickstart.md"
ENGINE = ROOT / "scripts" / "relation_endpoint_contract.py"


def test_quickstart_states_are_exactly_expected():
    payload = MOD.build_demo_payload()
    soft = payload["soft_contract"]
    hard = payload["hard_contract"]

    assert soft["consistent_example"] == "consistent"
    assert soft["attention_example"] == "attention_required"
    assert soft["unresolved_example"] == "unresolved"

    assert hard["function_present"] == "no_observed_violation"
    assert hard["unqualified_absence"] == "unresolved"
    assert hard["qualified_absence"] == "hard_violation_authorized"
    assert hard["antecedent_false"] == "noninformative_for_implication"


def test_quickstart_exposes_frozen_contract_fingerprints_and_opening_references():
    payload = MOD.build_demo_payload()
    soft = payload["soft_contract"]
    hard = payload["hard_contract"]
    assert soft["opening_rule_reference"] == "synthetic_reference_envelope_v1"
    assert hard["opening_rule_reference"] == "synthetic_negative_state_qualification_v1"
    soft_fp = soft["fingerprint_sha256"]
    hard_fp = hard["fingerprint_sha256"]
    assert len(soft_fp) == 64
    assert len(hard_fp) == 64
    assert soft_fp != hard_fp


def test_quickstart_ablation_matches_generalized_identity():
    r = MOD.build_demo_payload()["invalid_state_ablation"]
    assert abs(r["false_violation_inflation"] - 0.30) < 1e-12
    assert abs(r["apparent_sensitivity_gain"] - 0.10) < 1e-12


def test_quickstart_reads_no_focal_level_c_values():
    boundary = MOD.build_demo_payload()["claim_boundary"]
    assert boundary["synthetic_only"] is True
    assert boundary["focal_level_c_values_read"] is False
    assert boundary["empirical_ledger_increment"] == 0


def test_documentation_explains_relation_field_authorization_freezing_and_rule_reference():
    text = DOC.read_text(encoding="utf-8")
    assert "A contract must state the relation explicitly" in text
    assert "`relation_level` names the endpoint class; `relation` states the actual" in text
    assert "fingerprinted with SHA-256" in text
    assert "The fingerprint is the prospective identity of the relation endpoint" in text
    assert "opening_rule_reference" in text
    assert "Biological authorization" in text
    assert "unqualified absence remains unresolved" in text
    assert "empirical ledger remains 1" in text


def test_engine_contains_explicit_relation_reference_and_fingerprint_surface():
    text = ENGINE.read_text(encoding="utf-8")
    assert "relation: str" in text
    assert "opening_rule_reference: str" in text
    assert '("relation", self.relation)' in text
    assert '("opening_rule_reference", self.opening_rule_reference)' in text
    assert "def canonical_json" in text
    assert "def fingerprint_sha256" in text
