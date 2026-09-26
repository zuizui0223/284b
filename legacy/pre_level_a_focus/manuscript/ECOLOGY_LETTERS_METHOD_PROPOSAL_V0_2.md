# Ecology Letters — unsolicited Method proposal package v0.2

## Working title

**Prospective validation of ecological answers: from cross-source reproducibility to identifiable biological absence**

Alternative short titles:

- **When ecological absence becomes evidence**
- **From reproducibility to dependency in ecological inference**
- **Identifiable absence for hard ecological dependency tests**

## Proposed article type

**Method**

The submission is framed as a transferable inferential technique, not as a review of the 284b project and not as a taxon-specific biological paper.

## <=300-word proposal text

Ecologists increasingly combine answers reconstructed from heterogeneous observation sources, model classes and biological roles, yet reproducibility and biological dependency require different evidence. We introduce a prospective answer-check framework that freezes the ecological relation, biological event, relation-space adapter, adequacy gates and calibration before focal outcomes are opened. Role-specific estimators remain allowed; comparability is created only after projection to a common biological event space.

We first test the controlled same-target case using independent preserved-specimen and human-observation reconstructions. A successor panel prospectively froze 24 procedure-by-accessible-area reference cells before a 12-taxon held-out endpoint was opened. Of 288 held-out cells, 283 passed both source-specific adequacy gates and all 283 remained within their frozen source-discordance ceilings; five remained unresolved.

We then derive and benchmark the additional requirement for hard cross-role dependency. For event-to-function tests `E(k) -> F(k)`, we separate detected function, calibrated functional absence and unresolved observation. An exact 8,748-scenario synthetic sweep shows that, whenever the observation process qualifies, the excess apparent violation sensitivity of a naive “zero = absence” rule is exactly the mass of incomplete, missing or failed observation keys; the same mass is added to its false-violation rate. When calibration fails, our rule makes no hard calls.

Prospective candidate screens locate two fresh cross-role systems with independently separated relation, dependent-event and required-function streams, but both stop before focal opening because functional absence is not independently calibrated. The framework therefore turns a vague caution about non-detection into an auditable identifiability criterion and stopping rule, transferable to interaction ecology, host dependence, life-stage coupling, sensor ecology and distribution-based process inference.

**Word count:** 254 words.

## Why this is a Method rather than a Perspective

The novel object is an executable decision architecture with measurable statistical behavior:

1. relation/event/adapters are frozen prospectively;
2. answer existence and adequacy are separated from relation validity;
3. cross-role comparisons occur after role-specific answer construction;
4. hard negatives require calibrated negative-state identifiability;
5. invalid states are preserved as `unresolved` rather than silently promoted to biological negatives.

The paper derives the exact error decomposition of the zero-as-absence shortcut and supplies code that reproduces the benchmark.

## Statistical-performance component

For a qualified process with valid-key fraction `v`, key sensitivity `q` and specificity `sp`:

`FPR_naive - FPR_gated = 1-v`

`TPR_naive - TPR_gated = 1-v`.

Thus the apparent sensitivity gain of zero-as-absence is exactly the invalid-observation mass, and the same quantity is added to false violations. The result is exact, not simulation-noise dependent. The declared 8,748-scenario grid stress-tests the identities across event rarity, detection, opportunities, coverage, missingness, failure, specificity and violation prevalence.

## Case-study component

The controlled case study is the completed Level-A held-out endpoint:

- 24 prospectively frozen successor reference cells;
- 288 held-out cells;
- 283 eligible openings;
- 283/283 within frozen reference ceilings;
- 5 unresolved at predeclared adequacy;
- zero post-hoc rescue.

The Level-C sequence then serves as a second, deliberately unopened stress test showing where real ecological systems hit the negative-state-identifiability boundary.

## Transferability

The technique is defined on event/function relations rather than on any focal taxon. Immediate use cases include pollination, host dependence, trophic interactions, life-stage transitions, sensor-based interaction studies and distribution-based process attribution.

## Open-code component

Canonical implementation and tests:

- `scripts/run_pre_field_identifiability_benchmark.py`
- `tests/test_pre_field_identifiability_benchmark.py`
- prospective relation and Level-C implementation modules already versioned in the repository.

The benchmark uses only the Python standard library and exact formulas, making the central performance result independently reproducible.

## Author-qualification sentence for the email

Suggested concise wording:

> The lead author works across empirical pollination ecology, species-distribution modelling and reproducible computational inference, and the manuscript arises from a versioned prospective-validation programme spanning controlled cross-source reconstruction and cross-role ecological dependency.

This sentence should be revised once the final author list is fixed so that coauthor expertise is represented accurately.

## Proposal attachment strategy

If one figure is attached to the proposal, use a compact version of **Figure 5** rather than a project workflow diagram: show the exact `naive - gated = 1-v` identity plus the Level-A 283/283 case-study result in an inset. This most directly demonstrates both methodological novelty and quantitative support.
