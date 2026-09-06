# Product-B paired biological answer-check execution plan

## Scientific sequence

Product-B is now organized as three escalating validation layers rather than as a search for one universally best predictor set.

### Layer 1 — same-target cross-source reproducibility

Question:

> Does the same modeling procedure recover a coherent ecological answer for the same biological target when the observation system changes?

Calibration panel: the 36 pre-existing Product-A v2.7.1 taxon candidates selected before Product-B cross-source outcomes existed.

For each taxon:

1. resolve one snapshot-stable taxonomic identity without occurrence-count selection;
2. partition the frozen 2026-08-01 GBIF snapshot into disjoint `PRESERVED_SPECIMEN` and `HUMAN_OBSERVATION` records;
3. require the frozen 50 records / 30 unique 10-km cells / 10 effective cells floor separately for both modes;
4. reuse the Product-A response-blind M grid (150, 300, 500 km), never selecting M from cross-source results;
5. for each of the 8 frozen recovery procedures, fit the two observation modes independently under the same procedure and same M;
6. compute `1 - Schoener's D` as the primary cross-source discordance and rank-profile discordance as descriptive support;
7. for every procedure × M cell with at least 30 complete taxa, freeze the nearest-rank 95th percentile as that cell's cross-source reference ceiling.

Calibration-panel members are not confirmatory cases. Their role is to quantify ordinary reconstruction disagreement caused by changing the observation view.

### Layer 2 — held-out biological cross-validity

Question:

> When independent biology says two ecological answers should cohere, does a procedure stay within the amount of disagreement expected from Layer 1?

Candidate relation classes include:

- same target from a new independent observation source;
- soft expected concordance;
- directional dependency (`Y requires X`);
- mutual dependency (`X <-> Y`);
- life-stage coupling.

Soft relations are evaluated against the frozen procedure × M reference ceiling. Exceedance is `paired_crosscheck_attention_required`, not automatic proof that either answer is false.

Hard relations retain their dedicated biological invariant semantics. For example, a complete admissible directional dependency violation is still `invariant_violated` even if generic source-calibrated discordance would otherwise look ordinary.

### Layer 3 — process necessity by coherence intervention

Only after a procedure is coherent at baseline do process knockouts become informative.

For each frozen environmental process:

1. remove/marginalize that process under the existing no-rescue intervention contract;
2. recompute the paired biological answer-check without changing the relation, M, controls, or reference ceiling;
3. ask whether a previously coherent pair becomes unusually discordant or violates a hard invariant.

This distinguishes three ideas that ordinary prediction metrics conflate:

- predictive adequacy;
- cross-source reconstruction stability;
- biological cross-coherence.

A process is scientifically interesting when removing it selectively damages the third while the comparison remains otherwise admissible.

## Procedure-level interpretation

The eight frozen Product-A procedures are not collapsed into a single calibration score. Each procedure is calibrated against its own cross-source behavior at each M.

This makes cross-source coherence a procedure property:

- a procedure can be predictively adequate yet observation-view-sensitive;
- another can be predictively adequate and cross-source stable;
- only held-out biological relations can test whether that stability transfers to external ecological constraints.

Layer 1 therefore cannot promote a procedure as ecologically correct by itself. It can identify procedures whose answers are unusually fragile to observation source and procedures that are suitable for stronger held-out biological testing.

## Main claim if the sequence succeeds

A successful paper-level result would not be "one SDM algorithm is best." It would be:

> Ecological models can be evaluated by cross-consistency among independently obtained answers. Cross-source replication calibrates ordinary reconstruction disagreement; externally known biological relations then provide held-out answer checks; process interventions reveal which environmental information is required to preserve that cross-coherence.

## Main falsification outcomes

The design remains informative under failure.

- If same-target cross-source answers are broadly unstable across procedures, the bottleneck is reconstruction/observation sensitivity before stronger biology is interpreted.
- If same-target calibration is stable but held-out biological pairs diverge, the failure is relation-specific and biologically informative.
- If baseline pairs are coherent but a process knockout creates divergence, that process is a candidate coherence-critical environmental component.
- If all process knockouts preserve coherence, the tested processes are substitutable with respect to that biological answer-check under the frozen model set.
