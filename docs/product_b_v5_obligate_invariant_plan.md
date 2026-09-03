# Product-B v5 — obligate-association invariant plan

## Status

**Design-only / response-blind preflight.** This document does not freeze or authorize an empirical run.

This line does **not** reopen, rescue, retune, rerun, or reinterpret Product-A v2.8.4. It uses only the pre-existing measurement apparatus that can be defined without depending on a Product-A winner: a common audit space, absolute adequacy semantics, observation-corrected recovery semantics, and set-valued ecological candidate handling.

No Product-A scientific experiment is introduced here.

## 1. Goal redirection

### Previous Product-B question

> Freeze a promoted Product-A procedure, then determine which environmental rasters, substitutable groups, and processes are repeatedly necessary to recover niche geometry across unseen taxa.

That formulation is not executable when Product-A supplies no promoted representative.

### Product-B v5 question

> Do recovered niche representations satisfy biologically mandated invariants that the fitting procedure was never allowed to see, and which ecological processes cannot be removed without breaking those invariants?

The universal-driver question is retained. The answer-check changes from unavailable ground-truth niche geometry to an external ecological constraint.

## 2. Core invariant

An obligate association is a declared pair `(X, Y)` with independently justified biology at a declared association scale.

For a directed dependence `Y requires X`, the invariant is **nesting, not identity**:

> The recovered realized-niche support of `Y` should be contained within the recovered realized-niche support of `X` in the frozen common audit space and at the declared grain.

For bidirectional obligacy, evaluate both directed statements separately. Do not reduce bidirectional obligacy to a symmetric distance alone.

### Direction semantics

Only the dependent taxon's recovered support extending outside the required partner counts as a directional violation. A dependent taxon being substantially narrower than its required partner is expected and is not itself a violation.

## 3. Three-state answer semantics

Every directed pair evaluation ends in exactly one state:

- `invariant_violated`: a complete admissible witness shows that directional nesting fails.
- `invariant_consistent_under_frozen_contract`: the recovered representation is consistent with the declared invariant under the frozen analysis contract.
- `unresolved`: evidence is incomplete, adequacy fails, sampling rules fail, a breadth guardrail fails, or the predeclared evaluation cannot be completed.

Passing constrains the recovered representation; it does not establish biological truth or fundamental-niche correctness.

## 4. Primary quantities

All quantities are defined on a common set of audit cells/points. Support vectors are non-negative recovered masses normalized internally.

1. `directed_containment(Y|X, q)`
   - Construct the predeclared `q` highest-density support region of `X` by descending recovered mass until cumulative mass reaches `q`.
   - Return the fraction of normalized `Y` mass falling inside that region.
   - `q` belongs to a predeclared sensitivity set; it is never chosen after outcomes are opened.

2. `schoener_d_pair(X, Y)`
   - `1 - 0.5 * sum(|p_X - p_Y|)` for normalized support masses on the same audit cells.
   - Reported descriptively; it does not replace the directional invariant.

3. `centroid_separation_pair(X, Y)`
   - Euclidean separation between probability-weighted centroids in the common audit coordinates (normally PC1-PC2).

4. `breadth_ratio_pair(Y, X)`
   - Breadth is the weighted root-mean-square distance from the support centroid in the common audit space.
   - Report `breadth_Y / breadth_X` and `breadth_X` itself.
   - This definition is fixed before empirical outcomes. A zero-breadth denominator is unresolved rather than silently regularized.

5. `adequacy_both`
   - Both partners must independently pass the absolute prediction-adequacy gate.
   - Failure of either partner yields `unresolved`, not `invariant_violated`.

No weighted composite or single concordance score is permitted.

## 5. Mandatory trap closures

### 5.1 Same-record contamination

Before any outcome is opened, exclude record pairs sharing any declared lineage or collection identity, including:

- occurrence-ID lineage;
- event ID;
- catalog/specimen number;
- dataset key + event date + coordinate;
- recorder + date + coordinate.

The excluded count is a denominator-level result. If the exclusion removes the usable denominator for a pair, classify that pair `unresolved`.

### 5.2 Sampling asymmetry

Freeze before outcomes:

- minimum records per partner;
- minimum unique cells per partner;
- maximum admissible record-count / cell-count asymmetry ratio.

Pairs outside the declared admissible range are `unresolved`.

### 5.3 Trivial satisfaction by broad prediction

A broad support for the required partner can make nesting trivial. Therefore:

- `adequacy_both` is mandatory;
- absolute `breadth_X` is always reported;
- a predeclared maximum admissible required-partner breadth may convert the pair to `unresolved` rather than reward trivial breadth.

### 5.4 Grain mismatch

The invariant is evaluated only at the declared SDM audit grain. Manuscript language must not infer individual- or site-level co-occupancy from grid-cell-scale nesting.

