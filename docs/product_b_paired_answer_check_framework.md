# Product-B paired biological answer-check framework

## Core idea

The central object is not obligate mutualism itself. The central object is an
**independent biological answer-check**.

Two analyses, taxa, evidence channels or recovered ecological representations
may be expected from external biology to agree in a declared way. Neither answer
is allowed to define, tune or fit the other. After both are obtained independently,
they are compared through a frozen biological relation.

The scientific signal is therefore not merely prediction accuracy. It is whether
independent answers that should be biologically coupled remain mutually coherent.
Unexpected divergence is a warning that deserves explanation.

## Same-target replication is a special controlled case

The current preserved-specimen versus human-observation calibration is deliberately
special. The biological target and estimand are identical, so the design can hold
the estimator/procedure, M/background semantics and comparison rows fixed while
changing only the observation source.

That same-estimator requirement is an **experimental control for same-target
reconstruction stability**. It is not a general requirement of the biological
cross-check framework.

For different taxa, life histories or ecological roles, requiring one estimator
or one accessible area merely to make the outputs numerically comparable can be
biologically wrong.

## Role-specific answers and relation-space adaptation

For a cross-role relation, the framework is:

`role-specific estimator A -> ecological answer A`

`role-specific estimator B -> ecological answer B`

`A + B -> frozen relation-space adapter -> biological relation check`

The estimators may differ in model family, predictor set, movement/accessibility
assumptions, observation model, spatial unit and temporal grain. Each must be
adequate for its own declared estimand before any paired comparison is opened.

Comparability is created by a **relation-space adapter**, not by forcing the raw
models to be the same. The adapter freezes:

- the common relation keys;
- the biological event being constrained;
- how answer A is projected to those keys;
- how answer B is projected to those keys;
- the directional or symmetric relation evaluated afterward.

For an obligately pollinated plant, for example, plant reproductive support could
come from a plant niche/demographic model while pollinator visitation support
comes from a movement, dynamic occupancy or EOG-style reachability model. The
relation space might be `plant site x flowering window`. The hard candidate is
then about pollinator-dependent successful reproduction requiring pollinator
visitation/reachability at that opportunity — not about equality of raw plant and
pollinator occurrence surfaces.

## Two evidence strengths

### 1. Hard invariant

Use when independent biology states that a relation must hold for the declared
**event and scale**.

Current examples:

- `directional_dependency`: `Y requires X`, after both answers have been projected
  to a biologically meaningful dependency space;
- `mutual_obligacy`: two separately meaningful necessary directed constraints.

A complete admissible hard-constraint failure can be classified as
`invariant_violated`.

### 2. Soft paired cross-check

Use when external biology predicts concordance but does not justify an exact
logical constraint.

The two adapted answers are compared with a relation-appropriate discordance
measure. If both answers are adequate and complete but discordance exceeds a
reference ceiling frozen independently of the focal outcome, classify the pair as:

`paired_crosscheck_attention_required`

This is intentionally not called a biological violation. Large divergence may
reflect model misspecification, omitted processes, observation bias, scale
mismatch, historical contingency, or an incomplete biological expectation.

## What independence means

For a paired answer-check to be informative:

1. answer A cannot use answer B, B occurrence, B fitted surface or the focal
   cross-check outcome as a tuning target;
2. answer B cannot analogously use A;
3. each estimator is frozen for its own estimand before the relation outcome is
   opened;
4. the biological relation, event and relation-space adapter are declared before
   focal comparison;
5. adequacy is assessed for each answer independently;
6. a failed answer-construction or adequacy gate is `unresolved`, not evidence of
   discordance.

Shared environmental information is allowed where biologically justified. The
prohibition is circular use of the answer being checked.

## Answer existence precedes answer coherence

Cross-validity is defined only after each independent analysis can construct the
predeclared ecological answer. A procedure can therefore fail one level earlier
than paired discordance.

For a frozen answer cell:

1. the estimator must produce a complete ecological answer under its own
   predeclared semantics;
2. that answer must pass its own adequacy gate;
3. it must be projectable to the frozen relation space;
4. only then may the paired relation statistic be opened.

If step 1 fails, the state is an **answer-construction / identifiability failure**.
If step 2 fails, the answer is **prediction-inadequate**. If step 3 fails, the
relation is **not jointly observable at the declared scale**. In all three cases,
a paired cross-check statistic stays closed. A missing answer must never be
encoded as maximal discordance, perfect concordance, zero suitability, or a
dropped cell.

