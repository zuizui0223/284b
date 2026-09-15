# Paper 1 current argument spine v0.1

**Status:** noncanonical editorial synthesis; no empirical endpoint opened and empirical ledger unchanged.  
**Target:** Ecology Letters — Method.  
**Current working title:** **Relation endpoints for ecological inference: when independent answers can support joint biological claims**

## Editorial decision

Paper 1 should no longer read as a progression from Level A to an unfinished Level C biological result. The strongest defensible paper is a Method paper with one completed empirical anchor, one formal separation argument, one executable authorization framework and two real-system stopping-rule demonstrations.

The paper's central question is:

> When independently generated ecological answers are combined, what biological relation are they entitled to test, and what evidence is sufficient to open that relation endpoint?

The answer is the five-part relation-endpoint contract: freeze the biological relation, common biological key space, role-specific adapters, answer-adequacy gates and calibration/opening rule before focal outcomes are viewed; preserve unresolved states whenever the observation process does not identify the state required by the relation.

## Claim hierarchy

### Claim 1 — empirical anchor

A same-target relation can close prospectively on fresh held-out taxa when the estimand, comparison frame, adequacy logic and source-discordance envelope are frozen before opening.

- independent biological units: **12 held-out taxa**;
- prespecified repeated diagnostics: **288 cells**;
- evaluable: **283**;
- unresolved: **5**;
- taxa with any empirical-envelope exceedance among evaluable cells: **0/12**.

The independent replication is 12 taxa, not 283 cells. The q95 references are prospectively frozen empirical source-discordance envelopes, not nominal 95% prediction intervals or alpha=0.05 tests.

### Claim 2 — why a relation layer is necessary

Accurate role-specific answers do not themselves identify a joint biological relation. For directional dependency `E -> F`, define `v=P(E=1,F=0)`. Classical Frechet-Hoeffding bounds give

`max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`.

At exact `p_E=p_F=0.5`, the same perfect marginals admit both `v=0` and `v=0.5`. This is established probability theory used as a separation argument, not a new theorem. A JSDM can estimate joint statistical structure, but the biological endpoint still has to declare whether the licensed relation is co-occurrence, interaction, directional functional dependency, stage transition or something else.

### Claim 3 — executable authorization framework

The relation-endpoint contract is an executable object rather than a prose checklist. It stores the relation, key space, adapters, adequacy gates, opening-rule class and frozen opening-rule reference; it is canonically serialized and fingerprinted before focal opening. Soft relations return `consistent`, `attention_required` or `unresolved`; directional hard relations return `hard_violation_authorized`, `no_observed_violation`, `noninformative_for_implication` or `unresolved`.

The fingerprint is an audit mechanism, not proof of outcome blindness.

### Claim 4 — unresolved is a statistically consequential state

For a hard endpoint with state-dependent observation validity,

- `a1=P(valid | F=true)`;
- `a0=P(valid | F=false)`;
- `q` = key sensitivity on valid compatible keys;
- `sp` = specificity on valid true-violation keys.

Coercing invalid observations into biological negatives has exact class-specific costs:

`FPR_zero - FPR_gated = 1-a1`

`TPR_zero - TPR_gated = 1-a0`.

The earlier common `1-a` identity is the equal-validity special case `a1=a0=a`. Zero collapsing is an ablation of the unresolved-state guard, not a competitor to occupancy or other detection-aware models.

### Claim 5 — the method can refuse a biologically tempting conclusion

Two biologically different Level-C systems reached the same measurement boundary after relation definition, event-key alignment, direct estimands and provenance separation succeeded. Both stopped because functional absence was not independently calibrated.

These systems are not incomplete positive/negative biological results. They are real-system demonstrations of the stopping rule: when the state needed to contradict a dependency is not identified, the next admissible information is new measurement rather than stronger interpretation of the same observations.

## Manuscript order

### Introduction

1. Ecological synthesis increasingly combines independently generated answers.
2. Established methods address imperfect detection, model adequacy, data fusion, JSDMs, interaction inference and prospectivity.
3. The missing object is downstream authorization: **which biological relation may independently defensible answers jointly test?**
4. Use the Frechet-Hoeffding counterexample early to show why answer accuracy alone cannot solve the relation problem.
5. State the contribution: an executable, prospectively frozen relation-endpoint contract with explicit unresolved states.

Do not lead with the Level A/Level B/Level C ladder. Introduce the ladder only after the relation-endpoint object is clear.

### Methods

