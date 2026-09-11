# Synthetic negative-state benchmark result v0.1

## Status

This is a pre-field, synthetic inferential result. It reads no focal Level-C biological values, does not estimate candidate-specific detection performance, does not authorize endpoint opening, and does not increment the 284b empirical ledger.

Canonical code: `scripts/run_pre_field_identifiability_benchmark.py`  
Canonical summary: `results/pre_field_identifiability_benchmark_summary_v0_1.json`  
Representative scenarios: `results/pre_field_identifiability_benchmark_scenarios_v0_1.csv`

## Two rules

For an event key with `E=true`, compare:

1. **naive zero-as-absence** — invalid observation or a valid non-detection is treated as `F=false`;
2. **identifiability-gated** — `F=false` is eligible only when the observation process passes the frozen sensitivity/specificity gate and the key has complete, nonmissing, nonfailed observation.

Let

- `q` = key-level sensitivity `P(at least one detection | at least one true functional event)`;
- `sp` = key-level specificity;
- `v` = fraction of keys with complete, nonmissing, nonfailed observation.

The frozen qualification floor is `q >= 0.80` and `sp >= 0.95`.

## Exact identities

Conditional on a biologically compatible key (`F=true`):

`FPR_naive = 1 - v q`

and, when the process qualifies,

`FPR_gated = v (1 - q)`.

Therefore

`FPR_naive - FPR_gated = 1 - v`.

Conditional on a true violation (`F=false`):

`TPR_naive = 1 - v (1 - sp)`

and, when the process qualifies,

`TPR_gated = v sp`.

Therefore

`TPR_naive - TPR_gated = 1 - v`.

The apparent sensitivity gain of zero-as-absence is thus exactly the probability mass of incomplete, missing or failed observation keys. It is not additional biological information. The same invalid-state mass is added to the false-violation rate.

When the observation process fails calibration, the gated rule makes no hard calls and routes the relevant zero states to `unresolved`.

## Exact grid

The deterministic sweep spans 8,748 combinations of:

- violation prevalence: 0.05, 0.10, 0.20, 0.50;
- per-opportunity functional-event probability: 0.05, 0.20, 0.50;
- event detection sensitivity: 0.50, 0.80, 0.95;
- opportunities per key: 1, 5, 20;
- complete-window fraction: 0.50, 0.80, 1.00;
- missingness: 0, 0.10, 0.30;
- device/observer failure: 0, 0.05, 0.20;
- specificity: 0.80, 0.95, 0.99.

Of 8,748 grid points, 4,320 meet the frozen calibration floor and 4,428 do not. Across every qualifying grid point, gated false-violation probability is bounded by 0.20, exactly as implied by the frozen key-sensitivity floor. The largest naive false-violation probability among those same calibration-passing grid points is 0.776 because invalid keys are converted into biological negatives.

The two exact invalid-state identities above hold across the full passing grid to floating-point error below `1.2e-16`.

## Representative cases

### Fully observed, high-information key

With dense functional opportunity, key sensitivity is approximately 0.999998 and `v=1`. Naive and gated rules coincide: false-violation probability is approximately `1.6e-6`.

### 30% missingness with otherwise near-perfect detection

Key sensitivity remains approximately 0.999998 but `v=0.70`. The naive false-violation probability becomes approximately 0.300001, whereas the gated probability remains approximately `1.1e-6` and 30% of keys are explicitly unresolved.

### 20% device/observer failure

With the same near-perfect valid-key detection but `v=0.80`, naive false-violation probability is approximately 0.200001. The gated rate is approximately `1.3e-6`; the 20% failure mass is unresolved.

### 50% incomplete-window keys

With `v=0.50`, naive false-violation probability is approximately 0.500001 even though valid-key detection is near perfect. The gated rate is below `8e-7`, with half the keys unresolved.

### Mixed qualified regime

For key sensitivity 0.8653, specificity 0.95 and `v=0.684`, the naive false-violation probability is 0.4081 and the gated rate is 0.0921. Their difference is exactly 0.316, the invalid-key mass. The naive true-violation sensitivity is 0.9658 versus 0.6498 gated; that same 0.316 apparent gain is again entirely attributable to treating invalid keys as biological negatives.

### Below calibration

At key sensitivity 0.50, a fully observed naive rule produces a 0.50 false-violation probability. The gated rule produces no hard calls and routes zeros to unresolved. Likewise, specificity below 0.95 blocks hard calls even when sensitivity is near one.

## Important threshold interpretation

The current `q >= 0.80` calibration threshold is an **endpoint-opening qualification floor**, not a statement that a single calibrated zero is sufficient evidence for a final biological dependency violation. At the threshold and `v=1`, key-level false-negative probability can still be 0.20. A later focal endpoint must therefore freeze its own aggregation or replication rule before values are opened. The pre-field manuscript must not convert the v8 calibration pass into a biological conclusion.

## Manuscript consequence

The benchmark supplies a method-level result independent of the two retained Level-C systems:

> Preserving `unresolved` is not merely conservative bookkeeping. Under a qualified observation process, collapsing invalid states into zero adds exactly the invalid-state probability mass to both apparent violation sensitivity and false-violation probability.

This is the transferable methodological result that should anchor the Ecology Letters Method framing alongside the Level-A empirical demonstration.
