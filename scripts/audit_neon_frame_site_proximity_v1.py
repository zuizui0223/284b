#!/usr/bin/env python3
"""Label-blind NEON site-centroid distance to signed Level-A comparison frames.

Not a species occurrence or plot outcome. No model fitting. No NEON plant data.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from io import BytesIO
import argparse
import csv
import json
import math
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG=ROOT/"config/neon_original_frame_site_distance_proxy_v1.json"
SITE_META=ROOT/"results/neon_site_geography_preflight_v1.json"
EARTH_KM=6371.009


def closest_haversine_km(site_lat:float, site_lon:float, coords:np.ndarray)->float:
    if coords.ndim!=2 or coords.shape[1]!=2 or not len(coords):
        raise ValueError("frame coords must contain latitude, longitude pairs")
    phi1=np.radians(site_lat)
    phi2=np.radians(coords[:,0])
    dphi=phi2-phi1
    dlambda=np.radians(coords[:,1]-site_lon)
    term=np.sin(dphi/2)**2+np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    term=np.clip(term,0,1)
    dist=2*EARTH_KM*np.arctan2(np.sqrt(term),np.sqrt(1-term))
    if not np.isfinite(dist).all():raise ValueError("non-finite site distances")
    return float(np.min(dist))


def evaluate(root:Path, output:Path, csv_path:Path)->dict:
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    sites=json.loads(SITE_META.read_text(encoding="utf-8"))
    if cfg["schema"]!="284b.neon_original_frame_site_distance_proxy.v1":
        raise RuntimeError("wrong spatial audit protocol")
    if sites["schema"]!="284b.neon_site_geography_preflight.v1":
        raise RuntimeError("NEON site metadata missing")
    if sites["state"]!="site_centroid_metadata_confirmed":
        raise RuntimeError("NEON site metadata unqualified")
    by_site=sites["site_centroid_reference"]
    if len(by_site)!=47:
        raise RuntimeError("NEON 47 sites not frozen")
    entries=cfg["historical_frozen_taxa"]
    if len(entries)!=7 or len({x["taxon"] for x in entries})!=7:
        raise RuntimeError("frozen seven taxa changed")
    cutoffs=cfg["distance_cutoffs_km"]
    assert cutoffs==[10,25,50,100]
    if cfg["primary_distance_cutoff_km"]!=25:
        raise RuntimeError("primary 25km proxy threshold changed")
    all_rows=[]
    summaries=[]
    for e in entries:
        p=root/f"frame_{e['original_index']}.zip"
        raw=p.read_bytes()
        if "sha256:"+sha256(raw).hexdigest()!=e["frame_artifact_digest"]:
            raise RuntimeError("signed original frame artifact SHA mismatch")
        with zipfile.ZipFile(BytesIO(raw)) as z:
            receipt=json.loads(z.read("receipt.json"))
            if receipt["taxon"]!=e["taxon"] or receipt["taxon_index"]!=e["original_index"]:
                raise RuntimeError("signed original frame taxon/index mismatch")
            if len(receipt["cells"])!=3:
                raise RuntimeError("missing original frozen M")
            for cell in receipt["cells"]:
                m=int(cell["M_km"])
                if m not in (150,300,500) or cell["state"]!="core19_comparison_frame_frozen":
                    raise RuntimeError("not a frozen core19 comparison frame")
                frame_bytes=z.read(cell["comparison_frame_file"])
                if sha256(frame_bytes).hexdigest()!=cell["comparison_frame_sha256"]:
                    raise RuntimeError("frozen parquet SHA mismatch")
                df=pd.read_parquet(BytesIO(frame_bytes))
                if len(df)!=2000 or df["comparison_row_id"].astype(str).duplicated().any():
                    raise RuntimeError("original comparison frame count/identity changed")
                xy=df[["latitude","longitude"]].to_numpy(float)
                if not np.isfinite(xy).all() or np.abs(xy[:,0]).max()>90 or np.abs(xy[:,1]).max()>180:
                    raise RuntimeError("invalid frame coordinates")
                for code,meta in sorted(by_site.items()):
                    d=closest_haversine_km(meta["siteLatitude"],meta["siteLongitude"],xy)
                    row={"taxon":e["taxon"],"original_index":e["original_index"],
                         "M_km":m,"siteCode":code,"distance_nearest_frame_km":d,
                         **{f"site_within_{int(k)}km_of_frame":d<=k for k in cutoffs}}
                    all_rows.append(row)
    if len(all_rows)!=7*3*47:
        raise RuntimeError("taxon × M × NEON site denominator changed")
    group=defaultdict(list)
    for x in all_rows:group[(x["taxon"],x["M_km"])].append(x)
    for (taxon,m),rr in sorted(group.items()):
        if len(rr)!=47:raise RuntimeError("unexpected site count")
        counts={str(k):sum(x[f"site_within_{k}km_of_frame"] for x in rr) for k in cutoffs}
        summaries.append({
           "taxon":taxon,"M_km":m,"NEON_sites_total":47,
           "nearest_site_dist_km":min(x["distance_nearest_frame_km"] for x in rr),
           "median_site_nearest_dist_km":float(np.median([x["distance_nearest_frame_km"] for x in rr])),
           "site_count_within_cutoffs_km":counts,
           "three_site_25km_heuristic_met":counts["25"]>=cfg["minimum_independent_NEON_sites_for_further_screen"]
        })
    # No taxon may be selected or dropped for a biological analysis using these
    # post-hoc site-location proxies. These are descriptive feasibility values.
    outcome={
      "schema":"284b.neon_original_frame_site_distance_proxy.v1",
      "status":"historical_frame_neon_centroid_proximity_proxy_only",
      "signed_frame_archives_verified":7,
      "original_frozen_M_per_taxon":3,
      "site_metadata_inventory_count":47,
      "taxon_M_site_rows":len(all_rows),
      "primary_distance_cutoff_km":25,
      "count_taxon_M_with_at_least_three_sites_within_25km":
            sum(x["three_site_25km_heuristic_met"] for x in summaries),
      "taxon_M_summary":summaries,
      "unresolved_actual_accessible_area":True,
      "unresolved_within_site_plant_plot_predictor_contrast":True,
      "NEON_species_outcomes_read":False,
      "NEON_plot_locations_read":False,
      "model_predictions_run":False,
      "external_validation_authorized":False,
      "empirical_ledger_increment":0,
      "limitations":[
       "Distances compare NEON site centroids to a sample of 2000 frozen source-blind background comparison rows, not to complete species accessible areas or training records",
       "No site-level taxon detection or complete survey availability was evaluated",
       "NEON site centroid is not an exact plot location and may be several km from some plots",
       "Closeness does not prove a model can discriminate detections or that its environmental predictor vectors differ",
       "Seven candidate taxa remain unchanged regardless of spatial support counts",
      ],
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(outcome,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    with csv_path.open("w",encoding="utf-8",newline="") as f:
        fields=list(all_rows[0])
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(all_rows,key=lambda x:(x["taxon"],x["M_km"],x["siteCode"])))
    print(json.dumps({"taxon_M_site_rows":outcome["taxon_M_site_rows"],
                      "taxon_M_3site_25km":outcome["count_taxon_M_with_at_least_three_sites_within_25km"]}))
    return outcome


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-dir",required=True,type=Path)
    ap.add_argument("--out-json",required=True,type=Path)
    ap.add_argument("--out-csv",required=True,type=Path)
    args=ap.parse_args()
    evaluate(args.artifact_dir,args.out_json,args.out_csv)


if __name__=="__main__":
    main()
