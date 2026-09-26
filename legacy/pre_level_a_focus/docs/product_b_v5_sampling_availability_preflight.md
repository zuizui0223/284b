# Product-B v5 — sampling-availability preflight

## Status

**Specified and testable, not executed.** No occurrence counts, maps, unique-cell counts, environmental values or invariant outcomes have been opened for this step.

This preflight may only be executed later for pairs that first pass the taxonomy gate.

## 1. Purpose

The question is not whether a biologically eligible pair has "enough data" in an informal sense. The purpose is to decide, under one response-blind rule, whether the two partners can support a symmetric-enough comparison without turning detectability differences into apparent niche non-nesting.

Failure is `unresolved_sampling`, never biological violation and never permission to replace the pair after counts are known.

## 2. Spatial support grid

Sampling support is counted on a global equal-area grid:

- CRS: `EPSG:6933`;
- cell edge: `10,000 m`.

This grid is only a sampling-support audit grid. It does not claim that the obligate biological interaction operates at 10 km, and it does not itself define the later environmental audit space.

## 3. Primary predeclared thresholds

After all cross-partner same-record contamination is removed, each partner must satisfy:

- at least **50 independent records**;
- at least **30 unique 10-km cells**;
- at least **10 effective cells**, where effective cells are the inverse-Simpson effective number of cells based on record mass across occupied cells.

Between partners, all must satisfy:

- record-count asymmetry `max(n_X,n_Y)/min(n_X,n_Y) <= 10`;
- unique-cell asymmetry `<= 5`;
- effective-cell asymmetry `<= 5`.

These are operational adequacy floors, not ecological estimands. They are intentionally fixed before the counts are inspected.

## 4. Stricter sensitivity contract

A second, already-declared sensitivity condition is frozen simultaneously:

- at least 100 independent records per partner;
- at least 50 unique cells per partner;
- at least 20 effective cells per partner;
- record asymmetry <= 5;
- unique-cell asymmetry <= 3;
- effective-cell asymmetry <= 3.

The primary analysis is not retuned if few pairs pass the stricter condition. The stricter condition is reported only as a robustness tier.

## 5. Effective occupied cells

Let `c_i` be the number of retained records in occupied 10-km cell `i`, and `p_i = c_i / sum(c_i)`.

`effective_cells = 1 / sum(p_i^2)`.

This distinguishes a nominally broad set of occupied cells from a dataset overwhelmingly concentrated in one or two cells. It is a sampling-concentration diagnostic, not niche breadth.

## 6. Same-record contamination exclusion

Before any denominator or threshold is calculated, identify cross-partner records sharing any of the following evidence:

1. occurrence-ID lineage;
2. event ID;
3. catalog/specimen number;
4. dataset key + event date + coordinate;
5. recorder + date + coordinate.

If an identity group contains records from both partners, all records in that cross-partner group are removed from both sides before calculating the retained denominator. This is deliberately conservative: a shared collecting event must not create apparent obligate nesting by construction.

The audit must later report, per pair and per partner:

- raw record denominator;
- collision-excluded records;
- retained independent records.

If exclusion drives either partner below any primary floor, the pair is `unresolved_sampling`.

## 7. Cross-kingdom observation semantics

Phase 1 is plant–insect. Therefore:

- plant and insect target-group backgrounds are separate;
- both background frames must obey the pair's already-declared geographic scope;
- the background-frame rule is chosen without consulting pair outcomes;
- animal occurrence is not interpreted as proof of habitat use;
- later observation-correction activation is reported separately by kingdom.

The sampling preflight only decides whether the occurrence evidence architecture is admissible. It does not erase plant–animal detectability differences.

## 8. State machine

A pair entering this step has already passed `eligible_for_sampling_preflight` at the taxonomy layer.

Sampling result:

- `sampling_preflight_passed` — every primary floor and asymmetry ceiling passes after contamination exclusion;
- `unresolved_sampling` — at least one required quantity fails or cannot be computed.

There is no `sampling_failed_biology` state.

## 9. Forbidden adaptation after counts are opened

After a count is opened, do not:

- lower a minimum-record or minimum-cell floor;
- enlarge cells to rescue a sparse partner;
- relax an asymmetry ceiling;
- replace the pair with a better-sampled congener;
- broaden a taxon to genus level;
- change the declared geographic scope;
- switch taxonomy checklists;
- use record availability to redefine obligacy.

A sparse or asymmetric pair stays in the denominator as unresolved.

## 10. Execution boundary

This document and the pure functions/tests may be committed now. Actual occurrence retrieval and count computation remain a separate authorized step.

At the end of this step, Product-B v5 has a response-blind chain:

`literature pair declaration -> taxonomy gate -> sampling gate -> later model/invariant evaluation`.

No downstream layer may rewrite an upstream declaration.