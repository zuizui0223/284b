#!/usr/bin/env python3
"""Strict successor reference calibration after pre-discordance authorization.

Only taxon×procedure×M cells that (a) have two sealed final source fits,
(b) pass both frozen source-specific prediction-adequacy gates, and (c) belong
to a procedure×M reference cell with >=30 such taxa are allowed to materialize
sealed prediction rows. All other prediction vectors remain unopened.
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
PAIRING_CONTRACT = ROOT / "config/product_b_same_target_source_pairing_contract_v0_1.json"
CALIBRATION_CONTRACT = ROOT / "config/product_b_same_target_successor_pairing_calibration_contract_v0_1.json"
FIT_CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
SAMPLING = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"
FEASIBILITY = ROOT / "results/product_b_same_target_successor_reference_feasibility_v0_1.json"
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")


def _read_csv_or_empty(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _load_taxon_artifacts(root: Path, expected_names: set[str]) -> list[tuple[dict[str, object], Path]]:
    rows: list[tuple[dict[str, object], Path]] = []
    for path in sorted(root.rglob("contract.json")):
        contract = json.loads(path.read_text(encoding="utf-8"))
        if contract.get("result_version") == "product_b_same_target_successor_layer1_fit_taxon_v0.1":
            rows.append((contract, path.parent))
    taxa = [str(c["taxon"]) for c, _ in rows]
    if len(rows) != len(expected_names) or set(taxa) != expected_names or len(set(taxa)) != len(taxa):
        raise RuntimeError("successor sealed artifact inventory differs from frozen sampling-pass taxa")
    return rows


def _adequacy_by_key(folds: pd.DataFrame, fit_contract: dict[str, object]) -> dict[tuple[str, int, str], object]:
    if folds.empty:
        return {}
    required = {"source", "M_km", "procedure", "fold", "presence_rank"}
    missing = required - set(folds.columns)
    if missing:
        raise RuntimeError(f"successor outer CV file missing columns: {sorted(missing)}")
    frozen = fit_contract["prediction_adequacy"]
    out: dict[tuple[str, int, str], object] = {}
    for (source, m_km, procedure), group in folds.groupby(["source", "M_km", "procedure"], sort=True):
        fold_ids = pd.to_numeric(group["fold"], errors="raise").astype(int)
        if fold_ids.duplicated().any():
            raise RuntimeError("duplicate successor outer-fold evidence")
        values = pd.to_numeric(group["presence_rank"], errors="coerce").to_numpy(float)
        out[(str(source), int(m_km), str(procedure))] = evaluate_prediction_adequacy(
            values,
            expected_folds=int(frozen["outer_folds"]),
            chance_auc=float(frozen["chance_auc"]),
            minimum_auc_margin=float(frozen["minimum_auc_margin"]),
            auc_sem_multiplier=float(frozen["auc_sem_multiplier"]),
        )
    return out


def _feasibility_map(payload: dict[str, object]) -> dict[tuple[int, str], dict[str, object]]:
    if payload.get("paired_prediction_surfaces_read") is not False or payload.get("schoener_d_computed") is not False:
        raise RuntimeError("pre-discordance feasibility artifact already crossed the prediction boundary")
    rows = payload.get("reference_cells", [])
    result: dict[tuple[int, str], dict[str, object]] = {}
    for row in rows:
        key = (int(row["M_km"]), str(row["procedure"]))
        if key in result:
            raise RuntimeError("duplicate pre-discordance reference cell")
        result[key] = dict(row)
    if len(result) != 24:
        raise RuntimeError("pre-discordance feasibility matrix must contain 24 procedure/M cells")
    return result


def _preaudit_taxon(
    contract: dict[str, object],
    directory: Path,
    fit_contract: dict[str, object],
    feasibility: dict[tuple[int, str], dict[str, object]],
) -> tuple[list[dict[str, object]], set[tuple[int, str]]]:
    if contract.get("prediction_surfaces_sealed") is not True:
        raise RuntimeError("successor prediction artifact not sealed")
    if contract.get("paired_discordance_computed") is not False or contract.get("process_knockout_computed") is not False:
        raise RuntimeError("successor taxon crossed pairing/process boundary")
    inventory = _read_csv_or_empty(directory / "fit_inventory.csv")
    folds = _read_csv_or_empty(directory / "outer_cv_fold_metrics.csv")
    if len(inventory) != int(contract["expected_fit_cells"]):
        raise RuntimeError("successor fit inventory missing frozen source/procedure/M cells")
    adequacy = _adequacy_by_key(folds, fit_contract)
    taxon = str(contract["taxon"])
    procedures = sorted(str(x) for x in inventory["procedure"].dropna().unique())
    m_values = sorted(int(x) for x in inventory["M_km"].dropna().unique())
    if len(procedures) != 8 or m_values != [150, 300, 500]:
        raise RuntimeError("successor procedure/M universe drifted")

    rows: list[dict[str, object]] = []
    materialize: set[tuple[int, str]] = set()
    for m_km in m_values:
        for procedure in procedures:
            key = (m_km, procedure)
            gate = feasibility[key]
            inv = inventory[(inventory["M_km"].astype(int) == m_km) & (inventory["procedure"].astype(str) == procedure)]
            if len(inv) != 2:
                raise RuntimeError("successor paired inventory must contain exactly two source cells")
            by_state = {str(r["source"]): str(r["state"]) for _, r in inv.iterrows()}
            if set(by_state) != set(MODES):
                raise RuntimeError("successor paired inventory source universe drifted")
            both_sealed = all(by_state[m] == "successor_layer1_model_fit_sealed" for m in MODES)
            qa = adequacy.get((MODES[0], m_km, procedure))
            qb = adequacy.get((MODES[1], m_km, procedure))
            a_ok = bool(qa is not None and qa.adequate)
            b_ok = bool(qb is not None and qb.adequate)
            taxon_eligible = bool(both_sealed and a_ok and b_ok)
            reference_open = bool(gate["discordance_opening_authorized"])
            opening_allowed = bool(taxon_eligible and reference_open)
            if opening_allowed:
                materialize.add(key)
            reasons: list[str] = []
            if not reference_open:
                reasons.append("reference_calibration_unresolved_pre_discordance")
            if not both_sealed:
                if by_state[MODES[0]] != "successor_layer1_model_fit_sealed":
                    reasons.append("preserved_specimen_final_fit_unresolved")
                if by_state[MODES[1]] != "successor_layer1_model_fit_sealed":
                    reasons.append("human_observation_final_fit_unresolved")
            if not a_ok:
                reasons.append("preserved_specimen_answer_inadequate_or_missing")
            if not b_ok:
                reasons.append("human_observation_answer_inadequate_or_missing")
            rows.append({
                "taxon": taxon,
                "M_km": int(m_km),
                "procedure": procedure,
                "both_final_fits_sealed": bool(both_sealed),
                "preserved_specimen_adequate": a_ok,
                "human_observation_adequate": b_ok,
                "taxon_pre_discordance_eligible": taxon_eligible,
                "reference_pre_discordance_opening_authorized": reference_open,
                "prediction_materialization_authorized": opening_allowed,
                "pre_discordance_eligible_taxa_for_reference": int(gate["eligible_distinct_taxa_pre_discordance"]),
                "reasons": reasons,
            })
    return rows, materialize


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--fit-audit", required=True)
    parser.add_argument("--output-cells", required=True)
    parser.add_argument("--output-reference", required=True)
    parser.add_argument("--output-summary", required=True)
    args = parser.parse_args()

    calibration = json.loads(CALIBRATION_CONTRACT.read_text(encoding="utf-8"))
    pairing = json.loads(PAIRING_CONTRACT.read_text(encoding="utf-8"))
    fit_contract = json.loads(FIT_CONTRACT.read_text(encoding="utf-8"))
    sampling = json.loads(SAMPLING.read_text(encoding="utf-8"))
    feasibility_payload = json.loads(FEASIBILITY.read_text(encoding="utf-8"))
    feasibility = _feasibility_map(feasibility_payload)
    fit_audit = json.loads(Path(args.fit_audit).read_text(encoding="utf-8"))
    if fit_audit.get("paired_discordance_opened") is not False or fit_audit.get("process_knockout_opened") is not False:
        raise RuntimeError("successor aggregate indicates pairing/process already opened")
    if fit_audit.get("prediction_surfaces_opened_for_pairing") is not False:
        raise RuntimeError("successor aggregate indicates predictions already opened for pairing")
    expected_names = {
        str(row["requested_name"])
        for row in sampling.get("results", [])
        if row.get("state") == "successor_source_mode_sampling_passed"
    }
    if len(expected_names) != int(sampling["source_mode_sampling_passed"]) or len(expected_names) < 30:
        raise RuntimeError("successor calibration lacks frozen >=30 sampling-pass taxa")
    if int(calibration["minimum_distinct_calibration_taxa_per_reference_cell"]) != 30:
        raise RuntimeError("successor reference minimum drifted")
    if float(calibration["reference_quantile"]) != 0.95 or calibration["quantile_method"] != "nearest_rank":
        raise RuntimeError("successor reference quantile contract drifted")
    if int(pairing["reference_ceiling_rule"]["minimum_complete_calibration_taxa_per_procedure_M"]) != 30:
        raise RuntimeError("base reference minimum drifted")

    cell_rows: list[dict[str, object]] = []
    for contract, directory in _load_taxon_artifacts(Path(args.input_root), expected_names):
        prelim, materialize = _preaudit_taxon(contract, directory, fit_contract, feasibility)
        predictions = read_authorized_prediction_cells(directory / "sealed_prediction_surfaces.parquet", materialize)
        taxon = str(contract["taxon"])
        for row in prelim:
            key = (int(row["M_km"]), str(row["procedure"]))
            d = None
            comparison_rows = None
            reasons = list(row.pop("reasons"))
            if row["prediction_materialization_authorized"]:
                group = predictions[
                    (predictions["taxon"].astype(str) == taxon)
                    & (predictions["M_km"].astype(int) == key[0])
                    & (predictions["procedure"].astype(str) == key[1])
                ]
                by_source = {source: frame.copy() for source, frame in group.groupby("source", sort=False)}
                if set(by_source) != set(MODES):
                    reasons.append("sealed_prediction_source_rows_missing")
                else:
                    a = by_source[MODES[0]]
                    b = by_source[MODES[1]]
                    try:
                        qa_values = _read_csv_or_empty(directory / "outer_cv_fold_metrics.csv")
                        adequacy = _adequacy_by_key(qa_values, fit_contract)
                        qa = adequacy[(MODES[0], key[0], key[1])]
                        qb = adequacy[(MODES[1], key[0], key[1])]
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
                    except Exception as exc:
                        d = None
                        reasons.append(f"paired_surface_integrity_error:{type(exc).__name__}")
            row.update({
                "paired_prediction_surface_opened": d is not None,
                "comparison_rows": comparison_rows,
                "schoener_d": None if d is None else float(d),
                "one_minus_schoener_d": None if d is None else float(1.0 - d),
                "calibration_contribution_authorized": d is not None,
                "state": "successor_calibration_cell_observed" if d is not None else "successor_calibration_cell_unresolved",
                "reasons": ";".join(dict.fromkeys(reasons)),
            })
            cell_rows.append(row)

    frame = pd.DataFrame(cell_rows).sort_values(["taxon", "M_km", "procedure"], kind="mergesort").reset_index(drop=True)
    expected_cells = len(expected_names) * 24
    if len(frame) != expected_cells:
        raise RuntimeError(f"expected {expected_cells} successor calibration pair cells, found {len(frame)}")

    reference_rows: list[dict[str, object]] = []
    for key in sorted(feasibility):
        m_km, procedure = key
        gate = feasibility[key]
        group = frame[(frame["M_km"].astype(int) == m_km) & (frame["procedure"].astype(str) == procedure)]
        opened = group[group["calibration_contribution_authorized"]]
        vals = pd.to_numeric(opened["one_minus_schoener_d"], errors="coerce").to_numpy(float)
        if len(vals) and not np.isfinite(vals).all():
            raise RuntimeError("authorized successor discordance contains non-finite value")
        pre_open = bool(gate["discordance_opening_authorized"])
        if not pre_open:
            if len(vals) != 0:
                raise RuntimeError("discordance was opened for a pre-discordance-unresolved reference cell")
            reference_rows.append({
                "M_km": int(m_km),
                "procedure": str(procedure),
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
        reference_rows.append({
            "M_km": int(m_km),
            "procedure": str(procedure),
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

    reference = pd.DataFrame(reference_rows).sort_values(["M_km", "procedure"], kind="mergesort").reset_index(drop=True)
    if len(reference) != 24:
        raise RuntimeError("strict successor reference matrix must contain 24 cells")
    available = reference["reference_state"] == "reference_ceiling_frozen"
    out_cells = Path(args.output_cells); out_cells.parent.mkdir(parents=True, exist_ok=True); frame.to_csv(out_cells, index=False)
    out_ref = Path(args.output_reference); out_ref.parent.mkdir(parents=True, exist_ok=True); reference.to_csv(out_ref, index=False)
    summary = {
        "result_version": "product_b_same_target_successor_pairing_calibration_v0.2_strict_opening",
        "sampling_pass_taxa_in_audit": len(expected_names),
        "paired_cells_expected": expected_cells,
        "paired_cells_audited": int(len(frame)),
        "pre_discordance_reference_cells_authorized": int(reference["pre_discordance_opening_authorized"].sum()),
        "pre_discordance_reference_cells_unresolved": int((~reference["pre_discordance_opening_authorized"]).sum()),
        "paired_surfaces_opened_authorized_cells": int(frame["paired_prediction_surface_opened"].sum()),
        "paired_surfaces_kept_closed_cells": int((~frame["paired_prediction_surface_opened"]).sum()),
        "reference_cells_expected": 24,
        "reference_cells_frozen": int(available.sum()),
        "reference_cells_unresolved": int((~available).sum()),
        "full_reference_matrix_available": bool(available.all()),
        "minimum_distinct_calibration_taxa_per_reference_cell": 30,
        "reference_quantile": 0.95,
        "quantile_method": "nearest_rank",
        "successor_consistent_labels_emitted": 0,
        "successor_attention_required_labels_emitted": 0,
        "current_12_taxon_paired_discordance_read": False,
        "process_knockout_opened": False,
        "procedure_selected_from_outcome": False,
        "M_selected_from_outcome": False,
        "taxa_replaced_after_outcome": False,
        "unauthorized_prediction_cells_materialized": 0,
        "claim_strength": "reference_calibration_only_not_confirmatory_biological_evidence",
    }
    out_summary = Path(args.output_summary); out_summary.parent.mkdir(parents=True, exist_ok=True)
    out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
