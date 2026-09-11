# Ecology Letters — unsolicited Method proposal package v0.3

## Working title

**Prospective validation of ecological answers: from cross-source reproducibility to identifiable biological absence**

Short alternatives:

- **When ecological answers can test a dependency**
- **From reproducibility to dependency in ecological inference**
- **Identifiable absence for hard ecological dependency tests**

## Article type

**Method**

The proposal should present a transferable inferential technique, not a report on the internal development history of 284b and not a taxon-specific biological study.

## Proposal text (271 words)

Detection-aware occupancy models already separate ecological state from imperfect observation, and independent datasets are widely recognized as stronger tests of predictive models. A different problem arises when independently constructed ecological answers are combined to support a biological relation: what relation are those answers entitled to test, and when is the state required to contradict it identifiable? We introduce a prospective answer-check framework that freezes the relation, biological event, relation-space adapter, answer-adequacy gates and calibration before focal outcomes are opened.

We first test a controlled same-target case using independent preserved-specimen and human-observation reconstructions. A successor panel prospectively froze 24 procedure-by-accessible-area reference cells before a 12-taxon held-out endpoint was opened. Of 288 held-out cells, 283 passed both source-specific adequacy gates and all 283 remained within their frozen source-discordance ceilings; five remained unresolved.

For hard cross-role dependency `E(k) -> F(k)`, the framework requires the negative function state `F(k)=false` itself to be identifiable. An exact 8,748-scenario benchmark shows that, for a qualified observation process, collapsing incomplete, missing or failed keys into zero increases both apparent violation sensitivity and false-violation probability by exactly the invalid-key mass. When calibration fails, hard calls remain sealed rather than turning non-detection into biological evidence.

Prospective screens then identified two fresh ecological systems with independently separated relation, dependent-event and required-function streams, yet both stopped before focal biological opening because functional absence was not independently calibrated. The method therefore links external validation, relation-specific comparison and detection identifiability into an auditable stopping rule: when the falsifying state is not identified by the observation design, the next scientific step is new measurement rather than stronger interpretation of the same data.

## Why this is not occupancy modelling

The proposal should explicitly concede that imperfect detection, false absence, multispecies occupancy and missed species interactions already have mature literatures. The new object is the **prospective relation endpoint**: the method decides what relation independently constructed answers are permitted to test and whether the negative state required to contradict a hard biological dependency is identifiable enough for that endpoint to be opened.

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

The exact benchmark gives a closed-form performance result for a zero-collapsing comparator versus the identifiability gate. For a qualified process with valid-key mass `v`,

`FPR_zero - FPR_gated = 1-v`

and

`TPR_zero - TPR_gated = 1-v`.

The result is checked across 8,748 exact parameter combinations. A separate outcome-blind audit quantifies the operating characteristics of the proposed calibration gate.

### Open code

The central benchmark and calibration-audit code are versioned and testable with standard Python. All focal Level-C biological values remain sealed.

### Case study

The completed Level-A case study contains 24 prospectively frozen successor reference cells and 288 fresh held-out cells. Of 283 eligible openings, 283/283 remained within frozen source-discordance ceilings; five inadequate cells remained unresolved.

### Generality

The endpoint architecture applies to pollination, host dependence, trophic interactions, life-stage coupling, sensor-based interaction studies and distribution-based process attribution.

## Quantitative figure to attach with the proposal

Use one compact conceptual/performance figure with three elements:

1. the relation ladder from same-target reproducibility to event-to-function dependency;
2. the exact identity `zero-collapsing minus gated = invalid-key mass (1-v)`;
3. a small empirical inset: `283/283` eligible Level-A held-out cells within frozen ceilings; `5` unresolved.

This figure makes the novelty, performance result and case study visible before the editor reads the full manuscript.

## Author-qualification paragraph for the proposal email

Final wording depends on the author list. Current lead-author wording:

> The lead author works across empirical pollination ecology, species-distribution modelling and reproducible computational inference. The proposed method emerged from a version-controlled prospective-validation programme spanning independent-source ecological reconstruction, explicit falsification boundaries and cross-role biological dependency.

Add one concise sentence per coauthor only if it establishes directly relevant expertise; do not turn the email into a biography.

## Editorial-risk sentence

If the editor views the contribution as too conceptual for Method, invite advice on whether the same quantitative framework would be better considered as a Perspective. Do not submit it as a Perspective without editorial guidance: the current package is deliberately built to satisfy the Method requirements for executable technique, performance characterization, code and case study.
