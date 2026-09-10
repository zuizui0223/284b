# Product-B same-target core19 empirical result

## Status

This document records the first distinct Product-B same-target endpoint in the current repair sequence that genuinely transitioned from sealed to a terminal empirical result.

Canonical endpoint:

`same_target_cross_source_reproducibility_heldout12_core19_v0_4`

Canonical terminal artifact:

- workflow run: `34439487385`
- artifact: `product-b-same-target-heldout-final-core19-v0-4`
- artifact ID: `10137399646`
- artifact digest: `sha256:c44b250aaa512d564418b2973a8d56c03bf9a800e9a6d89dbfc3d7a40ce4b27a`
- final endpoint fingerprint: `80465bdefd484a8e9d5adcdbd792820ff1716c2b589ff9ad2a278c6c9494646c`

The machine-readable receipt is frozen at:

`results/product_b_same_target_core19_v0_4_heldout_final_receipt.json`

This endpoint/fingerprint pair is a deduplication key and must not be counted again as a new empirical conclusion.

## What was prospectively controlled

The endpoint is a Level-A same-target reconstruction test. Preserved-specimen and human-observation records were used to construct independent ecological answers for the same biological target while holding fixed, within each procedure-by-M cell:

- target identity and estimand;
- active predictor universe (`bio1`–`bio19`);
- estimator/procedure identity;
- M/background semantics;
- the exact 2,000-row comparison frame;
- comparison-row identity;
- adequacy logic;
- the successor-derived reference rule.

The focal held-out outcome was not used to select procedure, M, taxa, or a rescue path.

## Frozen reference

The repaired successor audit sealed 2,255/2,256 successor fit cells, with one unresolved cell retained rather than rescued or dropped. The original pre-D rule remained unchanged: each procedure-by-M reference cell required at least 30 prospectively adequate successor taxa.

Reference calibration run `34439012066` froze all **24/24** procedure-by-M reference cells using the unchanged nearest-rank q95 rule. The minimum number of adequate successor taxa in a frozen reference cell was 34. Held-out paired discordance remained unread through reference calibration.

Reference artifact:

- ID: `10137248940`
- digest: `sha256:b25ff78668b73c19a5e87e66680d06b026ebebb612ae0c94a3ae1fa400d5b535`

## Held-out empirical result

The frozen held-out matrix contained 12 taxa × 3 M values × 8 procedures = **288 cells**.

Observed terminal counts:

- cells audited: **288/288**;
- paired prediction surfaces opened: **283**;
- kept closed because one independent answer failed its predeclared adequacy gate: **5**;
- opened cells within the frozen successor reference ceiling: **283/283**;
- `paired_crosscheck_attention_required`: **0**;
- calibration-unresolved cells: **0**;
- process knockout opened: **false**.

The terminal status is:

`heldout_cross_source_consistent_on_opened_cells`

The five unopened cells are unresolved answer-existence/adequacy cases, not discordance failures. They must not be recoded as either agreement or disagreement.

The opened cell closest to its frozen reference ceiling was:

- taxon: *Nothofagus betuloides*;
- M: 150 km;
- procedure: `predictive_forward|logit_l2_C1_degree2`;
- observed discordance (`1 - Schoener D`): `0.3862495699632878`;
- frozen q95 ceiling: `0.3908491775040753`;
- margin: `-0.0045996075407875`.

Thus every opened held-out cell remained on the consistent side of the prospectively frozen ceiling, but at least one cell was close enough to the boundary that the result should not be paraphrased as trivial or unlimited robustness.

## Empirical claim that is now supported

The supported claim is:

> Under a prospectively frozen same-target design, independently reconstructed ecological answers from preserved-specimen and human-observation sources reproduced on fresh held-out taxa within the source-to-source discordance envelope calibrated from successor taxa.

Equivalently, Product-B now has empirical support for **same-target cross-source answer reproducibility conditional on answer adequacy**.

This is stronger than a feasibility statement. The project no longer only shows that two independent answers can be built; it shows that, when both answers exist and pass adequacy, fresh held-out cross-source answers can satisfy a prospectively calibrated coherence relation.

## What this result does not support

This endpoint does **not** establish:

- that preserved specimens and human observations have identical observation processes;
- that raw suitability values should be equal;
- that all ecological estimators are source-invariant;
- that the same q95 ceiling applies across different taxa, biological roles, life stages, or estimands;
- that a plant-pollinator or other cross-role dependency has been validated;
- that an omitted biological process has been identified;
- that any process is necessary or causal.

Process knockout remained closed, so this endpoint is not direct biological-process falsification or necessity evidence.

## Position in the Product-B hierarchy

The empirical result changes the status of the five-level hierarchy:

1. **Observability** — established for the admitted same-target endpoint.
2. **Identifiability / answer construction** — established for the opened cells; five held-out cells remained unresolved at adequacy and correctly stayed closed.
3. **Relation-space compatibility** — controlled directly because both answers refer to the same target, estimand, M/background frame, and comparison rows.
4. **Cross-validity** — **now empirically supported for Level A**: 283/283 opened held-out cells remained within the frozen successor reference ceiling.
5. **Necessity / process intervention** — still unopened.

The scientific advance is therefore not a jump directly from model fitting to mechanism. It is the first empirical closure of the cross-validity layer under a prospectively frozen independent-answer design.

## Consequence for the broader relation ladder

Level A now serves as an empirically demonstrated controlled case of the independent-answer-check framework. It shows that the framework can produce a nontrivial, fresh, terminal cross-validity result without using focal outcomes to tune the two answers or their tolerance.

However, this result cannot simply be exported upward to Levels B–E. Cross-role and life-stage checks still require role-specific estimators and a prospectively frozen relation-space adapter. Their soft tolerances require relation-specific calibration, and hard dependencies require separately justified biological invariants.

Accordingly, the next scientific frontier is not another same-target rerun. It is a prospectively frozen Level-B/C relation in which two genuinely different biological roles are constructed independently, mapped to a common biological event, and checked without importing the Level-A q95 as a universal tolerance.

## Empirical ledger

This endpoint contributes exactly **one** new 284b empirical conclusion.

Deduplication key:

`same_target_cross_source_reproducibility_heldout12_core19_v0_4:80465bdefd484a8e9d5adcdbd792820ff1716c2b589ff9ad2a278c6c9494646c`

Any future monitoring that encounters the same endpoint and fingerprint must treat it as already reported.