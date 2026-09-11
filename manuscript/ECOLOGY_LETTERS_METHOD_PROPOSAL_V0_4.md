# Ecology Letters — unsolicited Method proposal package v0.4

## Working title

**Prospective validation of ecological answers: from cross-source reproducibility to identifiable biological absence**

Short alternatives:

- **When ecological answers can test a dependency**
- **From reproducibility to dependency in ecological inference**
- **Identifiable absence for hard ecological dependency tests**

## Article type

**Method**

The proposal presents a transferable inferential technique, not an internal development history of 284b and not a taxon-specific biological study.

## Proposal text (280 words under the repository word-count rule)

Detection-aware occupancy models already separate ecological state from imperfect observation, ecological model-adequacy work asks whether data support intended inference, and independent datasets are widely recognized as stronger tests of predictive models. A different problem arises when independently constructed ecological answers are combined to support a biological relation: what relation are those answers entitled to test, and when is the state required to contradict it identifiable? We introduce a prospective relation-endpoint framework that freezes the relation, biological event, relation-space adapter, answer-adequacy gates and calibration before focal outcomes are opened.

We first test a controlled same-target case using independent preserved-specimen and human-observation reconstructions. A successor panel prospectively froze 24 procedure-by-accessible-area reference cells before a 12-taxon held-out endpoint was opened. Of 288 held-out cells, 283 passed both source-specific adequacy gates and all 283 remained within their frozen source-discordance ceilings; five remained unresolved.

For hard cross-role dependency `E(k) -> F(k)`, the framework requires the negative function state `F(k)=false` itself to be identifiable. An exact 8,748-scenario benchmark shows that, for a qualified observation process, collapsing incomplete, missing or failed keys into zero increases both apparent violation sensitivity and false-violation probability by exactly the invalid-key mass. When calibration fails, hard calls remain sealed rather than turning non-detection into biological evidence.

Prospective screens then identified two fresh ecological systems with independently separated relation, dependent-event and required-function streams, yet both stopped before focal biological opening because functional absence was not independently calibrated. The method links relation-specific comparison, independent evidence architecture and negative-state identifiability into an auditable stopping rule: when the falsifying state is not identified by the observation design, the next scientific step is new measurement rather than stronger interpretation of the same data.

## Why this is not occupancy modelling, generic model adequacy, or preregistration

The proposal explicitly concedes three antecedent literatures.

1. Imperfect-detection and occupancy methods already separate ecological state from observation error.
2. Ecological model-adequacy work already argues that data determinacy, sensitivity and validity must be audited; Getz et al. (2018, *Ecology Letters*) is a close conceptual ancestor.
3. Preregistration and Registered Reports already establish prospective outcome-blind design in ecology.

The new object is the **prospective relation endpoint**: what relation independently constructed answers are permitted to test, how role-specific answers are mapped to a common biological event, and whether the negative state required to contradict a hard dependency is identifiable enough for that endpoint to be opened. Prospectivity is an enforcement mechanism, not the novelty claim itself.

## Why this fits the Method criteria

### Specific generalizable technique

The transferable technique consists of:

1. prospectively classifying the intended relation;
2. constructing role-specific ecological answers independently;
3. mapping answers to a frozen biological relation space;
4. separating answer inadequacy from relation discordance;
5. requiring negative-state identifiability before hard falsification;
6. preserving unresolved observation states rather than coercing them into biological negatives.

### Statistical performance

The exact benchmark gives a closed-form performance result for a zero-collapsing comparator versus the identifiability gate. With `a` denoting valid-key fraction,

`FPR_zero - FPR_gated = 1-a`

and

`TPR_zero - TPR_gated = 1-a`.

The result is checked across 8,748 exact parameter combinations. A second analytic result shows why calibration is an opening condition rather than a posterior guarantee: with true violation prevalence `pi`, key sensitivity `q` and specificity `sp`, the false-discovery fraction among gated calls is

`FDF = (1-pi)(1-q) / [(1-pi)(1-q) + pi sp]`.

A separate outcome-blind audit quantifies the operating characteristics of the proposed calibration gate.

### Open code

The central benchmark and calibration-audit code are versioned and testable with standard Python. All focal Level-C biological values remain sealed.

### Case study

The completed Level-A case study contains 24 prospectively frozen successor reference cells and 288 fresh held-out cells. Of 283 eligible openings, 283/283 remained within frozen source-discordance ceilings; five inadequate cells remained unresolved.

### Generality

The endpoint architecture applies to pollination, host dependence, trophic interactions, life-stage coupling, sensor-based interaction studies and distribution-based process attribution.

## Quantitative figure to attach with the proposal

Use:

`manuscript/figures/ecology_letters_method_proposal_figure_v0_1.svg`

It combines:

1. the relation distinction between same-target reproducibility and event-to-function dependency;
2. the fresh Level-A empirical anchor (`283/283` eligible openings inside frozen ceilings; `5` unresolved);
3. the exact invalid-state identity for hard dependency testing.

No focal Level-C biological values appear.

## Author-qualification paragraph for the proposal email

Final wording depends on the frozen author list. Current lead-author wording supported by the project is:

> The lead author works across empirical pollination ecology, species-distribution modelling and reproducible computational inference. The proposed method emerged from a version-controlled prospective-validation programme spanning independent-source ecological reconstruction, explicit falsification boundaries and cross-role biological dependency.

Add one concise sentence per coauthor only if it establishes directly relevant expertise; do not turn the email into a biography.

## Editorial-risk sentence

If the editor views the contribution as too conceptual for Method, invite advice on whether the same quantitative framework would be better considered as a Perspective. Do not submit it as a Perspective without editorial guidance: the package is deliberately built to satisfy Method requirements for an executable technique, performance characterization, open code and a case study.

## Proposal-readiness boundary

The proposal does **not** require Level-C field data. Before sending, close only the remaining presentation tasks: notation consistency, final author qualifications, and visual QA of the proposal figure. New focal Level-C data should not be inserted into this pre-field proposal state.
