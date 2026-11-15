#!/usr/bin/env python3
"""Retrospective Level-A reference-transfer audit (NOT a new confirmatory endpoint).

Inputs: frozen core19 reference/heldout CSVs from GitHub Actions artifacts.
No model fitting, new source sampling, biological mismatch labels or Level-C opening.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median

EXPECTED_SHA256 = {
    "core19_heldout_final_cells.csv": "d9194ea416dcc3bbae339167e271d3cbcd522327b41fe573325770a94bd90b0d",
    "core19_pairing_cells.csv": "3fc1a76e78fb1581b20fd15a129fb82775b196658b8329c612d3b513dc4a869c",
    "core19_reference_ceiling.csv": "10759c6e0ffc70ff403c0eabd9c7ce30765ebbf1ce6403fa29562a7c7bb2b039",
}


def read_verified(path: Path):
    assert path.name in EXPECTED_SHA256
    assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED_SHA256[path.name]
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def nearest_rank(values, q=.95):
    if not values or not 0 < q <= 1:
        raise ValueError("nonempty sample and 0 < q <= 1 required")
    return sorted(values)[math.ceil(len(values) * q) - 1]


def key(row):
    return (int(row["M_km"]), row["procedure"])


def truth(row, field):
    assert row[field] in ("True", "False")
    return row[field] == "True"


def audit(heldout_csv: Path, reference_csv: Path, ceiling_csv: Path):
    heldout, reference, ceilings = (
        read_verified(heldout_csv), read_verified(reference_csv), read_verified(ceiling_csv)
    )
    assert (len(heldout), len(reference), len(ceilings)) == (288, 1128, 24)
    for rows in (heldout, reference):
        assert len({(x["taxon"], *key(x)) for x in rows}) == len(rows)

    source = defaultdict(list)
    for row in reference:
        if truth(row, "calibration_contribution_authorized"):
            assert truth(row, "paired_prediction_surface_opened")
            d = float(row["one_minus_schoener_d"])
            assert math.isfinite(d) and 0 <= d <= 1
            source[key(row)].append((row["taxon"], d))
    assert len(source) == 24 and sum(len(v) for v in source.values()) == 1024
    assert min(len(v) for v in source.values()) >= 34

    fixed = {}
    for row in ceilings:
        k = key(row)
        vals = [d for _, d in source[k]]
        assert len(vals) == int(row["authorized_distinct_calibration_taxa"])
        v = float(row["one_minus_schoener_d_reference_ceiling"])
        assert math.isclose(v, nearest_rank(vals), rel_tol=0, abs_tol=1e-12)
        fixed[k] = v
    assert len(fixed) == 24

    held = []
    unresolved = []
    for row in heldout:
        k = key(row)
        if not truth(row, "paired_prediction_surface_opened"):
            assert row["paired_state"] == "paired_crosscheck_unresolved"
            unresolved.append(row)
            continue
        assert truth(row, "preserved_specimen_adequate")
        assert truth(row, "human_observation_adequate")
        assert row["paired_state"] == "paired_crosscheck_consistent"
        d, v = float(row["one_minus_schoener_d"]), float(row["frozen_reference_ceiling"])
        assert 0 <= d <= v <= 1 and math.isclose(v, fixed[k], rel_tol=0, abs_tol=1e-12)
        ecdf = sum(x <= d for _, x in source[k]) / len(source[k])
        held.append({"taxon": row["taxon"], "distance": d, "ceiling": v,
                     "ratio": d/v, "reference_ecdf": ecdf, "key": k})
    assert len(held) == 283 and len(unresolved) == 5
    assert len({r["taxon"] for r in heldout}) == 12
    assert math.isclose(max(r["ratio"] for r in held), .988232, abs_tol=1e-6)

    hgroup = defaultdict(list)
    for row in held:
        hgroup[row["taxon"]].append(row)
    htaxa = [
        {"taxon": name, "evaluable": len(rows),
         "maximum_observed_to_reference_ratio": max(r["ratio"] for r in rows),
         "mean_discordance": mean(r["distance"] for r in rows),
         "median_reference_ecdf": median(r["reference_ecdf"] for r in rows)}
        for name, rows in sorted(hgroup.items())
    ]

    # Every reference taxon is evaluated against q95 refit on OTHER taxa only.
    # Not a random out-of-sample test, and reference taxa may be dependent.
    rgroup = defaultdict(list)
    for k, rows in source.items():
        assert len({name for name, _ in rows}) == len(rows)
        for name, d in rows:
            others = [x for other_name, x in rows if other_name != name]
            assert len(others) >= 33
            cutoff = nearest_rank(others)
            rgroup[name].append((d, cutoff, d > cutoff))
    assert len(rgroup) == 47
    rtaxa = [
        {"taxon": name, "evaluable": len(rows),
         "exceedances": sum(int(x[2]) for x in rows),
         "maximum_observed_to_loo_ratio": max(d/c for d, c, _ in rows),
         "mean_discordance": mean(x[0] for x in rows)}
        for name, rows in sorted(rgroup.items())
    ]
    nexceed = sum(x["exceedances"] > 0 for x in rtaxa)
    ncells = sum(x["exceedances"] for x in rtaxa)
    assert (nexceed, ncells) == (11, 65)

    # Descriptive alternatives; neither has independently known biological truth.
    pooled = nearest_rank([d for rows in source.values() for _, d in rows])
    pooled_fail = [x for x in held if x["distance"] > pooled]
    stress = {}
    for delta in (.025, .05, .10, .20):
        hits = [x for x in held if min(1., x["distance"] + delta) > x["ceiling"]]
        stress[str(delta)] = {"cells": len(hits),
                              "taxa": len({x["taxon"] for x in hits})}
    result = {
        "schema": "284b.level_a_retrospective_discriminability_audit.v1",
        "status": "exploratory_posthoc_not_confirmatory",
        "source_artifact_ids": {"heldout": 10137399646, "reference": 10137248940},
        "sha256_inputs": EXPECTED_SHA256,
        "original_endpoint_modified": False,
        "empirical_ledger_increment": 0,
        "heldout": {
            "taxa": len(hgroup), "cells": len(heldout), "evaluable": len(held),
            "unresolved": len(unresolved), "taxa_exceeding_original_frozen_q95": 0,
            "cell_weighted_mean_discordance": mean(x["distance"] for x in held),
            "cell_weighted_median_reference_ecdf": median(x["reference_ecdf"] for x in held),
            "cells_below_reference_median": sum(x["reference_ecdf"] < .5 for x in held),
            "taxon_table": htaxa,
        },
        "reference": {
            "taxa": len(rgroup), "evaluable_cells": sum(map(len, source.values())),
            "cell_weighted_mean_discordance":
                mean(d for rows in source.values() for _, d in rows),
            "loo_taxa_with_exceedance": nexceed, "loo_cells_with_exceedance": ncells,
            "loo_taxa_without_exceedance": len(rgroup)-nexceed,
            "loo_taxon_table": rtaxa,
        },
        "exploratory_comparators": {
            "pooled_q95": pooled, "heldout_cells_above_pooled_q95": len(pooled_fail),
            "heldout_taxa_above_pooled_q95": sorted({x["taxon"] for x in pooled_fail}),
            "additive_distance_stress_only": stress,
        },
        "limitations": [
            "Reference LOO reuses the same taxon panel and cannot establish a nominal false-alarm rate.",
            "Reference and heldout taxa are not exchangeable random samples.",
            "Each taxon contributes correlated procedure-by-area cells, not independent replicates.",
            "Pooled q95 ignores procedure/area heterogeneity; flagged pairs have no ground-truth labels.",
            "Additive-distance stress is algebraic, not a biological mismatch or a sensitivity estimate.",
            "No real hard-relation violation, Level-C effect, or causal mechanism is tested.",
        ],
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--heldout", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--ceilings", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.heldout, args.reference, args.ceilings)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)+"\n",
                        encoding="utf-8")
    print(json.dumps({
        "heldout": result["heldout"]["taxa_exceeding_original_frozen_q95"],
        "ref_loo_taxa": result["reference"]["loo_taxa_with_exceedance"],
        "ref_loo_cells": result["reference"]["loo_cells_with_exceedance"],
        "pooled_q95_cells": result["exploratory_comparators"]["heldout_cells_above_pooled_q95"],
    }))


if __name__ == "__main__":
    main()
