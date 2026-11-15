#!/usr/bin/env python3
"""Post-hoc, taxon-cluster-aware descriptive audit of target-identity controls.

Uses only archived, SHA-verified source outputs. Does not open new ecological
endpoint, reselect pairs, alter model predictions, or retune thresholds.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
from statistics import mean
import math

ROOT=Path(__file__).resolve().parents[1]
TARGETS=ROOT/"config/target_identity_controls_v1.json"
CELLS=ROOT/"results/target_identity_controls_v1/climate_transport_cells_v1.csv"
IDENTITY=ROOT/"results/target_identity_controls_v1/target_identity_results_v1.json"
CLIMATE=ROOT/"results/target_identity_controls_v1/climate_transport_proxy_v1.json"
EXPECTED_GIT_BLOBS={
    TARGETS:"026584e141e157e80adc81cbe68020fc53832dae",
    CELLS:"a0077b9ade7aa21af21e730ef655bc78731fffd9",
    IDENTITY:"2e142c78e374d947cdcf7fee74eeb77208bca02b",
    CLIMATE:"ac47ee9d70874a5120a5e8b89ef1f0acecb455ea",
}
MEAN_FEATURE_THRESHOLDS=(0.90,0.95,0.97,0.98,0.99)
ALL19_ROW_THRESHOLDS=(0.50,0.70,0.80,0.85,0.90)


def verify_git_blob(path:Path)->None:
    blob=path.read_bytes()
    payload=f"blob {len(blob)}\0".encode()+blob
    sha=hashlib.sha1(payload).hexdigest()
    if sha!=EXPECTED_GIT_BLOBS[path]:
        raise RuntimeError(f"frozen source blob SHA mismatch: {path}: {sha}")


def row_flag(text:str)->bool:
    if text not in ("True","False"):
        raise ValueError(f"Unexpected state {text!r}")
    return text=="True"


def correlation(pairs:list[tuple[float,float]])->float:
    if len(pairs)<3:raise ValueError("not enough units for descriptive correlation")
    x=[a for a,_ in pairs]; y=[b for _,b in pairs]
    cx,cy=mean(x),mean(y)
    cross=sum((a-cx)*(b-cy) for a,b in pairs)
    den=math.sqrt(sum((a-cx)**2 for a in x)*sum((b-cy)**2 for b in y))
    return cross/den if den else float("nan")


def aggregate(rows:list[dict])->dict:
    t={r["target"] for r in rows}
    flagged=sum(r["flag"] for r in rows)
    return {"cells":len(rows),"flagged":flagged,"silent":len(rows)-flagged,
            "target_taxa":len(t),
            "silence_fraction":(len(rows)-flagged)/len(rows) if rows else None}


def summarize()->dict:
    for f in EXPECTED_GIT_BLOBS:verify_git_blob(f)
    manifest=json.loads(TARGETS.read_text())
    identity=json.loads(IDENTITY.read_text())
    climate=json.loads(CLIMATE.read_text())
    assert manifest["schema"]=="284b.target_identity_controls_v1"
    assert identity["schema"]=="284b.target_identity_controls_results_v1"
    assert climate["schema"]=="284b.target_swap_transport_proxy.v1"
    with CELLS.open(encoding="utf-8",newline="") as f:raw=list(csv.DictReader(f))
    assert len(raw)==288
    assert len({(r["target"],r["M_km"],r["procedure"]) for r in raw})==288
    entries=manifest["entries"]
    taxa={r["taxon"]:r["donor_taxon"] for r in entries}
    if len(taxa)!=12: raise RuntimeError("wrong number of targets")
    rows=[]
    unresolved=0
    for r in raw:
        if taxa[r["target"]]!=r["donor"]:raise RuntimeError("wrong frozen donor")
        if r["state"]=="unresolved_by_prelabeled_adequacy":
            unresolved+=1
            continue
        if r["state"]!="source_target_mismatch_constructed":
            raise RuntimeError("unknown constructed-control state")
        x={"target":r["target"],"donor":r["donor"],"M":int(r["M_km"]),
           "flag":row_flag(r["matched_flag"]), "pooled_flag":row_flag(r["pooled_flag"]),
           "mean_coverage":float(r["mean_feature_coverage_1_99"]),
           "all19_coverage":float(r["fraction_rows_all19_covered_1_99"]),
           "same_distance":float(r["observed_same_discordance"]),
           "wrong_distance":float(r["cross_target_discordance"])}
        if not all(math.isfinite(v) for k,v in x.items() if isinstance(v,float)):
            raise RuntimeError("nonfinite environmental diagnostics")
        if not 0<=x["mean_coverage"]<=1 or not 0<=x["all19_coverage"]<=1:
            raise RuntimeError("climate coverage out of range")
        rows.append(x)
    assert len(rows)==identity["computed_wrong_target_cells"]==climate["evaluable"]==280
    assert unresolved==identity["unresolved_wrong_target_cells"]==8
    assert sum(r["flag"] for r in rows)==identity["matched_flags_on_wrong_target"]==165
    assert sum(r["pooled_flag"] for r in rows)==identity["pooled_flags_on_wrong_target"]==148

    by_taxon=defaultdict(list)
    by_target_m=defaultdict(list)
    for r in rows:
        by_taxon[r["target"]].append(r)
        by_target_m[(r["target"],r["M"])].append(r)
    assert len(by_taxon)==12 and len(by_target_m)==36
    for group in by_target_m.values():
        if max(z["mean_coverage"] for z in group)!=min(z["mean_coverage"] for z in group):
            raise RuntimeError("climate support should be constant within taxon×M")
    taxon_table=[]
    for taxon in sorted(by_taxon):
        g=by_taxon[taxon]
        taxon_table.append({
            "taxon":taxon,"donor":taxa[taxon],"evaluable":len(g),
            "flags":sum(z["flag"] for z in g),"silent":sum(not z["flag"] for z in g),
            "flag_fraction":mean(float(z["flag"]) for z in g),
            "mean_feature_coverage":mean(z["mean_coverage"] for z in g),
            "mean_all19_row_coverage":mean(z["all19_coverage"] for z in g),
        })
    group_table=[{"taxon":taxon,"M_km":m,"evaluable":len(g),
                  "flags":sum(z["flag"] for z in g),
                  "flag_fraction":mean(float(z["flag"]) for z in g),
                  "mean_feature_coverage":g[0]["mean_coverage"],
                  "all19_row_coverage":g[0]["all19_coverage"]}
                 for (taxon,m),g in sorted(by_target_m.items())]
    flagged=[r for r in rows if r["flag"]]
    silent=[r for r in rows if not r["flag"]]
    cflag=mean(z["mean_coverage"] for z in flagged)
    csilent=mean(z["mean_coverage"] for z in silent)
    assert math.isclose(cflag,climate["flagged_mean_feature_coverage"],abs_tol=1e-12)
    assert math.isclose(csilent,climate["not_flagged_mean_feature_coverage"],abs_tol=1e-12)
    mean_strata={f"{v:.2f}":aggregate([r for r in rows if r["mean_coverage"]>=v])
                 for v in MEAN_FEATURE_THRESHOLDS}
    full_strata={f"{v:.2f}":aggregate([r for r in rows if r["all19_coverage"]>=v])
                 for v in ALL19_ROW_THRESHOLDS}
    assert (mean_strata["0.95"]["cells"],mean_strata["0.95"]["silent"])==(180,104)
    assert (full_strata["0.80"]["cells"],full_strata["0.80"]["silent"])==(102,62)
    r12=correlation([(r["mean_feature_coverage"],r["flag_fraction"]) for r in taxon_table])
    r36=correlation([(r["mean_feature_coverage"],r["flag_fraction"]) for r in group_table])
    return {
        "schema":"284b.target_identity_climate_stratification_v1",
        "status":"retrospective_descriptive_and_posthoc_strata_not_confirmatory",
        "source_git_blobs":{str(p.relative_to(ROOT)):sha for p,sha in EXPECTED_GIT_BLOBS.items()},
        "empirical_ledger_increment":0,
        "overall":aggregate(rows),
        "unresolved":unresolved,
        "flagged_mean_feature_coverage":cflag,
        "silent_mean_feature_coverage":csilent,
        "mean_feature_support_minimum":mean_strata,
        "all19_row_support_minimum":full_strata,
        "correlation_12_taxa_descriptive_only":r12,
        "correlation_36_target_M_blocks_descriptive_only":r36,
        "taxon_table":taxon_table,
        "target_M_table":group_table,
        "limitations":[
          "Previously opened targets and post hoc overlap thresholds are not confirmatory.",
          "Donor comparison-frame quantiles are only a proxy for training support, and cannot rule out model extrapolation.",
          "A climate-support stratum changes species composition; differences across strata are not causal.",
          "12 taxon-level units; 36 taxon×M blocks and 280 procedure×M cells are correlated.",
          "A mismatch in source taxon name is a known metadata error, not a known ecological-process violation.",
          "No new Level-A endpoint or Level-C claim, no mechanism or method superiority.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    d=summarize()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:d[k] for k in ("overall","unresolved","mean_feature_support_minimum","all19_row_support_minimum","correlation_12_taxa_descriptive_only")}))


if __name__=="__main__":
    main()
