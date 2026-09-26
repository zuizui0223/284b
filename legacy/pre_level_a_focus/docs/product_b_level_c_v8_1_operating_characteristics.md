# Product-B Level-C v8.1 — prospective calibration operating characteristics

## Question

The v8/v8.1 package specifies minimum resolved calibration counts of 30 known-positive and 60 known-negative units. Those minima make a pass mathematically possible, but how likely is a pass under different true observation-process performance levels?

This audit is performed before field calibration. It reads no candidate calibration outcomes and no focal Level-C values.

## Exact minimum-design decision boundaries

Under the v8.1 one-sided 95% exact Clopper-Pearson rule:

- sensitivity floor 0.80 with `n_pos=30` requires at least **28/30** detected known-positive units;
- specificity floor 0.95 with `n_neg=60` requires **60/60** correctly classified known-negative units.

Thus the documented clean 30/30 + 60/60 design passes, but the minimum counts should be understood as feasibility minima rather than as a power-optimized design.

## Nominal probability of passing at the minimum counts

If independent positive calibration units have true sensitivity:

- 0.80 -> pass probability 0.0442;
- 0.85 -> 0.1514;
- 0.90 -> 0.4114;
- 0.95 -> 0.8122;
- 0.98 -> 0.9783;
- 0.99 -> 0.9967.

If independent negative calibration units have true specificity:

- 0.95 -> pass probability 0.0461;
- 0.97 -> 0.1608;
- 0.98 -> 0.2976;
- 0.99 -> 0.5472;
- 0.995 -> 0.7403;
- 0.999 -> 0.9417.

The low pass probability at a true rate equal to the qualification threshold is expected: requiring a 95% lower confidence bound to exceed that threshold is a stronger evidentiary condition than merely observing a point estimate above it.

## Sample-size planning examples

Under independent binomial calibration units, the first predeclared sample size reaching at least 80% nominal probability of passing is:

Sensitivity threshold 0.80:

- true sensitivity 0.85 -> `n=365`, critical successes 305;
- true sensitivity 0.90 -> `n=82`, critical successes 72;
- true sensitivity 0.95 -> the minimum `n=30`, critical successes 28.

Specificity threshold 0.95:

- true specificity 0.97 -> `n=601`, critical successes 580;
- true specificity 0.98 -> `n=234`, critical successes 228;
- true specificity 0.99 -> `n=124`, critical successes 122;
- true specificity 0.995 -> `n=93`, critical successes 92;
- true specificity 0.999 -> the minimum `n=60`, critical successes 60.

## Interpretation

This does **not** justify increasing sample size after looking at field outcomes. The opposite: if a larger planned calibration is desired, its sample size must be frozen before data collection or outcome inspection.

These calculations also assume independent binomial calibration units. Flowers on the same inflorescence or repeated scores on the same tree may be correlated. The candidate-specific field design must therefore define the inferential unit and clustering structure before collection. Nominal binomial operating characteristics are a planning baseline, not a substitute for that design choice.

No sample-size change is authorized by this audit. It identifies a decision that should be made prospectively before field data are entered.

Canonical audit:
- `scripts/audit_level_c_calibration_operating_characteristics_v8_1.py`
- `results/level_c_calibration_operating_characteristics_v8_1.json`

Empirical ledger increment: 0.
