import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/"scripts"/"build_invited_m1_m2_figures.py"

def test_frozen_heldout_denominator():
    a=json.loads((ROOT/"results"/"reviewer2_level_a_structure_audit_v0_1.json").read_text())
    h=a["heldout_design"]
    assert (h["independent_heldout_taxa"],h["prespecified_cells"],h["evaluable_cells"],
            h["unresolved_cells"],h["taxa_with_any_ceiling_exceedance"]) == (12,288,283,5,0)

def test_exact_invalid_state_decomposition():
    x=json.loads((ROOT/"results"/"pre_field_state_dependent_invalidity_v0_2.json").read_text())
    p=x["representative_state_dependent_scenario"]["parameters"]
    z=x["representative_state_dependent_scenario"]["result"]
    assert abs((z["zero_false_violation_rate"]-z["gated_false_violation_rate"])-(1-p["a1"]))<1e-9
    assert abs((z["zero_true_violation_sensitivity"]-z["gated_true_violation_sensitivity"])-(1-p["a0"]))<1e-9

def test_figure_package_from_frozen_receipts(tmp_path):
    subprocess.run([sys.executable,str(RUNNER),"--output-dir",str(tmp_path)],
                   cwd=ROOT,check=True)
    for number in range(1,5):
        matches=list(tmp_path.glob(f"figure{number}_*.pdf"))
        assert len(matches)==1
        stem=matches[0].stem
        for suffix in (".pdf",".svg",".png"):
            p=tmp_path/(stem+suffix)
            assert p.exists() and p.stat().st_size>4000
    assert (tmp_path/"FIGURE_README.md").exists()


def test_figure4_population_prevalence_conditioning():
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_invited_m1_m2_figures import fdf_population
    equal = fdf_population(0.10, 0.80, 0.99)
    dependent = fdf_population(0.10, 0.80, 0.99, a1=0.70, a0=0.90)
    assert abs(equal - 0.6451612903225806) < 1e-12
    assert abs(dependent - (0.126 / 0.2151)) < 1e-12
    captions = (ROOT / "manuscript" /
                "ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_CAPTIONS_V1.md"
               ).read_text(encoding="utf-8")
    assert "π_all" in captions
    assert "π_valid" in captions
    assert "0.586" in captions
    assert "0.700" in captions


def test_repaired_signed_288_cell_matrix_and_reference_integrity():
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_invited_m1_m2_figures import frozen_sources, restored_sources
    historical, empirical, _ = frozen_sources()
    repaired, coverage, ratios = restored_sources(historical, empirical)
    assert repaired["paired_prediction_surfaces_opened_cells"] == 285
    assert repaired["paired_prediction_surfaces_kept_closed_cells"] == 3
    assert repaired["source_completeness_0_of_12_robust"] is False
    assert repaired["empirical_ledger_increment"] == 0
    assert (coverage["original_opened_retained"],
            coverage["original_opened_lost"],
            coverage["newly_opened_restored_cells"]) == (282, 1, 3)
    assert coverage["full_original_cell_coverage_preserved"] is False
    assert len(ratios) == 12 and all(0.0 < v < 1.0 for v in ratios.values())
    assert max(ratios, key=ratios.get) == "Eucalyptus globulus"
    assert abs(max(ratios.values()) - 0.9502954933291597) < 1e-12


def test_three_state_dependent_fdf_anchors():
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_invited_m1_m2_figures import fdf_population
    assert abs(fdf_population(.10,.80,.99,1,1) - .6451612903225806) < 1e-12
    assert abs(fdf_population(.10,.80,.99,.70,.90) - .5857740585774057) < 1e-12
    assert abs(fdf_population(.10,.80,.99,.90,.70) - .7003891050583658) < 1e-12
    assert fdf_population(.10,.80,.99,0.0,0.0) is None


def test_readme_discloses_nonindependent_source_version_sensitivity(tmp_path):
    subprocess.run([sys.executable,str(RUNNER),"--output-dir",str(tmp_path)],
                   cwd=ROOT,check=True)
    summary=(tmp_path/"FIGURE_README.md").read_text()
    for token in ("282", "283", "285", "0/12", "FALSE", "not independent"):
        assert token in summary
