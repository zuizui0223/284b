# Paper 1 Supplement routing v0.1

**Purpose:** keep the Ecology Letters Method main text conceptually tight while preserving auditability and reproducibility. This routing changes presentation only; no empirical endpoint or threshold changes.

## Main-text rule

A detail stays in the main text only if removing it would weaken one of the five paper claims:

1. accurate answers do not determine the biological relation;
2. the relation endpoint is executable/fingerprintable;
3. Level A closes on 12 fresh held-out taxa;
4. preserving `unresolved` prevents exact class-specific error inflation;
5. two real systems prospectively stop at the same negative-state measurement boundary.

Everything else should support those claims from Supplement rather than compete with them.

## Keep in main text

### Relation-endpoint architecture

- five contract objects;
- `opening_rule_reference` and fingerprint concept;
- soft/hard endpoint state semantics;
- short Fréchet–Hoeffding separation argument (`p_E=p_F=0.5`, `v=0` versus `v=0.5`);
- explicit concession that JSDMs can estimate joint structure and that co-occurrence is not identical to interaction semantics.

### Level-A empirical anchor

- 12 independent held-out taxa;
- 288 prespecified repeated diagnostics;
- 283 evaluable / five unresolved;
- **0/12 taxa with an envelope exceedance among evaluable cells**;
- one sentence that q95 is a prospectively frozen empirical source-discordance envelope, not nominal 95% coverage.

### Unresolved-state result

- definitions of `a1`, `a0`, `q`, `sp`;
- exact identities `FPR_zero-FPR_gated=1-a1` and `TPR_zero-TPR_gated=1-a0`;
- one representative numerical example at most;
- one sentence that calibration qualification is not false-discovery control.

### Real-system stopping rule

- Cremastra and Belonocnema identities and biological roles;
- R/X/Y separation and common-key qualification in one concise paragraph;
- the common stopping point: candidate-specific functional absence is not calibrated;
- conclusion: next admissible information is new calibration/direct functional measurement.

## Route to Supplement

### Supplement S1 — Level-A calibration and held-out implementation

Move or retain here:

- all 24 procedure × accessible-area reference-cell definitions;
- complete 34–47 successor-taxon counts per reference cell;
- successor-sealing details including the 2,255/2,256 fit-cell history;
- exact 2,000-row comparison-frame construction;
- full held-out taxon × area × procedure diagnostic table;
- margins to ceiling for all 283 evaluable cells;
- full adequacy failure reasons for the five unresolved cells.

Main text should not enumerate these unless a reviewer requests them.

### Supplement S2 — Endpoint contract implementation and fingerprint audit

- canonical field schema and serialization details;
- synthetic freeze receipt;
- fingerprint stability/change tests;
- unknown/missing-field rejection;
- quickstart examples for every soft/hard state;
- explicit statement that hashing is an audit mechanism, not proof of outcome blindness.

### Supplement S3 — Invalid-state benchmark and operating characteristics

- complete 8,748-scenario equal-validity grid;
- 4,320 passing / 4,428 failing calibration combinations;
- floating-point equality audit;
- full state-dependent `a1/a0` synthetic audit;
- false-discovery-fraction derivation and prevalence sensitivity table/curve;
- all scenario-specific maxima/minima beyond the single main-text example.

### Supplement S4 — v8 → v8.1 prospective implementation repair

Move the implementation-history detail out of the main narrative:

- original one-sided exact-or-more-conservative contract;
- discovery that v8 evaluator used a Wilson lower bound;
- immutable v8 provenance;
- v8.1 Clopper–Pearson repair;
- proof that thresholds, candidates and minimum counts were unchanged;
- proof that field calibration data had not been seen.

Main text needs at most: “A pre-data implementation audit corrected the confidence-bound implementation without changing scientific thresholds or candidate identities (Supplement S4).”

### Supplement S5 — Calibration feasibility and minimum-count operating characteristics

- 28/30 known-positive success threshold under the frozen rule;
- 60/60 known-negative specificity threshold;
- pass probabilities at candidate true sensitivity/specificity values;
- any larger prospective design calculations;
- explicit ban on outcome-dependent sample-size extension.

These are useful design diagnostics, not core Method results.

### Supplement S6 — Level-C candidate discovery and source qualification

- finite candidate universe and hard-stop logic;
- full candidate-screening ledger;
- source-materialization details;
- provenance-separation audits;
- candidate-specific absence-calibration searches;
- supplementary/raw-source reconstruction attempts;
- evidence that unavailable sources were never recoded as biological negatives.

Main text should retain only the two retained systems and their common stopping point.

### Supplement S7 — Scope extensions

- Level B relation-specific soft calibration examples;
- composition logic for mutual dependency and life-stage coupling;
- additional host, trophic, pollination and sensor examples;
- any extended discussion of provider-set closure versus direct aggregate function.

Levels B/D/E should not read as missing empirical results in Paper 1.

## Display routing

Main display package remains six items under `FULL_SUBMISSION_DISPLAY_MANIFEST_V0_2.md`.

Recommended Supplement displays:

- S1: full Level-A diagnostic matrix/table;
- S2: fingerprint round-trip / contract schema table;
- S3: full benchmark operating-characteristic surfaces;
- S4: v8/v8.1 provenance timeline;
- S5: calibration pass-probability curves;
- S6: Level-C candidate flow diagram and source-qualification table.

## Main-text deletion test

Before final promotion, each detailed paragraph should be challenged with: “If this paragraph moves to Supplement, does one of the five main claims become harder to understand or defend?” If not, move it. The goal is not minimal documentation; it is maximum conceptual signal in the main text with complete auditability outside it.
