#!/usr/bin/env python3
"""Aggregate the six sanitized source-mode sampling shards.

This script sees only shard summary JSONs, never raw occurrence rows. It preserves
all frozen-panel taxa: taxonomy failures and snapshot-identity failures remain
not-entered; sampling failures remain unresolved and are never replaced.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "results/product_b_same_target_source_snapshot_identity_v0_1.json"
SHARD_DIR = ROOT / "artifacts/sampling_shards"
OUTPUT = ROOT / "results/product_b_same_target_source_mode_sampling_v0_1.json"


def main() -> int:
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    files = sorted(SHARD_DIR.glob("product_b_same_target_source_sampling_shard_*.json"))
    if len(files) != 6:
        raise RuntimeError(f"expected 6 sampling shard summaries, found {len(files)}")

    seen_shards: set[int] = set()
    results: list[dict[str, object]] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        shard = int(payload["shard_index"])
        if shard in seen_shards:
            raise RuntimeError("duplicate sampling shard index")
        seen_shards.add(shard)
        if payload.get("shard_count") != 6:
            raise RuntimeError("sampling shard count mismatch")
        if payload.get("raw_rows_persisted") is not False:
            raise RuntimeError("raw row persistence boundary violated")
        if payload.get("coordinates_persisted") is not False:
            raise RuntimeError("coordinate persistence boundary violated")
        if payload.get("row_identifiers_persisted") is not False:
            raise RuntimeError("row identifier persistence boundary violated")
        results.extend(payload.get("results", []))

    passed_identity_names = {
        str(row["requested_name"])
        for row in identity.get("identity_results", [])
        if row.get("passed") is True
    }
    result_names = {str(row["requested_name"]) for row in results}
    if result_names != passed_identity_names:
        missing = sorted(passed_identity_names - result_names)
        extra = sorted(result_names - passed_identity_names)
        raise RuntimeError(f"sampling result coverage mismatch missing={missing} extra={extra}")

    panel_order: list[str] = []
    provenance: dict[str, dict[str, object]] = {}
    for row in identity.get("identity_results", []):
        name = str(row["requested_name"])
        panel_order.append(name)
        provenance[name] = row
    for row in identity.get("not_entered", []):
        name = str(row["requested_name"])
        panel_order.append(name)
        provenance[name] = row

    by_name = {str(row["requested_name"]): row for row in results}
    ordered_results: list[dict[str, object]] = []
    for name in panel_order:
        if name in by_name:
            row = dict(by_name[name])
            row["validation_stratum"] = provenance[name].get("validation_stratum")
            row["candidate_rank"] = provenance[name].get("candidate_rank")
            ordered_results.append(row)
        else:
            source = provenance[name]
            ordered_results.append(
                {
                    "requested_name": name,
                    "validation_stratum": source.get("validation_stratum"),
                    "candidate_rank": source.get("candidate_rank"),
                    "state": source.get("snapshot_identity_state") or source.get("status") or "not_entered",
                    "reasons": source.get("reasons", [source.get("current_taxonomy_state", "upstream_taxonomy_unresolved")]),
                }
            )

    sampling_passed = sum(row.get("state") == "source_mode_sampling_passed" for row in ordered_results)
    sampling_unresolved = sum(
        str(row.get("state", "")).startswith("source_mode_sampling_")
        and row.get("state") != "source_mode_sampling_passed"
        for row in ordered_results
    )
    upstream_not_entered = len(ordered_results) - sampling_passed - sampling_unresolved

    stratum_summary: dict[str, dict[str, int]] = {}
    for row in ordered_results:
        stratum = str(row.get("validation_stratum") or "unknown")
        bucket = stratum_summary.setdefault(stratum, {"panel": 0, "sampling_passed": 0, "sampling_unresolved_or_not_entered": 0})
        bucket["panel"] += 1
        if row.get("state") == "source_mode_sampling_passed":
            bucket["sampling_passed"] += 1
        else:
            bucket["sampling_unresolved_or_not_entered"] += 1

    outcome = {
        "result_version": "product_b_same_target_source_mode_sampling_v0.1",
        "panel_size": 36,
        "snapshot_identity_passed_entering_sampling": len(passed_identity_names),
        "source_mode_sampling_passed": sampling_passed,
        "source_mode_sampling_unresolved": sampling_unresolved,
        "upstream_taxonomy_or_identity_not_entered": upstream_not_entered,
        "minimum_complete_taxa_needed_for_cross_source_calibration": 30,
        "calibration_sampling_feasible_at_panel_level": sampling_passed >= 30,
        "stratum_summary": stratum_summary,
        "results": ordered_results,
        "raw_rows_persisted": False,
        "coordinates_persisted": False,
        "row_identifiers_persisted": False,
        "paired_discordance_opened": False,
        "model_fit_opened": False,
        "replacement_taxa_selected": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
