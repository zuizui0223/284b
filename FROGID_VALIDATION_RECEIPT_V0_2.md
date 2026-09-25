# FrogID independent rain-synchrony validation receipt v0.2

The prospectively frozen external validation **passes**.

## Frozen sample

- 40,754 FrogID recordings
- 18,174 recordings with >=2 calling species
- 1,623 ERA5 0.25-degree weather cells
- 13,148 recorders
- all retained recordings also satisfy <=10 km coordinate uncertainty

Weather was extracted from Earthmover's public Icechunk ERA5 `tp` variable using the final frozen local-calendar-day aggregation. The validation read 470 ERA5 chunks.

## Primary

`z(log1p antecedent dry days)`:

- beta = **-0.1592**
- cluster-robust SE = 0.0155
- 95% beta CI = **[-0.1896, -0.1288]**
- OR = **0.8528**
- 95% OR CI = **[0.8273, 0.8792]**
- p = **1.13e-24**
- frozen support rule: **PASS**

Recorder-clustered sensitivity also passes (p = 6.19e-33).

## Biological interpretation

FrogID recordings are already conditioned on an acoustically active event: each retained recording contains at least one expert-validated calling frog species.

Therefore this validation is stronger than a generic “rain activates frogs” result. Within active calling events, **multi-species calling is more likely closer to recent rainfall**.

This independently supports the direction found in NAAMP.

## Boundaries

- This is an observational association, not a causal rainfall manipulation.
- It does not imply pairwise facilitation among frog species.
- It does not replace the NAAMP primary endpoint.
- No sample, rain threshold, dry-spell cap, transform, state/month subset, or support rule was retuned after opening.
