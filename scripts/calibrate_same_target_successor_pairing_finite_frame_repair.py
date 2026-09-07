#!/usr/bin/env python3
"""Open only prospectively authorized repaired reference cells and freeze q95.

The input feasibility artifact must have been sealed before this script starts.
Prediction rows are materialized only for taxon x procedure x M cells whose two
repaired answers are sealed and adequate and whose procedure x M reference cell
had >=30 eligible taxa pre-discordance. Held-out outcomes remain closed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from product_b_v5.prediction_opening import read_authorized_prediction_cells
from product_b_v5.reference_calibration import freeze_reference_ceiling
from product_b_v5.same_target_pairing import evaluate_prediction_adequacy, schoener_d_if_both_answers_adequate

ROOT = Path(__file__).resolve().parents[1]
SAMPLING = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"
FIT_CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
PAIRING_CONTRACT = ROOT / "config/product_b_same_target_source_pairing_contract_v0_1.json"
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")
REPAIRED_RESULT = "product_b_same_target_successor_layer1_fit_taxon_finite_frame_repair_v0.1"
SEALED_STATE = "successor_layer1_model_fit_sealed_finite_frame_repair"
FEASIBILITY_VERSION = "product_b_same_target_successor_reference_feasibility_finite_frame_repair_v0.1"


def _read_csv_or_empty(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _adequacy_by_key(folds: pd.DataFrame, fit_contract: dict[str, object]) -> dict[tuple[str, int, str], object]:
    if folds.empty:
        return {}
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
        raise RuntimeError("repaired calibration fit inventory differs from frozen 47 taxa")
    return found


def _feasibility_map(payload: dict[str, object]) -> dict[tuple[int, str], dict[str, object]]:
    if payload.get("result_version") != FEASIBILITY_VERSION:
        raise RuntimeError("wrong repaired feasibility artifact version")
    if payload.get("paired_prediction_surfaces_read") is not False or payload.get("schoener_d_computed") is not False:
        raise RuntimeError("repaired feasibility artifact already crossed paired boundary")
    if payload.get("reference_ceiling_computed") is not False or payload.get("heldout_12_paired_discordance_read") is not False:
        raise RuntimeError("repaired feasibility artifact crossed reference/heldout boundary")
    out: dict[tuple[int, str], dict[str, object]] = {}
    for row in payload.get("reference_cells", []):
        key = (int(row["M_km"]), str(row["procedure"]))
        if key in out:
            raise RuntimeError("duplicate repaired feasibility reference cell")
        out[key] = dict(row)
    if len(out) != 24:
        raise RuntimeError("repaired feasibility matrix must contain 24 cells")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", required=True)
    ap.add_argument("--feasibility", required=True)
    ap.add_argument("--output-cells", required=True)
    ap.add_argument("--output-reference", required=True)
    ap.add_argument("--output-summary", required=True)
    args = ap.parse_args()

    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    fit_contract = json.loads(FIT_CONTRACT.read_text(encoding="utf-8"))
    pairing = json.loads(PAIRING_CONTRACT.read_text(encoding="utf-8"))
    feasibility_payload = json.loads(Path(args.feasibility).read_text(encoding="utf-8"))
    feasibility = _feasibility_map(feasibility_payload)
    expected_names = {
        str(r["requested_name"])
        for r in sampling.get("results", [])
        if r.get("state") == "successor_source_mode_sampling_passed"
    }
    if len(expected_names) != 47:
        raise RuntimeError("repaired calibration requires frozen 47 taxa")
    if int(pairing["reference_ceiling_rule"]["minimum_complete_calibration_taxa_per_procedure_M"]) != 30:
        raise RuntimeError("reference minimum drifted")
    if float(pairing["reference_ceiling_rule"]["quantile"]) != 0.95 or pairing["reference_ceiling_rule"]["quantile_method"] != "nearest_rank":
        raise RuntimeError("reference q95 rule drifted")

    cell_rows: list[dict[str, object]] = []
    loaded = _load(Path(args.input_root), expected_names)
    for contract, directory in loaded:
        if contract.get("all_prediction_scores_finite_by_contract") is not True:
            raise RuntimeError("repaired calibration received non-finite-contract surface")
        if contract.get("same_frozen_finite_background_rows_used_for_both_sources") is not True:
            raise RuntimeError("repaired calibration received asymmetric background")
        inventory = _read_csv_or_empty(directory / "fit_inventory.csv")
        folds = _read_csv_or_empty(directory / "outer_cv_fold_metrics.csv")
        adequacy = _adequacy_by_key(folds, fit_contract)
        taxon = str(contract["taxon"])
        procedures = sorted(str(x) for x in inventory["procedure"].dropna().unique())
        m_values = sorted(int(x) for x in inventory["M_km"].dropna().unique())
        materialize: set[tuple[int, str]] = set()
        prelim: list[dict[str, object]] = []
        for m_km in m_values:
            for procedure in procedures:
                gate = feasibility[(m_km, procedure)]
                inv = inventory[(inventory["M_km"].astype(int) == m_km) & (inventory["procedure"].astype(str) == procedure)]
                if len(inv) != 2:
                    raise RuntimeError("repaired calibration paired inventory incomplete")
                by_state = {str(r["source"]): str(r["state"]) for _, r in inv.iterrows()}
                both_sealed = set(by_state) == set(MODES) and all(by_state[m] == SEALED_STATE for m in MODES)
                qa = adequacy.get((MODES[0], m_km, procedure))
                qb = adequacy.get((MODES[1], m_km, procedure))
                a_ok = bool(qa is not None and qa.adequate)
                b_ok = bool(qb is not None and qb.adequate)
                eligible = bool(both_sealed and a_ok and b_ok)
                reference_open = bool(gate["discordance_opening_authorized"])
                allowed = bool(eligible and reference_open)
                if allowed:
                    materialize.add((m_km, procedure))
                reasons: list[str] = []
                if not reference_open: reasons.append("reference_unresolved_pre_discordance")
                if not both_sealed: reasons.append("one_or_both_repaired_final_fits_unresolved")
                if not a_ok: reasons.append("preserved_specimen_answer_inadequate_or_missing")
                if not b_ok: reasons.append("human_observation_answer_inadequate_or_missing")
                prelim.append({
                    "taxon": taxon,
                    "M_km": m_km,
                    "procedure": procedure,
                    "both_final_fits_sealed": both_sealed,
                    "preserved_specimen_adequate": a_ok,
                    "human_observation_adequate": b_ok,
                    "taxon_pre_discordance_eligible": eligible,
                    "reference_pre_discordance_opening_authorized": reference_open,
                    "prediction_materialization_authorized": allowed,
                    "pre_discordance_eligible_taxa_for_reference": int(gate["eligible_distinct_taxa_pre_discordance"]),
                    "reasons": reasons,
                })

        predictions = read_authorized_prediction_cells(directory / "sealed_prediction_surfaces.parquet", materialize)
        for row in prelim:
            key = (int(row["M_km"]), str(row["procedure"]))
            reasons = list(row.pop("reasons"))
            d = None
            comparison_rows = None
            if row["prediction_materialization_authorized"]:
                group = predictions[(predictions["taxon"].astype(str) == taxon) & (predictions["M_km"].astype(int) == key[0]) & (predictions["procedure"].astype(str) == key[1])]
                by_source = {str(src): frame.copy() for src, frame in group.groupby("source", sort=False)}
                if set(by_source) != set(MODES):
                    reasons.append("sealed_prediction_source_rows_missing")
                else:
                    a = by_source[MODES[0]]
                    b = by_source[MODES[1]]
                    qa = adequacy[(MODES[0], key[0], key[1])]
                    qb = adequacy[(MODES[1], key[0], key[1])]
                    try:
                        d = schoener_d_if_both_answers_adequate(
                            adequacy_a=qa,
                            adequacy_b=qb,
                            row_ids_a=a["comparison_row_id"].astype(str).tolist(),
                            scores_a=pd.to_numeric(a["ecological_score"], errors="coerce").tolist(),
                            row_ids_b=b["comparison_row_id"].astype(str).tolist(),
                            scores_b=pd.to_numeric(b["ecological_score"], errors="coerce").tolist(),
                        )
                        if d is None:
                            reasons.append("paired_surface_integrity_unresolved")
                        else:
                            comparison_rows = int(len(a))
                            if comparison_rows != 2000:
                                raise RuntimeError("repaired paired surface denominator is not 2000")
                    except Exception as exc:
                        d = None
                        reasons.append(f"paired_surface_integrity_error:{type(exc).__name__}:{str(exc)}")
            row.update({
                "paired_prediction_surface_opened": d is not None,
                "comparison_rows": comparison_rows,
                "schoener_d": None if d is None else float(d),
                "one_minus_schoener_d": None if d is None else float(1.0 - d),
                "calibration_contribution_authorized": d is not None,
                "state": "repaired_calibration_cell_observed" if d is not None else "repaired_calibration_cell_unresolved",
                "reasons": ";".join(dict.fromkeys(reasons)),
            })
            cell_rows.append(row)

    frame = pd.DataFrame(cell_rows).sort_values(["taxon", "M_km", "procedure"], kind="mergesort").reset_index(drop=True)
    if len(frame) != 47 * 24:
        raise RuntimeError("repaired calibration denominator incomplete")

    refs: list[dict[str, object]] = []
    for key in sorted(feasibility):
        m_km, procedure = key
        gate = feasibility[key]
        group = frame[(frame["M_km"].astype(int) == m_km) & (frame["procedure"].astype(str) == procedure)]
        opened = group[group["calibration_contribution_authorized"]]
        vals = pd.to_numeric(opened["one_minus_schoener_d"], errors="coerce").to_numpy(float)
        if len(vals) and not np.isfinite(vals).all():
            raise RuntimeError("repaired authorized discordance contains non-finite value")
        if not bool(gate["discordance_opening_authorized"]):
            if len(vals):
                raise RuntimeError("repaired discordance opened for unauthorized reference cell")
            refs.append({
                "M_km": m_km,
                "procedure": procedure,
                "pre_discordance_eligible_taxa": int(gate["eligible_distinct_taxa_pre_discordance"]),
                "pre_discordance_opening_authorized": False,
                "authorized_distinct_calibration_taxa": 0,
                "minimum_required_taxa": 30,
                "quantile": 0.95,
                "quantile_method": "nearest_rank",
                "nearest_rank_index_1_based": None,
                "one_minus_schoener_d_reference_ceiling": None,
                "reference_state": "reference_ceiling_unresolved",
            })
            continue
        decision = freeze_reference_ceiling(vals.tolist(), minimum_n=30, quantile=0.95)
        refs.append({
            "M_km": m_km,
            "procedure": procedure,
            "pre_discordance_eligible_taxa": int(gate["eligible_distinct_taxa_pre_discordance"]),
            "pre_discordance_opening_authorized": True,
            "authorized_distinct_calibration_taxa": int(decision.n),
            "minimum_required_taxa": 30,
            "quantile": 0.95,
            "quantile_method": "nearest_rank",
            "nearest_rank_index_1_based": decision.nearest_rank_index_1_based,
            "one_minus_schoener_d_reference_ceiling": decision.ceiling,
            "reference_state": decision.state,
        })

    reference = pd.DataFrame(refs).sort_values(["M_km", "procedure"], kind="mergesort").reset_index(drop=True)
    frozen = reference["reference_state"] == "reference_ceiling_frozen"
    Path(args.output_cells).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_cells, index=False)
    reference.to_csv(args.output_reference, index=False)
    summary = {
        "result_version": "product_b_same_target_successor_pairing_calibration_finite_frame_repair_v0.1",
        "sampling_pass_taxa_in_audit": 47,
        "paired_cells_expected": 1128,
        "paired_cells_audited": int(len(frame)),
        "pre_discordance_reference_cells_authorized": int(reference["pre_discordance_opening_authorized"].sum()),
        "paired_surfaces_opened_authorized_cells": int(frame["paired_prediction_surface_opened"].sum()),
        "paired_surfaces_kept_closed_cells": int((~frame["paired_prediction_surface_opened"]).sum()),
        "reference_cells_expected": 24,
        "reference_cells_frozen": int(frozen.sum()),
        "reference_cells_unresolved": int((~frozen).sum()),
        "full_reference_matrix_available": bool(frozen.all()),
        "minimum_distinct_calibration_taxa_per_reference_cell": 30,
        "reference_quantile": 0.95,
        "quantile_method": "nearest_rank",
        "heldout_12_paired_discordance_read": False,
        "process_knockout_opened": False,
        "procedure_selected_from_outcome": False,
        "M_selected_from_outcome": False,
        "taxa_replaced_after_outcome": False,
        "counts_as_empirical_conclusion": False,
        "claim_strength": "repaired_successor_reference_calibration_only_not_heldout_empirical_conclusion",
    }
    Path(args.output_summary).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
