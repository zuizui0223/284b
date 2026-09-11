# Ecology Letters — unsolicited Method proposal package v0.5

## Working title

**Prospective validation of ecological answers: from cross-source reproducibility to identifiable biological absence**

Short alternatives:

- **When ecological answers can test a dependency**
- **Relation endpoints for ecological inference**
- **From reproducibility to dependency in ecological inference**
- **Identifiable absence for hard ecological dependency tests**

## Article type

**Method**

The proposal presents a transferable inferential technique for authorizing relations among independently constructed ecological answers. It is not an internal development history of 284b and not a taxon-specific biological study.

## Proposal text

Use the exact body frozen in `ECOLOGY_LETTERS_300WORD_PITCH_V0_5.md`. It remains below the 300-word ceiling under the repository word-count rule and now includes the lead-author qualification required by the Method editorial guidance.

The proposal begins by conceding the closest antecedent explicitly: Chadwick et al. (2024) already systematize observation-process problems through the LIES framework (Latency, Identifiability, Effort and Scale). This prevents the proposal from claiming observation-process identifiability itself as new.

## The methodological object

The central object is a **prospective relation endpoint**. Before focal comparison values are opened, the endpoint freezes:

1. the biological relation to be tested;
2. the biological event/key space in which the relation is meaningful;
3. adapters from each role-specific answer into that relation space;
4. answer-adequacy rules that determine whether an answer exists for the endpoint;
5. the calibration/opening rule used to distinguish admissible relation evidence from unresolved observation.

This object sits above any one ecological estimator. Occupancy models, JSDMs, SDMs, sensor classifiers, phenology models or direct observations may generate role-specific answers if their own assumptions are defensible. The relation endpoint asks the separate question: **what biological relation may those answers jointly test, and is the state required to contradict that relation actually identifiable?**

## Why this is not LIES, occupancy modelling, generic model adequacy, or preregistration

### Observation-process frameworks

Chadwick et al. (2024) show that observation processes can be as complex as biological processes and organize their problems as Latency, Identifiability, Effort and Scale. The proposed method accepts that result. It does not offer a competing typology of observation processes.

The additional step is relation authorization across independently generated answers. A well-characterized observation process does not by itself determine whether two fitted outputs should be equal, concordant, directionally nested, or linked only at a specific event key.

### Imperfect detection

Occupancy and interaction models already separate latent ecological state from imperfect observation. A candidate-specific detection model can satisfy part of the proposed negative-state gate. We do not introduce another occupancy model.

### Model adequacy

Getz et al. (2018) already establish ecological model adequacy and data determinacy as explicit methodological concerns. The relation endpoint is not a replacement for model adequacy; it composes individually adequate answers into a declared biological relation.

### Prospectivity

Preregistration and Registered Reports already establish outcome-blind design. Prospectivity is therefore an enforcement mechanism, not the novelty claim. What is frozen here is the relation endpoint itself.

## Why this fits the Method criteria

### A specific transferable technique

The technique is executable as a sequence:

1. classify the intended relation (same-target reproducibility, soft cross-role concordance, directional dependency, mutual dependency or stage coupling);
2. construct role-appropriate ecological answers independently;
3. map them to a frozen common biological key/event space;
4. separate answer inadequacy from relation discordance;
5. for hard dependency, require the negative state needed for contradiction to be identifiable under the observation process;
6. preserve incomplete, missing and failed observations as unresolved rather than biological negatives;
7. open the focal endpoint only after the relevant calibration contract passes.

### Statistical performance

For a qualified hard-dependency process, let `a` denote the fraction of event keys valid for negative inference. The exact endpoint decision decomposition is

`FPR_zero - FPR_gated = 1-a`

and

`TPR_zero - TPR_gated = 1-a`.

Thus the apparent sensitivity gained by coercing invalid keys into zero is exactly matched by additional false hard violations. The identity is evaluated over 8,748 exact parameter combinations with no Monte Carlo error and no focal Level-C biological values.

A second analytic result separates process qualification from endpoint evidentiary reliability. With true violation prevalence `pi`, valid-key sensitivity `q` and specificity `sp`, the false-discovery fraction among gated calls is

`FDF = (1-pi)(1-q) / [(1-pi)(1-q) + pi sp]`.

Calibration therefore authorizes an endpoint to be opened; it is not itself posterior false-discovery control.

### Outcome-blind operating-characteristic audit

The proposed Level-C calibration gate has also been audited before field data. Under the frozen exact one-sided confidence rule and minimum design, sensitivity requires at least 28/30 known-positive successes and specificity requires 60/60 known-negative successes. These are feasibility minima, not adaptive sample-size permissions.

### Open code

The benchmark, calibration evaluator, candidate/source gate receipts and submission-boundary tests are versioned and executable. All focal Level-C biological values remain sealed.

### Empirical case study

The completed Level-A controlled case contains 24 prospectively frozen procedure-by-accessible-area reference cells followed by a fresh 12-taxon held-out matrix. Of 288 held-out cells, 283 passed both source-specific adequacy gates and all 283 remained within the corresponding frozen source-discordance ceilings; five inadequate cells stayed unresolved.

### Real-system stress test

Prospective Level-C screens identified two fresh systems with independently separated relation, dependent-event and required-function streams. Both nevertheless remained sealed because the negative function state was not independently calibrated. Existing supplementary/raw sources did not repair that gap. This is not a negative biological result; it demonstrates the method's stopping rule in real systems.

### Generality

The endpoint architecture is applicable to pollination, host dependence, trophic interactions, life-stage coupling, sensor-based interaction studies and distribution-based process attribution because it does not require one estimator, one accessible area, one predictor universe or one raw output scale across roles.

## Quantitative figure to attach with the proposal

Use:

`manuscript/figures/ecology_letters_method_proposal_figure_v0_3.svg`

This version was rendered and visually audited after generation; it fixes text overflow in the held-out design panel without changing any scientific content.

The figure combines:

1. the relation distinction between same-target reproducibility and event-to-function dependency;
2. the fresh Level-A empirical anchor (`24/24` reference cells; `283/283` eligible openings inside frozen ceilings; `5` unresolved);
3. the exact invalid-key identity;
4. a concrete benchmark callout showing that with near-perfect valid-key detection but 30% missingness, zero collapsing produces false-violation probability about `0.300001`, whereas the gated rule yields about `1.1e-6` and retains the missing 30% as unresolved.

No focal Level-C biological values appear.

## Author-qualification paragraph

The 300-word pitch now includes the lead-author qualification directly. For the email wrapper, use:

> The lead author works across empirical pollination ecology, species-distribution modelling and reproducible computational inference. The proposed method emerged from a version-controlled prospective-validation programme spanning independent-source ecological reconstruction, explicit falsification boundaries and cross-role biological dependency.

Add one concise sentence per coauthor only when the frozen author list is available and the sentence establishes directly relevant expertise.

## Editorial-risk sentence

If the editor views relation-endpoint authorization as too conceptual for Method despite the executable gate, exact performance result and case study, invite advice on whether the same quantitative contribution would be better considered as a Perspective. Do not self-reclassify it before editorial guidance.

## Proposal-readiness boundary

The proposal does **not** require Level-C field data. Before sending, the remaining tasks are presentational rather than scientific:

- final author list/qualification sentences;
- one last citation/notation audit;
- immutable archive/release identifiers if desired before full manuscript submission.

No focal Level-C value, candidate replacement, threshold relaxation or post-hoc endpoint opening is authorized by proposal preparation.
