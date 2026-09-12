from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "manuscript" / "ECOLOGY_LETTERS_SUBMISSION_READY_SNAPSHOT_V0_2.md"


def test_snapshot_routes_only_through_manifest_v04():
    text = SNAPSHOT.read_text(encoding="utf-8")
    assert "ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_4.md" in text
    assert "pitch v0.7" in text
    assert "Method proposal rationale v0.7" in text
    assert "proposal email v0.4" in text
    assert "compliance v0.4" in text


def test_snapshot_preserves_full_manuscript_and_empirical_boundary():
    text = SNAPSHOT.read_text(encoding="utf-8")
    assert "PREFIELD_FLAGSHIP_V0_7.md" in text
    assert "Do not silently rewrite the full manuscript before invitation" in text
    assert "12 independent held-out taxa" in text
    assert "0/12 taxa with any empirical-envelope exceedance" in text
    assert "Empirical ledger: **1**" in text
    assert "None increments the empirical ledger" in text


def test_snapshot_records_relation_layer_as_nonempirical_method_evidence():
    text = SNAPSHOT.read_text(encoding="utf-8")
    assert "exact marginal answers do not generally identify a hard directional relation" in text
    assert "classical coupling bounds" in text
    assert "JSDMs are explicitly treated as antecedent/upstream joint-modelling tools" in text
    assert "relation-layer separation counterexample and exact bounds" in text
