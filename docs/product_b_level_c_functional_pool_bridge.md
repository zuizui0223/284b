# Product-B Level-C functional-pool bridge

## The problem exposed by set-valued dependency

For a dependent event `E(k)`, a set-valued hard relation can be written as

`E(k) -> OR_{r in R(k)} S_r(k)`.

This handles biological redundancy correctly, but it creates a negative-evidence problem: if every *represented* member is absent, a hard violation is licensed only when `R(k)` is externally known to be complete.

In many ecological systems, exhaustive provider-species closure is harder to defend than the event relation itself.

## Two routes to the same required role

There are therefore two distinct routes.

### Route 1 — enumerate the provider set

Freeze every admissible member `r` and independently estimate `S_r(k)`.

When the set is complete, define

`F(k) = OR_{r in R(k)} S_r(k)`.

Then the set-valued relation and the direct functional relation

`E(k) -> F(k)`

are logically equivalent on the same complete event key.

### Route 2 — observe the required function directly

Instead of inferring the union from individually enumerated provider species, independently measure or model the aggregate biological function `F(k)` itself.

Examples of the *form* include effective pollination service, adequate visitation at a reproductive opportunity, or availability of a biologically defined compatible resource class. The answer must actually measure that function. A generic occurrence or suitability surface is not automatically `F`.

A direct functional channel can avoid taxonomic set-completeness only if the channel itself is adequate to establish both support and absence for the declared function at the frozen key.

For example, zero observed visits with weak observation effort is not functional absence. It remains unresolved.

## The key identifiability difference

Suppose a positively triggered dependent event has two represented provider species and both are adequately negative.

- if the provider universe is incomplete, member-level OR remains `unresolved`;
- if an independent aggregate functional channel is prospectively validated and adequately establishes `F(k)=false`, the direct functional relation can be `violated`.

The second result does not infer aggregate absence from the incomplete member list. It uses a different, separately adequate answer channel.

This creates a useful design choice:

> close the alternative-provider universe, **or** close the aggregate functional observation channel.

Neither closure can be assumed from the other.

## Why this matters for the v1 hard stop

The finite v1 candidate screen should not be retrospectively rescued by relabelling its multi-partner systems as functional-pool endpoints. Those systems were already seen under a different admission contract.

Instead, the v1 result motivates a future fresh design in which the required-role answer is specified at the function level before candidate search and before focal data access.

## Current boundary

This bridge is pure theory/synthetic validation only. It does not authorize a new candidate search, source-feasibility inspection, functional-pool dataset, hard invariant, soft cross-check, or process knockout.

The 284b empirical ledger remains **1**.
