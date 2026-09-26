# Product-B mutual-obligacy positive-control extension

## Status

This is a hard-invariant example inside the broader paired biological answer-check framework. It is not the framework itself, not a new Product-B generation, and not an empirical authorization.

The general framework is documented in `docs/product_b_paired_answer_check_framework.md`: independently obtained ecological answers are compared only after fitting, using a biological relation declared before focal outcomes are opened. Unexpected divergence is a diagnostic signal. Mutual obligacy is a particularly strong positive-control case because both directions may be biologically required.

The constraint class is `mutual_obligacy` and is represented as two necessary directed statements:

- `Y requires X`; and
- `X requires Y`.

The existing `directed_dependency` class remains unchanged.

The completed same-target core19 v0.4 endpoint now demonstrates that the independent-answer machinery can close empirically at Level A. This document defines what would be required to move to a genuinely cross-role Level C/D endpoint without importing the Level-A q95 or forcing raw range equality.

## Scientific role

The primary use of a mutual-obligacy pair is as a **hard positive control for ecological relation checking**.

The question is not simply whether two independently fitted environmental niche maps overlap. The stronger question is:

> If two biological roles are independently known to require one another for a declared event, can role-appropriate ecological answers recover support for that required event even though the partner relation was never supplied to either upstream estimator?

The pair identity, dependency directions, biological event, spatial/temporal grain and relation-space adapter must all be established independently of occurrence/model outcomes.

## Why raw bidirectional niche containment is not the confirmatory hard invariant

An earlier formulation proposed testing mutual obligacy by asking whether each taxon's raw environmental support was contained in the other's support region. That quantity remains a possible engineering diagnostic, but it is **not** the confirmatory hard invariant.

Raw range containment can fail even when a biological dependency is real because:

- adults may persist after a partner becomes locally absent;
- the two roles can have different dispersal and accessible areas;
- occurrence records can represent different life stages or seasons;
- one role can be mobile while the other is stationary;
- the biologically mandatory event may be reproduction or visitation rather than adult occupancy;
- multiple alternative obligate partners can exist in parts of the range.

Therefore `support(Y) subset support(X)` and its reverse must not be interpreted as a hard mutual-obligacy law unless external biology specifically justifies raw support containment at the declared scale.

## Admission boundary

A confirmatory mutual-obligacy pair must be frozen before focal occurrence or fitted-outcome inspection and must satisfy all of the following.

1. Independent literature supports each claimed dependency direction at a precisely declared biological event and scale.
2. The event is named explicitly, for example successful reproduction, host use, larval development, or partner-mediated establishment; it is not replaced by generic adult co-occurrence.
3. Known alternative obligate partners, host switches, facultative states, geographic exceptions and life-stage exceptions are declared prospectively.
4. The geographic and temporal evaluation frame is defined independently of observed pair overlap.
5. Pair selection does not use GBIF/iNaturalist overlap maps, occurrence counts, fitted suitability, invariant values or process-knockout values.
6. Confirmatory positive controls dominated by deliberate human release, cultivation or experimental placement are excluded or explicitly downgraded to engineering-only.
7. Each role has its own predeclared estimator, accessible-area semantics and adequacy gate. Symmetry of estimator family or M is not required unless biology independently justifies it.
8. The common relation-space keys and both role-to-relation projections are frozen before the focal relation is opened.

## Role-specific answer construction

The two upstream ecological answers are constructed independently.

### Role X

Freeze before focal comparison:

- estimand;
- estimator family;
- predictor universe;
- accessible-area / movement semantics;
- spatial and temporal resolution;
- answer-adequacy gate.

### Role Y

Freeze the same categories independently for Y. Y is not required to share X's estimator, predictors, M, movement model or raw output scale.

Neither answer may use the partner's occurrence, fitted surface or focal relation outcome as a tuning target unless that partner information is itself part of a separately declared mechanistic estimator whose use predates pair selection. A confirmatory positive control should prefer estimators that leave the cross-role relation genuinely external.

## Relation-space adapter

Comparability is created after answer construction through a prospectively frozen relation-space adapter.

For each dependency direction the adapter declares:

- common opportunity keys;
- the biological event being constrained;
- how role X is projected to those keys;
- how role Y is projected to those keys;
- missingness/adequacy semantics;
- the hard or soft relation evaluated afterward.

Example for an obligate plant-pollinator direction:

`plant population/site x flowering window`

Plant answer: reproductive opportunity/support at that site-window.

Pollinator answer: visitation or reachability support at the same site-window.

Candidate hard statement:

> pollinator-dependent successful reproduction requires adequate pollinator visitation/reachability at the same opportunity.

This statement does not require equality of plant and pollinator raw suitability surfaces and does not require the plant's M to equal the pollinator's movement-accessible area.

