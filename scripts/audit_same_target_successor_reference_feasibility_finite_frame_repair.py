#!/usr/bin/env python3
"""Audit repaired successor reference feasibility before opening paired surfaces.

Reads only repaired fit contracts, fit inventories and source-specific outer-CV
metrics. It does not materialize sealed prediction surfaces, compute Schoener D,
freeze reference ceilings, read held-out paired outcomes or run process knockouts.
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
REPAIRED_RESULT = "product_b_same_target_successor_layer1_fit_taxon_finite_frame_repair_v0.1"
SEALED_STATE = "successor_layer1_model_fit_sealed_finite_frame_repair"


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
        raise RuntimeError(f"repaired outer CV file missing columns: {sorted(missing)}")
    frozen = fit_contract["prediction_adequacy"]
    out: dict[tuple[str, int, str], object] = {}
    for (source, m_km, procedure), group in folds.groupby(["source", "M_km", "procedure"], sort=True):
        fold_ids = pd.to_numeric(group["fold"], errors="raise").astype(int)
        if fold_ids.duplicated().any():
            raise RuntimeError("duplicate repaired outer-fold evidence")
        values = pd.to_numeric(group["presence_rank"], errors="coerce").to_numpy(float)
        out[(str(source), int(m_km), str(procedure))] = evaluate_prediction_adequacy(
            values,
            expected_folds=int(frozen["outer_folds"]),
            chance_auc=float(frozen["chance_auc"]),
            minimum_auc_margin=float(frozen["minimum_auc_margin"]),
            auc_sem_multiplier=float(frozen["auc_sem_multiplier"]),
        )
    return out


def _load(root: Path, expected_names: set[str]) -> list[tuple[dict[str, object], Path]]:
    found: list[tuple[dict[str, object], Path]] = []
    for p in sorted(root.rglob("contract.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        if c.get("result_version") == REPAIRED_RESULT:
            found.append((c, p.parent))
    names = [str(c["taxon"]) for c, _ in found]
    if len(found) != 47 or set(names) != expected_names or len(set(names)) != 47:
        raise RuntimeError("repaired fit artifact inventory differs from frozen 47 taxa")
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    fit_contract = json.loads(FIT_CONTRACT.read_text(encoding="utf-8"))
    feasibility_contract = json.loads(FEASIBILITY_CONTRACT.read_text(encoding="utf-8"))
    expected_names = {
        str(r["requested_name"])
        for r in sampling.get("results", [])
        if r.get("state") == "successor_source_mode_sampling_passed"
    }
    if len(expected_names) != 47 or int(sampling.get("source_mode_sampling_passed", -1)) != 47:
        raise RuntimeError("repaired feasibility requires frozen 47-taxon sampling-pass panel")
    minimum = int(feasibility_contract["minimum_eligible_taxa_per_procedure_M"])
    if minimum != 30:
        raise RuntimeError("reference feasibility minimum drifted")

    rows: list[dict[str, object]] = []
    for contract, directory in _load(Path(args.input_root), expected_names):
        if contract.get("prediction_surfaces_sealed") is not True:
            raise RuntimeError("repaired prediction surfaces are not sealed")
        if contract.get("all_prediction_scores_finite_by_contract") is not True:
            raise RuntimeError("repaired fit lacks all-finite score contract")
        for k in ("paired_discordance_computed", "reference_ceiling_read", "heldout_12_paired_discordance_read", "process_knockout_computed"):
            if contract.get(k) is not False:
                raise RuntimeError(f"repaired fit crossed information boundary: {k}")
        if contract.get("same_frozen_finite_background_rows_used_for_both_sources") is not True:
            raise RuntimeError("repaired fit did not use common finite frame")
        if contract.get("background_rows_resampled_during_refit") is not False or contract.get("posthoc_prediction_row_drop_used") is not False:
            raise RuntimeError("repaired fit changed frozen comparison rows")

        inventory = _read_csv_or_empty(directory / "fit_inventory.csv")
        folds = _read_csv_or_empty(directory / "outer_cv_fold_metrics.csv")
        if len(inventory) != 48:
            raise RuntimeError("repaired fit inventory must contain 48 source/procedure/M cells")
        adequacy = _adequacy_by_key(folds, fit_contract)
        procedures = sorted(str(x) for x in inventory["procedure"].dropna().unique())
        m_values = sorted(int(x) for x in inventory["M_km"].dropna().unique())
        if len(procedures) != 8 or m_values != [150, 300, 500]:
            raise RuntimeError("repaired procedure/M universe drifted")
        taxon = str(contract["taxon"])
        for m_km in m_values:
            for procedure in procedures:
                inv = inventory[(inventory["M_km"].astype(int) == m_km) & (inventory["procedure"].astype(str) == procedure)]
                if len(inv) != 2:
                    raise RuntimeError("repaired paired inventory must contain exactly two sources")
                by_state = {str(r["source"]): str(r["state"]) for _, r in inv.iterrows()}
                if set(by_state) != set(MODES):
                    raise RuntimeError("repaired source universe drifted")
                both_sealed = all(by_state[m] == SEALED_STATE for m in MODES)
                qa = adequacy.get((MODES[0], m_km, procedure))
                qb = adequacy.get((MODES[1], m_km, procedure))
                a_ok = bool(qa is not None and qa.adequate)
                b_ok = bool(qb is not None and qb.adequate)
                reasons: list[str] = []
                if not both_sealed: reasons.append("one_or_both_repaired_final_fits_unresolved")
                if not a_ok: reasons.append("preserved_specimen_answer_inadequate_or_missing")
                if not b_ok: reasons.append("human_observation_answer_inadequate_or_missing")
                rows.append({
                    "taxon": taxon,
                    "M_km": m_km,
                    "procedure": procedure,
                    "both_final_fits_sealed": both_sealed,
                    "preserved_specimen_adequate": a_ok,
                    "human_observation_adequate": b_ok,
                    "reference_contribution_eligible_pre_discordance": bool(both_sealed and a_ok and b_ok),
                    "reasons": ";".join(reasons),
                })

    frame = pd.DataFrame(rows)
    if len(frame) != 47 * 24:
        raise RuntimeError("repaired pre-D cell denominator incomplete")
    reference_cells: list[dict[str, object]] = []
    for (m_km, procedure), group in frame.groupby(["M_km", "procedure"], sort=True):
        eligible = int(group["reference_contribution_eligible_pre_discordance"].sum())
        decision = evaluate_reference_feasibility(eligible, minimum_required_taxa=minimum)
        reference_cells.append({
            "M_km": int(m_km),
            "procedure": str(procedure),
            "eligible_distinct_taxa_pre_discordance": int(decision.eligible_taxa),
            "minimum_required_taxa": int(decision.minimum_required_taxa),
            "discordance_opening_authorized": bool(decision.discordance_opening_authorized),
            "state": decision.state,
        })
    if len(reference_cells) != 24:
        raise RuntimeError("repaired reference feasibility matrix must contain 24 cells")

    out = {
        "result_version": "product_b_same_target_successor_reference_feasibility_finite_frame_repair_v0.1",
        "sampling_pass_taxa": 47,
        "candidate_pair_cells": int(len(frame)),
        "reference_cells_expected": 24,
        "reference_cells_authorized_to_open_discordance": int(sum(x["discordance_opening_authorized"] for x in reference_cells)),
        "reference_cells_unresolved_pre_discordance": int(sum(not x["discordance_opening_authorized"] for x in reference_cells)),
        "minimum_eligible_taxa_per_procedure_M": 30,
        "reference_cells": reference_cells,
        "paired_prediction_surfaces_read": False,
        "schoener_d_computed": False,
        "reference_ceiling_computed": False,
        "heldout_12_paired_discordance_read": False,
        "process_knockout_opened": False,
        "procedure_or_M_selected_from_outcome": False,
        "taxa_replaced_after_outcome": False,
        "counts_as_empirical_conclusion": False,
        "claim_strength": "repaired_reference_pre_discordance_feasibility_only",
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
