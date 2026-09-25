#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"incubator"/"frog_chorus_synchrony"
OUT=BASE/"figures"
OUT.mkdir(parents=True,exist_ok=True)

def read(name):
    return json.loads((BASE/name).read_text(encoding="utf-8"))

def text(x,y,s,size=26,weight="normal",anchor="start",italic=False):
    style=f"font-family:Arial,Helvetica,sans-serif;font-size:{size}px;font-weight:{weight};"
    if italic: style+="font-style:italic;"
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="{style}">{escape(str(s))}</text>'

def line(x1,y1,x2,y2,w=2,dash=None):
    extra=f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111" stroke-width="{w}"{extra}/>'

def rect(x,y,w,h,rx=18,fill="#fff",stroke="#111",sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def circle(cx,cy,r,fill="#111"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'

def fig1():
    el=[]
    el.append('<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="108mm" viewBox="0 0 1200 720">')
    el.append('<rect width="1200" height="720" fill="white"/>')
    el.append(text(60,55,"Figure 1. Independent acoustic systems test the same short-window co-calling prediction",30,"bold"))

    # NAAMP
    el.append(rect(55,100,500,235,24,"#f7f7f7"))
    el.append(text(80,140,"NAAMP — North America",28,"bold"))
    el.append(text(80,178,"Standardized 5-min route stops",22))
    el.append(text(80,210,"9,399 runs · 900 routes · 93,383 stops",20))
    el.append(rect(90,235,185,62,14,"#fff"))
    el.append(text(182,273,"recent rainfall",21,"bold","middle"))
    el.append(text(305,273,"→",34,"bold","middle"))
    el.append(rect(335,235,185,62,14,"#fff"))
    el.append(text(427,263,"≥2 calling species",19,"bold","middle"))
    el.append(text(427,286,"at a stop",18,"normal","middle"))

    # FrogID
    el.append(rect(645,100,500,235,24,"#f7f7f7"))
    el.append(text(670,140,"FrogID — Australia",28,"bold"))
    el.append(text(670,178,"Expert-validated short recordings",22))
    el.append(text(670,210,"40,754 recordings · 13,148 recorders",20))
    el.append(rect(680,235,185,62,14,"#fff"))
    el.append(text(772,273,"recent rainfall",21,"bold","middle"))
    el.append(text(895,273,"→",34,"bold","middle"))
    el.append(rect(925,225,185,82,14,"#fff"))
    el.append(text(1018,252,"1 vs ≥2 calling",18,"bold","middle"))
    el.append(text(1018,276,"species, conditional",17,"normal","middle"))
    el.append(text(1018,298,"on ≥1 already calling",17,"normal","middle"))

    # convergence
    el.append(line(305,335,305,405,3))
    el.append(line(895,335,895,405,3))
    el.append(line(305,405,600,455,3))
    el.append(line(895,405,600,455,3))
    el.append(rect(305,445,590,108,20,"#efefef",sw=3))
    el.append(text(600,482,"Cross-system directional claim",25,"bold","middle"))
    el.append(text(600,516,"More recent rainfall ↔ greater short-window multispecies co-calling",21,"normal","middle"))
    el.append(text(600,542,"No pooling of effect sizes",18,"normal","middle"))

    # robustness
    el.append(rect(120,585,390,70,16,"#fff"))
    el.append(text(315,614,"NAAMP robustness",20,"bold","middle"))
    el.append(text(315,642,"within the same route",19,"normal","middle"))
    el.append(rect(690,585,390,70,16,"#fff"))
    el.append(text(885,614,"FrogID robustness",20,"bold","middle"))
    el.append(text(885,642,"within the same ERA5 cell",19,"normal","middle"))
    el.append(line(510,620,690,620,2,"8 8"))
    el.append(text(600,697,"Association, not causation · no facilitation or network-rewiring inference",17,"normal","middle"))
    el.append('</svg>')
    return "\n".join(el)+"\n"

def mapx(v,lo,hi,x0,x1):
    return x0+(v-lo)/(hi-lo)*(x1-x0)

def fig2():
    naamp=read("NAAMP_PRIMARY_RECEIPT_V0_1.json")["primary"]
    frog=read("FROGID_VALIDATION_RECEIPT_V0_2.json")["primary"]
    rob=read("SPATIAL_CONFOUNDING_ROBUSTNESS_RECEIPT_V0_1.json")["artifacts"]
    el=[]
    el.append('<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="115mm" viewBox="0 0 1200 770">')
    el.append('<rect width="1200" height="770" fill="white"/>')
    el.append(text(60,52,"Figure 2. Rain-recency associations replicate and persist within spatial units",30,"bold"))

    # Panel A
    el.append(text(65,105,"A  Primary logistic associations",25,"bold"))
    x0,x1=360,1080; lo,hi=0.75,1.05
    yaxis=280
    el.append(line(x0,yaxis,x1,yaxis,2))
    for tick in [0.75,0.8,0.85,0.9,0.95,1.0,1.05]:
        x=mapx(tick,lo,hi,x0,x1)
        el.append(line(x,yaxis-7,x,yaxis+7,2))
        el.append(text(x,yaxis+34,f"{tick:.2f}",17,"normal","middle"))
    xn=mapx(1.0,lo,hi,x0,x1); el.append(line(xn,135,xn,270,2,"7 7"))
    rows=[
      ("NAAMP",naamp["odds_ratio_per_sd_log1p_days_since_rain"],naamp["ci95_or"][0],naamp["ci95_or"][1],165,"programme days since rain"),
      ("FrogID",frog["odds_ratio_per_sd_log1p_dry_days"],frog["ci95_or"][0],frog["ci95_or"][1],225,"ERA5 antecedent dry days"),
    ]
    for label,v,l,h,y,sub in rows:
        el.append(text(70,y+6,label,22,"bold"))
        el.append(text(165,y+6,sub,17))
        xl,xv,xh=mapx(l,lo,hi,x0,x1),mapx(v,lo,hi,x0,x1),mapx(h,lo,hi,x0,x1)
        el.append(line(xl,y,xh,y,5)); el.append(line(xl,y-9,xl,y+9,3)); el.append(line(xh,y-9,xh,y+9,3)); el.append(circle(xv,y,8))
        el.append(text(1090,y+6,f"{v:.3f}",18,"bold","end"))
    el.append(text(720,340,"Odds ratio per 1 SD increase in dryness",18,"normal","middle"))
    el.append(text(720,365,"Different exposure metrics; no pooled effect",16,"normal","middle"))

    # Panel B
    el.append(text(65,425,"B  Within-spatial-unit diagnostics",25,"bold"))
    x0,x1=360,1080; lo,hi=-0.06,0.02; yaxis=640
    el.append(line(x0,yaxis,x1,yaxis,2))
    for tick in [-0.06,-0.04,-0.02,0.0,0.02]:
        x=mapx(tick,lo,hi,x0,x1)
        el.append(line(x,yaxis-7,x,yaxis+7,2))
        el.append(text(x,yaxis+34,f"{tick:.2f}",17,"normal","middle"))
    xz=mapx(0.0,lo,hi,x0,x1); el.append(line(xz,455,xz,630,2,"7 7"))
    rows2=[
      ("NAAMP within route",rob["NAAMP"]["beta_rain_within_probability_scale"],rob["NAAMP"]["ci95_beta"][0],rob["NAAMP"]["ci95_beta"][1],505),
      ("FrogID within ERA5 cell",rob["FrogID"]["beta_dry_within_probability_scale"],rob["FrogID"]["ci95_beta"][0],rob["FrogID"]["ci95_beta"][1],570),
    ]
    for label,v,l,h,y in rows2:
        el.append(text(70,y+6,label,20,"bold"))
        xl,xv,xh=mapx(l,lo,hi,x0,x1),mapx(v,lo,hi,x0,x1),mapx(h,lo,hi,x0,x1)
        el.append(line(xl,y,xh,y,5)); el.append(line(xl,y-9,xl,y+9,3)); el.append(line(xh,y-9,xh,y+9,3)); el.append(circle(xv,y,8))
        el.append(text(1090,y+6,f"{v:.4f}",18,"bold","end"))
    el.append(text(720,700,"Within-unit probability-scale coefficient",18,"normal","middle"))
    el.append(text(600,748,"Both diagnostics negative with 95% CI excluding 0 · association, not causation",17,"normal","middle"))
    el.append('</svg>')
    return "\n".join(el)+"\n"

(OUT/"FIGURE_1_DESIGN_V0_1.svg").write_text(fig1(),encoding="utf-8")
(OUT/"FIGURE_2_EFFECTS_V0_1.svg").write_text(fig2(),encoding="utf-8")
print(OUT/"FIGURE_1_DESIGN_V0_1.svg")
print(OUT/"FIGURE_2_EFFECTS_V0_1.svg")
