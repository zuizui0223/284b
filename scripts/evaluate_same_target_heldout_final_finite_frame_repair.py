#!/usr/bin/env python3
"""Open the repaired held-out paired endpoint under a frozen successor reference.

This is the first stage in the finite-frame repair path that may count as a new
empirical conclusion. Prediction vectors are materialized only for held-out
cells whose two repaired source answers pass the frozen adequacy rule and whose
matching successor reference ceiling is frozen. All other paired outcomes stay
closed. Process knockouts remain closed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import pandas as pd

from product_b_v5.heldout_crosscheck import classify_heldout_crosscheck
from product_b_v5.prediction_opening import read_authorized_prediction_cells
from product_b_v5.same_target_pairing import evaluate_prediction_adequacy, schoener_d_if_both_answers_adequate

ROOT = Path(__file__).resolve().parents[1]
FIT_CONTRACT = ROOT / "config/product_b_same_target_source_model_fit_contract_v0_1.json"
MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")
HELDOUT_RESULT = "product_b_same_target_source_layer1_baseline_fit_taxon_finite_frame_repair_v0.1"
SEALED_STATE = "layer1_model_fit_sealed_finite_frame_repair"
REFERENCE_RESULT = "product_b_same_target_successor_pairing_calibration_finite_frame_repair_v0.1"


def _read_csv_or_empty(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _load_heldout(root: Path) -> list[tuple[dict[str, object], Path]]:
    rows: list[tuple[dict[str, object], Path]] = []
    for p in sorted(root.rglob("contract.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        if c.get("result_version") == HELDOUT_RESULT:
            rows.append((c, p.parent))
    indices = sorted(int(c["taxon_index"]) for c, _ in rows)
    names = [str(c["taxon"]) for c, _ in rows]
    if len(rows) != 12 or indices != list(range(12)) or len(set(names)) != 12:
        raise RuntimeError("repaired held-out root must contain exactly the frozen 12 taxa")
    for c, _ in rows:
        if c.get("finite_frame_preflight_result_version") != "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.2":
            raise RuntimeError("held-out final requires v0.2 finite-frame fits")
        if c.get("finite_frame_repair_contract_version") != "product_b_same_target_heldout_finite_frame_repair_v0.2":
            raise RuntimeError("held-out final repair-contract identity mismatch")
        if c.get("prediction_surfaces_sealed") is not True or c.get("all_prediction_scores_finite_by_contract") is not True:
            raise RuntimeError("held-out repaired prediction surface is not sealed all-finite")
        if c.get("same_frozen_finite_background_rows_used_for_both_sources") is not True:
            raise RuntimeError("held-out final received asymmetric comparison frame")
        if c.get("background_rows_resampled_during_refit") is not False or c.get("posthoc_prediction_row_drop_used") is not False:
            raise RuntimeError("held-out repaired fit changed frozen comparison rows")
        for key in ("paired_discordance_computed", "reference_ceiling_read", "heldout_pairing_opened", "process_knockout_computed"):
            if c.get(key) is not False:
                raise RuntimeError(f"held-out repaired fit crossed boundary before final: {key}")
    return rows


def _adequacy_by_key(folds: pd.DataFrame, fit_contract: dict[str, object]) -> dict[tuple[str, int, str], object]:
    if folds.empty:
        return {}
    required = {"source", "M_km", "procedure", "fold", "presence_rank"}
    missing = required - set(folds.columns)
    if missing:
        raise RuntimeError(f"held-out repaired outer CV missing columns: {sorted(missing)}")
    frozen = fit_contract["prediction_adequacy"]
    out: dict[tuple[str, int, str], object] = {}
    for (source, m_km, procedure), group in folds.groupby(["source", "M_km", "procedure"], sort=True):
        fold_ids = pd.to_numeric(group["fold"], errors="raise").astype(int)
        if fold_ids.duplicated().any():
            raise RuntimeError("duplicate held-out repaired outer-fold evidence")
        values = pd.to_numeric(group["presence_rank"], errors="coerce").to_numpy(float)
        out[(str(source), int(m_km), str(procedure))] = evaluate_prediction_adequacy(
            values,
            expected_folds=int(frozen["outer_folds"]),
            chance_auc=float(frozen["chance_auc"]),
            minimum_auc_margin=float(frozen["minimum_auc_margin"]),
            auc_sem_multiplier=float(frozen["auc_sem_multiplier"]),
        )
    return out


def _reference_map(table: pd.DataFrame) -> dict[tuple[int, str], dict[str, object]]:
    required = {"M_km", "procedure", "reference_state", "one_minus_schoener_d_reference_ceiling"}
    missing = required - set(table.columns)
    if missing:
        raise RuntimeError(f"repaired reference table missing columns: {sorted(missing)}")
    if len(table) != 24:
        raise RuntimeError("repaired reference table must contain 24 procedure/M cells")
    out: dict[tuple[int, str], dict[str, object]] = {}
    for _, row in table.iterrows():
        key = (int(row["M_km"]), str(row["procedure"]))
        if key in out:
            raise RuntimeError("duplicate repaired reference cell")
        raw = row["one_minus_schoener_d_reference_ceiling"]
        ceiling = None if pd.isna(raw) else float(raw)
        state = str(row["reference_state"])
        if state == "reference_ceiling_frozen" and ceiling is None:
            raise RuntimeError("frozen repaired reference lacks ceiling")
        if state != "reference_ceiling_frozen" and ceiling is not None:
            raise RuntimeError("unfrozen repaired reference carries ceiling")
        out[key] = {"state": state, "ceiling": ceiling}
    return out


def _evaluate_taxon(
    contract: dict[str, object],
    directory: Path,
    fit_contract: dict[str, object],
    reference: dict[tuple[int, str], dict[str, object]],
) -> list[dict[str, object]]:
    inventory = _read_csv_or_empty(directory / "fit_inventory.csv")
    folds = _read_csv_or_empty(directory / "outer_cv_fold_metrics.csv")
    if len(inventory) != 48:
        raise RuntimeError("held-out repaired fit inventory must contain 48 cells")
    adequacy = _adequacy_by_key(folds, fit_contract)
    taxon = str(contract["taxon"])
    procedures = sorted(str(x) for x in inventory["procedure"].dropna().unique())
    m_values = sorted(int(x) for x in inventory["M_km"].dropna().unique())
    if len(procedures) != 8 or m_values != [150, 300, 500]:
        raise RuntimeError("held-out repaired procedure/M universe drifted")

    prelim: list[dict[str, object]] = []
    materialize: set[tuple[int, str]] = set()
    for m_km in m_values:
        for procedure in procedures:
            key = (m_km, procedure)
            ref = reference[key]
            inv = inventory[(inventory["M_km"].astype(int) == m_km) & (inventory["procedure"].astype(str) == procedure)]
            if len(inv) != 2:
                raise RuntimeError("held-out repaired inventory lacks exactly two sources")
            by_state = {str(r["source"]): str(r["state"]) for _, r in inv.iterrows()}
            if set(by_state) != set(MODES):
                raise RuntimeError("held-out repaired source universe drifted")
            both_sealed = all(by_state[m] == SEALED_STATE for m in MODES)
            qa = adequacy.get((MODES[0], m_km, procedure))
            qb = adequacy.get((MODES[1], m_km, procedure))
            a_ok = bool(qa is not None and qa.adequate)
            b_ok = bool(qb is not None and qb.adequate)
            both_adequate = bool(both_sealed and a_ok and b_ok)
            reference_frozen = str(ref["state"]) == "reference_ceiling_frozen"
            opening_allowed = bool(both_adequate and reference_frozen)
            if opening_allowed:
                materialize.add(key)
            prelim.append({
                "taxon": taxon,
                "M_km": m_km,
                "procedure": procedure,
                "both_final_fits_sealed": both_sealed,
                "preserved_specimen_adequate": a_ok,
                "human_observation_adequate": b_ok,
                "both_answers_adequate": both_adequate,
                "reference_state": str(ref["state"]),
                "reference_ceiling": ref["ceiling"],
                "prediction_materialization_authorized": opening_allowed,
            })

    predictions = read_authorized_prediction_cells(directory / "sealed_prediction_surfaces.parquet", materialize)
    rows: list[dict[str, object]] = []
    for row in prelim:
        key = (int(row["M_km"]), str(row["procedure"]))
        d = None
        comparison_rows = None
        integrity_reason = None
        if row["prediction_materialization_authorized"]:
            group = predictions[
                (predictions["taxon"].astype(str) == taxon)
                & (predictions["M_km"].astype(int) == key[0])
                & (predictions["procedure"].astype(str) == key[1])
            ]
            by_source = {str(src): frame.copy() for src, frame in group.groupby("source", sort=False)}
            if set(by_source) != set(MODES):
                integrity_reason = "sealed_prediction_source_rows_missing"
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
                        integrity_reason = "paired_surface_integrity_unresolved"
                    else:
                        comparison_rows = int(len(a))
                        if comparison_rows != 2000 or int(len(b)) != 2000:
                            raise RuntimeError("held-out repaired paired surface denominator is not 2000")
                except Exception as exc:
                    d = None
                    integrity_reason = f"paired_surface_integrity_error:{type(exc).__name__}:{str(exc)}"

        both_adequate_for_classification = bool(row["both_answers_adequate"] and integrity_reason is None)
        discordance = None if d is None else float(1.0 - d)
        decision = classify_heldout_crosscheck(
            both_answers_adequate=both_adequate_for_classification,
            discordance=discordance,
            reference_state=str(row["reference_state"]),
            reference_ceiling=row["reference_ceiling"],
        )
        reasons = list(decision.reasons)
        if not row["both_final_fits_sealed"]:
            reasons.append("one_or_both_repaired_final_fits_unresolved")
        if not row["preserved_specimen_adequate"]:
            reasons.append("preserved_specimen_answer_inadequate_or_missing")
        if not row["human_observation_adequate"]:
            reasons.append("human_observation_answer_inadequate_or_missing")
        if integrity_reason:
            reasons.append(integrity_reason)
        rows.append({
            "taxon": taxon,
            "M_km": key[0],
            "procedure": key[1],
            "both_final_fits_sealed": row["both_final_fits_sealed"],
            "preserved_specimen_adequate": row["preserved_specimen_adequate"],
            "human_observation_adequate": row["human_observation_adequate"],
            "reference_state": row["reference_state"],
            "prediction_materialization_authorized": row["prediction_materialization_authorized"],
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", required=True)
    ap.add_argument("--reference-summary", required=True)
    ap.add_argument("--reference-table", required=True)
    ap.add_argument("--source-manifest", required=True)
    ap.add_argument("--output-cells", required=True)
    ap.add_argument("--output-final", required=True)
    args = ap.parse_args()

    fit_contract = json.loads(FIT_CONTRACT.read_text(encoding="utf-8"))
    reference_summary_bytes = Path(args.reference_summary).read_bytes()
    reference_table_bytes = Path(args.reference_table).read_bytes()
    reference_summary = json.loads(reference_summary_bytes)
    if reference_summary.get("result_version") != REFERENCE_RESULT:
        raise RuntimeError("held-out final requires repaired successor reference")
    if reference_summary.get("heldout_12_paired_discordance_read") is not False or reference_summary.get("process_knockout_opened") is not False:
        raise RuntimeError("repaired reference already crossed held-out/process boundary")
    if int(reference_summary.get("reference_cells_frozen", 0)) < 1:
        raise RuntimeError("held-out final may not open without at least one frozen reference cell")
    reference = _reference_map(pd.read_csv(args.reference_table))
    source_manifest = json.loads(Path(args.source_manifest).read_text(encoding="utf-8"))

    cells: list[dict[str, object]] = []
    for contract, directory in _load_heldout(Path(args.input_root)):
        cells.extend(_evaluate_taxon(contract, directory, fit_contract, reference))
    frame = pd.DataFrame(cells).sort_values(["taxon", "M_km", "procedure"], kind="mergesort").reset_index(drop=True)
    if len(frame) != 288:
        raise RuntimeError(f"expected 288 repaired held-out cells, found {len(frame)}")

    counts = frame["paired_state"].value_counts().to_dict()
    opened = int(frame["paired_prediction_surface_opened"].sum())
    authorized = int(frame["prediction_materialization_authorized"].sum())
    if opened != authorized:
        raise RuntimeError("authorized held-out paired surface failed to open; final endpoint fails closed")
    if opened < 1:
        raise RuntimeError("no repaired held-out paired outcome opened; do not emit empirical final")

    out_cells = Path(args.output_cells)
    out_cells.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out_cells, index=False)
    cells_sha = sha256(out_cells.read_bytes()).hexdigest()
    attention = int(counts.get("paired_crosscheck_attention_required", 0))
    consistent = int(counts.get("paired_crosscheck_consistent", 0))
    if attention and consistent:
        status = "mixed_heldout_cross_source_reproducibility_with_attention"
    elif attention:
        status = "heldout_cross_source_attention_detected"
    else:
        status = "heldout_cross_source_consistent_on_opened_cells"

    fingerprint_payload = {
        "endpoint": "product_b_same_target_heldout_final_finite_frame_repair_v0.1",
        "cells_sha256": cells_sha,
        "reference_summary_sha256": sha256(reference_summary_bytes).hexdigest(),
        "reference_table_sha256": sha256(reference_table_bytes).hexdigest(),
        "source_manifest": source_manifest,
        "opened_cells": opened,
        "consistent": consistent,
        "attention_required": attention,
    }
    fingerprint = sha256(json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    result = {
        "result_version": "product_b_same_target_heldout_final_finite_frame_repair_v0.1",
        "endpoint_id": "same_target_cross_source_reproducibility_heldout12_finite_frame_v0_1",
        "opened_at_utc": datetime.now(timezone.utc).isoformat(),
        "terminal_class": "empirical_result",
        "status": status,
        "counts_as_empirical_conclusion": True,
        "counts_as_empirical_evidence": True,
        "final_endpoint_fingerprint": fingerprint,
        "heldout_taxa": 12,
        "heldout_cells_expected": 288,
        "heldout_cells_audited": 288,
        "paired_prediction_surfaces_opened_cells": opened,
        "paired_prediction_surfaces_kept_closed_cells": int(288 - opened),
        "paired_crosscheck_consistent": consistent,
        "paired_crosscheck_attention_required": attention,
        "paired_crosscheck_unresolved": int(counts.get("paired_crosscheck_unresolved", 0)),
        "paired_crosscheck_calibration_unresolved": int(counts.get("paired_crosscheck_calibration_unresolved", 0)),
        "reference_cells_frozen": int(reference_summary["reference_cells_frozen"]),
        "reference_cells_unresolved": int(reference_summary["reference_cells_unresolved"]),
        "cells_sha256": cells_sha,
        "reference_summary_sha256": sha256(reference_summary_bytes).hexdigest(),
        "reference_table_sha256": sha256(reference_table_bytes).hexdigest(),
        "source_manifest": source_manifest,
        "reference_derived_from_heldout_taxa": False,
        "procedure_selected_from_heldout_outcome": False,
        "M_selected_from_heldout_outcome": False,
        "heldout_taxa_replaced": False,
        "process_knockout_opened": False,
        "attention_required_is_biological_falsification": False,
        "claim_strength": "heldout_cross_source_answer_reproducibility_under_frozen_successor_reference_not_direct_biological_process_falsification",
    }
    out_final = Path(args.output_final)
    out_final.parent.mkdir(parents=True, exist_ok=True)
    out_final.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