1. Five-part relation-endpoint contract and fingerprinting.
2. Relation-layer separation using the classical coupling bounds.
3. Level-A controlled same-target experiment.
4. Hard dependency and negative-state identifiability.
5. Invalid-state coercion ablation and generalized `a1/a0` decomposition.
6. Prospective Level-C openability audit.

Move implementation-history detail about the v8 -> v8.1 Wilson/Clopper-Pearson repair to Supplement unless needed to demonstrate auditability. It is good provenance but currently interrupts the conceptual arc.

### Results

Use this order:

1. **Level A closes prospectively on 12 fresh held-out taxa.**
2. **The endpoint contract formalizes a relation layer not determined by accurate marginals.** Keep the Frechet-Hoeffding result method-facing/nonempirical.
3. **Preserving unresolved states prevents exact, quantifiable error inflation.**
4. **Two real systems stop at the same negative-state measurement boundary.**
5. Calibration operating characteristics are secondary; keep only the design implication in main text and move detailed minimum-count pass probabilities to Supplement.

### Discussion

Organize around four points:

1. **What is new:** relation choice and endpoint authorization across independently generated ecological answers.
2. **What is not new:** occupancy/detection modelling, JSDMs, data fusion, LIES, model adequacy, external validation and preregistration.
3. **Why refusal is a result:** an inferential framework is useful when it can say that an attractive biological claim is not yet identified.
4. **What changes practice:** predeclare the relation and contradiction rule, preserve unresolved states, and collect the measurement needed to identify the falsifying state.

## What to demote or remove from the main narrative

- **Level B:** keep as a relation class, not as a missing result that the reader expects to see completed.
- **Levels D/E:** composition-only scope note; do not make them central.
- **v8 historical repair:** Supplement/provenance unless a reviewer specifically asks about implementation audit trails.
- **minimum-count pass-probability examples:** Supplement after one short main-text sentence that minima are feasibility minima, not power guarantees.
- **283/283 phrasing:** retain only with immediate clarification that cells are repeated diagnostics; preferably lead with `0/12 held-out taxa with an exceedance among evaluable cells`.

## Display logic

1. **Figure 1 — Relation-endpoint contract.** Relation, key, adapters, adequacy, opening rule, state machine and fingerprint.
2. **Figure 2 — Level-A empirical anchor.** Twelve taxa as the independent units; repeated cell matrix shown as diagnostics, not n=283 replication.
3. **Figure 3 — Why the relation layer exists.** Compact Frechet-Hoeffding inset plus event-to-function dependency versus raw surface matching/provider occurrence.
4. **Figure 4 — Real-system stopping rule.** Cremastra and Belonocnema shown in parallel through the same gates, both ending at uncalibrated functional absence.
5. **Figure 5 — Unresolved-state ablation.** `a1`, `a0`, `q`, `sp`, exact increments and equal-validity corollary.
6. **Table 1 — Claim/evidence matrix.** Separate empirical, mathematical/synthetic, qualification and unopened claims.

## Candidate abstract

Ecological synthesis increasingly combines answers generated by different observation processes and biological roles, but accurate answers do not by themselves specify the biological relation they may jointly test. We introduce an executable relation-endpoint contract that prospectively freezes the relation, biological key space, role-specific adapters, adequacy gates and opening rule. Twelve fresh held-out taxa provided a controlled empirical anchor: 283 of 288 prespecified same-target diagnostics were evaluable, five remained unresolved, and no taxon contained an exceedance of its frozen empirical source-discordance envelopes. Classical coupling bounds show that even exact role-specific marginals need not identify a directional dependency. For hard endpoints, coercing invalid observations into biological negatives inflates false violations by `1-a1` and apparent violation sensitivity by `1-a0`. Two independent cross-role systems reached the same stopping point because functional absence was not calibrated. Relation endpoints separate answer construction from biological authorization and identify when new measurement is required.

## One-sentence paper claim

**Independently defensible ecological answers support a joint biological claim only after the relation connecting them is prospectively specified and the observation state required to open or contradict that relation is itself identifiable.**

## Frozen boundaries carried forward

- Level A remains the sole completed empirical relation endpoint.
- Level B remains empirically unopened.
- Level C focal hard/soft/knockout outcomes remain sealed.
- Cremastra and Belonocnema non-detection must not be converted to functional absence.
- No new threshold, candidate replacement, rescue path or empirical ledger increment is authorized by this editorial synthesis.
- Empirical ledger remains **1**.