## No universal estimator or universal M across biological roles

Cross-role validity does not require estimator equality. In particular, unless
external biology itself justifies it, the framework must not require different
roles to share:

- the same estimator family;
- the same predictor universe;
- the same accessible area `M`;
- the same movement model;
- the same observation process;
- the same raw output scale.

This matches the broader research-program boundary. EOG separates viability,
reachability, persistence and observation quantities rather than collapsing them
into one prediction. SDMR explicitly treats M as taxon-specific and challenges
transfer across taxa, life forms and dispersal contexts rather than assuming one
universal ecological representation.

## Why raw prediction equality is not required

Even independently fitted answers for the same target need not have identical raw
suitability probabilities. Across different estimands the problem is stronger:
a plant reproductive-support score and a pollinator reachability score need not
even share a probability interpretation.

Therefore raw values such as `0.8 for A == 0.8 for B` are not a valid default
cross-role answer-check.

Current comparison tools instead include:

- directional containment after relation-space projection;
- bidirectional containment for two mandatory directions;
- same-target Schoener D on matched rows;
- relation-specific rank/opportunity profiles.

## Calibration boundary

The same-target independent-source q95 estimates disagreement under a controlled
case where target, estimand, estimator and M/background are held fixed and only
the observation source changes.

It must **not** be imported automatically as the tolerance for a plant-pollinator,
host-dependent, life-stage or movement-persistence relation. Those comparisons
have different estimands and require either:

- a dedicated hard biological invariant; or
- relation-specific soft calibration, such as prospectively matched non-obligate
  controls, shuffled partners, or another external reference design.

Same-target calibration remains useful as a reconstruction-stability diagnostic,
not as a universal biological-discordance ruler.

## Attention logic

The soft cross-check asks:

> Are two independently obtained, relation-space-compatible answers more discordant
> than allowed under a prospectively frozen relation-specific reference contract?

A focal pair exceeding this ceiling is flagged for diagnosis rather than declared
biologically false.

## Diagnostic hierarchy after a warning

When a paired cross-check returns `attention_required`, diagnose in this order:

1. **observation mismatch** — unequal detectability, sampling, taxonomy or data
   transport;
2. **estimand/adapter mismatch** — the two upstream answers were projected to an
   inappropriate common biological event;
3. **scale mismatch** — spatial, temporal or life-history grain is wrong;
4. **model mismatch** — one or both role-specific estimators are inadequate;
5. **omitted-process mismatch** — a frozen process may be needed to preserve
   coherence;
6. **biological exception** — the external relation may have a real boundary.

## Role of mutual obligacy

Mutual obligacy is a particularly strong positive-control example, but mutuality
does not imply identical distributions. Each direction may constrain a different
biological event and may therefore require a different adapter.

The broader framework is:

`independent role-specific answer A + independent role-specific answer B`

-> `frozen relation-space adapter`

-> `predeclared biological relation`

-> `coherent / attention required / hard violation / unresolved`

-> optional role-specific process intervention.

## Relation to the Product-B hierarchy

The project now has five nested questions:

1. **Observability** — can each biological target and the relation event be
   represented without deriving the answer from focal outcomes?
2. **Identifiability** — can each role-appropriate estimator construct its
   ecological answer?
3. **Relation-space compatibility** — can those different answers be mapped to a
   common biological event without forcing estimator/M equality?
4. **Cross-validity** — conditional on two adequate adapted answers existing, do
   answers that should cohere actually do so?
5. **Necessity** — which frozen role-specific process removals create or amplify
   biologically unexpected divergence?

The hierarchy is deliberately non-substitutable. More data cannot rescue an
unobservable target; a cross-source distance cannot rescue a failed estimator;
forcing one M cannot manufacture valid comparability across mobility regimes;
and process interpretation cannot precede a frozen baseline relation check.

## Current boundary

The currently running same-target source calibration remains unchanged and keeps
its common-estimator/common-M control. The new role-specific relation-space layer
applies to future cross-species, cross-role and life-stage checks. It does not
retroactively rescue or reinterpret any terminal v5-v7 endpoint, and it does not
authorize opening a new cross-species outcome before the role-specific estimators
and relation adapter are prospectively frozen.
