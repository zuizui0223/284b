#!/usr/bin/env python3
"""Rebuild the invited M1+M2 Ecology Letters figures from frozen receipts only.

No GBIF, model fit, empirical endpoint opening, or candidate search is performed.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results" / "reviewer2_level_a_structure_audit_v0_1.json"
EMPIRICAL = ROOT / "results" / "product_b_same_target_core19_v0_4_heldout_final_receipt.json"
INVALIDITY = ROOT / "results" / "pre_field_state_dependent_invalidity_v0_2.json"
RESTORED = ROOT / "results" / "gbif_repaired_heldout12_sensitivity_v1.json"
COVERAGE = ROOT / "results" / "gbif_repaired_heldout12_postterminal_coverage_audit_v1.json"
RESTORED_CELLS = ROOT / "results" / "gbif_repaired_heldout12_sensitivity_cells_v1.csv"
REPAIRED_Q95 = ROOT / "results" / "gbif_repaired_reference47_q95_ceiling_v1.csv"

INK = "#233444"
BLUE = "#3267A0"
GOLD = "#C99037"
MUTED = "#647481"
GRID = "#DCE2E8"


def frozen_sources():
    audit = json.loads(AUDIT.read_text())
    empirical = json.loads(EMPIRICAL.read_text())
    invalid = json.loads(INVALIDITY.read_text())

    h = audit["heldout_design"]
    held = empirical["heldout"]
    ratios = audit["taxon_level_max_observed_to_ceiling_ratio"]
    assert h["independent_heldout_taxa"] == held["taxa"] == len(ratios) == 12
    assert h["prespecified_cells"] == held["cells_expected"] == 288
    assert h["evaluable_cells"] == held["paired_prediction_surfaces_opened_cells"] == 283
    assert h["unresolved_cells"] == held["paired_prediction_surfaces_kept_closed_cells"] == 5
    assert h["taxa_with_any_ceiling_exceedance"] == 0
    assert max(ratios.values()) < 1
    assert abs(max(ratios.values()) - 0.988232) < 1e-5

    c = empirical["heldout"]["closest_opened_cell"]
    assert c["taxon"] == "Nothofagus betuloides"
    assert abs(c["one_minus_schoener_d"] - c["frozen_reference_ceiling"]
               - c["discordance_minus_reference"]) < 1e-10
    assert invalid["general_result"]["false_violation_inflation"] == "1-a1"
    assert invalid["general_result"]["apparent_true_violation_sensitivity_gain"] == "1-a0"
    return audit, empirical, invalid


def restored_sources(audit, empirical):
    """Fail closed on exact restored-source 288-key agreement and q95 identity."""
    repaired = json.loads(RESTORED.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    with RESTORED_CELLS.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with REPAIRED_Q95.open(newline="", encoding="utf-8") as f:
        thresholds = list(csv.DictReader(f))
    q95 = {(int(x["M_km"]), x["procedure"]):
           float(x["one_minus_schoener_d_reference_ceiling"])
           for x in thresholds}
    assert len(thresholds) == len(q95) == 24
    assert all(int(x["authorized_distinct_calibration_taxa"]) >= 30 for x in thresholds)
    assert all(x["reference_state"] == "reference_ceiling_frozen" for x in thresholds)
    assert repaired["status"] == "repaired_source_no_attention_but_original_283_cell_coverage_decreased"
    assert repaired["submission_status"] == "HOLD_FOR_SENSITIVITY_REVIEW"
    assert repaired["empirical_ledger_increment"] == 0
    assert repaired["source_completeness_0_of_12_robust"] is False
    assert repaired["historical_endpoint_fingerprint"] == empirical["final_endpoint_fingerprint"]
    assert repaired["final_endpoint_fingerprint"] == coverage["restored_endpoint_fingerprint"]
    assert repaired["heldout_cells_expected"] == repaired["heldout_cells_audited"] == len(rows) == 288
    assert repaired["paired_prediction_surfaces_opened_cells"] == 285
    assert repaired["paired_prediction_surfaces_kept_closed_cells"] == 3
    assert repaired["repaired_heldout_taxa_with_attention"] == 0
    assert coverage["original_opened_retained"] == 282
    assert coverage["original_opened_lost"] == 1
    assert coverage["newly_opened_restored_cells"] == 3
    assert coverage["still_unresolved_restored_cells"] == 3
    assert repaired["historical_heldout_opened_cells"] == 283

    names = set(audit["taxon_level_max_observed_to_ceiling_ratio"])
    got_keys = set()
    per_taxon = {name: 0 for name in names}
    restored_ratios = {name: 0.0 for name in names}
    opened = 0
    unresolved = 0
    for row in rows:
        name = row["taxon"]
        key = (name, int(row["M_km"]), row["procedure"])
        ref_key = (key[1], key[2])
        assert name in names and ref_key in q95
        assert key not in got_keys
        got_keys.add(key)
        per_taxon[name] += 1
        assert row["both_final_fits_sealed"] == "True"
        assert row["reference_state"] == "reference_ceiling_frozen"
        assert math.isclose(float(row["frozen_reference_ceiling"]),
                            q95[ref_key], rel_tol=0, abs_tol=1e-12)
        if row["paired_prediction_surface_opened"] == "True":
            opened += 1
            assert row["paired_state"] == "paired_crosscheck_consistent"
            assert row["preserved_specimen_adequate"] == row["human_observation_adequate"] == "True"
            d = float(row["one_minus_schoener_d"])
            gap = float(row["discordance_minus_reference"])
            assert math.isfinite(d) and 0 <= d <= 1
            assert math.isclose(gap, d-q95[ref_key], rel_tol=0, abs_tol=1e-10)
            assert gap <= 0 and q95[ref_key] > 0
            restored_ratios[name] = max(restored_ratios[name], d/q95[ref_key])
        else:
            unresolved += 1
            assert row["paired_prediction_surface_opened"] == "False"
            assert row["paired_state"] == "paired_crosscheck_unresolved"
            assert not row["one_minus_schoener_d"] and not row["discordance_minus_reference"]
            assert row["preserved_specimen_adequate"] == "False" or row["human_observation_adequate"] == "False"

    assert len(got_keys) == 288 and set(per_taxon.values()) == {24}
    assert opened == 285 and unresolved == 3 and max(restored_ratios.values()) < 1
    assert len(coverage["transition_cells"]) == 4
    assert sum(x["transition"] == "original_open_lost" for x in coverage["transition_cells"]) == 1
    assert sum(x["transition"] == "restored_newly_open" for x in coverage["transition_cells"]) == 3
    assert 282+1 == 283 and 282+3 == 285 and 2+1 == 3 and 2+3 == 5
    return repaired, coverage, restored_ratios


def set_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelcolor": INK,
        "axes.edgecolor": MUTED,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })


def save(fig, path, dpi=300):
    for ext in ("pdf", "svg", "png"):
        fig.savefig(path.with_suffix("." + ext), dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def fig1_design(out):
    fig, ax = plt.subplots(figsize=(11.2, 3.2))
    ax.set(xlim=(0, 12), ylim=(0, 3.5))
    ax.axis("off")
    cards = [
        (0.15, "Independent records", "Preserved specimen\nHuman observation"),
        (3.25, "Source-specific models", "Same target, climate\nand comparison geometry"),
        (6.35, "Prospective reference", "24 frozen procedure ×\naccessible-area envelopes"),
        (9.45, "Held-out opening", "12 fresh taxa\nAdequate / unresolved"),
    ]
    for x, title, subtitle in cards:
        patch=FancyBboxPatch((x,1.05),2.4,1.6,
            boxstyle="round,pad=0.13,rounding_size=0.12",
            linewidth=1.1,edgecolor="#C1CCD7",facecolor="#F5F8FA")
        ax.add_patch(patch)
        ax.text(x+1.2,2.17,title,ha="center",va="center",fontsize=10.5,
                fontweight="bold")
        ax.text(x+1.2,1.55,subtitle,ha="center",va="center",fontsize=9.2,
                color=MUTED,linespacing=1.3)
    for x in (2.75,5.85,8.95):
        ax.add_patch(FancyArrowPatch((x,1.85),(x+0.37,1.85),
                     arrowstyle="-|>",mutation_scale=13,lw=1.6,color=BLUE))
    ax.text(6.0,3.12,"Figure 1  |  Same-target relation endpoint",
            ha="center",fontweight="bold",fontsize=13.0)
    ax.text(6.0,0.42,
        "No held-out taxon, procedure, area, or envelope selected after outcome opening",
        ha="center",va="center",fontsize=9.3,color=MUTED)
    save(fig,out/"figure1_design")


def fig2_level_a(out, audit, empirical, repaired, coverage, restored_ratios):
    """Figure 2: matched taxon panel with explicit evaluability transitions."""
    historical = audit["taxon_level_max_observed_to_ceiling_ratio"]
    names = sorted(historical, key=lambda n: historical[n], reverse=True)
    y = np.arange(len(names))
    original = np.asarray([historical[n] for n in names])
    restored = np.asarray([restored_ratios[n] for n in names])
    assert len(names) == 12 and np.max(original) < 1 and np.max(restored) < 1

    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=(11.5, 5.9),
        gridspec_kw={"width_ratios": [2.35, 1.2]},
    )
    for row_y, a, b in zip(y, original, restored):
        ax.plot([a, b], [row_y, row_y], color=GRID, lw=1.6, zorder=1)
    ax.scatter(original, y, s=64, color=BLUE, label="Original GBIF (historical)",
               marker="o", zorder=3)
    ax.scatter(restored, y, s=64, color=GOLD,
               label="Restored GBIF (retrospective)", marker="D", zorder=3)
    ax.axvline(1.0, color=INK, linestyle="--", lw=1.1)
    ax.set(xlim=(0.40, 1.05), ylim=(-0.65, len(names)-0.35),
           xlabel="Maximum discordance / own-source q95 reference")
    ax.set_yticks(y, [n.replace(" ", "\n", 1) for n in names])
    ax.invert_yaxis()
    ax.grid(axis="x", lw=0.7, color=GRID)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", frameon=False, fontsize=9.1)
    ax.set_title("A   Same 12 taxa, two source versions", loc="left",
                 fontsize=11, fontweight="bold", pad=12)
    ax.text(1.0, 0.01, "q95 ceiling", fontsize=9.0, ha="right",
            transform=ax.get_xaxis_transform(), color=MUTED)

    # exact 2x2 correspondence; descriptive, not independent replication
    matrix = np.array([
        [coverage["original_opened_retained"], coverage["original_opened_lost"]],
        [coverage["newly_opened_restored_cells"], 2],
    ], dtype=int)
    assert matrix.tolist() == [[282, 1], [3, 2]]
    colors = [[BLUE, "#F6E8D2"], ["#DEEAF3", "#E8EDF1"]]
    for r in range(2):
        for c in range(2):
            ax2.add_patch(Rectangle((c-.48, r-.48), .96, .96,
                                    facecolor=colors[r][c], edgecolor="white",
                                    linewidth=2, zorder=0))
            n = int(matrix[r, c])
            ax2.text(c, r-.10, str(n), va="center", ha="center",
                     fontweight="bold", fontsize=21,
                     color="white" if (r,c)==(0,0) else INK)
            annotation = {(0,0):"retained", (0,1):"lost",
                          (1,0):"newly eligible", (1,1):"still unresolved"}[(r,c)]
            ax2.text(c, r+.21, annotation, va="center", ha="center",
                     color="white" if (r,c)==(0,0) else INK, fontsize=9)
    ax2.set(xlim=(-.5,1.5), ylim=(1.5,-.5))
    ax2.set_xticks([0,1],["Evaluable\n(285)", "Unresolved\n(3)"])
    ax2.set_yticks([0,1],["Evaluable\n(283)", "Unresolved\n(5)"])
    ax2.xaxis.tick_top()
    ax2.tick_params(length=0, labelsize=9.4)
    ax2.set_title("B   Eligibility transitions (288 cells)", loc="left",
                  fontsize=11, fontweight="bold", pad=24)
    ax2.set_xlabel("Restored input", labelpad=10)
    ax2.set_ylabel("Original input", labelpad=6)

    fig.suptitle("Figure 2  |  Cross-source consistency after repairing GBIF completeness",
                 fontsize=13.0, fontweight="bold", x=.06, ha="left")
    fig.text(.065, .018,
             "No reference-envelope exceedance in either input arm (0/12 taxa); "
             "283/288 vs 285/288 evaluable. Original coverage retained only 282/283: "
             "strict full-retention robustness FAILED.\n"
             "Same taxa and procedures; repaired q95 was recalibrated independently. "
             "Dots are taxon maxima from repeated cells, not independent replications.",
             fontsize=8.7, color=MUTED, ha="left", linespacing=1.35)
    fig.subplots_adjust(left=.17, right=.98, top=.79, bottom=.18, wspace=.48)
    save(fig, out / "figure2_level_a")


def fig3_invalidity(out,invalid):
    scenario=invalid["representative_state_dependent_scenario"]
    p=scenario["parameters"]
    r=scenario["result"]
    a0=float(p["a0"]);a1=float(p["a1"])
    assert abs((r["zero_false_violation_rate"]-r["gated_false_violation_rate"])-(1-a1))<1e-10
    assert abs((r["zero_true_violation_sensitivity"]-r["gated_true_violation_sensitivity"])-(1-a0))<1e-10
    fig,(ax0,ax1,ax2)=plt.subplots(1,3,figsize=(11.6,3.9),gridspec_kw={"width_ratios":[1,1,1.35]})
    for ax,heading,items,delta in [
      (ax0,"False violations",[
        float(r["gated_false_violation_rate"]),float(r["zero_false_violation_rate"])],1-a1),
      (ax1,"True-violation sensitivity",[
        float(r["gated_true_violation_sensitivity"]),float(r["zero_true_violation_sensitivity"])],1-a0),
    ]:
        ax.bar([0,1],items,color=[BLUE,GOLD],width=0.56)
        ax.set_xticks([0,1],["Gate","Force 0"])
        ax.set_ylim(0,1.10)
        ax.set_title(heading,fontsize=10.5,pad=9)
        ax.yaxis.grid(True,color=GRID,lw=0.7)
        ax.set_axisbelow(True)
        for i,v in enumerate(items):
            ax.text(i,v+0.035,f"{v:.3f}",ha="center",fontsize=9)
        ax.text(0.5,1.04,f"Increment  +{delta:.2f}",
                ha="center",fontsize=9,fontweight="bold",transform=ax.transAxes)
    a=np.linspace(0,1,201)
    ax2.plot(a,1-a,color=BLUE,lw=2)
    ax2.scatter([a1,a0],[1-a1,1-a0],s=50,zorder=4,
                color=[GOLD,INK],edgecolor="white",linewidth=0.8)
    ax2.annotate(r"$1-a_1=0.30$",(a1,1-a1),xytext=(0.09,0.52),
                textcoords="axes fraction",fontsize=9,
                arrowprops={"arrowstyle":"-","color":GOLD})
    ax2.annotate(r"$1-a_0=0.10$",(a0,1-a0),xytext=(0.48,0.37),
                textcoords="axes fraction",fontsize=9,
                arrowprops={"arrowstyle":"-","color":INK})
    ax2.set(xlim=(0,1.02),ylim=(0,1.05),xlabel="Valid-key fraction  a",
            ylabel="Exact increment  1 − a")
    ax2.set_title("Class-specific invalid mass",fontsize=10.5,pad=9)
    ax2.grid(True,color=GRID,lw=0.7)
    fig.suptitle("Figure 3  |  The exact cost of treating invalid keys as biological zero",
                 x=0.06,ha="left",fontsize=13,fontweight="bold")
    fig.text(0.06,0.008,
        "State-dependent frozen example: a₁=0.70, a₀=0.90, q=0.95, specificity=0.99. "
        "The increments are analytic identities, not estimated causal effects.",
        fontsize=8.5,color=MUTED)
    fig.tight_layout(rect=[0,0.09,1,0.88],w_pad=2.7)
    save(fig,out/"figure3_invalidity")


from relation_endpoint_contract import qualified_violation_false_discovery_fraction


def fdf_population(pi, q, sp, a1=1.0, a0=1.0):
    """Qualified-call FDF with prevalence defined before validity filtering."""
    return qualified_violation_false_discovery_fraction(
        violation_prevalence=float(pi),
        valid_if_function_present=a1,
        valid_if_function_absent=a0,
        key_sensitivity=q,
        specificity=sp,
    )


def fig4_fdf(out):
    """Plot corrected qualified-call FDF at fixed unconditional prevalence."""
    q, sp, anchor = 0.80, 0.99, 0.10
    scenarios = [
        ("Equal validity (a₁ = a₀ > 0)", 1.0, 1.0, BLUE, "-"),
        ("Violation more valid (a₁=.70, a₀=.90)", .70, .90, GOLD, "--"),
        ("Compatible more valid (a₁=.90, a₀=.70)", .90, .70, INK, "-."),
    ]
    expected = [0.6451612903225806, 0.5857740585774057, 0.7003891050583658]
    fig, ax = plt.subplots(figsize=(9.9, 5.0))
    xs = np.linspace(.005, .80, 500)
    for (label, a1, a0, color, style), value in zip(scenarios, expected):
        f = fdf_population(anchor, q, sp, a1=a1, a0=a0)
        assert math.isclose(f, value, rel_tol=0, abs_tol=1e-12)
        ys = np.array([fdf_population(x, q, sp, a1=a1, a0=a0) for x in xs])
        ax.plot(xs, ys, color=color, lw=2.4, ls=style,
                label=f"{label} — FDF={f:.3f} at π=.10")
        ax.scatter([anchor], [f], marker="o", s=53, edgecolor="white",
                   color=color, linewidth=.7, zorder=4)

    ax.axvline(anchor, color=MUTED, lw=.9, ls=":")
    ax.set(xlim=(0,.80), ylim=(0,1.0),
           xlabel="Population prevalence of true violation, before validity gate (π_all)",
           ylabel="False discovery among issued qualified violation calls")
    ax.grid(color=GRID, lw=.7)
    ax.set_title("Figure 4  |  Conditional inference and state-dependent observability",
                 fontsize=13, fontweight="bold", loc="left", pad=16)
    ax.legend(frameon=False, fontsize=9.2, loc="upper right")
    fig.text(.13,.018,
        "Analytic illustration only: q=.80, sp=.99; a₁=P(valid|compatible), a₀=P(valid|violation). "
        "Equal-validity cancellation fails for a₁≠a₀.\n"
        "π_all is unconditional; the formula is undefined when no qualified violation calls can occur.",
        color=MUTED, fontsize=8.8, linespacing=1.45)
    fig.tight_layout(rect=[0,.095,1,1])
    save(fig, out / "figure4_fdf")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True,type=Path)
    args=parser.parse_args()
    audit,empirical,invalid=frozen_sources()
    repaired,coverage,restored_ratios=restored_sources(audit,empirical)
    out=args.output_dir
    out.mkdir(parents=True,exist_ok=True)
    set_style()
    fig1_design(out)
    fig2_level_a(out,audit,empirical,repaired,coverage,restored_ratios)
    fig3_invalidity(out,invalid)
    fig4_fdf(out)
    generated=sorted(p.name for p in out.iterdir() if p.is_file())
    assert len(generated)==12
    (out/"FIGURE_README.md").write_text(
       "# Invited Ecology Letters M1+M2 figure package\n\n"
       "Four figures (PDF/SVG/300-dpi PNG) are rebuilt from the original signed "
       "Level-A endpoint and the separately audited retrospective repaired-GBIF "
       "288-cell sensitivity, plus the independent 24 q95 reference cells and M1 mathematics.\n\n"
       "Original 283/288 versus restored 285/288 evaluable; only 282 of the original "
       "283 opened cells remained opened, so full-retention robustness is FALSE. "
       "Both arms had 0/12 taxa above their own reference envelopes; they are "
       "not independent biological replications.\n\n"
       "Figure 4 uses q=.80, sp=.99 and unconditional pi=.10 with equal validity, "
       "a1=.70/a0=.90 and a1=.90/a0=.70 as analytical illustrations only. "
       "The 288 diagnostics are within-taxon repeated settings, not independent "
       "biological replicates. Empirical nearest-rank q95 is not a nominal "
       "95% prediction interval.\n",
       encoding="utf-8"
    )
    print("\n".join(generated))

if __name__=="__main__":
    main()
