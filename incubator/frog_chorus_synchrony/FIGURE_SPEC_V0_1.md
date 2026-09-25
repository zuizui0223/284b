# Submission figure specification v0.1

## Figure 1 — independent-system design

Purpose: show that the manuscript is not a pooled opportunistic correlation.

Required visual logic:
1. NAAMP discovery: standardized North American 5-min route stops.
2. Frozen rain-recency predictor -> proportion of stops with >=2 calling species.
3. Independent FrogID validation: expert-validated Australian short recordings.
4. FrogID outcome is conditional on >=1 calling species already being present.
5. Both systems feed the same directional biological claim.
6. Spatial robustness is tested within route and within ERA5 cell.
7. Pairwise-network and seasonal-shoulder mechanisms remain explicitly unsupported.

## Figure 2 — primary effects and spatial robustness

Panel A: the two primary logistic effects, shown separately and **not pooled**.
- NAAMP OR 0.9693 [0.9411, 0.9984]
- FrogID OR 0.8528 [0.8273, 0.8792]

The label must state that exposures differ:
- NAAMP: programme DaysSinceRain
- FrogID: ERA5 antecedent dry days

Panel B: fixed-spatial-unit probability-scale diagnostics.
- NAAMP within-route beta -0.01367 [-0.01998, -0.00737]
- FrogID within-cell beta -0.04265 [-0.05175, -0.03354]

No pooled effect or common standardized effect size is authorized.

## Figure style

- 180-mm physical width.
- vector SVG generated from committed receipts.
- monochrome/grayscale-friendly.
- no decorative significance stars.
- exact CIs printed in accompanying caption, not crowded into axis labels.
- “association, not causation” footer on both figures.
