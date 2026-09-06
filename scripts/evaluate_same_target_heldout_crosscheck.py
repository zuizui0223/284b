#!/usr/bin/env python3
"""Evaluate the frozen 12-taxon held-out cross-source answer-check.

The successor reference table must already be committed and frozen. This stage
never changes calibration thresholds, procedures, M, or taxa. Paired prediction
vectors remain closed for any cell lacking two sealed final fits or two adequate
source answers. All 12×8×3 cells remain in the audit denominator.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from product_b_v5.heldout_crosscheck import classify_heldout_crosscheck
from product_b_v5.same_target_pairing import evaluate_prediction_adequacy, schoener_d_if_both_answers_adequate

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/product_b_same_target_heldout_crosscheck_contract_v0_1.json"
PAIRING_CONTRACT = ROOT / "config/product_b_same_target_source_pairing_contract_v0_1.json"
FIT_CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
REFERENCE_SUMMARY = ROOT / "results/product_b_same_target_successor_pairing_calibration_v0_1.json"
REFERENCE_TABLE = ROOT / "results/product_b_same_target_successor_reference_ceiling_v0_1.csv"
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")


def _read_csv_or_empty(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _load_taxon_artifacts(root: Path) -> list[tuple[dict[str, object], Path]]:
    rows: list[tuple[dict[str, object], Path]] = []
    for path in sorted(root.rglob("contract.json")):
        contract = json.loads(path.read_text(encoding="utf-8"))
        if contract.get("result_version") == "product_b_same_target_source_layer1_baseline_fit_taxon_v0.1":
            rows.append((contract, path.parent))
    names = [str(row[0]["taxon"]) for row in rows]
    if len(rows) != 12 or len(set(names)) != 12:
        raise RuntimeError("held-out artifact root must contain exactly the frozen 12 taxa")
    return rows


def _adequacy_by_key(folds: pd.DataFrame, fit_contract: dict[str, object]) -> dict[tuple[str, int, str], object]:
    if folds.empty:
        return {}
    required = {"source", "M_km", "procedure", "fold", "presence_rank"}
    missing = required - set(folds.columns)
    if missing:
        raise RuntimeError(f"held-out outer CV file missing columns: {sorted(missing)}")
    frozen = fit_contract["prediction_adequacy"]
    result: dict[tuple[str, int, str], object] = {}
    for (source, m_km, procedure), group in folds.groupby(["source", "M_km", "procedure"], sort=True):
        fold_ids = pd.to_numeric(group["fold"], errors="raise").astype(int)
        if fold_ids.duplicated().any():
            raise RuntimeError("duplicate held-out outer-fold evidence")
        values = pd.to_numeric(group["presence_rank"], errors="coerce").to_numpy(float)
        result[(str(source), int(m_km), str(procedure))] = evaluate_prediction_adequacy(
            values,
            expected_folds=int(frozen["outer_folds"]),
            chance_auc=float(frozen["chance_auc"]),
            minimum_auc_margin=float(frozen["minimum_auc_margin"]),
            auc_sem_multiplier=float(frozen["auc_sem_multiplier"]),
        )
    return result


def _reference_map(table: pd.DataFrame) -> dict[tuple[int, str], dict[str, object]]:
    required = {"M_km", "procedure", "reference_state", "one_minus_schoener_d_reference_ceiling"}
    if required - set(table.columns):
        raise RuntimeError("successor reference table missing required columns")
    if len(table) != 24:
        raise RuntimeError("successor reference table must contain 24 procedure×M cells")
    result: dict[tuple[int, str], dict[str, object]] = {}
    for _, row in table.iterrows():
        key = (int(row["M_km"]), str(row["procedure"]))
        if key in result:
            raise RuntimeError("duplicate successor reference procedure×M cell")
        raw = row["one_minus_schoener_d_reference_ceiling"]
        ceiling = None if pd.isna(raw) else float(raw)
        result[key] = {"state": str(row["reference_state"]), "ceiling": ceiling}
    if len(result) != 24:
        raise RuntimeError("successor reference procedure×M universe incomplete")
    return result


def _evaluate_taxon(
    contract: dict[str, object],
    directory: Path,
    fit_contract: dict[str, object],
    reference: dict[tuple[int, str], dict[str, object]],
) -> list[dict[str, object]]:
    if contract.get("prediction_surfaces_sealed") is not True:
        raise RuntimeError("held-out taxon prediction artifact not sealed")
    if contract.get("paired_discordance_computed") is not False or contract.get("process_knockout_computed") is not False:
        raise RuntimeError("held-out outcome/process was opened before frozen reference evaluation")
    inventory = _read_csv_or_empty(directory / "fit_inventory.csv")
    folds = _read_csv_or_empty(directory / "outer_cv_fold_metrics.csv")
    predictions = pd.read_parquet(directory / "sealed_prediction_surfaces.parquet")
    if len(inventory) != int(contract["expected_fit_cells"]):
        raise RuntimeError("held-out fit inventory missing frozen source/procedure/M cells")
    adequacy = _adequacy_by_key(folds, fit_contract)
    taxon = str(contract["taxon"])
    procedures = sorted(str(x) for x in inventory["procedure"].dropna().unique())
    m_values = sorted(int(x) for x in inventory["M_km"].dropna().unique())
    if len(procedures) != 8 or m_values != [150, 300, 500]:
        raise RuntimeError("held-out procedure/M universe drifted")

    rows: list[dict[str, object]] = []
    for m_km in m_values:
        for procedure in procedures:
            ref = reference[(m_km, procedure)]
            inv = inventory[(inventory["M_km"].astype(int) == m_km) & (inventory["procedure"].astype(str) == procedure)]
            by_state = {str(r["source"]): str(r["state"]) for _, r in inv.iterrows()}
            if set(by_state) != set(MODES) or len(inv) != 2:
                raise RuntimeError("held-out inventory cell lacks exactly two sources")
            both_sealed = all(by_state[m] == "layer1_model_fit_sealed" for m in MODES)
            qa = adequacy.get((MODES[0], m_km, procedure))
            qb = adequacy.get((MODES[1], m_km, procedure))
            both_adequate = bool(both_sealed and qa is not None and qb is not None and qa.adequate and qb.adequate)
            d = None
            comparison_rows = None
            integrity_reason = None
            if both_adequate:
                group = predictions[
                    (predictions["taxon"].astype(str) == taxon)
                    & (predictions["M_km"].astype(int) == m_km)
                    & (predictions["procedure"].astype(str) == procedure)
                ]
                by_source = {source: frame.copy() for source, frame in group.groupby("source", sort=False)}
                if set(by_source) != set(MODES):
                    both_adequate = False
                    integrity_reason = "sealed_prediction_source_rows_missing"
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
                            both_adequate = False
                            integrity_reason = "paired_surface_integrity_unresolved"
                        else:
                            comparison_rows = int(len(a))
                    except Exception as exc:
                        both_adequate = False
                        d = None
                        integrity_reason = f"paired_surface_integrity_error:{type(exc).__name__}"
            discordance = None if d is None else float(1.0 - d)
            decision = classify_heldout_crosscheck(
                both_answers_adequate=both_adequate,
                discordance=discordance,
                reference_state=str(ref["state"]),
                reference_ceiling=ref["ceiling"],
            )
            reasons = list(decision.reasons)
            if not both_sealed:
                if by_state[MODES[0]] != "layer1_model_fit_sealed": reasons.append("preserved_specimen_final_fit_unresolved")
                if by_state[MODES[1]] != "layer1_model_fit_sealed": reasons.append("human_observation_final_fit_unresolved")
            if qa is None or not qa.adequate: reasons.append("preserved_specimen_answer_inadequate_or_missing")
            if qb is None or not qb.adequate: reasons.append("human_observation_answer_inadequate_or_missing")
            if integrity_reason: reasons.append(integrity_reason)
            rows.append({
                "taxon": taxon,
                "M_km": int(m_km),
                "procedure": procedure,
                "both_final_fits_sealed": bool(both_sealed),
                "preserved_specimen_adequate": bool(qa is not None and qa.adequate),
                "human_observation_adequate": bool(qb is not None and qb.adequate),
                "paired_prediction_surface_opened": d is not None,
                "comparison_rows": comparison_rows,
                "schoener_d": None if d is None else float(d),
                "one_minus_schoener_d": decision.discordance,
                "frozen_reference_ceiling": decision.reference_ceiling,
                "discordance_minus_reference": decision.exceedance,
                "paired_state": decision.state,
                "reasons": ";".join(dict.fromkeys(reasons)),
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--fit-audit", required=True)
    parser.add_argument("--output-cells", required=True)
    parser.add_argument("--output-summary", required=True)
    args = parser.parse_args()

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    pairing = json.loads(PAIRING_CONTRACT.read_text(encoding="utf-8"))
    fit_contract = json.loads(FIT_CONTRACT.read_text(encoding="utf-8"))
    reference_summary = json.loads(REFERENCE_SUMMARY.read_text(encoding="utf-8"))
    fit_audit = json.loads(Path(args.fit_audit).read_text(encoding="utf-8"))
    if int(contract["expected_heldout_pair_cells"]) != 288:
        raise RuntimeError("held-out denominator contract drifted")
    if reference_summary.get("current_12_taxon_paired_discordance_read") is not False:
        raise RuntimeError("successor calibration already read held-out outcome")
    if reference_summary.get("process_knockout_opened") is not False:
        raise RuntimeError("process knockout opened before held-out baseline")
    if fit_audit.get("prediction_surfaces_opened_for_pairing") is not False or fit_audit.get("paired_discordance_opened") is not False:
        raise RuntimeError("held-out prediction outcomes were already opened")
    if fit_audit.get("process_knockout_opened") is not False:
        raise RuntimeError("held-out process knockout already opened")
    reference = _reference_map(pd.read_csv(REFERENCE_TABLE))
    if int(pairing["reference_ceiling_rule"]["minimum_complete_calibration_taxa_per_procedure_M"]) != 30:
        raise RuntimeError("base reference minimum drifted")

    cells: list[dict[str, object]] = []
    for taxon_contract, directory in _load_taxon_artifacts(Path(args.input_root)):
        cells.extend(_evaluate_taxon(taxon_contract, directory, fit_contract, reference))
    frame = pd.DataFrame(cells).sort_values(["taxon", "M_km", "procedure"], kind="mergesort").reset_index(drop=True)
    if len(frame) != 288:
        raise RuntimeError(f"expected 288 held-out cells, found {len(frame)}")
    counts = frame["paired_state"].value_counts().to_dict()
    out_cells = Path(args.output_cells)
    out_cells.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out_cells, index=False)
    summary = {
        "result_version": "product_b_same_target_heldout_crosscheck_v0.1",
        "heldout_taxa": int(frame["taxon"].nunique()),
        "heldout_cells_expected": 288,
        "heldout_cells_audited": int(len(frame)),
        "paired_crosscheck_consistent": int(counts.get("paired_crosscheck_consistent", 0)),
        "paired_crosscheck_attention_required": int(counts.get("paired_crosscheck_attention_required", 0)),
        "paired_crosscheck_unresolved": int(counts.get("paired_crosscheck_unresolved", 0)),
        "paired_crosscheck_calibration_unresolved": int(counts.get("paired_crosscheck_calibration_unresolved", 0)),
        "paired_prediction_surfaces_opened_cells": int(frame["paired_prediction_surface_opened"].sum()),
        "paired_prediction_surfaces_kept_closed_cells": int((~frame["paired_prediction_surface_opened"]).sum()),
        "reference_derived_from_heldout_taxa": False,
        "procedure_selected_from_heldout_outcome": False,
        "M_selected_from_heldout_outcome": False,
        "heldout_taxa_replaced": False,
        "process_knockout_opened": False,
        "attention_required_is_biological_falsification": False,
        "claim_strength": "heldout_cross_source_answer_reproducibility_test_under_frozen_successor_reference",
    }
    out_summary = Path(args.output_summary)
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
