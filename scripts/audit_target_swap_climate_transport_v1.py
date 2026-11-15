#!/usr/bin/env python3
"""Annotate cross-taxon swap cells with donor reference-FRAME climate overlap.

A proxy for extrapolation, not a proof of training-domain support.
Does NOT remove rows, retune q95, or change the 280/288 evaluation.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd

CLIM = [f"bio{i}" for i in range(1,20)]


def per_feature_overlap(target, donor) -> dict[str, float]:
    t, d = np.asarray(target,float), np.asarray(donor,float)
    if t.shape != (2000,19) or d.shape != (2000,19):
        raise ValueError("both frames must contain 2000 rows x 19 climate predictors")
    if not np.isfinite(t).all() or not np.isfinite(d).all():
        raise ValueError("missing or infinite climate predictor")
    lo=np.quantile(d,.01,axis=0)
    hi=np.quantile(d,.99,axis=0)
    cover=(t >= lo[None,:]) & (t <= hi[None,:])
    return {
        "mean_feature_coverage_1_99":float(cover.mean()),
        "fraction_rows_all19_covered_1_99":float(cover.all(axis=1).mean()),
        "fraction_rows_at_least15_features_covered_1_99":
            float((cover.sum(axis=1)>=15).mean()),
        "fraction_features_80pct_rows_covered_1_99":
            float((cover.mean(axis=0)>=.80).mean()),
    }


def evaluate(manifest_path:Path,root:Path,raw_cells:Path,out_json:Path,out_csv:Path):
    d=json.loads(manifest_path.read_text(encoding="utf-8"))
    assert d["schema"]=="284b.target_identity_controls_v1"
    names={e["taxon"]:e for e in d["entries"]}
    assert len(names)==12
    env={}
    for e in d["entries"]:
        zip_path=root/f"frame_{e['index']}.zip"
        if sha256(zip_path.read_bytes()).hexdigest()!=e["frame_artifact_digest"].split(":",1)[1]:
            raise RuntimeError("frame archive digest changed")
        z=zipfile.ZipFile(zip_path)
        receipt=json.loads(z.read("receipt.json"))
        assert receipt["taxon"]==e["taxon"]
        for m in (150,300,500):
            c=next(x for x in receipt["cells"] if int(x["M_km"])==m)
            raw=z.read(c["comparison_frame_file"])
            assert sha256(raw).hexdigest()==c["comparison_frame_sha256"]
            tab=pd.read_parquet(BytesIO(raw))
            env[(e["taxon"],m)]=tab[CLIM].to_numpy(float)
    overlaps={}
    for e in d["entries"]:
        t=e["taxon"]; donor=e["donor_taxon"]
        for m in (150,300,500):
            overlaps[(t,m)]=per_feature_overlap(env[(t,m)],env[(donor,m)])
    with raw_cells.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==288
    fields=list(rows[0])
    fields+=["mean_feature_coverage_1_99","fraction_rows_all19_covered_1_99",
             "fraction_rows_at_least15_features_covered_1_99",
             "fraction_features_80pct_rows_covered_1_99"]
    for r in rows:
        ov=overlaps[(r["target"],int(r["M_km"]))]
        r.update(ov)
    valid=[r for r in rows if r["state"]=="source_target_mismatch_constructed"]
    assert len(valid)==280
    flagged=[r for r in valid if r["matched_flag"]=="True"]
    missed=[r for r in valid if r["matched_flag"]=="False"]
    summary={
        "schema":"284b.target_swap_transport_proxy.v1",
        "status":"posthoc_descriptive_donor_comparison_frame_proxy_only",
        "taxa":12,"pair_m_pairs":36,"cells":288,"evaluable":280,
        "matched_flags":len(flagged),"not_flagged":len(missed),
        "all_evaluable_mean_feature_coverage":
            float(np.mean([float(r["mean_feature_coverage_1_99"]) for r in valid])),
        "flagged_mean_feature_coverage":
            float(np.mean([float(r["mean_feature_coverage_1_99"]) for r in flagged])),
        "not_flagged_mean_feature_coverage":
            float(np.mean([float(r["mean_feature_coverage_1_99"]) for r in missed])),
        "no_cell_removed_or_retuned":True,
        "empirical_ledger_increment":0,
        "interpretation":"Donor comparison-frame quantiles are an environmental-support proxy; they do not define true donor training support, causal ecological similarity, or out-of-sample generalization.",
        "per_target":[
            {"taxon":t,
             "mean_feature_coverage":float(np.mean([overlaps[(t,m)]["mean_feature_coverage_1_99"] for m in (150,300,500)])),
             "mean_rows_all19_covered":float(np.mean([overlaps[(t,m)]["fraction_rows_all19_covered_1_99"] for m in (150,300,500)]))}
            for t in names
        ]
    }
    out_json.parent.mkdir(parents=True,exist_ok=True)
    out_json.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    with out_csv.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(rows)
    print(json.dumps({k:summary[k] for k in ("evaluable","all_evaluable_mean_feature_coverage",
              "flagged_mean_feature_coverage","not_flagged_mean_feature_coverage")}))


def main():
    p=argparse.ArgumentParser()
    for name in ("manifest","root","cells","out-json","out-csv"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    evaluate(a.manifest,a.root,a.cells,a.out_json,a.out_csv)


if __name__=="__main__":
    main()
