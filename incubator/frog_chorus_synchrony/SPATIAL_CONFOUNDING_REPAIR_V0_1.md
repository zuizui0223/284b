# Spatial-confounding diagnostic repair v0.1.1

The original FrogID spatial diagnostic specified conditional logistic regression with ERA5-cell strata.

That implementation failed **before any FrogID within-cell coefficient was produced** because `statsmodels.ConditionalLogit` recursively evaluates large strata and exceeded Python's recursion depth.

No biological effect value, sign, confidence interval or p-value was opened.

## Repair

The scientific estimand is unchanged: use only weather variation **within the same 0.25-degree ERA5 cell**.

The repaired estimator is a fixed-effects linear-probability diagnostic implemented by exact within-cell demeaning:

- outcome: one vs multiple calling species;
- predictor: frozen `dry_z`;
- adjustments: month indicators, year, local-hour sine/cosine;
- every variable is demeaned within ERA5 cell;
- no intercept;
- SEs are cluster-robust by ERA5 cell.

This is the linear fixed-effects analogue of the already successful NAAMP within-route diagnostic. It is not used to replace the primary logistic odds ratio.

The no-upgrade and no-retuning rules from v0.1 remain in force.
