# Product-B v6 — directed dependency witness invariant

## Status

**Successor design only; not empirically executed.**

Product-B v5 Phase 1 is terminal and is not reinterpreted here. Its seven-pair panel reached zero invariant evaluations because upstream response-blind gates stopped all pairs. The three pairs whose occurrences were opened in v5 (`OPM_FIG_001`, `OPM_YUC_001`, `OPM_YUC_002`) are permanently excluded from any confirmatory v6 primary panel. They may be used only as engineering examples after the v6 contract is frozen.

## 1. Why v6 exists

v5 required both partners of `Y_requires_X` to support symmetric niche recovery. Real public data were strongly asymmetric: host plants could have thousands of records while obligate insects had only a handful. Lowering the v5 floors would be post-outcome rescue, so v5 remains unresolved.

v6 changes the experimental unit rather than changing the v5 threshold:

- fit/recover environmental support only for the required partner `X`;
- treat independently observed `Y` records as **dependency witnesses**, not as a second niche to estimate;
- ask whether those witnesses fall inside recovered `X` support more often than matched shuffled-host controls;
- apply process knockouts to the already-fitted `X` response surface without refitting.

The biological direction remains `Y_requires_X`.

## 2. Confirmatory-data firewall

The v6 primary panel must contain only literature-declared pairs that were **not occurrence-opened in v5**.

Before any new occurrence query:

1. freeze pair identity and `Y_requires_X` direction from independent literature;
2. freeze taxonomy keys and concepts;
3. freeze operational geographic scope;
4. freeze witness and host sampling floors;
5. freeze shuffled-host control eligibility;
6. freeze process-knockout admissibility.

No v5 empirical count may be used to choose a v6 primary pair.

## 3. Predeclared sampling architecture

### 3.1 Required partner X

Reuse the v5 host-side adequacy floor unchanged:

- >= 50 independent `X` records;
- >= 30 unique 10-km EPSG:6933 cells;
- >= 10 inverse-Simpson effective cells.

The existing coordinate-quality and cross-partner collision rules are reused unchanged.

### 3.2 Dependent partner Y as witnesses

`Y` is not fitted as a niche. After the same quality and collision exclusions, require only:

- >= **5 independent witness records**;
- >= **3 unique 10-km cells**.

These values are frozen before a new held-out v6 pair is queried. A pair below either floor is `unresolved_witness_sampling`; it is not replaced or widened after counts are seen.

Within each 10-km cell, multiple `Y` records contribute one witness so duplicated observation effort does not dominate the score.

## 4. Recovered support

For each candidate procedure `p`, let `S_X,p(c)` be a fixed recovered-support indicator or support probability on the audit grid for required partner `X`.

`S_X,p` must come from the already-fitted complete adequate candidate apparatus. v6 must not refit a model using `Y` witnesses.

A breadth guardrail remains mandatory: a procedure cannot pass merely by making `X` support nearly universal across the audit space.

## 5. Primary quantities

For unique witness cells `W_Y`:

### Directed witness containment

`C_p = mean_{c in W_Y} S_X,p(c)`

For binary support, `C_p` is the fraction of dependent witness cells contained in recovered `X` support.

### Shuffled-host contrast

For matched alternative hosts `X*` that are not the literature-declared required partner:

`Delta_p = C_p(actual X) - mean[C_p(shuffled X*)]`

The primary evidence is the actual-pair excess over shuffled-host controls, not raw containment alone.

### Process-knockout drop

For frozen process knockout `k` applied without refitting:

`K_{p,k} = C_p(full) - C_p(knockout k)`

A process is informative only when its knockout preferentially erodes actual-pair witness containment relative to shuffled-host controls.

## 6. Control requirements

Before outcomes are opened:

- at least 5 eligible shuffled required-partner replacements;
- replacement host uses the same broad taxonomic/observation stratum where possible;
- replacement host must pass the same `X` sampling floor;
- replacement cannot be a documented obligate host of the focal `Y`;
- 100 deterministic SHA256-seeded shuffled draws;
- no family/caliper relaxation after control availability is seen.

If fewer than 5 replacements survive, state is `unresolved_controls`.

## 7. Three-state procedure result

A candidate procedure is classified only after host adequacy, witness sampling, control availability and breadth guardrails pass.

- `compatible_with_dependency_witnesses`: actual directed witness containment is above the predeclared shuffled-host reference criterion and no guardrail fails;
- `violates_dependency_witness_constraint`: recovered `X` support is systematically less compatible with the known `Y_requires_X` witnesses than the predeclared control criterion permits;
- `unresolved`: any prerequisite, control, breadth or numerical condition fails.

This classifier evaluates the **recovered model/procedure**, not the truth of the biological dependency.

## 8. Claim boundary

v6 can support the claim that a candidate environmental procedure better preserves externally declared dependency constraints than matched alternatives and can identify which frozen process knockouts are responsible for that preservation.

It cannot prove the complete fundamental niche of either partner, infer obligacy from occurrence overlap, or retroactively turn the v5 feasibility failure into a positive result.

## 9. Current execution boundary

Allowed now:

- pure v6 functions;
- synthetic tests;
- empty new-pair registry schema;
- preflight contracts.

Not allowed yet:

- choosing primary v6 pairs from observed GBIF counts;
- querying occurrences for a new v6 pair before registry/scope freeze;
- reusing the three occurrence-opened v5 pairs as confirmatory v6 evidence;
- process-knockout outcomes on real data.
