#!/usr/bin/env python3
"""Score fixed cross-taxon target-identity swaps on original, hashed CHELSA frames.

RETROSPECTIVE constructed negative controls on already-opened taxa.
Not a biological-process experiment, not a new Level-A endpoint, no new fitting.
No silently discarded score failures; all counts stay on a 12 x 24 denominator.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
from io import BytesIO
import csv
import json
import math
from pathlib import Path
import zipfile

import joblib
import numpy as np
import pandas as pd

CORE19 = tuple(f"bio{k}" for k in range(1, 20))
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")
MAX_REPRO_ERROR = 1e-10


def checksum(blob: bytes) -> str:
    return sha256(blob).hexdigest()


def discordance(a, b) -> float:
    x, y = np.asarray(a, float), np.asarray(b, float)
    if x.ndim != 1 or y.ndim != 1 or x.shape != y.shape or len(x) != 2000:
        raise ValueError("both source vectors must contain exactly 2,000 common rows")
    if (not np.isfinite(x).all() or not np.isfinite(y).all()
            or np.any(x < 0) or np.any(y < 0) or x.sum() <= 0 or y.sum() <= 0):
        raise ValueError("invalid suitability vector")
    return float(0.5 * np.abs(x / x.sum() - y / y.sum()).sum())


def read_csv(z: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    with z.open(name) as handle:
        import io
        return list(csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8")))


def get_bundle(entry: dict, root: Path):
    fit_path = root / f"fit_{entry['index']}.zip"
    frame_path = root / f"frame_{entry['index']}.zip"
    if checksum(fit_path.read_bytes()) != entry["fit_artifact_digest"].split(":", 1)[1]:
        raise RuntimeError(f"fit ZIP checksum changed: {entry['taxon']}")
    if checksum(frame_path.read_bytes()) != entry["frame_artifact_digest"].split(":", 1)[1]:
        raise RuntimeError(f"frame ZIP checksum changed: {entry['taxon']}")
    fit = zipfile.ZipFile(fit_path)
    frames = zipfile.ZipFile(frame_path)
    contract = json.loads(fit.read("contract.json"))
    receipt = json.loads(frames.read("receipt.json"))
    if contract["taxon"] != entry["taxon"] or contract["taxon_index"] != entry["index"]:
        raise RuntimeError("fit archive taxon/index drift")
    if receipt["taxon"] != entry["taxon"] or receipt["taxon_index"] != entry["index"]:
        raise RuntimeError("frame archive taxon/index drift")
    if contract["active_predictors"] != list(CORE19) or receipt["active_predictors"] != list(CORE19):
        raise RuntimeError("core19 predictor identity drift")
    pred_bytes = fit.read("sealed_prediction_surfaces.parquet")
    if checksum(pred_bytes) != contract["prediction_surface_sha256"]:
        raise RuntimeError("source prediction surface sha mismatch")
    pred = pd.read_parquet(BytesIO(pred_bytes))
    if len(pred) != 96000 or set(pred["source"]) != set(MODES):
        raise RuntimeError("unexpected original source surface size")
    fdata: dict[int, pd.DataFrame] = {}
    for v in receipt["cells"]:
        m = int(v["M_km"])
        raw = frames.read(v["comparison_frame_file"])
        if checksum(raw) != v["comparison_frame_sha256"]:
            raise RuntimeError(f"inner frame sha mismatch M={m}")
        if v["comparison_frame_sha256"] != contract["core19_frame_sha256_by_M"][str(m)]:
            raise RuntimeError("frame and model contract disagree")
        df = pd.read_parquet(BytesIO(raw))
        if len(df) != 2000 or df["comparison_row_id"].astype(str).duplicated().any():
            raise RuntimeError("comparison row count or uniqueness violation")
        if set(CORE19) - set(df) or not np.isfinite(df[list(CORE19)].to_numpy(float)).all():
            raise RuntimeError("comparison frame missing finite CHELSA variables")
        fdata[m] = df.sort_values("comparison_row_id").reset_index(drop=True)
    if set(fdata) != {150, 300, 500}:
        raise RuntimeError("missing frozen M")
    inventory = {(int(r["M_km"]),r["procedure"],r["source"]):r
                 for r in read_csv(fit,"fit_inventory.csv")}
    if len(inventory) != 48:
        raise RuntimeError("expected 48 model inventory cells")
    scores = {}
    for (m, proc, source), group in pred.groupby(["M_km", "procedure", "source"]):
        sub = group.sort_values("comparison_row_id").reset_index(drop=True)
        if sub["comparison_row_id"].astype(str).tolist() != fdata[int(m)]["comparison_row_id"].astype(str).tolist():
            raise RuntimeError("source predictions and finite frame have unequal row IDs")
        vec = sub["ecological_score"].to_numpy(float)
        if len(vec) != 2000 or not np.isfinite(vec).all():
            raise RuntimeError("source prediction vector shape or finite violation")
        scores[(int(m),proc,source)] = vec
    if len(scores) != 48:
        raise RuntimeError("source prediction inventory incomplete")
    return {"fit":fit,"frames":fdata,"inventory":inventory,"scores":scores,"contract":contract}


def model_scores(bundle: dict, m: int, proc: str, source: str, on_frame: pd.DataFrame):
    from sdmr.model import score_ecological_suitability
    row = bundle["inventory"][(m, proc, source)]
    if row["state"] != "core19_layer1_model_fit_sealed" or not row["model_file"]:
        raise RuntimeError(f"model not sealed: {bundle['contract']['taxon']}/{m}/{proc}/{source}")
    selected = row["selected_predictors"].split(",")
    if not selected or not set(selected).issubset(CORE19):
        raise RuntimeError("unrecognized model predictor")
    model_blob = bundle["fit"].read(row["model_file"])
    model = joblib.load(BytesIO(model_blob))
    scores = score_ecological_suitability(model, on_frame, selected, observation_predictors=())
    if len(scores) != 2000 or not np.isfinite(scores).all() or (scores < 0).any():
        raise RuntimeError("cross-frame model scores not finite and valid")
    return scores


def nearest_rank_q95(values):
    return sorted(values)[math.ceil(0.95*len(values))-1]


def evaluate(manifest_path: Path, root: Path, heldout_csv: Path, ref_csv: Path,
             out_json: Path, out_csv: Path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["schema"] != "284b.target_identity_controls_v1":
        raise RuntimeError("target-identity contract missing")
    entries = manifest["entries"]
    if len(entries) != 12 or {x["index"] for x in entries} != set(range(12)):
        raise RuntimeError("target inventory must be 12 indices")
    taxa = [x["taxon"] for x in sorted(entries, key=lambda x: x["index"])]
    if len(set(taxa)) != 12 or any(e["donor_taxon"] == e["taxon"] or taxa[e["donor_index"]] != e["donor_taxon"] for e in entries):
        raise RuntimeError("target/donor map not frozen or invalid")
    if checksum(heldout_csv.read_bytes()) != manifest["source_frozen_endpoint"]["source_cell_sha256"]:
        raise RuntimeError("frozen heldout cell CSV sha mismatch")
    with heldout_csv.open(newline="", encoding="utf-8") as f:
        h = list(csv.DictReader(f))
    assert len(h) == 288
    original = {(r["taxon"],int(r["M_km"]),r["procedure"]):r for r in h}
    if len(original) != 288:
        raise RuntimeError("duplicate original key")
    with ref_csv.open(newline="", encoding="utf-8") as f:
        rref = list(csv.DictReader(f))
    if checksum(ref_csv.read_bytes()) != manifest["reference_csv_sha256"]:
        raise RuntimeError("reference cell CSV SHA drift")
    vals = [float(x["one_minus_schoener_d"]) for x in rref if x["calibration_contribution_authorized"]=="True"]
    if len(vals) != 1024:
        raise RuntimeError("reference cells changed")
    pooled = nearest_rank_q95(vals)
    bundles = {e["taxon"]:get_bundle(e,root) for e in entries}
    verified_models = set()
    out = []
    for ent in sorted(entries,key=lambda x:x["index"]):
        target, donor = ent["taxon"], ent["donor_taxon"]
        target_bundle, donor_bundle = bundles[target], bundles[donor]
        keys = sorted((m,p) for name,m,p in original if name == target)
        if len(keys)!=24:
            raise RuntimeError("target has not 24 prespecified cells")
        for m,p in keys:
            t = original[(target,m,p)]
            b = original[(donor,m,p)]
            base = {"target":target,"donor":donor,"M_km":m,"procedure":p,
                    "target_key_matched":False,"original_target_evaluable":t["paired_prediction_surface_opened"]=="True",
                    "donor_human_adequate":b["human_observation_adequate"]=="True"}
            if not base["original_target_evaluable"] or not base["donor_human_adequate"]:
                out.append({**base,"state":"unresolved_by_prelabeled_adequacy",
                            "observed_same_discordance":"","cross_target_discordance":"",
                            "frozen_ceiling":"","matched_flag":"","pooled_flag":"","same_pooled_flag":""})
                continue
            if not bool(t["preserved_specimen_adequate"] == "True"):
                raise RuntimeError("source adequacy consistency error")
            tgt_frame = target_bundle["frames"][m]
            own_preserved = target_bundle["scores"][(m,p,"PRESERVED_SPECIMEN")]
            own_human = target_bundle["scores"][(m,p,"HUMAN_OBSERVATION")]
            original_dist = discordance(own_preserved, own_human)
            if not math.isclose(original_dist,float(t["one_minus_schoener_d"]),rel_tol=0,abs_tol=1e-10):
                raise RuntimeError("original within-target discordance not reproduced")
            donor_key = (donor,m,p)
            if donor_key not in verified_models:
                n_scores = model_scores(donor_bundle,m,p,"HUMAN_OBSERVATION",
                                        donor_bundle["frames"][m])
                stored = donor_bundle["scores"][(m,p,"HUMAN_OBSERVATION")]
                if np.max(np.abs(n_scores-stored)) > MAX_REPRO_ERROR:
                    raise RuntimeError(f"donor model cannot reproduce signed original surface: {donor}/{m}/{p}")
                verified_models.add(donor_key)
            borrowed_scores = model_scores(donor_bundle,m,p,"HUMAN_OBSERVATION",tgt_frame)
            wrong = discordance(own_preserved, borrowed_scores)
            ceiling = float(t["frozen_reference_ceiling"])
            out.append({**base,"state":"source_target_mismatch_constructed",
                        "observed_same_discordance":original_dist,
                        "cross_target_discordance":wrong,"frozen_ceiling":ceiling,
                        "matched_flag":wrong>ceiling,
                        "pooled_flag":wrong>pooled,
                        "same_pooled_flag":original_dist>pooled})
    assert len(out)==288
    evaluated=[r for r in out if r["state"]=="source_target_mismatch_constructed"]
    unevaluated=[r for r in out if r["state"]!="source_target_mismatch_constructed"]
    assert len(evaluated)+len(unevaluated)==288
    if len(evaluated)==0:
        raise RuntimeError("no known-label target-swap evaluation possible")
    bytarget=defaultdict(list)
    for row in evaluated:bytarget[row["target"]].append(row)
    taxon_summary=[]
    for taxon in taxa:
        xs=bytarget[taxon]
        taxon_summary.append({
            "taxon":taxon,"donor":next(e["donor_taxon"] for e in entries if e["taxon"]==taxon),
            "evaluable":len(xs),"unresolved":24-len(xs),
            "matched_flags":sum(x["matched_flag"] for x in xs),
            "pooled_flags":sum(x["pooled_flag"] for x in xs),
            "median_wrong_minus_same_distance":float(np.median([x["cross_target_discordance"]-x["observed_same_discordance"] for x in xs])) if xs else None,
        })
    result = {
        "schema":"284b.target_identity_controls_results_v1",
        "status":"exploratory_retrospective_constructed_identity_mismatch",
        "original_endpoint_unchanged":True,
        "original_288_cell_total":288,"computed_wrong_target_cells":len(evaluated),
        "unresolved_wrong_target_cells":len(unevaluated),
        "model_original_surface_reconstruction_verified":len(verified_models),
        "matched_flags_on_wrong_target":sum(x["matched_flag"] for x in evaluated),
        "pooled_flags_on_wrong_target":sum(x["pooled_flag"] for x in evaluated),
        "matched_taxa_with_any_wrong_target_flag":sum(x["matched_flags"]>0 for x in taxon_summary),
        "pooled_taxa_with_any_wrong_target_flag":sum(x["pooled_flags"]>0 for x in taxon_summary),
        "wrong_target_cells_below_same_target_distance":sum(x["cross_target_discordance"]<x["observed_same_discordance"] for x in evaluated),
        "pooled_q95":pooled,
        "taxon_summary":taxon_summary,
        "artifact_checksum_gates":True,
        "empirical_ledger_increment":0,
        "cannot_claim":["biological violation","true species niche difference","nominal sensitivity/specificity","causal inference","new independent test taxa","equal domain adequacy for donor models on target frame"],
    }
    out_json.parent.mkdir(parents=True,exist_ok=True)
    out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with out_csv.open("w",encoding="utf-8",newline="") as f:
        cols=list(out[0])
        writer=csv.DictWriter(f,fieldnames=cols)
        writer.writeheader(); writer.writerows(out)
    print(json.dumps({k:v for k,v in result.items() if k in [
        "computed_wrong_target_cells","unresolved_wrong_target_cells",
        "matched_flags_on_wrong_target","pooled_flags_on_wrong_target",
        "wrong_target_cells_below_same_target_distance"]}))


def main():
    p=argparse.ArgumentParser()
    for name in ("manifest","root","heldout","reference","out-json","out-csv"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    evaluate(args.manifest,args.root,args.heldout,args.reference,args.out_json,args.out_csv)


if __name__=="__main__":
    main()
