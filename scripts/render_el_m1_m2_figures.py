#!/usr/bin/env python3
"""Render Ecology Letters M1+M2 main figures from frozen repository evidence."""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"manuscript/generated/el_m1_m2_v1"
AUDIT=ROOT/"results/reviewer2_level_a_structure_audit_v0_1.json"
RECEIPT=ROOT/"results/product_b_same_target_core19_v0_4_heldout_final_receipt.json"
INVALID=ROOT/"results/pre_field_state_dependent_invalidity_v0_2.json"

def save(fig,name):
    OUT.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/f"{name}.pdf",bbox_inches="tight")
    fig.savefig(OUT/f"{name}.png",dpi=300,bbox_inches="tight")
    plt.close(fig)

def fig1():
    fig,axs=plt.subplots(2,2,figsize=(10,7))
    for ax in axs.ravel():
        ax.set_axis_off()
    # A
    ax=axs[0,0]
    ax.text(.5,.93,"A  Independent answers",ha="center",va="top",weight="bold",transform=ax.transAxes)
    for x,label in [(.22,"Source A\nanswer"),(.78,"Source B\nanswer")]:
        ax.text(x,.55,label,ha="center",va="center",
                bbox=dict(boxstyle="round,pad=.5",fc="white",ec="black"),transform=ax.transAxes)
    ax.annotate("",xy=(.43,.55),xytext=(.34,.55),arrowprops=dict(arrowstyle="->"),xycoords=ax.transAxes)
    ax.annotate("",xy=(.57,.55),xytext=(.66,.55),arrowprops=dict(arrowstyle="<-"),xycoords=ax.transAxes)
    ax.text(.5,.28,"No relation claim yet",ha="center",transform=ax.transAxes)

    # B
    ax=axs[0,1]
    ax.text(.5,.93,"B  Prospective relation endpoint",ha="center",va="top",weight="bold",transform=ax.transAxes)
    labels=["common key","answer adequacy","opening rule"]
    xs=[.18,.50,.82]
    for x,l in zip(xs,labels):
        ax.text(x,.55,l,ha="center",va="center",
                bbox=dict(boxstyle="round,pad=.4",fc="white",ec="black"),transform=ax.transAxes)
    for a,b in zip(xs[:-1],xs[1:]):
        ax.annotate("",xy=(b-.12,.55),xytext=(a+.12,.55),arrowprops=dict(arrowstyle="->"),xycoords=ax.transAxes)
    ax.text(.5,.24,"Frozen before focal opening",ha="center",transform=ax.transAxes)

    # C
    ax=axs[1,0]
    ax.text(.5,.93,"C  Soft comparison states",ha="center",va="top",weight="bold",transform=ax.transAxes)
    for y,label in [(.68,"consistent"),(.46,"attention"),(.24,"unresolved")]:
        ax.text(.5,y,label,ha="center",va="center",
                bbox=dict(boxstyle="round,pad=.45",fc="white",ec="black"),transform=ax.transAxes)
    ax.text(.5,.04,"Unresolved is a valid inferential state",ha="center",fontsize=9,transform=ax.transAxes)

    # D
    ax=axs[1,1]
    ax.text(.5,.93,"D  Hard-negative authorization",ha="center",va="top",weight="bold",transform=ax.transAxes)
    ax.text(.20,.58,"antecedent\npositive",ha="center",va="center",
            bbox=dict(boxstyle="round,pad=.4",fc="white",ec="black"),transform=ax.transAxes)
    ax.text(.50,.58,"same valid\nkey",ha="center",va="center",
            bbox=dict(boxstyle="round,pad=.4",fc="white",ec="black"),transform=ax.transAxes)
    ax.text(.80,.58,"identified\nnegative",ha="center",va="center",
            bbox=dict(boxstyle="round,pad=.4",fc="white",ec="black"),transform=ax.transAxes)
    for a,b in [(.32,.38),(.62,.68)]:
        ax.annotate("",xy=(b,.58),xytext=(a,.58),arrowprops=dict(arrowstyle="->"),xycoords=ax.transAxes)
    ax.text(.5,.24,"Only this chain can contradict the relation",ha="center",transform=ax.transAxes)
    fig.suptitle("Evidence-bounded relation endpoints",weight="bold")
    fig.tight_layout()
    save(fig,"figure_1_relation_endpoint")

