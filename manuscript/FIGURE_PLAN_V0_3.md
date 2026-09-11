# Pre-field flagship figure plan v0.3

Target: Ecology Letters Method  
Maximum display items: 6  
Design rule: every empirical panel must point to a canonical frozen artifact; synthetic panels must be generated only from synthetic benchmark code/results and must not read focal Level-C values.

## Notation used in figures

To avoid symbol collision:

- `q` = key-level sensitivity;
- `sp` = specificity;
- `a` = valid-key fraction (complete, nonmissing, nonfailed);
- `pi` = true biological violation prevalence.

Do **not** use `v` for both valid-key mass and violation prevalence.

## Figure 1 — What relation are we actually testing?

**Purpose:** establish the inferential ladder before any results.

Panels:
- A: Level A same target / independent observation source.
- B: Level B soft cross-role concordance after relation-space adaptation.
- C: Level C directional dependency `E(k) -> F(k)` at a biological event key.
- D: state machine: `detected function`, `calibrated absence`, `unresolved non-detection`, `failure/missingness`.

Main visual message: raw model outputs are not directly comparable across roles; comparison occurs only after relation-specific adaptation.

Canonical source:
- `docs/product_b_paired_answer_check_relation_ladder.md`

No numerical focal Level-C values appear.

## Figure 2 — Controlled Level-A empirical closure

**Purpose:** provide the paper's completed empirical anchor.

Panels:
- A: successor calibration design: 24 procedure × M cells, >=30 adequate successor taxa per cell.
- B: held-out design: 12 taxa × 3 M × 8 procedures = 288 cells.
- C: outcome counts: 283 opened / 5 closed; 283/283 below frozen q95 ceiling; zero `attention_required`.
- D: margin-to-ceiling display for the 283 opened cells if canonical cell-level receipt is materialized for plotting; otherwise show the closest-cell example and outcome-count panel only.

Canonical sources:
- `docs/product_b_same_target_core19_empirical_result.md`
- `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json`

Forbidden: treating the five closed cells as successes or failures.

## Figure 3 — Why dependency belongs to events and functions

**Purpose:** explain the conceptual move that makes Level C biologically meaningful.

Panels:
- A: rejected raw-surface containment intuition.
- B: accepted event-key implication: dependent event at site × biological window -> required function at the same key.
- C: named-provider set versus functional pool; complete provider set can map to aggregate function, incomplete set cannot establish absence.

Canonical sources:
- `docs/product_b_paired_answer_check_relation_ladder.md`
- Level-C set-valued / functional-pool bridge artifacts.

No focal outcome values.

## Figure 4 — Level-C identifiability funnel

**Purpose:** show that Level C did not simply 'fail'; each prospective version moved the binding constraint.

Suggested funnel:

`named provider` -> `function-level relation` -> `R/X/Y source architecture` -> `negative-state adequacy` -> `candidate-specific calibration` -> `raw/supplementary reconstruction` -> `prospective field calibration`.

Annotate:
- v2: 12 screened, 0 fully admitted; binding constraint becomes focal evidence independence.
- v3: 12 screened, 2 architecture-qualified; binding constraint becomes absence adequacy.
- v4: synthetic absence rule qualifies; actual candidates remain blocked.
- v5: 0/2 candidate-specific calibration streams available.
- v6: 0/2 calibration streams reconstructed from identified existing raw/supplementary sources.
- v7-v8: prospective field-calibration workflow frozen; focal endpoint remains closed.
- v8.1: pre-data exact-confidence implementation repair; thresholds/candidates/minimum counts unchanged.

Canonical sources:
- v2-v8 hard-stop/receipt artifacts;
- `docs/product_b_level_c_v8_1_exact_confidence_repair.md`.

Every Level-C state shown here is design/identifiability evidence, not a focal biological conclusion.

## Figure 5 — Exact cost of collapsing invalid observation into zero

**Purpose:** make the transferable method contribution quantitative.

### Panel A — invalid-state inflation

For qualified processes:

`FPR_zero = 1 - a q`

`FPR_gated = a(1-q)`

therefore

`FPR_zero - FPR_gated = 1-a`.

Likewise:

`TPR_zero - TPR_gated = 1-a`.

Show zero-collapsing and gated curves against valid-key fraction `a` for fixed `q` values. The vertical gap is exactly `1-a`.

### Panel B — qualification is not false-discovery control

For valid gated calls, plot

`FDF = (1-pi)(1-q) / [(1-pi)(1-q) + pi sp]`

against true violation prevalence `pi`, for representative `q` values with fixed high specificity. Mark the threshold example `pi=0.10`, `q=0.80`, `sp=0.99`, where FDF is approximately 0.645.

Interpretation: calibration controls whether a hard-negative state may enter the endpoint; it does not by itself determine posterior reliability of a called biological violation.

### Optional supplement panels

Move representative scenario bars and the calibration pass/fail boundary to Supplement unless editors request them in the main figure.

Canonical synthetic sources:
- `scripts/run_pre_field_identifiability_benchmark.py`
- `results/pre_field_identifiability_benchmark_summary_v0_1.json`
- `results/pre_field_identifiability_benchmark_scenarios_v0_1.csv`
- `manuscript/SYNTHETIC_BENCHMARK_RESULT_V0_1.md`.

The equal-weight grid is a stress test, not an estimate of environmental frequencies.

## Table 1 — Claim/evidence matrix

Columns:
- inferential level;
- relation;
- evidence needed;
- completed evidence;
- current status;
- allowed claim;
- prohibited claim.

Rows:
- Level A observability / answer construction;
- Level A cross-validity;
- Level A process necessity;
- Level B relation-specific soft calibration;
- Level C event/function architecture;
- Level C negative-state calibration;
- Level C focal hard invariant;
- Level C process knockout.

Canonical source:
- `manuscript/CLAIM_EVIDENCE_LEDGER_V0_2.md`.

## Figure priority if editors request fewer items

Keep in this order:
1. Figure 5 — method novelty.
2. Figure 2 — empirical validation.
3. Figure 1 — framework.
4. Figure 4 — real-system identifiability stress test.
5. Figure 3 — merge into Figure 1 if needed.
6. Table 1 — move to Supplement first.
