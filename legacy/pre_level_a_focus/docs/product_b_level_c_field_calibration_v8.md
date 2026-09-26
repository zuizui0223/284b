# Product B Level-C field calibration operational package v8

This package operationalizes the v7 prospective field-calibration design without changing any scientific threshold or candidate identity.

## Frozen systems

- `CREMV3-007` — Cremastra
- `BELV3-012` — Belonocnema

No new candidate search, replacement, prior-system rescue, Level-A q95 import, or post hoc threshold relaxation is authorized.

## Field workflow

1. Collect calibration-only observations using the v7 candidate-specific design.
2. Enter one resolved calibration unit per row in `registry/level_c_field_calibration_v8_template.csv`.
3. Record any device failure, observer failure, missingness, occlusion, or unresolved adjudication explicitly. Such rows cannot carry a biological negative classification.
4. Run `scripts/evaluate_level_c_field_calibration_v8.py` separately for each candidate.
5. Preserve the resulting JSON as the calibration receipt.
6. Endpoint opening is authorized only when `opening_authorized=true` for that candidate.

## Frozen decision rule

For each candidate independently:

- resolved gold-positive units >= 30;
- resolved gold-negative units >= 60;
- sensitivity >= 0.80;
- hard false-negative rate <= 0.20;
- specificity >= 0.95;
- one-sided 95% confidence lower bounds for sensitivity and specificity must also exceed the corresponding thresholds;
- QC and missingness separation must pass.

A clean 30/30 positive and 60/60 negative result passes. Sample-size extension after observed failures cannot be used as post hoc rescue.

## Interpretation boundary

A calibration pass is not a biological conclusion and does not increment the empirical ledger. It only permits a later, separately frozen endpoint-opening stage for that candidate. Until that later stage is completed, focal cross-role values, hard invariants, soft cross-checks, and process knockouts remain closed.
