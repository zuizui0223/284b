# SMIL001 role-specific answer design v0.1

## Purpose

This note defines what would count as a valid role-X and role-Y answer for the
prospective Level-C candidate `SMIL001` before any focal cross-role relation is
opened.

The admitted direction is:

> successful *Smilax insularis* reproduction at a frozen reproductive opportunity
> requires adequate *Dasineura heterosmilacicola* visitation/reachability support
> at the same opportunity.

The design deliberately does not compare raw plant and midge range maps.

## Common relation key

The intended key is:

`dependency experiment population x reproductive event window`

Both parts remain unresolved for confirmatory execution because the reviewed 2026
plant-dependency experiment is published at Amami-Oshima grain without an exact
coordinate, and the event-specific temporal key has not yet been reduced to one
prospectively justified unit.

No role answer may be evaluated until the exact key inventory is frozen.

## Role X: dependent reproductive event

### Scientific estimand

The relevant quantity is successful sexual reproduction, not adult plant
occupancy and not generic climatic suitability.

### Preferred confirmatory route: independent reproductive observations

For each frozen relation key, role X should be based on an independent observation
of natural/open-pollinated reproductive outcome linked to a previously flowering
female inflorescence or population.

A positive dependent event must be defined prospectively from a biological outcome
such as mature fruit or seed production. The exact threshold and observation unit
must be frozen before focal role-Y answers are opened.

An adequately observed absence of reproduction does not validate the dependency;
it simply does not trigger the hard implication on that key.

### Secondary route: validated reproductive-success model

A model may be used only if it is trained and validated against reproductive
outcomes rather than adult occurrences alone. Its predictor set, accessible-area
semantics, output interpretation, threshold, and adequacy gate must be frozen
without access to the focal cross-role relation.

### Forbidden substitutions

The following do not by themselves count as a role-X hard-event answer:

- adult *S. insularis* occurrence;
- an ordinary plant SDM;
- flowering presence without a reproductive-success outcome;
- habitat suitability relabelled as fruit-set probability.

These may be lower-level covariates or feasibility information only.

## Role Y: required midge support

### Scientific estimand

The relevant quantity is midge visitation or reachability during the same
reproductive opportunity, not generic midge occurrence somewhere in the region.

### Preferred confirmatory route: effort-certified visitation

For a frozen key, direct observation of *D. heterosmilacicola* visiting the focal
plant opportunity is a positive required-support answer.

A non-detection can count as required-support absence only if observation effort,
time-of-day coverage, taxonomic identification, and detection adequacy satisfy a
prospectively frozen absence-certification rule. Otherwise non-detection is
`unresolved`, never absence.

The 2026 Current Biology visitation observations and the 2025 interaction
observations helped establish the external biological relation and therefore are
not eligible to double as the confirmatory focal role-Y answer.

### Secondary route: prospectively frozen reachability model

A reachability answer may be used if its own source states, movement/transition
rules, spatial grain, temporal horizon, local support representation, and adequacy
gates are frozen before the focal relation is opened.

If an EOG-style finite-world representation is used, Product-B should preserve the
EOG distinction among robust support, contingent/possible support, unresolved
support, and robustly unreachable states. A contingent or unresolved reachability
state must not be collapsed to required-support presence or absence merely to make
the hard relation executable.

### Forbidden substitutions

The following do not by themselves count as a role-Y hard-event answer:

- raw *D. heterosmilacicola* occurrence anywhere on Amami-Oshima;
- an ordinary midge SDM relabelled as visitation probability;
- island-level presence used to stand in for support at an unknown focal plant
  population;
- failure to detect the midge without certified observation effort.

## Evidence independence

The external literature that admits the hard relation may establish biological
prior knowledge and response-blind site/time provenance, but it may not also score
the confirmatory focal endpoint.

A confirmatory endpoint therefore requires fresh or otherwise independent role-X
and role-Y answer sources. If only the relation-defining studies are available,
SMIL001 remains an engineering/qualification example rather than confirmatory
cross-validity evidence.

## Event-relation classification

The pure classifier in `product_b_v7_3/event_relation.py` implements the following
logic on the full frozen key set:

- dependent event positive + required support positive -> consistent key;
- dependent event positive + adequately established required support absent ->
  violated key;
- missing/inadequate answer -> unresolved key;
- adequately negative dependent event -> implication not triggered.

Any complete violation is sufficient for `invariant_violated`. In the absence of a
violation, unresolved predeclared keys keep the aggregate unresolved. Consistency
requires at least one triggered event and no unresolved keys; a set containing
only negative dependent events is not promoted by vacuous truth.

## Current execution state

No confirmatory SMIL001 role-X or role-Y source has been admitted.

No focal relation statistic is open.

- hard invariant opening authorized: false
- soft cross-check opening authorized: false
- process knockout authorized: false
- counts as empirical conclusion: false
- 284b empirical ledger remains: 1
