# Product-B v7 — independent literature-witness invariant

## 1. Why v7 exists

Product-B v5 and v6 established a repeated feasibility limitation before any invariant outcome could be opened. v5 required both partners to support occurrence-based niche recovery; v6 retained a full occurrence-based host X but reduced dependent Y to a sparse directional witness. Nevertheless, held-out v6 pairs still terminated before the invariant layer because confirmed obligate dependents were absent or nearly absent from the frozen GBIF evidence scope.

v7 is **not a rescue or reinterpretation of any opened v5/v6 endpoint**. Every pair admitted to v5 or v6 is firewalled from v7 confirmatory use. v7 changes the independent answer-check source for Y while preserving the v6 host and witness floors.

## 2. Estimand

For a directed biological dependence `Y requires X`, recover environmental support for X only, using the frozen Product-B measurement apparatus. Evaluate independently published, georeferenced Y occurrences as witness cells:

> What fraction of unique, predeclared literature-witness cells for Y fall inside the recovered support of X, and is that containment stronger than the same witness cells evaluated against a frozen pool of biologically non-required replacement hosts?

Y is never fitted as a niche in v7.

## 3. What changes from v6 — and what does not

### Changes

- Y witness evidence comes from primary-literature coordinates or primary-literature specimen tables, not from GBIF occurrence availability.
- The geographic evaluation frame must be independent of the Y witness coordinates. It is a pre-existing named boundary (administrative unit, protected area, ecoregion, or an independently supplied primary-literature study-region polygon).
- The Y witness coordinates are test points only. They may not determine the host training background, frame geometry, support threshold, procedure set, or control pool.

### Unchanged

- host X sampling floor: at least 50 independent records, 30 unique 10-km cells, and 10 effective cells;
- dependent witness floor: at least 5 independent literature witnesses and at least 3 unique 10-km cells;
- 10-km equal-area cell semantics and the existing coordinate-quality ceiling;
- host-support breadth guardrail: recovered X support may occupy at most 0.80 of the frozen audit frame;
- at least 5 frozen replacement hosts;
- 100 deterministic shuffled-host draws and q05/q95 three-state comparison;
- no post-outcome relaxation, pair replacement, frame widening, or threshold adjustment;
- no refitting after process knockout in any later process-necessity layer.

## 4. Literature-witness admission contract

A Y witness is admissible only if all of the following were declared before any occurrence/model outcome is opened:

1. it comes from a primary source independently establishing the relevant taxon identity or biological association;
2. latitude/longitude are printed directly in the source or supplied in a stable primary supplementary table;
3. the coordinate was not geocoded by this project from a locality name;
4. stated or inferable positional uncertainty does not exceed 10 km;
5. a stable specimen, sample, site, voucher, or source-row identifier is available so duplicate witnesses can be removed;
6. the witness is not part of a v5/v6 opened or development pair.

Witnesses sharing the same stable source identifier are duplicates. After quality filtering, the frozen 10-km equal-area cell rule collapses repeated witnesses in one cell for containment scoring. Missing evidence is unresolved, never consistency.

## 5. Independent frame contract

The v7 evaluation frame must not be a convex hull, buffer, range estimate, or density surface derived from Y witness coordinates or X/Y occurrence availability.

Allowed frame sources are frozen before occurrence access:

- `preexisting_admin_boundary`;
- `protected_area_boundary`;
- `ecoregion_boundary`;
- `primary_literature_study_region_geometry` only when the source supplies the geometry independently of the Y witness table.

A deterministic boundary version/source identifier is mandatory. If no such frame is available, the pair is `unresolved_frame` and stops before host occurrence access.

## 6. Focal host and controls

X is the only species requiring occurrence-based sampling adequacy. The same 50/30/10 host floor used in v6 remains binding.

Replacement hosts are declared from biology/taxonomy before occurrence availability is inspected. At least 5 must survive taxonomy and host-sampling gates. The pool cannot be enlarged after counts are seen.

The same Y witness cells are evaluated against focal X and every eligible replacement host. Thus the negative-control contrast asks whether the declared biological host contains the independent witness set more strongly than plausible non-required hosts under the same observation grain.

## 7. Primary quantities and classification

Reuse the pure v6 quantities:

- `directed_witness_containment(X, Y_witness_cells)`;
- host support fraction across the entire frozen frame;
- 100 shuffled-host witness containments;
- q05/q95 reference band.

Classification remains:

- `compatible_with_dependency_witnesses` if actual focal containment is strictly above shuffled q95;
- `violates_dependency_witness_constraint` if actual focal containment is strictly below shuffled q05;
- `unresolved` otherwise or if any upstream gate fails.

Passing is contract-relative answer-check consistency, not proof that the recovered niche is true.

## 8. Non-retroactivity firewall

The following pairs are permanently excluded from v7 confirmatory registration because they were already admitted to v5 or v6 development or occurrence execution:

- OPM_FIG_001;
- OPM_YUC_001;
- OPM_YUC_002;
- OPM_GLO_001 through OPM_GLO_004;
- SEN001;
- EPV001;
- HTR001.

No taxon pair, scope, or threshold from those endpoints may be redefined as a v7 success.

## 9. Frozen execution order

For each new held-out v7 pair:

1. literature dependency declaration;
2. literature witness registry and witness-quality validation;
3. independent-frame declaration;
4. focal and replacement-host taxonomy resolution;
5. response-blind model-pool differentiability precheck;
6. separately freeze and authorize host occurrence sampling;
7. if X fails 50/30/10, stop `unresolved_host_sampling` without opening controls/model outcomes;
8. if X passes, test replacement-host sampling; fewer than 5 adequate controls -> `unresolved_controls_sampling`;
9. separately freeze model/invariant contract;
10. only then open X/control recovered supports and compute witness containment;
11. process knockouts remain a still-later separately frozen step.

## 10. Claim boundary

v7 tests whether an X-only recovered support respects independently published directional Y witnesses more strongly than frozen replacement hosts. It does not establish fundamental-niche recovery, site-level obligatory co-occupancy, causal physiology, demographic fitness, dispersal history, or interaction strength. A violation can implicate the recovered representation, observation process, literature taxon/host assignment, grain choice, or frame contract. Consistency constrains; it does not confirm.
