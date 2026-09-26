import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_ecology_letters_stage1_email.py"

SPEC = importlib.util.spec_from_file_location("stage1_email_renderer", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def complete_metadata():
    return {
        "authors_order": ["Author A", "Author B"],
        "affiliations": ["Department A, University B", "Institute C"],
        "corresponding_author_name": "Author A",
        "corresponding_email": "author@example.org",
        "author_qualifications": (
            "Author A and Author B work across empirical ecology, ecological modelling "
            "and reproducible computational inference."
        ),
        "orcid_ids": [],
        "funding_notes": "",
        "coi_notes": "",
    }


def test_renderer_refuses_incomplete_human_metadata():
    metadata = complete_metadata()
    metadata["corresponding_email"] = ""
    try:
        MOD.render(metadata)
    except ValueError as exc:
        assert "corresponding_email" in str(exc)
    else:
        raise AssertionError("renderer should refuse incomplete metadata")


def test_renderer_preserves_author_order_and_fills_contact_fields():
    rendered = MOD.render(complete_metadata())
    assert "Proposed author list: Author A; Author B" in rendered
    assert "Author A\nDepartment A, University B\nInstitute C\nauthor@example.org" in rendered
    assert "Author A and Author B work across empirical ecology" in rendered
    assert "[Affiliation]" not in rendered
    assert "[Email]" not in rendered
    assert "[Insert final author-qualification sentence(s) here" not in rendered


def test_renderer_embeds_exact_current_pitch_and_attachment():
    rendered = MOD.render(complete_metadata())
    pitch_body = MOD._pitch_body()
    assert pitch_body in rendered
    assert "Proposal text — exact canonical 295-word body" in rendered
    assert "manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg" in rendered
    assert MOD.TITLE in rendered


def test_renderer_keeps_scientific_boundary_intact():
    rendered = MOD.render(complete_metadata())
    assert "12 independently held-out taxa" in rendered
    assert "283 evaluable procedure-by-area cells are repeated diagnostics" in rendered
    assert "Focal cross-role biological outcomes remain sealed" in rendered
    assert "Level C confirmed" not in rendered
    assert "Level C falsified" not in rendered
