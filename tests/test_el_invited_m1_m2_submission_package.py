import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_MANIFEST_V1.json"

def test_manifest_points_to_positive_core_assets():
    p=json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert p["scientific_core"]["level_a_independent_taxa"] == 12
    assert p["scientific_core"]["diagnostics_evaluable"] == 283
    assert p["scientific_core"]["diagnostics_unresolved"] == 5
    assert p["scientific_core"]["taxa_with_envelope_exceedance"] == 0
    for key in ("manuscript","claim_ledger","figure_plan","cover_letter","title_page","readiness"):
        assert (ROOT/p[key]).exists()

def test_submission_assets_do_not_reintroduce_level_c():
    paths=[
        ROOT/"manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COVER_LETTER_V1.md",
        ROOT/"manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_TITLE_PAGE_V1.md",
        ROOT/"manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_READINESS_V1.md",
    ]
    joined="\n".join(x.read_text(encoding="utf-8") for x in paths)
    for forbidden in ("Cremastra", "Belonocnema", "SMIL001"):
        assert forbidden not in joined
    assert "12 taxa" in joined
    assert "283" in joined

def test_fallback_is_level_a_only():
    p=json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert p["fallback"] == "manuscript/LEVEL_A_SHORT_REPORT_V0_1.md"
