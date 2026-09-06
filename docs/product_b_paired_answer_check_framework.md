# Product-B paired biological answer-check framework

## Core idea

The central object is not obligate mutualism itself. The central object is an
**independent biological answer-check**.

Two analyses, taxa, evidence channels or recovered ecological representations
may be expected from external biology to agree in a declared way. Neither answer
is allowed to define, tune or fit the other. After both are obtained
independently, they are compared on a frozen common audit space.

The scientific signal is therefore not merely prediction accuracy. It is whether
independent answers that should be biologically coupled remain mutually coherent.
Unexpected divergence is a warning that deserves explanation.

## Two evidence strengths

### 1. Hard invariant

Use when independent biology states that a relation must hold at the declared
scale.

Current examples:

- `directed_dependency`: `Y requires X`, so the recovered Y support must respect
  the predeclared directional constraint relative to X;
- `mutual_obligacy`: `X <-> Y`, represented as two necessary directed
  constraints.

A complete admissible hard-constraint failure can be classified as
`invariant_violated`.

### 2. Soft paired cross-check

Use when external biology predicts concordance but does not justify exact
identity or a hard logical constraint.

The two answers are compared with a scale-appropriate discordance measure. If
both answers are adequate and complete but discordance exceeds a reference
ceiling frozen independently of the focal outcome, classify the pair as:

`paired_crosscheck_attention_required`

This is intentionally not called a biological violation. Large divergence may
reflect model misspecification, omitted processes, observation bias, scale
mismatch, historical contingency, or a genuinely incomplete external biological
expectation.

## What independence means

For a paired answer-check to be informative:

1. answer A cannot use answer B, B occurrence, B fitted surface or the focal
   cross-check outcome as a predictor or tuning target;
2. answer B cannot analogously use A;
3. pair identity and the expected biological relation are declared before the
   focal outcomes are opened;
4. the audit space and comparison metric are frozen prospectively;
5. adequacy is assessed for each answer independently;
6. a failed adequacy gate is `unresolved`, not evidence of discordance.

Shared environmental predictors are allowed. The prohibition is circular use of
the answer being checked.

## Answer existence precedes answer coherence

Cross-validity is defined only after each independent analysis can construct the
predeclared ecological answer. A procedure can therefore fail one level earlier
than paired discordance.

For a frozen `taxon x source x procedure x M` cell:

1. the procedure must produce a complete final ecological answer under its own
   predeclared selection/recovery semantics;
2. that answer must pass its source-specific prediction-adequacy gate;
3. only then may its sealed prediction surface be opened against the other
   source on the common comparison rows.

If step 1 fails, the state is an **answer-construction / identifiability failure**.
If step 2 fails, the answer is **prediction-inadequate**. In either case, paired
Schoener D or another cross-check statistic stays closed. A missing answer must
never be encoded as maximal discordance, perfect concordance, zero suitability,
or a dropped cell.

This distinction matters because a procedure may be applicable for one taxon,
source and M but unable to define a complete ecological-recovery profile for
another. That is evidence about the domain of the procedure itself, not evidence
that the two observation systems disagree.

## Why raw prediction equality is not required

Two independently fitted taxa or evidence channels need not have numerically
identical suitability probabilities. Prevalence, observation processes,
calibration and response breadth can differ.

Therefore a statement such as `0.8 for A should equal 0.8 for B` is not a valid
default answer-check.

Current comparison tools instead include:

- directional containment;
- bidirectional containment;
- taxon-specific rank-profile discordance;
- reciprocal-containment asymmetry;
- same-target Schoener D on exactly matched sealed comparison rows.

These compare the location and structure of ecological support rather than
assuming cross-taxon probability calibration.

## Attention logic

The soft cross-check asks:

> Are two independently obtained answers more discordant than they were allowed
> to be under a prospectively frozen reference contract?

The reference ceiling must not be chosen from the focal result. It may come from:

- a preregistered biological tolerance;
- an independent calibration panel;
- a held-out matched-reference distribution whose construction rule was frozen
  before the focal pair was opened.

A focal pair exceeding this ceiling is flagged for diagnosis.

## Diagnostic hierarchy after a warning

When a paired cross-check returns `attention_required`, diagnose in this order:

1. **observation mismatch** — unequal detectability, sampling, taxonomy or data
   transport;
2. **scale mismatch** — the biological relation was declared at a different
   spatial, temporal or life-history scale;
3. **model mismatch** — one or both recovered representations are inadequate;
4. **omitted-process mismatch** — a frozen environmental process may be needed to
   preserve coherence;
5. **biological exception** — the externally declared relation may have a real
   geographic, historical or partner-specific boundary.

The warning is useful precisely because it localizes where the model/evidence
system stops agreeing with an independent biological expectation.

## Role of mutual obligacy

Mutual obligacy is a particularly strong positive-control example because both
answers constrain one another. It is not the framework itself.

The broader framework is:

`independent answer A + independent answer B + predeclared biological relation`

-> `paired answer-check`

-> `coherent / attention required / hard violation / unresolved`

-> optional process knockout to explain why coherence is preserved or lost.

## Relation to the Product-B hierarchy

The project can now be read as four nested questions:

1. **Observability** — can the biological target/relation be represented in the
   evidence layer without deriving the answer from focal outcomes?
2. **Identifiability** — can the frozen procedure actually construct a complete
   ecological answer for this target/source/scale, and are alternative
   procedures/processes structurally distinguishable?
3. **Cross-validity** — conditional on two independently adequate answers
   existing, do answers that should agree actually remain coherent?
4. **Necessity** — which frozen process removals create or amplify biologically
   unexpected divergence?

This reframes process discovery: a process is interesting not merely because it
improves prediction, but because removing it can make independently constrained
biological answers cease to agree.

The hierarchy is deliberately non-substitutable. More data cannot rescue a
biological target that is not cleanly represented by the evidence layer; a
cross-source distance cannot rescue a procedure that failed to construct an
answer; and a process-knockout interpretation cannot precede a frozen baseline
cross-check.

## Current boundary

This document authorizes the frozen framework, synthetic tests, registry schemas,
response-blind candidate design, and the prospectively ordered execution gates.
It does not authorize adapting a discordance threshold after seeing a focal pair,
turning an unresolved answer into a discordance value, replacing terminal taxa,
or reinterpreting any terminal v5-v7 endpoint.
