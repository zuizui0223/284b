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
