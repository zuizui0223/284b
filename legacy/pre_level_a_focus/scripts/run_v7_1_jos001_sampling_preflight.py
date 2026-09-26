#!/usr/bin/env python3
"""Run the authorized JOS001 engineering host/control sampling preflight once.

Raw GBIF rows remain in memory. The persisted artifact contains transport and
sampling audits only. Literature witnesses are not re-fetched and no model,
invariant, or process-knockout outcome is opened.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
import json
import os
from pathlib import Path
import sys
import traceback
from typing import Any, Mapping

from product_b_v7_1.gbif_transport import AuthorizedV71GBIFSearchTransport
from product_b_v7_1.jos001_execution import execute_jos001_sampling_preflight

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "config/product_b_v7_1_jos001_execution_manifest_v0_1.json"
OUTPUT_PATH = ROOT / "artifacts/product_b_v7_1_jos001_sampling_preflight.json"


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


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    transport = AuthorizedV71GBIFSearchTransport(timeout_seconds=90.0)

    outcome: dict[str, Any] = {
        "status": "started",
        "pair_id": "JOS001",
        "engineering_only": True,
        "confirmatory_promotion_allowed": False,
        "manifest_version": manifest.get("manifest_version"),
        "pre_execution_package_commit": manifest.get("pre_execution_package_commit"),
        "runtime_github_sha": os.environ.get("GITHUB_SHA"),
        "literature_witness_reads_opened": False,
        "model_fit_reads_opened": False,
        "invariant_reads_opened": False,
        "process_knockout_reads_opened": False,
    }
    exit_code = 0
    try:
        result = execute_jos001_sampling_preflight(
            manifest=manifest,
            transport=transport,
        )
        outcome.update(
            {
                "status": "completed",
                "terminal_state": result.terminal_state,
                "terminal_reasons": list(result.terminal_reasons),
                "transport_audits": _jsonable(transport.audits),
                "focal_sampling": _jsonable(result.focal),
                "controls_opened": result.controls_opened,
                "control_results": _jsonable(result.control_results),
                "adequate_control_host_count": result.adequate_control_host_count,
                "minimum_required_control_hosts": result.minimum_required_control_hosts,
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

    OUTPUT_PATH.write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
