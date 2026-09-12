import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "PREFIELD_FLAGSHIP_V0_7.md"
PITCH = ROOT / "manuscript" / "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md"
PROPOSAL = ROOT / "manuscript" / "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md"
PROPOSAL_FIGURE = ROOT / "manuscript" / "figures" / "ecology_letters_method_proposal_figure_v0_5.svg"
ANTECEDENT_AUDIT = ROOT / "manuscript" / "CLOSER_ANTECEDENT_AUDIT_V0_4.md"
SEPARATION = ROOT / "manuscript" / "RELATION_LAYER_SEPARATION_V0_1.md"
REVIEWER2_AUDIT = ROOT / "manuscript" / "REVIEWER2_ADVERSARIAL_AUDIT_V0_1.md"
COMPLIANCE = ROOT / "manuscript" / "ECOLOGY_LETTERS_COMPLIANCE_V0_6.md"
MANIFEST = ROOT / "manuscript" / "ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_6.md"
ENGINE = ROOT / "scripts" / "relation_endpoint_contract.py"
FREEZER = ROOT / "scripts" / "freeze_relation_endpoint_contract.py"
QUICKSTART = ROOT / "scripts" / "relation_endpoint_quickstart.py"
INVITED_BUILDER = ROOT / "scripts" / "build_prefield_flagship_v0_8_candidate.py"
INVITED_HANDOFF = ROOT / "manuscript" / "INVITED_MANUSCRIPT_V0_8_HANDOFF.md"
SUMMARY = ROOT / "results" / "pre_field_identifiability_benchmark_summary_v0_1.json"
GENERALIZED = ROOT / "results" / "pre_field_state_dependent_invalidity_v0_2.json"
RELATION_SEPARATION = ROOT / "results" / "relation_layer_separation_v0_1.json"
LEVEL_A_AUDIT = ROOT / "results" / "reviewer2_level_a_structure_audit_v0_1.json"
V81 = ROOT / "results" / "product_b_level_c_operational_package_v8_1.json"


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text, flags=re.UNICODE))


def _abstract(manuscript: str) -> str:
    start = manuscript.index("## Abstract") + len("## Abstract")
    end = manuscript.index("## 1. Introduction")
    return manuscript[start:end]


def _main_text(manuscript: str) -> str:
    start = manuscript.index("## 1. Introduction")
    end = manuscript.index("## Data and code availability")
    return manuscript[start:end]


def test_ecology_letters_abstract_stays_within_method_limit():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert _word_count(_abstract(manuscript)) <= 150


def test_ecology_letters_main_text_stays_within_method_limit():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert _word_count(_main_text(manuscript)) <= 5000


def test_unsolicited_method_pitch_is_current_and_at_most_300_words():
    pitch = PITCH.read_text(encoding="utf-8")
    body = pitch.split("\n\n", 1)[1]
    assert _word_count(body) <= 300
    assert "The lead author works across" in body
    assert "12 fresh held-out taxa" in body
    assert "cell count is diagnostic rather than independent replication" in body
    assert "not reducible to better marginal models" in body
    assert "`P(E=1,F=0)` can range from 0 to 0.5" in body
    assert "canonically serialized and SHA-256 fingerprinted" in body
    assert "calibration/protocol reference" in body


def test_canonical_proposal_and_attachment_exist():
    for path in [
        PROPOSAL,
        PROPOSAL_FIGURE,
        ANTECEDENT_AUDIT,
        SEPARATION,
        REVIEWER2_AUDIT,
        COMPLIANCE,
        MANIFEST,
        ENGINE,
        FREEZER,
        QUICKSTART,
        INVITED_BUILDER,
        INVITED_HANDOFF,
    ]:
        assert path.exists(), path
    proposal = PROPOSAL.read_text(encoding="utf-8")
    figure = PROPOSAL_FIGURE.read_text(encoding="utf-8")
    assert "relation-endpoint contract" in proposal.lower()
    assert "Why this layer is not reducible to better upstream models" in proposal
    assert "A suitable JSDM may estimate the missing joint coupling" in proposal
    assert "### Auditable prospective freezing" in proposal
    assert "opening_rule_reference" in proposal
    assert "SHA-256 fingerprinted" in proposal
    assert "a1 = P(valid | F=true)" in proposal
    assert "a0 = P(valid | F=false)" in proposal
    assert "12 taxa" in proposal
    assert "independent biological units" in figure
    assert "a₁ = P(valid | F=true)" in figure
    assert "not independent n" in figure


def test_antecedent_audit_concedes_joint_modelling_and_preserves_novelty_boundary():
    audit = ANTECEDENT_AUDIT.read_text(encoding="utf-8")
    assert "LIES / observation-process identifiability" in audit
    assert "joint species distribution modelling and joint prediction" in audit
    assert "multi-source data fusion" in audit
    assert "Wilkinson et al. (2021)" in audit
    assert "Galiana et al. (2024)" in audit
    assert "statistical joint structure does not itself choose the endpoint semantics" in audit
    assert "does not claim new probability theory" in audit


