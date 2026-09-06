# Product-B paired biological answer-check execution plan

## Scientific sequence

Product-B is organized as escalating validation layers, but **same-target reconstruction and cross-role biological relations use different estimator/calibration logic**.

### Layer 1 — same-target cross-source reproducibility

Question:

> Does the same modeling procedure recover a coherent ecological answer for the same biological target when the observation system changes?

This is a controlled estimator-stability experiment. For each taxon, target,
estimand, procedure and M/background are held fixed while observation source
changes.

For each taxon:

1. resolve frozen taxonomy without occurrence-outcome selection;
2. partition the frozen snapshot into disjoint observation modes;
3. require source-specific sampling adequacy;
4. use the frozen M sensitivity grid without selecting M from cross-source results;
5. fit both modes independently with the same procedure and same M;
6. compare sealed answers on matched rows;
7. freeze a procedure × M same-target reconstruction reference only when its
   prospective calibration floor is met.

Layer 1 answers:

> How much disagreement can arise when the biological target and estimator are the same but the evidence view changes?

It does **not** answer how much disagreement is biologically acceptable between different species, estimands or mobility regimes.

### Layer 2 — held-out biological cross-validity in a relation space

Question:

> When independent biology says two role-specific ecological answers constrain one another, does the declared relation hold after each answer is estimated appropriately for its own role?

For each relation, prospectively freeze:

1. answer A's biological target, estimand and role-appropriate estimator;
2. answer B's biological target, estimand and role-appropriate estimator;
3. each role's own spatial/temporal accessibility semantics;
4. each answer's independent construction and adequacy gate;
5. a **relation-space adapter** declaring common relation keys, biological event,
   spatial/temporal grain and the two projections;
6. the hard invariant or relation-specific soft calibration.

Different roles are not required to share estimator family, predictors, accessible
area `M`, movement model, observation model or raw score scale.

Examples:

- same target from a genuinely new source: may still use Layer-1-style controlled calibration;
- soft cross-species concordance: requires an independent relation-specific reference;
- directional dependency (`Y requires X`): evaluate containment of the relevant dependency event after adaptation;
- mutual dependency: evaluate two separately meaningful directed events;
- life-stage coupling: allow stage-specific models and transition-specific relation space.

#### Plant–pollinator example

For an obligately pollinated plant:

- plant answer: reproductive/persistence support from an SDM, demographic or mechanistic plant model;
- pollinator answer: visitation/reachability support from a dynamic occupancy, movement or EOG-style model;
- plant and pollinator may have different `M` and temporal grains;
- relation space: for example `plant site × flowering window`;
- hard candidate: successful pollinator-dependent reproduction requires pollinator visitation/reachability at that opportunity.

Raw adult plant occurrence containment is not automatically a hard invariant because a long-lived plant can remain present after local pollinator loss.

#### Soft calibration boundary

The Layer-1 same-target q95 is **not** automatically used for cross-role relations.

Soft cross-role relations instead require a prospective relation-specific reference such as:

- matched non-obligate controls;
- shuffled partners under a frozen rule;
- an independent relation-specific calibration panel.

Hard relations use their dedicated biological invariant and do not borrow a generic soft ceiling.

### Layer 3 — process necessity by relation-coherence intervention

Only after a baseline relation is admissible and frozen do process interventions become informative.

Intervention is role-specific. A plant environmental-process intervention and a
pollinator movement/accessibility intervention need not be the same operation.

For each prospectively declared role/process intervention:

1. hold the baseline estimator, answer definition and relation adapter fixed;
2. erase/marginalize only the declared process information without outcome-driven rescue;
3. re-project the intervened answer to the same relation-space keys;
4. recompute the same hard invariant or relation-specific soft cross-check;
5. ask whether the biological relation ceases to hold or becomes unusually discordant.

This separates:

- target/relation observability;
- answer construction / identifiability;
- role-specific predictive adequacy;
- relation-space compatibility;
- biological cross-validity;
- process contribution to maintaining that relation.

## Procedure-level interpretation

The eight frozen Product-A procedures remain a **Layer-1 plant same-target calibration object**. They are not a universal estimator library that every future biological partner must use.

Layer 1 can characterize observation-view sensitivity of those procedures. It cannot establish that an animal, mobile stage, host-dependent partner or another estimand should be modeled with the same procedure.

For cross-role relations, the relevant question is instead:

> Is each role-appropriate estimator adequate for its own answer, and do the resulting answers satisfy the independently declared biological relation after adaptation?

## Main claim if the sequence succeeds

A successful result is not "one SDM algorithm is best" and not "two dependent species should have identical suitability maps." It is:

> Ecological models with different estimands can be externally checked against one another when each answer is estimated independently with a role-appropriate model and then projected to a prospectively declared biological relation space. Relation failure localizes where observation, estimator, scale, omitted process or biological expectation ceases to cohere.

## Main falsification outcomes

- If same-target cross-source answers are unstable, reconstruction/observation sensitivity is already large.
- If a role-specific estimator cannot construct an answer, the cell is identifiability-unresolved before cross-validity.
- If two adequate answers cannot be mapped to a defensible common relation event, the relation is not jointly observable at that scale.
- If an adapted hard dependency fails, compatibility under that frozen event/scale is violated.
- If a soft cross-role relation exceeds its own independent reference, it requires attention but does not identify which answer is wrong.
- If a frozen role-specific process intervention breaks a previously coherent relation, that process is a candidate coherence-critical component for that role.
