#!/usr/bin/env python3
"""Rebuild the invited M1+M2 Ecology Letters figures from frozen receipts only.

No GBIF, model fit, empirical endpoint opening, or candidate search is performed.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results" / "reviewer2_level_a_structure_audit_v0_1.json"
EMPIRICAL = ROOT / "results" / "product_b_same_target_core19_v0_4_heldout_final_receipt.json"
INVALIDITY = ROOT / "results" / "pre_field_state_dependent_invalidity_v0_2.json"

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


def fig2_level_a(out,audit,empirical):
    ratios=audit["taxon_level_max_observed_to_ceiling_ratio"]
    order=sorted(ratios,key=lambda k:ratios[k])
    fig,ax=plt.subplots(figsize=(9.1,5.9))
    vals=[ratios[k] for k in order]
    labels=[r"$\it{"+x.split()[0]+"}$ "+x.split()[1] for x in order]
    colors=[GOLD if x=="Nothofagus betuloides" else BLUE for x in order]
    bars=ax.barh(np.arange(len(order)),vals,height=0.7,color=colors)
    ax.set_yticks(np.arange(len(order)),labels)
    ax.set_xlim(0,1.16)
    ax.set_xlabel("Maximum evaluable discordance / frozen reference ceiling")
    ax.axvline(1.0,color=INK,lw=1.35,linestyle="--")
    ax.text(1.01,11.5,"Ceiling  =  1",fontsize=9,color=MUTED)
    ax.xaxis.grid(True,color=GRID,lw=0.7)
    ax.set_axisbelow(True)
    for bar,val in zip(bars,vals):
        ax.text(val+0.016,bar.get_y()+bar.get_height()/2,
                f"{val:.3f}",va="center",fontsize=8.8)
    ax.set_title("Figure 2  |  Prospective cross-source reproducibility",loc="left",
                 fontsize=13,fontweight="bold",pad=18)
    closest=empirical["heldout"]["closest_opened_cell"]
    fig.text(0.15,0.005,
        "12 independent held-out taxa  •  283/288 evaluable cells  •  5 unresolved  •  0/12 taxa exceed the frozen envelope\n"
        f"Closest observed discordance: {closest['one_minus_schoener_d']:.5f} "
        f"vs ceiling {closest['frozen_reference_ceiling']:.5f} "
        f"({closest['taxon']}, 150 km).  Cells are repeated sensitivity diagnostics, not independent replicates.",
        fontsize=8.9,color=MUTED,va="bottom",linespacing=1.5)
    fig.subplots_adjust(left=0.28,bottom=0.15,top=0.88)
    save(fig,out/"figure2_level_a")


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


def fdf(pi,q,sp):
    return (1-pi)*(1-q)/((1-pi)*(1-q)+pi*sp)


def fig4_fdf(out):
    # The frozen illustrative parameters in docs/evidence_boundary_structural_result.md.
    q,sp,anchor=0.8,0.99,0.1
    expect=0.645
    actual=fdf(anchor,q,sp)
    assert abs(actual-expect)<0.001
    xs=np.linspace(0.005,0.8,501)
    ys=fdf(xs,q,sp)
    fig,ax=plt.subplots(figsize=(8.5,4.4))
    ax.plot(xs,ys,lw=2.6,color=BLUE)
    ax.scatter([anchor],[actual],s=75,color=GOLD,zorder=4)
    ax.axvline(anchor,color=MUTED,linestyle=":",lw=1.0)
    ax.axhline(actual,color=MUTED,linestyle=":",lw=1.0)
    ax.annotate(f"π = 0.10   |   FDF ≈ {actual:.3f}",(anchor,actual),
                xytext=(0.31,0.80),textcoords="axes fraction",
                arrowprops={"arrowstyle":"->","color":MUTED},
                fontsize=10,fontweight="bold")
    ax.set(xlim=(0,0.8),ylim=(0,1.0),
           xlabel="Prevalence of true violations (π)",
           ylabel="False-discovery fraction among qualified calls")
    ax.set_title("Figure 4  |  Measurement qualification does not guarantee attribution",
                 loc="left",fontsize=13,fontweight="bold",pad=15)
    ax.grid(True,color=GRID,lw=0.75)
    fig.text(0.14,0.01,
       "Illustrative, not empirically estimated: valid-key sensitivity q = 0.80; specificity sp = 0.99. "
       "No nominal confidence interval is implied.",fontsize=8.7,color=MUTED)
    fig.tight_layout(rect=[0,0.06,1,1])
    save(fig,out/"figure4_fdf")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True,type=Path)
    args=parser.parse_args()
    audit,empirical,invalid=frozen_sources()
    out=args.output_dir
    out.mkdir(parents=True,exist_ok=True)
    set_style()
    fig1_design(out)
    fig2_level_a(out,audit,empirical)
    fig3_invalidity(out,invalid)
    fig4_fdf(out)
    generated=sorted(p.name for p in out.iterdir() if p.is_file())
    assert len(generated)==12
    (out/"FIGURE_README.md").write_text(
       "# Invited Ecology Letters M1+M2 figure package\n\n"
       "Four authored figures in PDF, SVG and 300-dpi PNG are derived from the "
       "frozen Level-A empirical receipt, Reviewer-2 structure audit and invalid-state "
       "mathematical audit. Figure 4 uses the previously documented illustrative "
       "FDF parameter scenario (q=.8, sp=.99, π=.1), not a real-world estimate.\n\n"
       "Independent biological n=12 taxa. The 283 evaluable cells are repeated "
       "sensitivity diagnostics, not independent replicates. The nearest-rank q95 "
       "reference envelope is not a nominal 95% predictive interval.\n",
       encoding="utf-8"
    )
    print("\n".join(generated))

if __name__=="__main__":
    main()