def test_relation_layer_separation_is_classical_nonempirical_method_support():
    memo = SEPARATION.read_text(encoding="utf-8")
    receipt = json.loads(RELATION_SEPARATION.read_text(encoding="utf-8"))
    assert "Even perfect marginal answers do not" in memo
    assert "identical marginal answers and opposite hard-relation status" in memo
    assert "statistical adequacy does not itself choose the biological relation endpoint" in memo
    assert receipt["two_world_counterexample"]["same_marginal_answers_opposite_relation_status"] is True
    assert receipt["two_world_counterexample"]["sharp_violation_bounds"] == {"lower": 0.0, "upper": 0.5}
    boundary = receipt["claim_boundary"]
    assert boundary["does_not_claim_frechet_hoeffding_bounds_are_new"] is True
    assert boundary["does_not_replace_joint_species_distribution_models"] is True
    assert boundary["does_not_read_focal_level_c_values"] is True
    assert boundary["empirical_ledger_increment"] == 0


def test_reviewer2_audit_names_main_overclaim_risks():
    audit = REVIEWER2_AUDIT.read_text(encoding="utf-8")
    assert "283/283 is pseudoreplication" in audit
    assert "q95 sounds like a 95% prediction interval" in audit
    assert "zero-collapsing is a straw-man" in audit.lower()
    assert "philosophy, not a Method" in audit


def test_manuscript_keeps_level_c_focal_claims_closed():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8").lower()
    forbidden = [
        "level c confirmed dependency",
        "level c falsified dependency",
        "level-c confirmed dependency",
        "level-c falsified dependency",
    ]
    for phrase in forbidden:
        assert phrase not in manuscript
    assert "no focal level-c cross-role value" in manuscript


def test_manuscript_explicitly_positions_against_prior_work():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert "The ingredients are established" in manuscript
    assert "Chadwick et al. (2024)" in manuscript
    assert "Latency, Identifiability, Effort and Scale" in manuscript
    assert "observation-process identifiability" in manuscript
    assert "Getz et al. (2018)" in manuscript
    assert "prospectivity itself is not the novelty claim" in manuscript.lower()


def test_manuscript_defines_executable_relation_endpoint_contract():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert "five-part **relation-endpoint contract**" in manuscript
    assert "scripts/relation_endpoint_contract.py" in manuscript
    assert "hard_violation_authorized" in manuscript
    assert "noninformative_for_implication" in manuscript


def test_manuscript_does_not_treat_cells_as_independent_replication():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert "independent held-out biological units were 12 taxa" in manuscript
    assert "not treated as 288 independent replicates" in manuscript
    assert "cell-level diagnostic summary, not an independent sample size" in manuscript
    assert "no binomial success-probability claim" in manuscript


def test_q95_is_explicitly_empirical_envelope_not_nominal_coverage():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert "prospectively frozen empirical source-discordance envelope" in manuscript
    assert "not interpreted as a nominal 95% predictive interval" in manuscript
    assert "alpha=0.05" in manuscript


def test_generalized_invalidity_notation_replaces_hidden_symmetry():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    assert "a1 = P(valid key | F=true)" in manuscript
    assert "a0 = P(valid key | F=false)" in manuscript
    assert "`FPR_zero - FPR_gated = 1-a1`" in manuscript
    assert "`TPR_zero - TPR_gated = 1-a0`" in manuscript
    assert "controlled special case `a1=a0=a`" in manuscript
    assert "zero-collapsing ablation" in manuscript


def test_synthetic_receipts_read_no_focal_level_c_values():
    original = json.loads(SUMMARY.read_text(encoding="utf-8"))
    generalized = json.loads(GENERALIZED.read_text(encoding="utf-8"))
    assert original["focal_level_c_values_read"] is False
    assert generalized["focal_level_c_values_read"] is False
    assert generalized["empirical_ledger_increment"] == 0
    assert generalized["general_result"]["false_violation_inflation"] == "1-a1"
    assert generalized["general_result"]["apparent_true_violation_sensitivity_gain"] == "1-a0"


def test_level_a_structure_audit_preserves_independent_unit_boundary():
    audit = json.loads(LEVEL_A_AUDIT.read_text(encoding="utf-8"))
    assert audit["heldout_design"]["independent_heldout_taxa"] == 12
    assert audit["heldout_design"]["evaluable_cells"] == 283
    assert audit["heldout_design"]["taxa_with_any_ceiling_exceedance"] == 0
    assert audit["reference_calibration"]["interpretation"].startswith(
        "prospectively frozen empirical source-discordance envelope"
    )
    assert audit["empirical_ledger_increment"] == 0


def test_v81_repair_is_pre_data_and_nonempirical():
    receipt = json.loads(V81.read_text(encoding="utf-8"))
    assert receipt["field_calibration_data_seen_before_repair"] is False
    assert receipt["scientific_thresholds_changed"] is False
    assert receipt["minimum_sample_counts_changed"] is False
    assert receipt["empirical_ledger_increment"] == 0
    assert receipt["global_284b_empirical_ledger_after_v8_1"] == 1


def test_stage1_manifest_is_v06_and_full_manuscript_stays_v07_until_invitation():
    text = MANIFEST.read_text(encoding="utf-8")
    assert "ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md" in text
    assert "ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md" in text
    assert "ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md" in text
    assert "ECOLOGY_LETTERS_COMPLIANCE_V0_6.md" in text
    assert "opening_rule_reference" in text
    assert "PREFIELD_FLAGSHIP_V0_7.md" in text
    assert "build_prefield_flagship_v0_8_candidate.py" in text
    assert "Empirical ledger remains **1**" in text


def test_manuscript_has_exactly_six_planned_display_items():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    section = manuscript.split("## Proposed display items", 1)[1]
    items = re.findall(r"^\d+\. \*\*", section, flags=re.MULTILINE)
    assert len(items) == 6
