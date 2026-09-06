#!/usr/bin/env python3
"""Calibrate procedure-by-M cross-source discordance ceilings on successor taxa.

This stage opens paired sealed prediction surfaces only when both final source
fits are sealed and both source-specific outer-CV answers pass the frozen
prediction-adequacy rule. It never substitutes taxa, tunes thresholds, reads the
current 12-taxon paired outcomes, or opens process knockouts. The successor panel
constructs reference ceilings; it is not itself labelled consistent/attention.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from product_b_v5.reference_calibration import freeze_reference_ceiling
from product_b_v5.same_target_pairing import evaluate_prediction_adequacy, schoener_d_if_both_answers_adequate

ROOT = Path(__file__).resolve().parents[1]
PAIRING_CONTRACT = ROOT / "config/product_b_same_target_source_pairing_contract_v0_1.json"
CALIBRATION_CONTRACT = ROOT / "config/product_b_same_target_successor_pairing_calibration_contract_v0_1.json"
FIT_CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
SAMPLING = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"
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
        if contract.get("result_version") != "product_b_same_target_successor_layer1_fit_taxon_v0.1":
            continue
        rows.append((contract, path.parent))
    taxa = [str(row[0]["taxon"]) for row in rows]
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
    result: dict[tuple[str, int, str], object] = {}
    for (source, m_km, procedure), group in folds.groupby(["source", "M_km", "procedure"], sort=True):
        fold_ids = pd.to_numeric(group["fold"], errors="raise").astype(int)
        if fold_ids.duplicated().any():
            raise RuntimeError("duplicate successor outer-fold evidence within source/procedure/M")
        values = pd.to_numeric(group["presence_rank"], errors="coerce").to_numpy(float)
        result[(str(source), int(m_km), str(procedure))] = evaluate_prediction_adequacy(
            values,
            expected_folds=int(frozen["outer_folds"]),
            chance_auc=float(frozen["chance_auc"]),
            minimum_auc_margin=float(frozen["minimum_auc_margin"]),
            auc_sem_multiplier=float(frozen["auc_sem_multiplier"]),
        )
    return result


def _pair_one_taxon(contract: dict[str, object], directory: Path, fit_contract: dict[str, object]) -> list[dict[str, object]]:
    if contract.get("prediction_surfaces_sealed") is not True:
        raise RuntimeError("successor prediction artifacts not sealed")
    if contract.get("paired_discordance_computed") is not False or contract.get("process_knockout_computed") is not False:
        raise RuntimeError("successor taxon crossed pairing/process boundary before calibration")
    if contract.get("historical_key_subset_selection_used") is not False:
        raise RuntimeError("successor taxon fit selected historical key subset")

    inventory = _read_csv_or_empty(directory / "fit_inventory.csv")
    predictions = pd.read_parquet(directory / "sealed_prediction_surfaces.parquet")
    folds = _read_csv_or_empty(directory / "outer_cv_fold_metrics.csv")
    required_inventory = {"source", "M_km", "procedure", "state"}
    if required_inventory - set(inventory.columns):
        raise RuntimeError("successor fit inventory missing required columns")
    if len(inventory) != int(contract["expected_fit_cells"]):
        raise RuntimeError("successor fit inventory does not contain every frozen source/procedure/M cell")

    adequacy = _adequacy_by_key(folds, fit_contract)
    taxon = str(contract["taxon"])
    procedures = sorted(str(x) for x in inventory["procedure"].dropna().unique())
    m_values = sorted(int(x) for x in inventory["M_km"].dropna().unique())
    if len(procedures) != 8 or m_values != [150, 300, 500]:
        raise RuntimeError("successor fit inventory procedure/M universe drifted")

    rows: list[dict[str, object]] = []
    for m_km in m_values:
        for procedure in procedures:
            inv = inventory[(inventory["M_km"].astype(int) == m_km) & (inventory["procedure"].astype(str) == procedure)]
            by_state = {str(r["source"]): str(r["state"]) for _, r in inv.iterrows()}
            if set(by_state) != set(MODES) or len(inv) != 2:
                raise RuntimeError("successor paired fit inventory does not contain exactly two source cells")
            both_sealed = all(by_state[m] == "successor_layer1_model_fit_sealed" for m in MODES)
            qa = adequacy.get((MODES[0], m_km, procedure))
            qb = adequacy.get((MODES[1], m_km, procedure))
            reasons: list[str] = []
            if not both_sealed:
                if by_state[MODES[0]] != "successor_layer1_model_fit_sealed":
                    reasons.append("preserved_specimen_final_fit_unresolved")
                if by_state[MODES[1]] != "successor_layer1_model_fit_sealed":
                    reasons.append("human_observation_final_fit_unresolved")
            if qa is None or not qa.adequate:
                reasons.append("preserved_specimen_answer_inadequate_or_missing")
            if qb is None or not qb.adequate:
                reasons.append("human_observation_answer_inadequate_or_missing")

            d = None
            comparison_rows = None
            if both_sealed and qa is not None and qb is not None and qa.adequate and qb.adequate:
                if predictions.empty:
                    reasons.append("sealed_prediction_rows_missing")
                else:
                    group = predictions[
                        (predictions["taxon"].astype(str) == taxon)
                        & (predictions["M_km"].astype(int) == m_km)
                        & (predictions["procedure"].astype(str) == procedure)
                    ]
                    by_source = {source: frame.copy() for source, frame in group.groupby("source", sort=False)}
                    if set(by_source) != set(MODES):
                        reasons.append("sealed_prediction_source_rows_missing")
                    else:
                        a = by_source[MODES[0]]
                        b = by_source[MODES[1]]
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
                        except Exception as exc:
                            reasons.append(f"paired_surface_integrity_error:{type(exc).__name__}")
                            d = None

            authorized = d is not None
            rows.append({
                "taxon": taxon,
                "M_km": int(m_km),
                "procedure": procedure,
                "both_final_fits_sealed": bool(both_sealed),
                "preserved_specimen_adequate": bool(qa is not None and qa.adequate),
                "human_observation_adequate": bool(qb is not None and qb.adequate),
                "paired_prediction_surface_opened": bool(authorized),
                "comparison_rows": comparison_rows,
                "schoener_d": None if d is None else float(d),
                "one_minus_schoener_d": None if d is None else float(1.0 - d),
                "calibration_contribution_authorized": bool(authorized),
                "state": "successor_calibration_cell_observed" if authorized else "successor_calibration_cell_unresolved",
                "reasons": ";".join(reasons),
            })
    return rows


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
    fit_audit = json.loads(Path(args.fit_audit).read_text(encoding="utf-8"))
    if fit_audit.get("paired_discordance_opened") is not False or fit_audit.get("process_knockout_opened") is not False:
        raise RuntimeError("successor aggregate indicates pairing/process already opened")
    expected_names = {
        str(row["requested_name"])
        for row in sampling.get("results", [])
        if row.get("state") == "successor_source_mode_sampling_passed"
    }
    if len(expected_names) != int(sampling["source_mode_sampling_passed"]) or len(expected_names) < 30:
        raise RuntimeError("successor calibration does not have frozen >=30 sampling-pass taxa")
    if int(calibration["minimum_distinct_calibration_taxa_per_reference_cell"]) != 30:
        raise RuntimeError("successor reference minimum drifted")
    if float(calibration["reference_quantile"]) != 0.95 or calibration["quantile_method"] != "nearest_rank":
        raise RuntimeError("successor reference quantile contract drifted")
    if int(pairing["reference_ceiling_rule"]["minimum_complete_calibration_taxa_per_procedure_M"]) != 30:
        raise RuntimeError("base pairing reference minimum drifted")

    artifacts = _load_taxon_artifacts(Path(args.input_root), expected_names)
    cells: list[dict[str, object]] = []
    for contract, directory in artifacts:
        cells.extend(_pair_one_taxon(contract, directory, fit_contract))
    frame = pd.DataFrame(cells).sort_values(["taxon", "M_km", "procedure"], kind="mergesort").reset_index(drop=True)
    expected_cells = len(expected_names) * 24
    if len(frame) != expected_cells:
        raise RuntimeError(f"expected {expected_cells} successor calibration pair cells, found {len(frame)}")

    reference_rows: list[dict[str, object]] = []
    for (m_km, procedure), group in frame.groupby(["M_km", "procedure"], sort=True):
        authorized = group[group["calibration_contribution_authorized"]].copy()
        vals = pd.to_numeric(authorized["one_minus_schoener_d"], errors="coerce").to_numpy(float)
        if len(vals) and not np.isfinite(vals).all():
            raise RuntimeError("authorized successor discordance contains non-finite value")
        decision = freeze_reference_ceiling(vals.tolist(), minimum_n=30, quantile=0.95)
        reference_rows.append({
            "M_km": int(m_km),
            "procedure": str(procedure),
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
        raise RuntimeError("successor reference matrix no longer contains 24 frozen procedure/M cells")
    available = reference["reference_state"] == "reference_ceiling_frozen"

    out_cells = Path(args.output_cells)
    out_cells.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out_cells, index=False)
    out_ref = Path(args.output_reference)
    out_ref.parent.mkdir(parents=True, exist_ok=True)
    reference.to_csv(out_ref, index=False)
    summary = {
        "result_version": "product_b_same_target_successor_pairing_calibration_v0.1",
        "sampling_pass_taxa_in_audit": len(expected_names),
        "paired_cells_expected": expected_cells,
        "paired_cells_audited": int(len(frame)),
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
        "claim_strength": "reference_calibration_only_not_confirmatory_biological_evidence",
    }
    out_summary = Path(args.output_summary)
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
