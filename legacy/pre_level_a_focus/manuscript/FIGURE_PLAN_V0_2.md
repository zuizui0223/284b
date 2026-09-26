# Pre-field flagship figure plan v0.2

Target: Ecology Letters Method  
Maximum display items: 6  
Design rule: every empirical panel must point to a canonical frozen artifact; synthetic panels must be generated only from the synthetic benchmark code/results and must not read focal Level-C values.

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
- A: rejected raw-surface containment intuition (e.g. adult plant occupancy contained within current pollinator occupancy).
- B: accepted event-key implication: reproductive event at site × flowering window -> effective pollination function at the same key.
- C: named-provider set versus functional pool; complete provider set can map to aggregate function, incomplete set cannot establish absence.

Canonical sources:
- `docs/product_b_paired_answer_check_relation_ladder.md`
- Level-C set-valued / functional-pool bridge artifacts.

No focal outcome values.

## Figure 4 — Level-C identifiability funnel

**Purpose:** show that Level C did not simply 'fail'; each version moved the binding constraint.

Suggested horizontal funnel:

`named provider` -> `function-level relation` -> `R/X/Y source architecture` -> `negative-state adequacy` -> `candidate-specific calibration` -> `raw/supplementary reconstruction` -> `prospective field calibration`

Annotate:
- v2 finite screen: 12 screened, 0 fully admitted; binding constraint becomes focal evidence independence.
- v3: 12 screened, 2 architecture-qualified (`CREMV3-007`, `BELV3-012`); binding constraint becomes absence adequacy.
- v4: synthetic absence rule qualifies; actual candidates remain blocked.
- v5: 0/2 candidate-specific calibration streams available.
- v6: 0/2 calibration streams reconstructed from identified existing raw/supplementary sources.
- v7-v8: field calibration protocol and evaluator frozen; focal endpoint remains closed.

Canonical sources:
- `docs/product_b_level_c_functional_pool_v2_hard_stop.md`
- `results/product_b_level_c_source_architecture_hard_stop_v3.json`
- `results/product_b_level_c_source_qualification_v3.json`
- `results/product_b_level_c_absence_candidate_audit_v4.json`
- `results/product_b_level_c_candidate_specific_calibration_audit_v5.json`
- `results/product_b_level_c_raw_calibration_reconstruction_v6.json`
- `results/product_b_level_c_field_calibration_handoff_v7.json`
- `results/product_b_level_c_operational_package_v8.json`

Every v2-v8 Level-C state remains design/identifiability evidence, not a focal biological conclusion.

## Figure 5 — Exact cost of collapsing invalid observation into zero

**Purpose:** make the transferable method contribution quantitative.

Panel A — exact false-violation decomposition.

For qualified processes:

`FPR_naive = 1 - vq`

`FPR_gated = v(1-q)`

so

`FPR_naive - FPR_gated = 1-v`.

Plot false-violation probability against invalid-key mass `1-v` for several fixed `q` values (e.g. 0.80, 0.90, 0.99). Naive lines increase with slope 1; gated lines decrease with `v` only through the residual valid-key false-negative term.

Panel B — exact apparent-sensitivity decomposition.

`TPR_naive - TPR_gated = 1-v`.

Show that the naive sensitivity gain is exactly the invalid-key mass rather than additional biological information.

Panel C — representative synthetic regimes from `results/pre_field_identifiability_benchmark_scenarios_v0_1.csv`: high-quality, high-missingness, device failure, incomplete window, mixed qualified and subthreshold sensitivity.

Panel D — decision boundary. Below `q=0.80` or `sp=0.95`, gated hard calls are zero and relevant zeros route to unresolved.

Canonical synthetic sources:
- `scripts/run_pre_field_identifiability_benchmark.py`
- `results/pre_field_identifiability_benchmark_summary_v0_1.json`
- `results/pre_field_identifiability_benchmark_scenarios_v0_1.csv`

Interpretation note: the equal-weight parameter grid is a stress test, not an estimate of the frequency of ecological conditions in nature.

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
- `manuscript/CLAIM_EVIDENCE_LEDGER_V0_1.md`

## Figure priority if editors request fewer items

Keep in this order:
1. Figure 5 — method novelty.
2. Figure 2 — empirical validation.
3. Figure 1 — framework.
4. Figure 4 — real-system identifiability stress test.
5. Figure 3 — merge into Figure 1 if needed.
6. Table 1 — can move to Supplement if necessary.
