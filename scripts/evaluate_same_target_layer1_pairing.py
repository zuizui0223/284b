#!/usr/bin/env python3
"""Evaluate sealed Layer-1 same-target prediction pairs descriptively.

This stage reads only sealed prediction artifacts and source-specific outer-CV
metrics from the completed baseline-fit run. It never reopens occurrence rows,
model fitting, predictor selection, a calibrated reference ceiling, or process
knockouts. With the current 12-taxon panel it may report descriptive Schoener D
but may not emit calibrated consistent/attention-required labels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from product_b_v5.same_target_pairing import (
    evaluate_prediction_adequacy,
    schoener_d_from_sealed_vectors,
)

ROOT = Path(__file__).resolve().parents[1]
PAIRING_CONTRACT = ROOT / "config/product_b_same_target_source_pairing_contract_v0_1.json"
FIT_CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")


def _load_taxon_artifacts(root: Path) -> list[tuple[dict[str, object], Path]]:
    rows: list[tuple[dict[str, object], Path]] = []
    for path in sorted(root.rglob("contract.json")):
        contract = json.loads(path.read_text(encoding="utf-8"))
        if contract.get("result_version") != "product_b_same_target_source_layer1_baseline_fit_taxon_v0.1":
            continue
        rows.append((contract, path.parent))
    if len(rows) != 12:
        raise RuntimeError(f"expected 12 sealed taxon artifacts, found {len(rows)}")
    taxa = [str(row[0]["taxon"]) for row in rows]
    if len(set(taxa)) != 12:
        raise RuntimeError("duplicate or missing taxon artifacts")
    return rows


def _adequacy_by_key(folds: pd.DataFrame, fit_contract: dict[str, object]) -> dict[tuple[str, int, str], object]:
    required = {"source", "M_km", "procedure", "fold", "presence_rank"}
    missing = required - set(folds.columns)
    if missing:
        raise RuntimeError(f"outer CV file missing columns: {sorted(missing)}")
    adequacy = fit_contract["prediction_adequacy"]
    expected_folds = int(adequacy["outer_folds"])
    result: dict[tuple[str, int, str], object] = {}
    for (source, m_km, procedure), group in folds.groupby(["source", "M_km", "procedure"], sort=True):
        # Duplicate fold rows would silently overstate evidence, so fail closed.
        fold_ids = pd.to_numeric(group["fold"], errors="raise").astype(int)
        if fold_ids.duplicated().any():
            raise RuntimeError("duplicate outer-fold evidence within source/procedure/M")
        values = pd.to_numeric(group["presence_rank"], errors="coerce").to_numpy(float)
        result[(str(source), int(m_km), str(procedure))] = evaluate_prediction_adequacy(
            values,
            expected_folds=expected_folds,
            chance_auc=float(adequacy["chance_auc"]),
            minimum_auc_margin=float(adequacy["minimum_auc_margin"]),
            auc_sem_multiplier=float(adequacy["auc_sem_multiplier"]),
        )
    return result


def _pair_one_taxon(
    contract: dict[str, object],
    directory: Path,
    fit_contract: dict[str, object],
    pairing_contract: dict[str, object],
) -> list[dict[str, object]]:
    if contract.get("prediction_surfaces_sealed") is not True:
        raise RuntimeError("prediction surfaces are not sealed")
    if int(contract.get("sealed_fit_cells", -1)) != int(contract.get("expected_fit_cells", -2)):
        raise RuntimeError("taxon has unresolved baseline fit cells")
    if int(contract.get("unresolved_fit_cells", -1)) != 0:
        raise RuntimeError("taxon has unresolved baseline fit cells")
    if contract.get("paired_discordance_computed") is not False:
        raise RuntimeError("paired discordance was opened before this stage")
    if contract.get("process_knockout_computed") is not False:
        raise RuntimeError("process knockout was opened before this stage")

    pred_path = directory / "sealed_prediction_surfaces.parquet"
    folds_path = directory / "outer_cv_fold_metrics.csv"
    predictions = pd.read_parquet(pred_path)
    folds = pd.read_csv(folds_path)
    required_pred = {"taxon", "source", "M_km", "procedure", "comparison_row_id", "ecological_score"}
    missing = required_pred - set(predictions.columns)
    if missing:
        raise RuntimeError(f"sealed prediction file missing columns: {sorted(missing)}")
    if set(predictions["source"].astype(str)) != set(MODES):
        raise RuntimeError("sealed prediction artifact does not contain exactly two frozen source modes")

    adequacy = _adequacy_by_key(folds, fit_contract)
    rows: list[dict[str, object]] = []
    pair_groups = predictions.groupby(["taxon", "M_km", "procedure"], sort=True)
    expected_pairs = len(fit_contract["M_km"]) * int(fit_contract["procedure_library"]["procedure_count"])
    if pair_groups.ngroups != expected_pairs:
        raise RuntimeError(f"expected {expected_pairs} paired cells per taxon, found {pair_groups.ngroups}")

    ref_rule = pairing_contract["reference_ceiling_rule"]
    if int(ref_rule["minimum_complete_calibration_taxa_per_procedure_M"]) != 30:
        raise RuntimeError("reference calibration minimum drifted")

    for (taxon, m_km, procedure), group in pair_groups:
        by_source = {source: frame.copy() for source, frame in group.groupby("source", sort=False)}
        if set(by_source) != set(MODES):
            raise RuntimeError("paired cell does not contain exactly two frozen sources")
        a = by_source[MODES[0]]
        b = by_source[MODES[1]]
        d = schoener_d_from_sealed_vectors(
            a["comparison_row_id"].astype(str).tolist(),
            pd.to_numeric(a["ecological_score"], errors="coerce").tolist(),
            b["comparison_row_id"].astype(str).tolist(),
            pd.to_numeric(b["ecological_score"], errors="coerce").tolist(),
        )
        qa = adequacy.get((MODES[0], int(m_km), str(procedure)))
        qb = adequacy.get((MODES[1], int(m_km), str(procedure)))
        if qa is None or qb is None:
            raise RuntimeError("missing source-specific prediction-adequacy evidence")
        reasons: list[str] = []
        if not qa.adequate:
            reasons.append("preserved_specimen_answer_inadequate")
        if not qb.adequate:
            reasons.append("human_observation_answer_inadequate")
        if reasons:
            state = "paired_crosscheck_unresolved"
        else:
            # The current panel has 12 taxa, below the frozen >=30 calibration
            # requirement. Descriptive discordance is legitimate; calibrated
            # consistent/attention labels are not.
            state = str(pairing_contract["when_reference_ceiling_unavailable"]["state"])
            reasons.append("reference_ceiling_unavailable_panel_below_30")

        rows.append({
            "taxon": str(taxon),
            "M_km": int(m_km),
            "procedure": str(procedure),
            "comparison_rows": int(len(a)),
            "schoener_d": float(d),
            "one_minus_schoener_d": float(1.0 - d),
            "preserved_specimen_adequate": bool(qa.adequate),
            "preserved_specimen_n_folds": int(qa.n_folds),
            "preserved_specimen_mean_presence_rank": qa.mean_presence_rank,
            "preserved_specimen_sem_presence_rank": qa.sem_presence_rank,
            "preserved_specimen_lower_evidence_bound": qa.lower_evidence_bound,
            "human_observation_adequate": bool(qb.adequate),
            "human_observation_n_folds": int(qb.n_folds),
            "human_observation_mean_presence_rank": qb.mean_presence_rank,
            "human_observation_sem_presence_rank": qb.sem_presence_rank,
            "human_observation_lower_evidence_bound": qb.lower_evidence_bound,
            "paired_state": state,
            "reasons": ";".join(reasons),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--fit-audit", required=True)
    parser.add_argument("--output-cells", required=True)
    parser.add_argument("--output-summary", required=True)
    args = parser.parse_args()

    fit_audit = json.loads(Path(args.fit_audit).read_text(encoding="utf-8"))
    if fit_audit.get("all_fit_cells_sealed") is not True:
        raise RuntimeError("baseline aggregate is not fully sealed")
    if int(fit_audit.get("sealed_fit_cells", -1)) != 576 or int(fit_audit.get("unresolved_fit_cells", -1)) != 0:
        raise RuntimeError("baseline aggregate does not contain 576 fully sealed fit cells")
    if fit_audit.get("prediction_surfaces_opened_for_pairing") is not False:
        raise RuntimeError("baseline audit indicates prediction surfaces were already paired")
    if fit_audit.get("process_knockout_opened") is not False:
        raise RuntimeError("process knockout opened before baseline pairing")

    pairing_contract = json.loads(PAIRING_CONTRACT.read_text(encoding="utf-8"))
    fit_contract = json.loads(FIT_CONTRACT.read_text(encoding="utf-8"))
    artifacts = _load_taxon_artifacts(Path(args.input_root))
    cells: list[dict[str, object]] = []
    for contract, directory in artifacts:
        cells.extend(_pair_one_taxon(contract, directory, fit_contract, pairing_contract))
    frame = pd.DataFrame(cells).sort_values(["taxon", "M_km", "procedure"], kind="mergesort").reset_index(drop=True)
    if len(frame) != 288:
        raise RuntimeError(f"expected 288 paired cells, found {len(frame)}")

    both_adequate = frame["preserved_specimen_adequate"] & frame["human_observation_adequate"]
    descriptive = frame.loc[both_adequate].copy()
    summary_by_m = []
    for m_km, group in descriptive.groupby("M_km", sort=True):
        values = pd.to_numeric(group["one_minus_schoener_d"], errors="coerce").to_numpy(float)
        values = values[np.isfinite(values)]
        summary_by_m.append({
            "M_km": int(m_km),
            "both_adequate_pair_cells": int(len(values)),
            "median_one_minus_schoener_d": float(np.median(values)) if len(values) else None,
            "mean_one_minus_schoener_d": float(np.mean(values)) if len(values) else None,
            "min_one_minus_schoener_d": float(np.min(values)) if len(values) else None,
            "max_one_minus_schoener_d": float(np.max(values)) if len(values) else None,
        })

    out_cells = Path(args.output_cells)
    out_cells.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out_cells, index=False)
    summary = {
        "result_version": "product_b_same_target_source_layer1_pairing_v0.1",
        "paired_cells_expected": 288,
        "paired_cells_evaluated": int(len(frame)),
        "both_sources_prediction_adequate_cells": int(both_adequate.sum()),
        "prediction_inadequate_or_incomplete_cells": int((~both_adequate).sum()),
        "taxa": int(frame["taxon"].nunique()),
        "M_km": sorted(int(x) for x in frame["M_km"].unique()),
        "procedures": int(frame["procedure"].nunique()),
        "reference_ceiling_available": False,
        "reference_ceiling_reason": "12_complete_taxa_below_frozen_minimum_30",
        "calibrated_consistent_labels_emitted": 0,
        "calibrated_attention_required_labels_emitted": 0,
        "descriptive_schoener_d_reported": True,
        "summary_by_M_across_both_adequate_cells": summary_by_m,
        "process_knockout_opened": False,
        "procedure_selected_from_cross_source_outcome": False,
        "M_selected_from_cross_source_outcome": False,
        "claim_strength": "engineering_descriptive_cross_source_coherence_only",
    }
    out_summary = Path(args.output_summary)
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
