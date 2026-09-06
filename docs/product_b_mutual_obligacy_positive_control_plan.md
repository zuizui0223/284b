# Product-B mutual-obligacy positive-control extension

## Status

This is a hard-invariant example inside the broader paired biological answer-check framework. It is not the framework itself, not a new Product-B generation, and not an empirical authorization.

The general framework is documented in `docs/product_b_paired_answer_check_framework.md`: independently obtained ecological answers are compared only after fitting, using a biological relation declared before focal outcomes are opened. Unexpected divergence is a diagnostic signal. Mutual obligacy is a particularly strong positive-control case because both directions are biologically required.

The constraint class is `mutual_obligacy` and is represented as two necessary directed statements:

- `Y requires X`; and
- `X requires Y`.

The existing `directed_dependency` class remains unchanged.

## Scientific role

The primary use of a mutual-obligacy pair is as a **hard positive control for ecological model cross-checking**.

The question is:

> If two taxa are independently known to be mutually required for persistence, can environmental niche models fitted independently for each taxon recover support surfaces that respect that biological constraint even though the partner relationship was never supplied to model fitting?

This is stronger than asking whether two predicted maps overlap. The pair identity and bidirectional dependency must be established independently of the occurrence/model outcomes.

## Admission boundary

A confirmatory mutual-obligacy pair must be frozen before occurrence inspection and must satisfy all of the following.

1. Independent literature supports both dependency directions at the declared biological scale.
2. The claimed scale is persistence/reproduction, not instantaneous co-detection. Failure to record both partners in the same visit is not itself a biological violation.
3. Known alternative obligate partners, host switches, facultative states, geographic exceptions and life-stage exceptions are declared prospectively.
4. The geographic evaluation frame is defined independently of observed pair overlap.
5. Pair selection does not use GBIF/iNaturalist overlap maps, occurrence counts, fitted suitability, invariant values or process-knockout values.
6. Confirmatory positive controls dominated by deliberate human release, cultivation or experimental placement are excluded or explicitly downgraded to engineering-only.
7. If both taxa are fitted symmetrically, each must independently pass the same predeclared adequacy and sampling requirements. Thresholds are not relaxed after inspection.

## Primary answer-check

Fit X and Y independently from environmental predictors. The partner's occurrence, identity or fitted surface is not a predictor in the other model.

On one frozen common audit space and one predeclared support quantile `q`, compute:

- `C(Y|X)`: Y recovered mass contained in X highest-density support region;
- `C(X|Y)`: X recovered mass contained in Y highest-density support region.

Mutual consistency requires **both** directions to pass the same predeclared containment criterion and both partner breadth/adequacy guardrails.

Decision semantics:

- if either complete admissible direction is `invariant_violated`, the mutual constraint is `invariant_violated`;
- only two consistent directions yield `invariant_consistent_under_frozen_contract`;
- otherwise the result is `unresolved`.

No weighted composite score is permitted.

## Prediction divergence

Raw suitability probabilities are not expected to be numerically identical across taxa because prevalence, calibration and observation processes differ.

Therefore raw probability differences are not a primary test. The extension reports a descriptive `rank_profile_discordance_pair` instead: each taxon's prediction surface is converted to its own percentile-rank profile and the absolute rank disagreement is weighted by joint recovered support. This asks whether the two models place their high-support regions in systematically different parts of the audit space without pretending that `0.8` for one taxon is calibrated identically to `0.8` for another.

Rank discordance can also feed the broader soft paired cross-check, where excessive divergence is `paired_crosscheck_attention_required`. It cannot rescue or override a hard mutual-invariant decision.

## Negative controls

Raw mutual overlap is not sufficient evidence. A future empirical contract must freeze matched non-obligate and/or shuffled-partner controls before outcomes.

The intended positive-control contrast is:

- stronger bidirectional containment for the true mutual pair than for matched/shuffled pairs; and
- descriptively lower rank-profile discordance for the true mutual pair than for controls.

Control availability and matching rules remain response-blind.

## Process knockout

Process necessity is evaluated only after the full model passes the baseline mutual-obligacy constraint.

For each frozen environmental process, intervene without refitting and recompute both directions. A process becomes a candidate `invariant_critical` process only if its removal breaks at least one previously admissible direction under the frozen control-relative rule.

More generally, under the paired answer-check framework, a process can also be diagnostically important if its removal creates or amplifies cross-answer discordance beyond a frozen soft-reference ceiling.

This yields the intended hierarchy:

1. **observability** — can the external biological constraint be represented independently?
2. **identifiability** — can candidate procedures/processes be distinguished structurally?
3. **cross-validity** — do independently fitted answers remain biologically coherent?
4. **necessity** — which process removals destroy or materially degrade that coherence?

## Current execution boundary

Allowed now:

- pure mutual-obligacy metric/classifier functions;
- synthetic tests;
- an empty prospective registry schema;
- response-blind candidate literature search.

Not authorized by this document:

- selecting a pair from observed occurrence overlap;
- opening a mutual-pair empirical invariant result;
- changing existing v5-v7 terminal outcomes;
- treating engineering pairs as confirmatory positive controls.
