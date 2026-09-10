#!/usr/bin/env python3
"""v0.2 provenance gate around the unchanged repaired pre-D feasibility audit."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from scripts import audit_same_target_successor_reference_feasibility_finite_frame_repair as base

FIT_RESULT = "product_b_same_target_successor_layer1_fit_taxon_finite_frame_repair_v0.1"
FRAME_RESULT = "product_b_same_target_successor_finite_frame_preflight_taxon_v0.2"
REPAIR_CONTRACT = "product_b_same_target_reference_finite_frame_repair_v0.2"
AUDIT_VERSION = "product_b_same_target_successor_reference_feasibility_finite_frame_repair_v0.2"


def _arg(flag: str) -> str:
    try:
        i = sys.argv.index(flag)
    except ValueError as exc:
        raise RuntimeError(f"missing {flag}") from exc
    return sys.argv[i + 1]


def main() -> int:
    root = Path(_arg("--input-root"))
    out = Path(_arg("--output"))
    contracts = []
    for p in sorted(root.rglob("contract.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        if c.get("result_version") == FIT_RESULT:
            contracts.append(c)
    if len(contracts) != 47:
        raise RuntimeError(f"v0.2 pre-D gate requires 47 repaired contracts, found {len(contracts)}")
    for c in contracts:
        if c.get("finite_frame_preflight_result_version") != FRAME_RESULT:
            raise RuntimeError("v0.2 pre-D gate rejects non-v0.2 finite-frame fit")
        if c.get("finite_frame_repair_contract_version") != REPAIR_CONTRACT:
            raise RuntimeError("v0.2 pre-D gate rejects wrong repair contract")
        if c.get("v0_2_adapter_changed_frame_bytes") is not False:
            raise RuntimeError("v0.2 pre-D gate rejects changed frame bytes")
        if c.get("v0_2_adapter_changed_model_fit_body") is not False:
            raise RuntimeError("v0.2 pre-D gate rejects changed model-fit body")
        for k in ("paired_discordance_computed", "reference_ceiling_read", "heldout_12_paired_discordance_read", "process_knockout_computed"):
            if c.get(k) is not False:
                raise RuntimeError(f"v0.2 pre-D gate found opened boundary: {k}")
    code = base.main()
    payload = json.loads(out.read_text(encoding="utf-8"))
    payload["result_version"] = AUDIT_VERSION
    payload["finite_frame_repair_contract_version"] = REPAIR_CONTRACT
    payload["input_finite_frame_preflight_result_version"] = FRAME_RESULT
    payload["input_repaired_fit_contracts"] = 47
    payload["counts_as_empirical_conclusion"] = False
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return int(code)


if __name__ == "__main__":
    raise SystemExit(main())