def fig2():
    audit=json.loads(AUDIT.read_text())
    receipt=json.loads(RECEIPT.read_text())
    ratios=audit["taxon_level_max_observed_to_ceiling_ratio"]
    items=sorted(ratios.items(),key=lambda kv:kv[1])
    names=[x[0].replace(" ","\n",1) for x in items]
    vals=[x[1] for x in items]
    fig=plt.figure(figsize=(10,6.5))
    gs=fig.add_gridspec(1,2,width_ratios=[2.3,1])
    ax=fig.add_subplot(gs[0,0])
    y=np.arange(len(vals))
    ax.barh(y,vals)
    ax.axvline(1.0,linestyle="--",linewidth=1.5)
    ax.set_yticks(y,names,fontsize=8)
    ax.set_xlim(0,1.05)
    ax.set_xlabel("Maximum observed discordance / frozen envelope")
    ax.set_title("A  Held-out taxon-level closure",loc="left",weight="bold")
    ax.text(.99,len(vals)-.2,"frozen boundary",ha="right",va="bottom",fontsize=8)
    # closest cell annotation
    closest=receipt["heldout"]["closest_opened_cell"]
    ax.annotate(
        f"closest: {closest['one_minus_schoener_d']:.5f} / {closest['frozen_reference_ceiling']:.5f}",
        xy=(vals[-1],len(vals)-1),xytext=(.63,len(vals)-2.1),
        arrowprops=dict(arrowstyle="->"),fontsize=8
    )

    bx=fig.add_subplot(gs[0,1]); bx.set_axis_off()
    d=audit["heldout_design"]
    lines=[
      ("12","independent held-out taxa"),
      ("288","prespecified diagnostics"),
      ("283","evaluable diagnostics"),
      ("5","unresolved diagnostics"),
      ("0/12","taxa with envelope exceedance"),
    ]
    bx.text(0,.97,"B  Design accounting",va="top",weight="bold",transform=bx.transAxes)
    yy=.82
    for n,label in lines:
        bx.text(.02,yy,n,fontsize=20,weight="bold",transform=bx.transAxes)
        bx.text(.02,yy-.07,label,fontsize=9,transform=bx.transAxes)
        yy-=.17
    bx.text(.02,.06,"Biological replication = taxa,\nnot the 283 diagnostic cells.",fontsize=9,transform=bx.transAxes)
    fig.suptitle("Positive cross-source reproducibility on prospectively held-out taxa",weight="bold")
    fig.tight_layout()
    save(fig,"figure_2_level_a_heldout")

def fig3():
    inv=json.loads(INVALID.read_text())
    rep=inv["representative_state_dependent_scenario"]
    a=np.linspace(0,1,201)
    fig,axs=plt.subplots(2,2,figsize=(10,7))

    axs[0,0].plot(a,1-a)
    axs[0,0].set(xlabel=r"$a_1=P(valid\ key\mid F=true)$",ylabel="False-violation increment")
    axs[0,0].set_title(r"A  $FPR_{zero}-FPR_{gated}=1-a_1$",loc="left",weight="bold")

    axs[0,1].plot(a,1-a)
    axs[0,1].set(xlabel=r"$a_0=P(valid\ key\mid F=false)$",ylabel="Apparent sensitivity increment")
    axs[0,1].set_title(r"B  $TPR_{zero}-TPR_{gated}=1-a_0$",loc="left",weight="bold")

    axs[1,0].plot(a,1-a,label="both increments")
    axs[1,0].set(xlabel=r"equal validity $a_1=a_0=a$",ylabel="Increment")
    axs[1,0].set_title(r"C  Equal-validity corollary: $1-a$",loc="left",weight="bold")
    axs[1,0].legend(frameon=False)

    ax=axs[1,1]
    vals=rep["result"]
    labels=["False violation","True-violation\nsensitivity"]
    gated=[vals["gated_false_violation_rate"],vals["gated_true_violation_sensitivity"]]
    zero=[vals["zero_false_violation_rate"],vals["zero_true_violation_sensitivity"]]
    x=np.arange(2);w=.36
    ax.bar(x-w/2,gated,w,label="gated")
    ax.bar(x+w/2,zero,w,label="invalid → zero")
    ax.set_xticks(x,labels)
    ax.set_ylim(0,1.05)
    ax.set_ylabel("Rate")
    ax.set_title("D  Representative state-dependent case",loc="left",weight="bold")
    ax.legend(frameon=False,fontsize=8)
    ax.text(.02,.02,r"$a_1=.70,\ a_0=.90,\ q=.95,\ sp=.99$",transform=ax.transAxes,fontsize=8)

    fig.suptitle("Exact cost of deleting the unresolved state",weight="bold")
    fig.tight_layout()
    save(fig,"figure_3_invalid_state_cost")

def fdf(pi,q,sp):
    return (1-pi)*(1-q)/((1-pi)*(1-q)+pi*sp)

def fig4():
    pi=np.linspace(.01,.80,500)
    curves=[(.80,.99),(.90,.99),(.80,.95)]
    fig,ax=plt.subplots(figsize=(7.5,5.5))
    for q,sp in curves:
        ax.plot(pi,[fdf(x,q,sp) for x in pi],label=f"q={q:.2f}, sp={sp:.2f}")
    x=.10;y=fdf(x,.80,.99)
    ax.scatter([x],[y],s=40,zorder=4)
    ax.annotate(f"π=.10 → FDF={y:.3f}",xy=(x,y),xytext=(.22,.73),
                arrowprops=dict(arrowstyle="->"))
    ax.set(xlabel="True biological violation prevalence, π",
           ylabel="False-discovery fraction among called violations",
           ylim=(0,1),xlim=(.01,.80))
    ax.set_title("Observation qualification does not determine endpoint reliability",weight="bold")
    ax.legend(frameon=False)
    ax.grid(alpha=.2)
    fig.tight_layout()
    save(fig,"figure_4_fdf")

def main():
    fig1();fig2();fig3();fig4()
    files=sorted(p.name for p in OUT.iterdir())
    manifest={"schema":"284b.el_m1_m2_figures.v1","files":files,"figure_count":4,
              "source_files":[str(AUDIT.relative_to(ROOT)),str(RECEIPT.relative_to(ROOT)),str(INVALID.relative_to(ROOT))]}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":
    main()
