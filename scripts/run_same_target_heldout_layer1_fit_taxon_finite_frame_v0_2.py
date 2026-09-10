#!/usr/bin/env python3
"""Run the unchanged held-out finite-frame refit body on a v0.2 receipt.

Only the receipt type marker is adapted in a temporary copy. Frozen comparison
parquet bytes and the model-fit implementation are unchanged. The resulting
contract is amended with the original v0.2 receipt digest and repair identity.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import tempfile

from scripts import run_same_target_heldout_layer1_fit_taxon_finite_frame as base

V2_RESULT = "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.2"
V1_RESULT = "product_b_same_target_heldout_finite_frame_preflight_taxon_v0.1"
V2_CONTRACT = "product_b_same_target_heldout_finite_frame_repair_v0.2"


def _arg_value(flag: str) -> str:
    try:
        i = sys.argv.index(flag)
    except ValueError as exc:
        raise RuntimeError(f"missing required argument {flag}") from exc
    if i + 1 >= len(sys.argv):
        raise RuntimeError(f"missing value for {flag}")
    return sys.argv[i + 1]


def main() -> int:
    finite_dir = Path(_arg_value("--finite-frame-dir"))
    output_dir = Path(_arg_value("--output-dir"))
    source_receipt = finite_dir / "receipt.json"
    original_bytes = source_receipt.read_bytes()
    receipt = json.loads(original_bytes)
    if receipt.get("result_version") != V2_RESULT:
        raise RuntimeError("held-out v0.2 adapter received wrong receipt type")
    if receipt.get("repair_contract_version") != V2_CONTRACT:
        raise RuntimeError("held-out v0.2 adapter received wrong repair contract")
    if receipt.get("all_three_M_frames_frozen") is not True:
        raise RuntimeError("held-out v0.2 adapter refuses unresolved finite frames")
    for key in (
        "model_refit_opened",
        "prediction_scores_computed",
        "paired_discordance_opened",
        "reference_ceiling_read",
        "heldout_pairing_opened",
        "process_knockout_opened",
    ):
        if receipt.get(key) is not False:
            raise RuntimeError(f"held-out v0.2 preflight boundary changed: {key}")

    original_argv = list(sys.argv)
    with tempfile.TemporaryDirectory(prefix="heldout_finite_frame_v0_2_adapter_") as tmp:
        adapted = Path(tmp)
        for p in finite_dir.iterdir():
            if p.name == "receipt.json":
                continue
            if p.is_file():
                shutil.copy2(p, adapted / p.name)
            elif p.is_dir():
                shutil.copytree(p, adapted / p.name)
        adapted_receipt = dict(receipt)
        adapted_receipt["result_version"] = V1_RESULT
        adapted_receipt.pop("repair_contract_version", None)
        (adapted / "receipt.json").write_text(
            json.dumps(adapted_receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        i = sys.argv.index("--finite-frame-dir")
        sys.argv[i + 1] = str(adapted)
        try:
            code = base.main()
        finally:
            sys.argv[:] = original_argv

    contract_path = output_dir / "contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract["finite_frame_preflight_receipt_sha256"] = sha256(original_bytes).hexdigest()
    contract["finite_frame_preflight_result_version"] = V2_RESULT
    contract["finite_frame_repair_contract_version"] = V2_CONTRACT
    contract["v0_2_adapter_changed_frame_bytes"] = False
    contract["v0_2_adapter_changed_model_fit_body"] = False
    contract_path.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return int(code)


if __name__ == "__main__":
    raise SystemExit(main())
