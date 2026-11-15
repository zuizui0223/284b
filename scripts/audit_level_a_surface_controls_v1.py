#!/usr/bin/env python3
"""Retrospective permutation stress of already-opened Level-A prediction surfaces.

This is a constructed score-alignment check, not a new biological endpoint.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd


def discordance(a, b) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.ndim != 1 or b.ndim != 1 or not len(a) or len(a) != len(b):
        raise ValueError("unmatched score vectors")
    if (not np.isfinite(a).all() or not np.isfinite(b).all()
            or (a < 0).any() or (b < 0).any() or a.sum() <= 0 or b.sum() <= 0):
        raise ValueError("scores must be finite, nonnegative and have positive total mass")
    return float(0.5 * np.abs(a/a.sum() - b/b.sum()).sum())


def antirank_maximum(a, b) -> float:
    """Largest discordance under permutations of b's existing score multiset."""
    return discordance(np.sort(a), np.sort(b)[::-1])


def evaluate(manifest_path: Path, heldout_csv: Path, artifact_dir: Path,
             out_json: Path, out_csv: Path, reps: int = 12) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest["heldout_taxon_artifacts"]
    assert len(entries) == 12 and 1 <= reps <= 40
    with heldout_csv.open(encoding="utf-8", newline="") as fh:
        source_rows = list(csv.DictReader(fh))
    assert len(source_rows) == 288
    opened = defaultdict(list)
    for row in source_rows:
        if row["paired_prediction_surface_opened"] == "True":
            assert row["paired_state"] == "paired_crosscheck_consistent"
            opened[row["taxon"]].append(row)
        else:
            assert row["paired_state"] == "paired_crosscheck_unresolved"
    assert len(opened) == 12 and sum(map(len, opened.values())) == 283

    computed = []
    for entry in sorted(entries, key=lambda v: v["name"]):
        archive = (artifact_dir / f"{entry['id']}.zip").read_bytes()
        assert hashlib.sha256(archive).hexdigest() == entry["digest"].split(":", 1)[1]
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            contract = json.loads(z.read("contract.json"))
            taxon = contract["taxon"]
            assert taxon in opened and contract["taxon_index"] in range(12)
            parquet = z.read("sealed_prediction_surfaces.parquet")
            assert hashlib.sha256(parquet).hexdigest() == contract["prediction_surface_sha256"]
            df = pd.read_parquet(io.BytesIO(parquet))
            assert len(df) == 96000
            required = {"taxon", "M_km", "procedure", "source", "comparison_row_id", "ecological_score"}
            assert required.issubset(df.columns) and (df["taxon"] == taxon).all()
            groups = {
                k: g.sort_values("comparison_row_id")
                for k, g in df.groupby(["M_km", "procedure", "source"])
            }
            assert len(groups) == 48
            for row in opened[taxon]:
                m, procedure = int(row["M_km"]), row["procedure"]
                a = groups[(m, procedure, "PRESERVED_SPECIMEN")]
                b = groups[(m, procedure, "HUMAN_OBSERVATION")]
                ids_a = a["comparison_row_id"].astype(str).tolist()
                ids_b = b["comparison_row_id"].astype(str).tolist()
                assert len(ids_a) == len(ids_b) == 2000
                assert ids_a == ids_b and len(set(ids_a)) == 2000
                pa = a["ecological_score"].to_numpy(float)
                pb = b["ecological_score"].to_numpy(float)
                d = discordance(pa, pb)
                assert abs(d - float(row["one_minus_schoener_d"])) < 1e-10
                ceiling = float(row["frozen_reference_ceiling"])
                assert d <= ceiling
                maximal = antirank_maximum(pa, pb)
                assert maximal + 1e-12 >= d
                shuffled = []
                for rep in range(reps):
                    token = f"{taxon}|{m}|{procedure}|perm{rep}".encode()
                    seed = int.from_bytes(hashlib.sha256(token).digest()[:8], "big")
                    order = np.random.default_rng(seed).permutation(len(pb))
                    ds = discordance(pa, pb[order])
                    assert ds <= maximal + 1e-10
                    shuffled.append(ds)
                computed.append({
                    "taxon": taxon, "M_km": m, "procedure": procedure,
                    "observed_distance": d, "frozen_ceiling": ceiling,
                    "max_reassignment_distance": maximal,
                    "random_shuffle_mean_distance": float(np.mean(shuffled)),
                    "random_shuffle_exceed_count": int(sum(x > ceiling for x in shuffled)),
                    "permutations": reps, "max_reassignment_exceeds": bool(maximal > ceiling),
                })

    assert len(computed) == 283 and len({x["taxon"] for x in computed}) == 12
    by_taxon = defaultdict(list)
    for row in computed:
        by_taxon[row["taxon"]].append(row)
    result = {
        "schema": "284b.level_a_score_alignment_stress_audit.v1",
        "status": "exploratory_constructed_negative_control_not_confirmatory",
        "artifact_ids": sorted(e["id"] for e in entries),
        "artifact_sha256_from_original_manifest_verified": True,
        "original_cells_reconstructed": len(computed),
        "original_taxa_reconstructed": len(by_taxon),
        "original_exceedance_cells": sum(x["observed_distance"] > x["frozen_ceiling"] for x in computed),
        "random_permutations_per_cell": reps,
        "random_shuffle_cell_replicates": len(computed) * reps,
        "random_shuffle_exceed_cell_replicates":
            sum(x["random_shuffle_exceed_count"] for x in computed),
        "cells_with_any_random_shuffle_exceedance":
            sum(x["random_shuffle_exceed_count"] > 0 for x in computed),
        "taxa_with_any_random_shuffle_exceedance":
            sum(any(x["random_shuffle_exceed_count"] > 0 for x in rows) for rows in by_taxon.values()),
        "antirank_cells_above_ceiling": sum(x["max_reassignment_exceeds"] for x in computed),
        "antirank_taxa_with_any_above_ceiling":
            sum(any(x["max_reassignment_exceeds"] for x in rows) for rows in by_taxon.values()),
        "antirank_cells_unable_to_exceed_ceiling_given_marginals":
            sum(not x["max_reassignment_exceeds"] for x in computed),
        "empirical_ledger_increment": 0,
        "limitations": [
            "Synthetic score permutation disrupts spatial matching; no biologically verified mismatch labels exist.",
            "Anti-rank controls are mathematical extremes under preserved score marginals, not realistic species differences.",
            "Permutations and procedure-by-area cells within each taxon are correlated, not independent species replicates.",
            "No nominal sensitivity, specificity, accuracy advantage, Level-C evidence, or causal mechanism is inferred.",
        ],
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(computed[0]))
        writer.writeheader()
        writer.writerows(sorted(computed, key=lambda x: (x["taxon"], x["M_km"], x["procedure"])))
    print(json.dumps({
        "reconstructed": result["original_cells_reconstructed"],
        "shuffle_exceed": result["random_shuffle_exceed_cell_replicates"],
        "antirank_above": result["antirank_cells_above_ceiling"],
    }))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--heldout", type=Path, required=True)
    p.add_argument("--artifact-dir", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    p.add_argument("--reps", type=int, default=12)
    a = p.parse_args()
    evaluate(a.manifest, a.heldout, a.artifact_dir, a.out_json, a.out_csv, a.reps)


if __name__ == "__main__":
    main()
