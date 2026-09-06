#!/usr/bin/env python3
"""Audit successor reference feasibility before any paired prediction is opened.

This stage reads only fit contracts, fit inventories, and source-specific outer-CV
metrics. It deliberately does not read sealed prediction surfaces, compute
Schoener D, freeze q95 ceilings, inspect held-out paired outcomes, or run process
interventions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from product_b_v5.reference_feasibility import evaluate_reference_feasibility
from product_b_v5.same_target_pairing import evaluate_prediction_adequacy

ROOT = Path(__file__).resolve().parents[1]
SAMPLING = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"
FIT_CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
FEASIBILITY_CONTRACT = ROOT / "config/product_b_same_target_successor_reference_feasibility_contract_v0_1.json"
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")


def _read_csv_or_empty(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _adequacy_by_key(folds: pd.DataFrame, fit_contract: dict[str, object]) -> dict[tuple[str, int, str], object]:
    if folds.empty:
        return {}
    required = {"source", "M_km", "procedure", "fold", "presence_rank"}
    missing = required - set(folds.columns)
    if missing:
        raise RuntimeError(f"outer CV file missing columns: {sorted(missing)}")
    frozen = fit_contract["prediction_adequacy"]
    out: dict[tuple[str, int, str], object] = {}
    for (source, m_km, procedure), group in folds.groupby(["source", "M_km", "procedure"], sort=True):
        fold_ids = pd.to_numeric(group["fold"], errors="raise").astype(int)
        if fold_ids.duplicated().any():
            raise RuntimeError("duplicate outer-fold evidence within source/procedure/M")
        values = pd.to_numeric(group["presence_rank"], errors="coerce").to_numpy(float)
        out[(str(source), int(m_km), str(procedure))] = evaluate_prediction_adequacy(
            values,
            expected_folds=int(frozen["outer_folds"]),
            chance_auc=float(frozen["chance_auc"]),
            minimum_auc_margin=float(frozen["minimum_auc_margin"]),
            auc_sem_multiplier=float(frozen["auc_sem_multiplier"]),
        )
    return out


def _load_artifacts(root: Path, expected_names: set[str]) -> list[tuple[dict[str, object], Path]]:
    found: list[tuple[dict[str, object], Path]] = []
    for path in sorted(root.rglob("contract.json")):
        contract = json.loads(path.read_text(encoding="utf-8"))
        if contract.get("result_version") != "product_b_same_target_successor_layer1_fit_taxon_v0.1":
            continue
        found.append((contract, path.parent))
    taxa = [str(c["taxon"]) for c, _ in found]
    if len(found) != len(expected_names) or set(taxa) != expected_names or len(set(taxa)) != len(taxa):
        raise RuntimeError("fit artifact inventory differs from frozen sampling-pass taxa")
    return found


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input-root", required=True)
    p.add_argument("--fit-audit", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    fit_contract = json.loads(FIT_CONTRACT.read_text(encoding="utf-8"))
    feasibility_contract = json.loads(FEASIBILITY_CONTRACT.read_text(encoding="utf-8"))
    fit_audit = json.loads(Path(args.fit_audit).read_text(encoding="utf-8"))

    if fit_audit.get("paired_discordance_opened") is not False:
        raise RuntimeError("paired discordance was opened before feasibility audit")
    if fit_audit.get("process_knockout_opened") is not False:
        raise RuntimeError("process knockout was opened before feasibility audit")
    expected_names = {
        str(row["requested_name"])
        for row in sampling.get("results", [])
        if row.get("state") == "successor_source_mode_sampling_passed"
    }
    if len(expected_names) != int(sampling["source_mode_sampling_passed"]):
        raise RuntimeError("sampling-pass taxon count mismatch")
    minimum = int(feasibility_contract["minimum_eligible_taxa_per_procedure_M"])
    if minimum != 30:
        raise RuntimeError("reference feasibility minimum drifted")

    cell_rows: list[dict[str, object]] = []
    for contract, directory in _load_artifacts(Path(args.input_root), expected_names):
        if contract.get("prediction_surfaces_sealed") is not True:
            raise RuntimeError("prediction artifact not sealed")
        if contract.get("paired_discordance_computed") is not False or contract.get("process_knockout_computed") is not False:
            raise RuntimeError("fit artifact crossed pairing/process boundary")
        inventory = _read_csv_or_empty(directory / "fit_inventory.csv")
        folds = _read_csv_or_empty(directory / "outer_cv_fold_metrics.csv")
        adequacy = _adequacy_by_key(folds, fit_contract)
        required = {"source", "M_km", "procedure", "state"}
        if required - set(inventory.columns):
            raise RuntimeError("fit inventory missing required columns")
        if len(inventory) != int(contract["expected_fit_cells"]):
            raise RuntimeError("fit inventory does not contain every frozen source/procedure/M cell")
        taxon = str(contract["taxon"])
        procedures = sorted(str(x) for x in inventory["procedure"].dropna().unique())
        m_values = sorted(int(x) for x in inventory["M_km"].dropna().unique())
        if len(procedures) != 8 or m_values != [150, 300, 500]:
            raise RuntimeError("procedure/M universe drifted")
        for m_km in m_values:
            for procedure in procedures:
                inv = inventory[(inventory["M_km"].astype(int) == m_km) & (inventory["procedure"].astype(str) == procedure)]
                if len(inv) != 2:
                    raise RuntimeError("paired inventory does not contain exactly two source cells")
                by_state = {str(r["source"]): str(r["state"]) for _, r in inv.iterrows()}
                if set(by_state) != set(MODES):
                    raise RuntimeError("source-mode inventory drifted")
                both_sealed = all(by_state[m] == "successor_layer1_model_fit_sealed" for m in MODES)
                qa = adequacy.get((MODES[0], m_km, procedure))
                qb = adequacy.get((MODES[1], m_km, procedure))
                a_ok = bool(qa is not None and qa.adequate)
                b_ok = bool(qb is not None and qb.adequate)
                eligible = bool(both_sealed and a_ok and b_ok)
                reasons: list[str] = []
                if not both_sealed:
                    reasons.append("one_or_both_final_fits_unresolved")
                if not a_ok:
                    reasons.append("preserved_specimen_answer_inadequate_or_missing")
                if not b_ok:
                    reasons.append("human_observation_answer_inadequate_or_missing")
                cell_rows.append({
                    "taxon": taxon,
                    "M_km": int(m_km),
                    "procedure": procedure,
                    "both_final_fits_sealed": bool(both_sealed),
                    "preserved_specimen_adequate": a_ok,
                    "human_observation_adequate": b_ok,
                    "reference_contribution_eligible_pre_discordance": eligible,
                    "reasons": reasons,
                })

    frame = pd.DataFrame(cell_rows)
    if len(frame) != len(expected_names) * 24:
        raise RuntimeError("pre-discordance cell inventory incomplete")
    references: list[dict[str, object]] = []
    for (m_km, procedure), group in frame.groupby(["M_km", "procedure"], sort=True):
        eligible = int(group["reference_contribution_eligible_pre_discordance"].sum())
        decision = evaluate_reference_feasibility(eligible, minimum_required_taxa=minimum)
        references.append({
            "M_km": int(m_km),
            "procedure": str(procedure),
            "eligible_distinct_taxa_pre_discordance": decision.eligible_taxa,
            "minimum_required_taxa": decision.minimum_required_taxa,
            "discordance_opening_authorized": decision.discordance_opening_authorized,
            "state": decision.state,
        })
    if len(references) != 24:
        raise RuntimeError("reference feasibility matrix must contain 24 procedure/M cells")

    out = {
        "result_version": "product_b_same_target_successor_reference_feasibility_v0.1",
        "sampling_pass_taxa": len(expected_names),
        "candidate_pair_cells": int(len(frame)),
        "reference_cells_expected": 24,
        "reference_cells_authorized_to_open_discordance": int(sum(r["discordance_opening_authorized"] for r in references)),
        "reference_cells_unresolved_pre_discordance": int(sum(not r["discordance_opening_authorized"] for r in references)),
        "minimum_eligible_taxa_per_procedure_M": minimum,
        "reference_cells": references,
        "paired_prediction_surfaces_read": False,
        "schoener_d_computed": False,
        "reference_ceiling_computed": False,
        "heldout_12_paired_discordance_read": False,
        "process_knockout_opened": False,
        "procedure_or_M_selected_from_outcome": False,
        "taxa_replaced_after_outcome": False,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
