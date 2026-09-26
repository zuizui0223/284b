#!/usr/bin/env python3
"""Freeze a relation-endpoint contract into a canonical fingerprint receipt.

The input JSON must contain exactly the fields required by
RelationEndpointContract. The output receipt contains the validated canonical
contract, deterministic JSON material and a SHA-256 fingerprint. No ecological
outcome data are read by this utility.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from relation_endpoint_contract import contract_from_mapping


def freeze_contract_payload(raw: dict[str, object]) -> dict[str, object]:
    contract = contract_from_mapping(raw)
    return {
        "schema_version": "relation_endpoint_contract_freeze_v0_1",
        "contract": contract.canonical_payload(),
        "canonical_json": contract.canonical_json(),
        "fingerprint_algorithm": "sha256",
        "fingerprint_sha256": contract.fingerprint_sha256(),
        "outcome_data_read": False,
        "empirical_ledger_increment": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("contract JSON must be an object")

    receipt = freeze_contract_payload(raw)
    rendered = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    if args.out is None:
        print(rendered, end="")
    else:
        args.out.write_text(rendered, encoding="utf-8")
        print(args.out)


if __name__ == "__main__":
    main()
