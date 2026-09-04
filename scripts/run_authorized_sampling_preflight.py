#!/usr/bin/env python3
"""Run the single authorized Product-B v5 sampling-availability preflight.

Raw occurrence rows stay in memory. The only persisted output is a compact JSON
summary/audit. This script is intended to run exactly once from the dedicated
GitHub Actions workflow after the execution manifest has been authorized.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, is_dataclass
from enum import Enum
import json
from pathlib import Path
import sys
import traceback
from typing import Any, Mapping

from product_b_v5.gbif_transport import AuthorizedGBIFSearchTransport
from product_b_v5.pipeline import execute_frozen_pair_sampling_preflight
from product_b_v5.scope import GeographicScopeDeclaration, ScopeState


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "config/product_b_v5_sampling_execution_manifest.json"
SCOPE_PATH = ROOT / "registry/obligate_pair_registry_scope_v0_2.csv"
OUTPUT_PATH = ROOT / "artifacts/product_b_v5_sampling_preflight_outcome.json"


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _load_scope() -> tuple[GeographicScopeDeclaration, ...]:
    rows: list[GeographicScopeDeclaration] = []
    with SCOPE_PATH.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            state_raw = row["operational_scope_state"]
            if state_raw == ScopeState.RESOLVED.value:
                state = ScopeState.RESOLVED
            elif state_raw == ScopeState.UNRESOLVED.value:
                state = ScopeState.UNRESOLVED
            else:
                raise ValueError("unknown operational_scope_state: " + state_raw)
            rows.append(
                GeographicScopeDeclaration(
                    pair_id=row["pair_id"],
                    literature_scope_text=row["literature_scope_text"],
                    evidence_doi=row["evidence_doi"],
                    state=state,
                    filter_type=row["filter_type"],
                    filter_value=row["filter_value"],
                    scope_source_type=row["scope_source_type"],
                    note=row["note"],
                )
            )
    return tuple(rows)


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    scope = _load_scope()
    transport = AuthorizedGBIFSearchTransport(timeout_seconds=90.0)

    outcome: dict[str, Any] = {
        "status": "started",
        "manifest_version": manifest.get("manifest_version"),
        "pre_execution_package_commit": manifest.get("pre_execution_package_commit"),
        "authorization_date": manifest.get("authorization_date"),
        "pair_id": "OPM_FIG_001",
    }
    exit_code = 0
    try:
        result = execute_frozen_pair_sampling_preflight(
            manifest=manifest,
            scope_declarations=scope,
            transport=transport,
        )
        outcome.update(
            {
                "status": "completed",
                "transport_audits": _jsonable(transport.audits),
                "primary_sampling": _jsonable(result.primary),
                "strict_sensitivity_sampling": _jsonable(result.strict_sensitivity),
                "raw_alias_collision_components": _jsonable(
                    result.adapted_batch.raw_collision_components
                ),
                "raw_alias_collision_excluded_x": result.adapted_batch.raw_collision_excluded_x,
                "raw_alias_collision_excluded_y": result.adapted_batch.raw_collision_excluded_y,
            }
        )
    except Exception as exc:  # terminal audit is persisted before failing the workflow
        exit_code = 1
        outcome.update(
            {
                "status": "execution_error",
                "transport_audits": _jsonable(transport.audits),
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "traceback": traceback.format_exc(),
            }
        )

    OUTPUT_PATH.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
