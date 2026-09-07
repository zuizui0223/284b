#!/usr/bin/env python3
"""Review continued successor reference outputs without opening held-out predictions."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path

import pandas as pd

EXPECTED_RESTORED = {"Alisma plantago-aquatica", "Populus tremula"}


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _require_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{path.name} is not a JSON object")
    return data


def review(
    continuation_path: Path,
    fit_audit_path: Path,
    feasibility_path: Path,
    reference_path: Path,
    summary_path: Path,
) -> dict:
    continuation = _require_json(continuation_path)
    fit_audit = _require_json(fit_audit_path)
    feasibility = _require_json(feasibility_path)
    summary = _require_json(summary_path)
    reference = pd.read_csv(reference_path)

    if continuation.get("completed_taxa") != 47:
        raise RuntimeError("continued bundle is not complete 47-taxon evidence")
    if continuation.get("original_artifact_taxa_retained") != 45:
        raise RuntimeError("original completed evidence was not retained exactly")
    if set(continuation.get("restored_taxa", [])) != EXPECTED_RESTORED:
        raise RuntimeError("continued taxa differ from the two timeout-censored taxa")
    if continuation.get("original_run_relabelled_success") is not False:
        raise RuntimeError("cancelled original run was relabelled as success")
    if continuation.get("heldout_opening_authorized") is not False:
        raise RuntimeError("held-out opening was authorized by continuation assembly")
    if continuation.get("predictions_decoded_for_assembly") is not False:
        raise RuntimeError("continuation assembly decoded predictions")

    if fit_audit.get("taxa_expected_from_sampling_pass") != 47:
        raise RuntimeError("fit audit taxon denominator changed")
    if fit_audit.get("taxa_with_prediction_artifacts") != 47:
        raise RuntimeError("fit audit lacks complete taxon artifacts")
    if fit_audit.get("expected_fit_cells") != 2256:
        raise RuntimeError("fit audit source-cell denominator changed")
    if fit_audit.get("paired_discordance_opened") is not False:
        raise RuntimeError("fit audit opened paired discordance")
    if fit_audit.get("reference_ceiling_opened") is not False:
        raise RuntimeError("fit audit opened a reference before calibration")
    if fit_audit.get("process_knockout_opened") is not False:
        raise RuntimeError("fit audit opened process knockout")

    if feasibility.get("result_version") != "product_b_same_target_successor_reference_feasibility_v0.1":
        raise RuntimeError("unexpected feasibility result version")
    if feasibility.get("sampling_pass_taxa") != 47 or feasibility.get("candidate_pair_cells") != 1128:
        raise RuntimeError("feasibility denominator changed")
    if feasibility.get("reference_cells_expected") != 24:
        raise RuntimeError("feasibility reference denominator changed")
    if feasibility.get("minimum_eligible_taxa_per_procedure_M") != 30:
        raise RuntimeError("reference minimum changed")
    if feasibility.get("paired_prediction_surfaces_read") is not False:
        raise RuntimeError("pre-D feasibility read prediction surfaces")
    if feasibility.get("schoener_d_computed") is not False or feasibility.get("reference_ceiling_computed") is not False:
        raise RuntimeError("pre-D feasibility opened discordance/reference")
    if feasibility.get("heldout_12_paired_discordance_read") is not False:
        raise RuntimeError("pre-D feasibility read held-out outcomes")
    if feasibility.get("process_knockout_opened") is not False:
        raise RuntimeError("pre-D feasibility opened process knockout")

    feasibility_map = {}
    for row in feasibility.get("reference_cells", []):
        key = (int(row["M_km"]), str(row["procedure"]))
        if key in feasibility_map:
            raise RuntimeError("duplicate feasibility reference cell")
        feasibility_map[key] = row
    if len(feasibility_map) != 24:
        raise RuntimeError("feasibility matrix is not 24 unique cells")

    required = {
        "M_km", "procedure", "pre_discordance_eligible_taxa",
        "pre_discordance_opening_authorized", "authorized_distinct_calibration_taxa",
        "minimum_required_taxa", "quantile", "quantile_method",
        "nearest_rank_index_1_based", "one_minus_schoener_d_reference_ceiling",
        "reference_state",
    }
    missing = required - set(reference.columns)
    if missing:
        raise RuntimeError(f"reference table missing columns: {sorted(missing)}")
    if len(reference) != 24:
        raise RuntimeError("reference table is not 24 cells")

    frozen = 0
    unresolved = 0
    seen = set()
    for _, row in reference.iterrows():
        key = (int(row["M_km"]), str(row["procedure"]))
        if key in seen or key not in feasibility_map:
            raise RuntimeError("reference key duplicate or outside feasibility matrix")
        seen.add(key)
        gate = feasibility_map[key]
        pre_n = int(row["pre_discordance_eligible_taxa"])
        gate_n = int(gate["eligible_distinct_taxa_pre_discordance"])
        if pre_n != gate_n:
            raise RuntimeError("calibration pre-D count differs from sealed feasibility")
        gate_authorized = bool(gate["discordance_opening_authorized"])
        if bool(row["pre_discordance_opening_authorized"]) != gate_authorized:
            raise RuntimeError("calibration opening authorization differs from sealed feasibility")
        if int(row["minimum_required_taxa"]) != 30:
            raise RuntimeError("reference table minimum changed")
        if float(row["quantile"]) != 0.95 or str(row["quantile_method"]) != "nearest_rank":
            raise RuntimeError("reference quantile rule changed")

        state = str(row["reference_state"])
        ceiling_raw = row["one_minus_schoener_d_reference_ceiling"]
        n_authorized = int(row["authorized_distinct_calibration_taxa"])
        if state == "reference_ceiling_frozen":
            if not gate_authorized or pre_n < 30 or n_authorized < 30:
                raise RuntimeError("frozen reference lacks frozen pre-D eligibility")
            if pd.isna(ceiling_raw) or not isfinite(float(ceiling_raw)) or not 0.0 <= float(ceiling_raw) <= 1.0:
                raise RuntimeError("frozen reference ceiling is invalid")
            if pd.isna(row["nearest_rank_index_1_based"]):
                raise RuntimeError("frozen reference lacks nearest-rank index")
            frozen += 1
        else:
            if gate_authorized:
                raise RuntimeError("authorized reference cell did not freeze a ceiling")
            if not pd.isna(ceiling_raw):
                raise RuntimeError("unfrozen reference carries a ceiling")
            unresolved += 1

    if len(seen) != 24:
        raise RuntimeError("reference matrix key coverage changed")

    if summary.get("result_version") != "product_b_same_target_successor_pairing_calibration_v0.2_strict_opening":
        raise RuntimeError("unexpected strict calibration summary version")
    if summary.get("sampling_pass_taxa_in_audit") != 47 or summary.get("paired_cells_expected") != 1128:
        raise RuntimeError("calibration denominator changed")
    if summary.get("reference_cells_expected") != 24:
        raise RuntimeError("calibration reference denominator changed")
    if summary.get("minimum_distinct_calibration_taxa_per_reference_cell") != 30:
        raise RuntimeError("calibration minimum changed")
    if summary.get("reference_quantile") != 0.95 or summary.get("quantile_method") != "nearest_rank":
        raise RuntimeError("calibration q95 rule changed")
    if summary.get("reference_cells_frozen") != frozen or summary.get("reference_cells_unresolved") != unresolved:
        raise RuntimeError("calibration summary/reference table disagree")
    if summary.get("current_12_taxon_paired_discordance_read") is not False:
        raise RuntimeError("held-out outcomes opened during reference calibration")
    if summary.get("process_knockout_opened") is not False:
        raise RuntimeError("process knockout opened during reference calibration")
    if summary.get("successor_consistent_labels_emitted") != 0 or summary.get("successor_attention_required_labels_emitted") != 0:
        raise RuntimeError("successor calibration emitted confirmatory labels")
    if summary.get("unauthorized_prediction_cells_materialized") != 0:
        raise RuntimeError("unauthorized successor predictions were materialized")

    return {
        "result_version": "product_b_same_target_continued_reference_review_v0.1",
        "continued_taxa_complete": 47,
        "original_taxa_retained": 45,
        "restored_taxa": sorted(EXPECTED_RESTORED),
        "reference_cells_expected": 24,
        "reference_cells_frozen": frozen,
        "reference_cells_unresolved": unresolved,
        "minimum_reference_taxa": 30,
        "reference_quantile": 0.95,
        "quantile_method": "nearest_rank",
        "heldout_prediction_opened": False,
        "heldout_crosscheck_opened": False,
        "process_knockout_opened": False,
        "input_sha256": {
            continuation_path.name: _hash(continuation_path),
            fit_audit_path.name: _hash(fit_audit_path),
            feasibility_path.name: _hash(feasibility_path),
            reference_path.name: _hash(reference_path),
            summary_path.name: _hash(summary_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuation", type=Path, required=True)
    parser.add_argument("--fit-audit", type=Path, required=True)
    parser.add_argument("--feasibility", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = review(args.continuation, args.fit_audit, args.feasibility, args.reference, args.summary)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
