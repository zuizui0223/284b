# 284b relation-space design relative to EOG and SDMR

## Why this note exists

A cross-species biological check can become invalid if comparability is created by
forcing biologically different organisms into one model. A stationary plant and a
mobile pollinator are a simple example: their accessible areas, observation
processes, relevant time scales and ecological estimands need not be the same.

This note records what the sibling `eog` and `sdmr` projects already solve and the
remaining role of 284b.

## What EOG already establishes

EOG v2 explicitly separates estimands:

- `V`: local viability/environmental support;
- `R`: source-conditioned reachability support;
- `C`: target-capture support;
- `P`: establishment/persistence support;
- `O`: observation/detection support.

`V` may come from an independently specified SDM, mechanistic model or expert
support surface. It is not redefined as reachability, occupancy, persistence or
observation probability. EOG likewise does not require these layers to collapse
to one cellwise output.

The EOG empirical program also keeps incompatible endpoints separate across
heterogeneous systems rather than putting their effect sizes on one axis, and it
uses stronger system-specific reference models where appropriate.

**Implication for 284b:** different biological roles do not need one estimator or
one raw score scale.

## What SDMR already establishes

SDMR is a plant niche-estimation program, not a universal model for every organism.
Its target-group background implementation explicitly states that SDMR does not
define one universal accessible area `M`; the caller supplies a biologically
defensible M-membership rule.

Its cross-taxon program treats transfer across taxa, life forms, biomes, range
sizes, dispersal contexts and sampling densities as something to challenge rather
than assume. Later Product-A design also separates structural transportability
from ecological confirmation when different taxa are not equally auditable.

**Implication for 284b:** model transportability and accessible-area equality
cannot be assumed merely because two organisms participate in one interaction.

## What remains for 284b

284b is not another estimator of viability or reachability. Its distinct object is:

> Can independently obtained ecological answers, possibly produced by different
> role-appropriate estimators, satisfy an external biological relation after both
> are projected to a prospectively frozen common relation space?

The architecture is:

`role-specific estimator A -> answer A`

`role-specific estimator B -> answer B`

`answer A + answer B -> relation-space adapter`

`-> hard invariant or relation-specific soft cross-check`

This differs from EOG because the final object is not reachability itself. It
differs from SDMR because the final object is not niche-recovery tuning. The new
object is **cross-estimand biological validity**.

## Plant-pollinator example

### Plant side

Possible estimand:

- reproductive support;
- persistence support conditional on reproduction.

Possible estimator:

- SDM/niche model;
- demographic model;
- mechanistic plant model.

The plant accessible area is defined for the plant question.

### Pollinator side

Possible estimand:

- visitation support;
- reachability support during flowering.

Possible estimator:

- dynamic occupancy;
- movement kernel/model;
- EOG-style reachability model.

The pollinator accessible area is defined for its movement/visitation question.

### Relation space

Example keys:

`plant population/site x flowering window`

Both answers are projected to those opportunities. A candidate hard statement is:

> pollinator-dependent successful reproduction requires adequate pollinator
> visitation/reachability at the same opportunity.

This does not require adult plant occupancy to disappear immediately when a
pollinator is absent, nor does it require plant and pollinator raw suitability
surfaces to be equal.

## Calibration consequences

The same-target specimen-versus-observation q95 measures one narrowly controlled
quantity: reconstruction disagreement when target, estimand, estimator and M are
held fixed and observation source changes.

It cannot be used as a universal cross-species tolerance.

For cross-role soft relations, use a relation-specific prospective reference such
as matched non-obligate controls, shuffled partners or a dedicated independent
reference panel. For genuine obligate relations, use a dedicated hard constraint
on the appropriate biological event.

## Process-intervention consequence

Role-specific estimators imply role-specific interventions. For example:

- plant water/temperature information can be marginalized on a frozen plant
  answer;
- pollinator movement resistance or reachability components can be intervened on
  in the frozen pollinator answer.

Both are then re-projected through the *same frozen relation-space adapter*.
A process is coherence-critical when its removal causes the external biological
relation to fail, not merely when it reduces one model's prediction score.

## Claim boundary

284b therefore should not claim that one modeling procedure is universally
appropriate across interacting organisms. Its stronger and more general claim is:

> **Estimator heterogeneity is allowed; biological relation constraints provide
> the common external check.**

The method is strongest when it keeps estimator adequacy, relation-space
compatibility and biological coherence as separate gates.
