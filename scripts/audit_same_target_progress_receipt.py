#!/usr/bin/env python3
"""Reproduce a partial fit/validation receipt without opening prediction members.

Diagnostic only: no new sampling rule, prediction gate, reference authorization,
model fitting, or candidate selection. A completion-order subset is not a panel
estimate. ZIP bytes are hashed; only the three allowlisted members are decoded.

Example (download each ZIP using its recorded artifact ID, without extracting):
  PYTHONPATH=. python scripts/audit_same_target_progress_receipt.py \
    --receipt results/product_b_same_target_successor_first4_progress_v0_1.json \
    --artifact-dir downloaded_zips --check
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
from zipfile import ZipFile

from product_b_v5.same_target_pairing import evaluate_prediction_adequacy

MEMBERS = ("contract.json", "fit_inventory.csv", "outer_cv_fold_metrics.csv")
CATEGORIES = ("answer_adequate", "final_fit_unresolved", "outer_fold_rows_incomplete",
              "validation_metric_nonfinite", "prediction_performance_below_floor")
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")
M_VALUES = (150, 300, 500)
PROCEDURES = tuple(f"{s}|{m}" for s in ("all", "vif", "predictive_forward", "niche_forward")
                   for m in ("logit_l2_C0.1_degree1", "logit_l2_C1_degree2"))


def summarize_archive(path: Path, receipt: dict, adequacy: dict) -> dict:
    """Validate an exact artifact and reuse the existing frozen adequacy helper."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != receipt["archive_sha256"]:
        raise ValueError("artifact archive SHA256 mismatch")
    with ZipFile(path) as archive:
        if any(archive.namelist().count(n) != 1 for n in MEMBERS):
            raise ValueError("missing or duplicate allowlisted artifact member")
        raw = {n: archive.read(n) for n in MEMBERS}
    contract = json.loads(raw["contract.json"])
    for flag in ("paired_discordance_computed", "process_knockout_computed", "reference_ceiling_read"):
        if contract.get(flag) is not False:
            raise ValueError(f"artifact crossed outcome boundary: {flag}")
    if contract.get("prediction_surfaces_sealed") is not True:
        raise ValueError("artifact is not sealed")
    if contract.get("result_version") != "product_b_same_target_successor_layer1_fit_taxon_v0.1":
        raise ValueError("wrong artifact type")
    if contract["taxon"] != receipt["taxon"] or int(contract["taxon_index"]) != receipt["taxon_index"]:
        raise ValueError("artifact taxon identity mismatch")
    if int(contract["expected_fit_cells"]) != 48:
        raise ValueError("artifact denominator mismatch")
    inv = list(csv.DictReader(io.StringIO(raw["fit_inventory.csv"].decode("utf-8"))))
    folds = list(csv.DictReader(io.StringIO(raw["outer_cv_fold_metrics.csv"].decode("utf-8"))))
    key = lambda r: (str(r["source"]), int(r["M_km"]), str(r["procedure"]))
    expected = set(itertools.product(MODES, M_VALUES, PROCEDURES))
    if len(inv) != 48 or {key(r) for r in inv} != expected:
        raise ValueError("fit inventory must contain exactly the frozen 48 cells")
    if any(r["taxon"] != contract["taxon"] for r in inv + folds):
        raise ValueError("cross-taxon inventory or validation evidence")
    grouped = defaultdict(list)
    for row in folds:
        if key(row) not in expected:
            raise ValueError("unexpected outer-fold source/procedure/M cell")
        grouped[key(row)].append(row)
    states = {}
    for row in inv:
        k = key(row)
        evidence = grouped[k]
        ids = [int(r["fold"]) for r in evidence]
        n_folds = int(adequacy["outer_folds"])
        if len(set(ids)) != len(ids) or not set(ids).issubset(range(n_folds)):
            raise ValueError("duplicate or out-of-range outer-fold identity")
        if row["state"] == "successor_layer1_model_fit_unresolved":
            state = "final_fit_unresolved"
        elif row["state"] != "successor_layer1_model_fit_sealed":
            raise ValueError("unexpected final-fit state")
        elif len(evidence) != n_folds:
            state = "outer_fold_rows_incomplete"
        else:
            values = [float(r["presence_rank"]) if r["presence_rank"] else math.nan for r in evidence]
            if not all(math.isfinite(v) for v in values):
                state = "validation_metric_nonfinite"
            else:
                qa = evaluate_prediction_adequacy(values, expected_folds=n_folds,
                    chance_auc=float(adequacy["chance_auc"]),
                    minimum_auc_margin=float(adequacy["minimum_auc_margin"]),
                    auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]))
                state = "answer_adequate" if qa.adequate else "prediction_performance_below_floor"
        states[k] = state
    counts = {c: sum(v == c for v in states.values()) for c in CATEGORIES}
    sealed = 48 - counts["final_fit_unresolved"]
    if sealed != int(contract["sealed_fit_cells"]) or counts["final_fit_unresolved"] != int(contract["unresolved_fit_cells"]):
        raise ValueError("fit receipt and inventory disagree")
    by_m = {str(m): sum(all(states[(s,m,p)] == "answer_adequate" for s in MODES)
                        for p in PROCEDURES) for m in M_VALUES}
    return {"taxon": contract["taxon"], "taxon_index": contract["taxon_index"],
            "expected_source_cells": 48, "sealed_source_cells": sealed,
            "source_cell_states": counts, "expected_pair_cells": 24,
            "pre_discordance_eligible_pairs": sum(by_m.values()),
            "pre_discordance_unresolved_pairs": 24 - sum(by_m.values()),
            "eligible_pairs_by_M_km": by_m,
            "decoded_member_sha256": {n: hashlib.sha256(raw[n]).hexdigest() for n in MEMBERS}}


def reproduce(receipt: dict, artifact_dir: Path) -> dict:
    artifacts = receipt["artifacts"]
    if not artifacts or len({a["taxon_index"] for a in artifacts}) != len(artifacts):
        raise ValueError("progress receipt has empty or duplicate taxon coverage")
    if len({a["artifact_id"] for a in artifacts}) != len(artifacts):
        raise ValueError("duplicate artifact IDs")
    total = int(receipt["expected_successor_taxa"])
    if len(artifacts) > total:
        raise ValueError("partial receipt exceeds panel denominator")
    summaries = [summarize_archive(artifact_dir / a["archive_filename"], a,
                 receipt["frozen_prediction_adequacy"]) for a in artifacts]
    states = Counter()
    for row in summaries: states.update(row["source_cell_states"])
    return {"taxa_audited": len(summaries), "taxa_not_audited_in_this_receipt": total-len(summaries),
            "source_cells_audited": 48*len(summaries),
            "source_cells_sealed": sum(r["sealed_source_cells"] for r in summaries),
            "source_cell_states": dict(states), "pair_cells_audited": 24*len(summaries),
            "pre_discordance_eligible_pairs": sum(r["pre_discordance_eligible_pairs"] for r in summaries),
            "pre_discordance_unresolved_pairs": sum(r["pre_discordance_unresolved_pairs"] for r in summaries),
            "prediction_members_decoded": [], "paired_discordance_computed": False,
            "reference_calibration_authorized_by_this_receipt": False,
            "taxa": summaries}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    observed = reproduce(receipt, args.artifact_dir)
    if args.check and observed != receipt["audit"]:
        raise RuntimeError("recomputed progress audit differs from committed receipt")
    print(json.dumps(observed, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