For a truly mutual pair, the reverse direction requires its own event and adapter. The two directions need not use identical event definitions.

## Confirmatory hard-invariant decision

A hard direction may be opened only when both role-specific answers exist, pass adequacy and can be projected onto the frozen relation keys.

Decision semantics for each direction:

- `invariant_consistent_under_frozen_contract`: all admissible required opportunities satisfy the frozen necessary relation;
- `invariant_violated`: at least one complete admissible required opportunity violates the declared hard relation under the predeclared rule;
- `unresolved`: one or both answers fail construction/adequacy, the relation-space projection is incomplete, or the hard event is not jointly observable at the declared scale.

For `mutual_obligacy`:

- if either complete admissible direction is `invariant_violated`, the mutual constraint is `invariant_violated`;
- only two consistent directions yield `invariant_consistent_under_frozen_contract`;
- otherwise the result is `unresolved`.

No weighted composite score is permitted.

## Engineering diagnostics that may accompany but not define the hard result

The following may be reported descriptively if frozen prospectively:

- raw environmental-support containment;
- reciprocal support overlap;
- rank-profile discordance;
- relation-space opportunity coverage;
- distance-to-partner-support summaries.

These quantities can diagnose why a hard relation succeeds or fails, but they cannot rescue, override or substitute for the event-level invariant.

Raw suitability probabilities are not expected to be numerically identical across roles because prevalence, calibration and observation processes differ. Rank-profile comparisons must therefore stay descriptive or use a separately calibrated soft relation.

## Negative and soft controls

Raw mutual overlap is not sufficient evidence. A future empirical contract should freeze appropriate controls before outcomes.

Possible control designs include:

- matched non-obligate partner pairs;
- biologically impossible shuffled partners;
- alternative valid partners where the biology predicts weaker directional specificity;
- spatial/temporal opportunity shuffles that preserve marginal sampling structure.

For soft Level-B comparisons, the true pair can be expected to show stronger relation-space coherence than controls under a prospectively calibrated statistic. That soft comparison remains separate from a hard event-level invariant.

The completed Level-A same-target q95 is **not** an admissible universal threshold for these cross-role controls.

## Process knockout

Process necessity is evaluated only after the full baseline relation passes the relevant hard or soft cross-role check.

For each frozen role-specific process, intervene without changing the baseline estimator, relation keys or adapter and recompute the relation-space answers.

Examples:

- plant water/temperature information marginalized from a frozen plant answer;
- pollinator movement resistance or reachability components intervened on in a frozen pollinator answer.

A process becomes a candidate `invariant_critical` process only if its removal breaks at least one previously admissible hard direction under the frozen rule.

Under a soft paired check, a process can be diagnostically important if its removal creates or amplifies cross-answer discordance beyond a separately frozen relation-specific ceiling.

This yields the hierarchy:

1. **observability** — can the external biological event and relation be represented independently?
2. **identifiability** — can each role-specific estimator construct an adequate answer?
3. **relation-space compatibility** — can both answers be projected to the same biological opportunity without forcing raw estimator equality?
4. **cross-validity** — do independently fitted answers satisfy the external biological relation?
5. **necessity** — which role-specific process removals destroy or materially degrade that coherence?

## Required frozen contract for the first empirical Level C/D endpoint

Before any candidate-pair occurrence/model outcome is opened, a new contract must contain at least:

- pair identity and literature provenance;
- dependency direction(s);
- declared biological event for each direction;
- known exceptions and alternative partners;
- role-X estimand and estimator contract;
- role-Y estimand and estimator contract;
- independent role-specific adequacy gates;
- spatial/temporal relation-space keys;
- both projection functions;
- hard-invariant rule or relation-specific soft-reference design;
- control-pair selection rules if used;
- process interventions, if any, listed but kept closed for baseline;
- one-shot opening rule;
- explicit statement that Level-A q95 is not imported.

## Current execution boundary

Allowed now:

- pure event-level mutual-obligacy metric/classifier functions;
- synthetic tests;
- an empty prospective registry schema;
- response-blind candidate literature search;
- role-specific estimator feasibility checks that do not inspect the focal relation outcome;
- freezing a Level C/D contract before focal data opening.

Not authorized by this document:

- selecting a pair from observed occurrence overlap;
- using raw niche containment as the confirmatory mutual-obligacy invariant without an independent biological justification for that exact relation;
- opening a mutual-pair empirical result before relation-space and estimator contracts are frozen;
- changing existing v5-v7 or core19 terminal outcomes;
- treating engineering pairs as confirmatory positive controls;
- importing the completed Level-A q95 as a cross-role tolerance.

The next empirical advance should therefore be a **fresh event-level cross-role endpoint**, not another reinterpretation of same-target reconstruction.