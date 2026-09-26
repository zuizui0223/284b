# Synthetic benchmark specification v0.1

Purpose: strengthen the pre-field Method paper without opening any focal Level-C biological values.

## Question

How often does a hard dependency test produce false biological violations when observation zero is naively treated as `F(k)=false`, and how much does the frozen identifiability rule reduce those false conclusions by routing ambiguous states to `unresolved`?

## Frozen comparison

Compare two decision rules on synthetic event keys with known latent truth:

1. **Naive-zero rule:** if `E_obs=positive` and `F_obs=zero`, declare a hard violation.
2. **Identifiability-gated rule:** declare a hard violation only if `E` is adequately positive and the observation process has prospectively qualified the negative `F` state; otherwise return `unresolved`.

## Synthetic axes

Vary independently:

- true prevalence of `E=true`;
- true prevalence of `F=true` conditional on `E=true`;
- function-detection sensitivity;
- specificity;
- observation-window coverage;
- missingness rate;
- device/observer failure rate;
- event rarity / number of observation opportunities.

No parameter may be estimated from the unopened Level-C focal values.

## Primary outputs

- false hard-violation rate;
- true hard-violation sensitivity;
- fraction routed to `unresolved`;
- false biological-negative rate;
- calibration status under the existing v4 qualification thresholds.

## Required scenarios

At minimum include:

- high sensitivity / low missingness;
- moderate sensitivity with zero missingness;
- sparse-event regime;
- high missingness;
- explicit device/observer failure;
- mixed regime where naive observed zeros are common despite `F=true`.

The existing v4 synthetic suite is a qualification baseline and currently records sensitivity = 0.8, hard FNR = 0.0 and specificity = 1.0 with underpowered/missing/failed states routed to `unresolved`. The manuscript benchmark should generalize beyond those hand-picked qualification cases into a parameter sweep or Monte Carlo surface.

## Figure candidate

A compact two-panel display:

A. False hard-violation probability as detection sensitivity declines, stratified by missingness/coverage.

B. Trade-off between false violation and unresolved fraction for naive versus identifiability-gated rules.

## Interpretation boundary

This benchmark tests inferential behavior of the decision architecture. It is not evidence about Cremastra, Belonocnema, pollination, budbreak, or any focal Level-C biological dependency. It must not be used to estimate candidate-specific detection performance or authorize endpoint opening.