### 5.5 Real biological narrowing

Dispersal limitation, additional partners, historical contingency, or other constraints may make `Y` much narrower than `X`. This does not violate the directional invariant.

## 6. Negative controls

Both control families are mandatory and must be frozen before outcomes.

### Matched non-obligate pairs

Match non-obligate pairs to obligate pairs using a response-blind rule based on at least:

- record count;
- unique-cell count;
- spatial extent;
- taxonomic distance.

### Shuffled-partner null

Repair each obligate species to a random non-obligate partner satisfying the same response-blind matching rule. Freeze random seeds before any outcome is opened.

### Primary contrast

The empirical quantity of interest is obligate-pair directional containment **relative to the matched/shuffled control distribution**, not raw nesting alone.

## 7. Process-exclusion semantics

For every declared ecological process `p`:

1. Assign every predictor/proxy belonging to `p` before outcomes.
2. Reconstruct each already-fitted fold model once from frozen selected predictors.
3. Intervene on `p` without refitting.
4. Marginalize the intervened process over a deterministic model-pool background reference while leaving non-intervened predictors at the evaluation row.
5. Recompute the obligate-vs-control invariant contrast.

No post-knockout refitting is allowed.

Classify each process across the complete adequate, ecologically non-dominated procedure set:

- `invariant_critical`: knockout breaks the obligate-relative-to-control invariant in at least the predeclared required fraction of admissible pairs/set members;
- `substitutable`: the invariant survives according to the frozen rule;
- `unresolved`: evidence is incomplete or the decision rule cannot be applied.

Set-valued heterogeneity is a result. Do not collapse the procedure set to a single representative for convenience.

## 8. Response-blind differentiability pre-check

This pre-check uses model-pool metadata/structure only. It must run before sealed data, invariant outcomes, or environmental values are opened.

Required checks:

1. `candidate_set_size > 1` after adequacy/ecological admissibility filtering.
2. Every declared process has at least one admissible frozen knockout target and leaves at least one non-intervened predictor/evaluable path where required by the implementation.
3. Candidate universes/strategies produce more than one distinct frozen selected-predictor signature.

### Proposed stop floor for this prototype

The preflight passes only when all are true:

- at least 2 admissible procedure members;
- at least 2 distinct selected-predictor signatures;
- every declared process knockout is structurally admissible.

Otherwise stop before outcomes are opened. The floor is part of the future contract and can only be changed before authorization, never in response to results.

## 9. Forbidden preflight reads or outputs

Preflight code must not read or emit any of the following values:

- `directed_containment`;
- `schoener_d_pair`;
- `centroid_separation_pair`;
- `breadth_ratio_pair`;
- any matched-control or shuffled-control contrast;
- any per-process knockout outcome;
- any sealed environmental value;
- any partner-specific invariant state;
- any downstream promotion/ranking derived from invariant outcomes.

Preflight may inspect field names, declared process membership, procedure IDs, strategy IDs, predictor names/signatures, and other response-blind structural metadata needed for differentiability.

## 10. Pair registry contract

The registry is a declaration artifact, not an occurrence-derived table. It must be populated from independent biological evidence before occurrence inspection.

Required schema is stored at `registry/obligate_pair_registry_schema.csv`.

Direction values are exactly:

- `X_requires_Y`
- `Y_requires_X`
- `bidirectional`

Admissible obligacy classes must be declared explicitly rather than inferred from co-distribution.

## 11. Cross-kingdom extension

Cross-kingdom pairs are optional. If used, freeze before outcomes:

- a target-group background frame per kingdom;
- a response-blind density/concentration asymmetry ceiling;
- kingdom-specific observation-correction activation reporting;
- a `do_not_conclude` statement that mobile-animal occurrence does not establish habitat use.

If the pre-check fails the asymmetry ceiling, stop before opening outcomes.

## 12. Claim boundary

Product-B v5 may support only contract-relative claims.

- Invariant consistency is not evidence of fundamental-niche recovery.
- It does not establish causal physiological requirement, demographic fitness, dispersal history, or interaction strength.
- Obligate-pair nesting is an answer-check, not ground truth.
- `invariant_critical` means candidate necessity only under the frozen evidence contract.
- Cross-kingdom differences are differences in recorded realized environmental distributions under declared observation semantics, not established ecological differences.

## 13. Explicitly out of scope for this branch step

Do not, in this step:

- fetch GBIF or other occurrence data;
- populate the registry from occurrence inspection;
- compute any empirical invariant outcome;
- inspect sealed environmental values;
- freeze the final empirical contract;
- authorize a one-shot execution;
- rerun or alter Product-A.

The branch should stop after design artifacts, pure metric/classifier functions, response-blind preflight logic, and synthetic tests are present.