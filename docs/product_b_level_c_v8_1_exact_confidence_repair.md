# Product-B Level-C v8.1 — prospective exact-confidence repair

## Why v8.1 exists

The frozen v8 operational package declared a `one_sided_95_percent_exact_or_more_conservative` confidence rule, but its evaluator implemented a one-sided Wilson score lower bound. Wilson intervals are asymptotic score intervals rather than exact binomial intervals, so the implementation did not literally satisfy the frozen contract.

This mismatch was identified during pre-field manuscript preparation **before any field-calibration data were entered, inspected, or used for decision making**.

## Repair boundary

v8 remains immutable as the historical frozen package. v8.1 is a separate prospective repair and changes only the confidence-bound implementation.

Unchanged:

- retained candidates: `CREMV3-007`, `BELV3-012`;
- minimum resolved gold positives: 30;
- minimum resolved gold negatives: 60;
- sensitivity threshold: >= 0.80;
- hard false-negative-rate threshold: <= 0.20;
- specificity threshold: >= 0.95;
- one-sided confidence level: 95%;
- candidate-specific opening;
- explicit separation of missing/device failure/observer failure/occlusion/unresolved adjudication from biological negatives;
- no candidate replacement or threshold relaxation;
- no post-hoc sample-size extension after observed failure;
- calibration pass is not a biological conclusion and does not increment the empirical ledger.

Changed:

- the lower confidence bounds are now exact one-sided Clopper-Pearson bounds, computed by exact binomial-tail inversion.

## Minimum-count implications

At the frozen minimum sample sizes and one-sided 95% exact rule:

- sensitivity requires at least **28/30** known-positive units to put the exact lower bound at or above 0.80;
- specificity requires **60/60** known-negative units to put the exact lower bound above 0.95.

Thus a clean 30/30 positive and 60/60 negative calibration still passes exactly as v8 documented. One false positive among the minimum 60 negatives fails the specificity confidence rule. These are consequences of the already-frozen thresholds and confidence requirement, not new threshold choices.

## Scientific status

This is a pre-data implementation repair, not empirical evidence. No Level-C focal cross-role value, hard invariant, soft cross-check, or process knockout is opened. The 284b empirical ledger remains 1.

Canonical repair artifacts:

- `config/product_b_level_c_operational_package_v8_1.json`
- `scripts/evaluate_level_c_field_calibration_v8_1.py`
- `tests/test_level_c_operational_package_v8_1.py`

Before field calibration is executed, the operating characteristics of the fixed minimum sample sizes should be audited prospectively so that any choice to collect more than the minima is made before outcomes are known rather than as a rescue after failure.
