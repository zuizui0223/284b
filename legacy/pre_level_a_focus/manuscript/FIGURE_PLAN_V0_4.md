# Pre-field flagship figure plan v0.4 — Reviewer-2 hardened

Target: Ecology Letters — Method  
Maximum display items: 6  
Canonical manuscript: `manuscript/PREFIELD_FLAGSHIP_V0_7.md`

Design rule: every empirical panel must point to a frozen artifact or outcome-blind audit. Synthetic panels must not read focal Level-C biological values.

## Notation

- `q` = key-level sensitivity conditional on `F=true` and a valid key;
- `sp` = specificity conditional on `F=false` and a valid key;
- `a1 = P(valid key | F=true)`;
- `a0 = P(valid key | F=false)`;
- `pi` = true biological violation prevalence.

The old single-`a` notation is permitted only for the explicit equal-validity corollary `a1=a0=a`.

## Figure 1 — Executable relation-endpoint contract

Purpose: make the Method an executable inferential object rather than a workflow philosophy.

Panels:
- A: five-part contract — relation, key space, adapters, adequacy gates, opening rule;
- B: calibrated soft endpoint state machine — `consistent`, `attention_required`, `unresolved`;
- C: hard directional state machine `E(k) -> F(k)` — `hard_violation_authorized`, `no_observed_violation`, `noninformative_for_implication`, `unresolved`;
- D: relation ladder A–E, clearly marking which primitives are directly implemented in the current paper.

Canonical sources:
- `scripts/relation_endpoint_contract.py`;
- `tests/test_relation_endpoint_contract.py`;
- `manuscript/PREFIELD_FLAGSHIP_V0_7.md`.

No focal Level-C values.

## Figure 2 — Controlled Level-A empirical anchor

Purpose: show the completed empirical result without pseudoreplication or q95 over-interpretation.

Panels:
- A: reference design — 24 procedure × accessible-area reference cells, 34–47 adequate successor taxa per cell, nearest-rank q95 frozen before held-out opening;
- B: held-out replication — **12 independent held-out taxa**; each has a prespecified 3-area × 8-procedure matrix;
- C: 288 prespecified diagnostics -> 283 evaluable / 5 unresolved; all 12 taxa have zero envelope exceedances among evaluable cells;
- D: taxon-level maximum observed-discordance / frozen-envelope ratio, emphasizing *Nothofagus betuloides* at 0.988 rather than displaying 283 cells as independent observations;
- optional inset: closest margin = 0.00460; only 1/283 evaluable cells within 0.025 of its envelope and 6/283 within 0.05.

Terminology:
- use **prospectively frozen empirical source-discordance envelope**;
- do not call q95 a 95% predictive interval or alpha=0.05 test;
- do not use 283 as an independent sample size.

Canonical sources:
- `results/reviewer2_level_a_structure_audit_v0_1.json`;
- `docs/product_b_same_target_core19_empirical_result.md`;
- `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json`.

## Figure 3 — Why dependency belongs to biological events and functions

Purpose: explain why raw distribution-surface overlap is generally the wrong object for a hard biological dependency.

Panels:
- A: rejected raw-surface containment intuition;
- B: accepted event-key implication `E(k) -> F(k)` at site × biological opportunity;
- C: named-provider set versus aggregate functional pool;
- D: incomplete provider set -> `unresolved`, direct calibrated functional absence -> potentially `F(k)=false`.

Canonical sources:
- `docs/product_b_paired_answer_check_relation_ladder.md`;
- Level-C set-valued and functional-pool bridge artifacts.

No focal Level-C values.

## Figure 4 — Two real systems reach the same openability boundary

Purpose: avoid presenting Level C as an unfinished biological experiment or a version-history funnel.

Use a parallel two-lane design rather than emphasizing v2–v8 chronology.

Shared gates:
1. external relation evidence (`R`);
2. dependent-event answer (`X`);
3. required-function answer (`Y`);
4. common event key;
5. provenance separation;
6. candidate-specific negative-state calibration.

Lanes:
- Cremastra: relation + fruit outcome + pollinia-carrying camera observations -> stops at calibrated functional absence;
- Belonocnema/live-oak: host relation + adult emergence + budbreak stream -> stops at calibrated usable-resource absence.

Bottom message: **same measurement boundary, no focal biological outcome opened**.

Put the v2–v8.1 development sequence in Supplement/Methods provenance rather than the main visual.

Canonical sources:
- v3 source-qualification artifacts;
- v5 candidate-specific calibration audit;
- v6 raw/supplementary reconstruction audit;
- v8.1 pre-data repair receipt.

## Figure 5 — Exact class-conditional cost of invalid-state coercion

Purpose: provide the central transferable quantitative result.

### Panel A — generalized decomposition

For qualified hard endpoints:

`FPR_zero - FPR_gated = 1-a1`

`TPR_zero - TPR_gated = 1-a0`.

Show false-violation inflation against `a1` and apparent sensitivity gain against `a0`. They need not be equal.

Mark the equal-validity corollary `a1=a0=a`, where both increments equal `1-a`.

### Panel B — state-dependent example

Use the outcome-blind representative scenario:

`a1=0.70`, `a0=0.90`, `q=0.95`, `sp=0.99`.

- false violation: gated 0.035 -> zero collapsing 0.335;
- true-violation sensitivity: gated 0.891 -> zero collapsing 0.991.

This makes the hidden-symmetry repair concrete.

### Panel C — qualification is not false-discovery control

Plot

`FDF = (1-pi)(1-q) / [(1-pi)(1-q) + pi sp]`

against `pi` for representative `q`, with `sp=0.99`. Mark `pi=0.10`, `q=0.80`, where FDF ~=0.645.

### Panel D — ablation interpretation

Small schematic: zero collapsing removes the `unresolved` state from the endpoint engine. Label it explicitly as an **ablation / forbidden operation**, not a competing observation model.

Canonical sources:
- `scripts/relation_endpoint_contract.py`;
- `results/pre_field_state_dependent_invalidity_v0_2.json`;
- `results/pre_field_identifiability_benchmark_summary_v0_1.json`.

## Table 1 — Claim/evidence matrix

Columns:
- inferential level;
- relation;
- evidence required;
- completed evidence;
- current status;
- allowed claim;
- prohibited claim.

Rows:
- Level A answer construction;
- Level A cross-validity;
- Level A process necessity;
- Level B relation-specific soft calibration;
- Level C event/function architecture;
- Level C negative-state calibration;
- Level C focal hard invariant;
- Level C process knockout.

Canonical source:
- `manuscript/CLAIM_EVIDENCE_LEDGER_V0_2.md` plus reviewer-hardened claim boundary in `PREFIELD_FLAGSHIP_V0_7.md`.

## Figure priority if editors request fewer display items

1. Figure 5 — quantitative Method contribution.
2. Figure 2 — empirical anchor.
3. Figure 1 — executable framework.
4. Figure 4 — real-system stopping-rule demonstration.
5. Figure 3 — merge into Figure 1 if necessary.
6. Table 1 — move to Supplement first.
