#!/usr/bin/env python3
"""Promote the sanitized grouped successor sampling audit to canonical schema."""
from __future__ import annotations

import json
from pathlib import Path

from product_b_v5.sampling_promotion import promote_grouped_successor_sampling

ROOT = Path(__file__).resolve().parents[1]
GROUPED = ROOT / "results/product_b_same_target_successor_source_mode_sampling_grouped_v0_1.json"
CONTRACT = ROOT / "config/product_b_same_target_successor_sampling_promotion_contract_v0_1.json"
OUTPUT = ROOT / "results/product_b_same_target_successor_source_mode_sampling_v0_1.json"


def main() -> int:
    grouped = json.loads(GROUPED.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    canonical = promote_grouped_successor_sampling(grouped, contract)
    OUTPUT.write_text(
        json.dumps(canonical, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "source_mode_sampling_passed": canonical["source_mode_sampling_passed"],
        "source_mode_sampling_unresolved": canonical["source_mode_sampling_unresolved"],
        "model_fit_authorized": canonical["model_fit_authorized"],
        "transport_only_promotion": canonical["promotion_provenance"]["transport_only_promotion"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
