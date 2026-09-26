#!/usr/bin/env python3
"""Run one frozen Yucca Product-B v5 sampling preflight.

Usage is limited to the two response-blind Yucca manifests. Raw GBIF rows remain
in memory; only compact transport and sampling audits are persisted.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, is_dataclass
from enum import Enum
import json
from pathlib import Path
import sys
import traceback
from typing import Any, Mapping

from product_b_v5.gbif_transport import AuthorizedGBIFSearchTransport
from product_b_v5.pipeline import execute_frozen_pair_sampling_preflight, frozen_pair_spec
from product_b_v5.scope import GeographicScopeDeclaration, ScopeState


ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = ROOT / "registry/obligate_pair_registry_scope_v0_3.csv"
MANIFESTS = {
    "OPM_YUC_001": ROOT / "config/product_b_v5_sampling_execution_manifest_yuc001_v0_1.json",
    "OPM_YUC_002": ROOT / "config/product_b_v5_sampling_execution_manifest_yuc002_v0_1.json",
}


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


def _load_scopes() -> tuple[GeographicScopeDeclaration, ...]:
    rows: list[GeographicScopeDeclaration] = []
    with SCOPE_PATH.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            raw_state = row["operational_scope_state"]
            state = ScopeState(raw_state)
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair-id", choices=tuple(MANIFESTS), required=True)
    args = parser.parse_args()
    pair_id = args.pair_id
    manifest_path = MANIFESTS[pair_id]
    output_path = ROOT / f"artifacts/product_b_v5_{pair_id.lower()}_sampling_preflight.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    scopes = _load_scopes()
    spec = frozen_pair_spec(pair_id)
    transport = AuthorizedGBIFSearchTransport(timeout_seconds=90.0)

    outcome: dict[str, Any] = {
        "status": "started",
        "pair_id": pair_id,
        "manifest_path": str(manifest_path.relative_to(ROOT)),
        "manifest_version": manifest.get("manifest_version"),
        "pre_execution_package_commit": manifest.get("pre_execution_package_commit"),
    }
    exit_code = 0
    try:
        result = execute_frozen_pair_sampling_preflight(
            manifest=manifest,
            scope_declarations=scopes,
            transport=transport,
            spec=spec,
        )
        outcome.update(
            {
                "status": "completed",
                "transport_audits": _jsonable(transport.audits),
                "raw_records_x": result.adapted_batch.raw_records_x,
                "raw_records_y": result.adapted_batch.raw_records_y,
                "raw_identity_component_count": len(result.adapted_batch.identity_components),
                "primary_sampling": _jsonable(result.primary),
                "strict_sensitivity_sampling": _jsonable(result.strict_sensitivity),
            }
        )
    except Exception as exc:
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

    output_path.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
