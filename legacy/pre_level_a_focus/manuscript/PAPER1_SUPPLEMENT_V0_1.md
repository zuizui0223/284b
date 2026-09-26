# Supplementary Information — Relation endpoints for ecological inference

**Paper:** *Relation endpoints for ecological inference: when independent answers can support joint biological claims*  
**Target:** Ecology Letters — Method  
**Version:** Supplement v0.1 for the noncanonical v0.9/v0.9.1 full-manuscript candidate  
**Scientific boundary:** Level A is the sole completed empirical endpoint; Level B is unopened; focal Level-C hard/soft/process-knockout outcomes remain sealed; empirical ledger = **1**.

This Supplement preserves implementation detail, design provenance and diagnostic breadth that are useful for auditability but would dilute the five-claim main-text spine. Nothing here opens a new focal biological endpoint.

## Supplement S1. Level-A calibration and held-out implementation

### S1.1 Controlled comparison design

Level A compares two independently generated answers to the **same biological target** using preserved-specimen and human-observation records. Within each procedure-by-accessible-area cell, the target, ecological estimand, `bio1-bio19` predictor universe, estimator/procedure identity, accessible-area semantics, exact 2,000-row comparison frame, adequacy logic and reference rule were fixed before held-out opening.

The calibration universe comprised 24 procedure-by-accessible-area reference cells. Each reference cell required at least 30 prospectively adequate successor taxa. All 24 passed that gate, with 34–47 distinct adequate successor taxa per cell. The reference statistic is the frozen nearest-rank q95 of source discordance. Throughout the paper, q95 is interpreted as a **prospectively frozen empirical source-discordance envelope**, not a nominal 95% predictive interval, an alpha=0.05 test or family-wise error control.

Canonical evidence:

- `docs/product_b_same_target_core19_empirical_result.md`;
- `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json`;
- `results/reviewer2_level_a_structure_audit_v0_1.json`.

### S1.2 Independent replication and repeated diagnostics

The independent held-out biological units are **12 taxa**. Each taxon contributes a prespecified 3 accessible-area × 8 procedure matrix, for 288 repeated cell diagnostics. Both answers passed adequacy in 283 cells; five stayed unresolved. The five unresolved cells are not failures and do not enter the relation check.

Among evaluable cells, **0 of 12 held-out taxa contained an envelope exceedance**. The 283/283 cell count is therefore a diagnostic summary nested within the 12 taxa, not an independent binomial sample size.

The closest evaluable cell was *Nothofagus betuloides* under the 150-km accessible area and `predictive_forward|logit_l2_C1_degree2`: discordance 0.38625 versus frozen envelope 0.39085, margin 0.00460. One evaluable cell lay within 0.025 of its envelope and six within 0.05. These margins are stress diagnostics only; they do not redefine the predeclared opening rule.

### S1.3 Successor sealing and adequacy

The successor audit sealed 2,255 of 2,256 fit cells and retained the unresolved cell rather than adding a rescue path. The held-out outcomes were not used to select procedures, accessible areas, taxa or post hoc exclusions. Detailed cell-level receipts remain the authoritative source for taxon × area × procedure outcomes.

## Supplement S2. Executable relation-endpoint contract and fingerprint audit

### S2.1 Contract schema

The reference contract stores:

1. `contract_id`;
2. relation level/class;
3. explicit biological relation;
4. biological key space;
5. left-role adapter;
6. right-role adapter;
7. left-role adequacy gate;
8. right-role adequacy gate;
9. opening-rule class;
10. `opening_rule_reference`.

The last field identifies the immutable/versioned empirical envelope, calibration artifact or negative-state qualification protocol that instantiates the opening rule. Without it, a contract could preserve the same verbal rule while silently switching the calibration object.

Canonical implementation:

- `scripts/relation_endpoint_contract.py`;
- `scripts/freeze_relation_endpoint_contract.py`;
- `config/relation_endpoint_contract_example.json`;
- `results/relation_endpoint_contract_example_freeze_v0_1.json`;
- `docs/relation_endpoint_quickstart.md`.

### S2.2 Serialization and fingerprint semantics

A valid contract is serialized to deterministic canonical JSON and fingerprinted with SHA-256. Missing or unknown fields are rejected. Semantic changes alter the fingerprint; JSON key order does not. The committed synthetic example has a stable fingerprint used by the test suite for exact round-trip reproduction.

Fingerprinting is an **audit mechanism**, not proof of outcome blindness. Its role is to make the endpoint object frozen before opening comparable with the object later used for evaluation.

### S2.3 Endpoint states

A calibrated soft relation returns `consistent`, `attention_required` or `unresolved`. `attention_required` denotes discordance under the frozen relation rule and is not automatically biological falsification.

A directional hard relation `E(k) -> F(k)` returns `hard_violation_authorized`, `no_observed_violation`, `noninformative_for_implication` or `unresolved`. A hard violation requires an adequately positive `E(k)` and an adequately negative `F(k)` at the same key, with the observation process qualified and the focal key valid for negative inference. Inadequate answers, missing comparison values and unqualified negatives cannot become hard biological contradictions.

## Supplement S3. Invalid-state ablation and operating characteristics

### S3.1 General state-dependent decomposition

For a qualified hard endpoint, let

`a1 = P(valid key | F=true)`,

`a0 = P(valid key | F=false)`,

`q` = key-level sensitivity on valid compatible keys, and

`sp` = specificity on valid true-violation keys.

The zero-collapsing ablation deliberately removes the rule that invalid/nonidentified observations remain unresolved. For biologically compatible keys,

`FPR_zero = 1 - a1 q`,

`FPR_gated = a1(1-q)`,

hence

`FPR_zero - FPR_gated = 1-a1`.

For true violations,

`TPR_zero = 1 - a0(1-sp)`,

`TPR_gated = a0 sp`,

hence

`TPR_zero - TPR_gated = 1-a0`.

The earlier equal increment `1-a` is only the controlled special case `a1=a0=a`.

Canonical generalized audit:

- `results/pre_field_state_dependent_invalidity_v0_2.json`;
- `scripts/relation_endpoint_contract.py` operating-characteristic helper.

### S3.2 Equal-validity benchmark

The original synthetic benchmark contains **8,748 scenarios**, of which 4,320 satisfy the frozen process-qualification rule and 4,428 fail it. In the passing equal-validity scenarios, both error increments equal `1-a` to floating-point error below `1.2 × 10^-16`. Under the frozen `q >= 0.80` qualification floor, gated key-level false-violation probability does not exceed 0.20 in that grid, whereas zero collapsing reaches 0.776 because invalid keys are relabelled as biological negatives. When calibration fails, the gated rule emits no hard-negative calls.

Canonical benchmark summary:

- `results/pre_field_identifiability_benchmark_summary_v0_1.json`.

The grid is a stress-test design space and is **not** an estimate of how common these observation regimes are in nature, nor an estimate of Cremastra or Belonocnema detection performance.

### S3.3 Process qualification versus endpoint reliability

For violation prevalence `pi`, the false-discovery fraction among called violations is

`FDF = (1-pi)(1-q) / [(1-pi)(1-q) + pi sp]`.

For example, `pi=0.10`, `q=0.80`, `sp=0.99` gives FDF ≈ 0.645. Observation-process qualification therefore determines whether a negative state is eligible to enter the endpoint; it does not by itself establish the reliability of a final biological conclusion. Replication and aggregation rules must be separately frozen before focal Level-C opening.

## Supplement S4. Prospective v8 → v8.1 implementation repair

The frozen operational contract required a one-sided 95% exact-or-more-conservative confidence rule for calibration, while audit found that the v8 evaluator implemented a Wilson lower bound. This mismatch was detected **before field calibration data were entered**.

v8 was retained as immutable provenance. v8.1 changed the confidence-bound implementation to one-sided exact Clopper–Pearson while leaving candidate identities, biological thresholds, minimum sample counts, missingness rules and the empirical ledger unchanged.

Canonical evidence:

- `results/product_b_level_c_operational_package_v8_1.json`;
- associated v8/v8.1 configuration, documentation and tests.

This repair is implementation/prospectivity evidence, not a biological result and not an empirical-ledger increment.

## Supplement S5. Calibration feasibility and minimum-count operating characteristics

The frozen minimum calibration design requires at least 30 known-positive and 60 known-negative units. Under the one-sided exact rule, the minimum positive sample requires at least **28/30** sensitivity successes and the minimum negative sample requires **60/60** specificity successes to clear the frozen lower-bound thresholds.

At true sensitivity 0.90, the nominal probability of passing the 28/30 positive criterion is approximately 0.411; at sensitivity 0.95 it is approximately 0.812. The probability of 60/60 successes is `0.99^60 ≈ 0.547` at true specificity 0.99 and approximately 0.942 at specificity 0.999.

These are prospective design diagnostics. The minimum counts are feasibility minima rather than power guarantees, and they do not authorize outcome-dependent sample-size extension. Any larger calibration design must be chosen before observing the focal calibration outcome.

## Supplement S6. Level-C candidate discovery, qualification and source audit

### S6.1 Evidence architecture

Directional dependency required three prospectively separated channels:

- `R`: external evidence defining the biological relation;
- `X`: an independent dependent-event stream;
- `Y`: an independent required-function/resource stream.

Independence was defined by observation generation rather than publication label. Candidate discovery was finite and response-blind. Gates required source materialization, a common biological key, direct role estimands, provenance separation and no post hoc redefinition.

Unavailable sources, failed downloads, missing records and uncalibrated zeros were never permitted to count as biological absence.

### S6.2 Retained architectures

Two biologically different systems survived the architecture gates:

- `CREMV3-007`: *Cremastra appendiculata* var. *variabilis*, combining external breeding-system evidence, same-inflorescence fruit outcome and pollinia-carrying camera observations;
- `BELV3-012`: *Belonocnema treatae* / live-oak budbreak, combining independent host-specificity evidence, natural adult emergence and live-oak budbreak observations.

Canonical qualification evidence:

- `results/product_b_level_c_source_qualification_v3.json`.

### S6.3 Common stopping point

Both systems stopped before focal endpoint opening because the negative functional state lacked candidate-specific calibration. Positive pollinia-carrying contacts are informative for Cremastra, but camera non-detection is not independently validated as absence of effective pollination. Belonocnema emergence and budbreak are separately observed, but an unrecorded usable-resource state cannot be distinguished from incomplete observation under the existing stream.

Candidate-specific calibration audit and raw/supplementary reconstruction did not identify an independent existing stream sufficient to estimate the required sensitivity/specificity without conditioning on focal outcomes.

Canonical evidence:

- `results/product_b_level_c_candidate_specific_calibration_audit_v5.json`;
- `results/product_b_level_c_raw_calibration_reconstruction_v6.json`.

These are **measurement-boundary results, not biological negatives**. The focal hard invariant, soft cross-check and process-knockout outcomes remain sealed.

## Supplement S7. Scope extensions and relation classes

### S7.1 Soft cross-role relations

Level B denotes different biological roles expected to show relation-specific soft coherence after adaptation to a common biological relation space. The soft endpoint primitive is implemented, but no fresh Level-B empirical reference endpoint is opened in Paper 1. Level-A source-discordance q95 must not be imported as a generic Level-B threshold.

### S7.2 Mutual dependency and life-stage coupling

Mutual dependency and life-stage coupling require biology-specific composition rather than a generic direct evaluator. A mutual relation can be represented by separately frozen directional primitives where justified. A life-stage relation must first define the transition event/key and then choose a supported primitive. These classes illustrate scope; they are not missing empirical results required for the present paper.

### S7.3 General biological interpretation

The same architecture applies when the required state is:

- effective pollination during a reproductive opportunity;
- compatible host resource during a developmental opportunity;
- accessible prey during a foraging opportunity;
- transition-compatible habitat during a life-stage transition;
- a sensor-detected interaction only when the observation process is calibrated strongly enough that non-observation can support the negative state demanded by the endpoint.

The recurring rule is: construct role-appropriate answers independently, map them to the biological event where the relation applies, preserve unresolved states, and verify that the state needed to contradict the relation is identifiable before allowing hard inference.

## Supplementary claim boundary

This Supplement cannot be used to claim any of the following:

- Level C confirmed dependency;
- Level C falsified dependency;
- no record = no function;
- unavailable source = biological absence;
- five unresolved Level-A cells = failures;
- 283 Level-A diagnostics = independent replicates;
- q95 = nominal 95% predictive coverage or a universal cross-role threshold;
- process necessity/causality or an opened process knockout;
- universal `1-a` inflation under state-dependent validity;
- fingerprinting = proof of outcome blindness;
- calibration qualification = proof that an individual called violation is true.

Any future focal Level-C empirical result requires a separately authorized opening event and a new claim-ledger version rather than insertion into this Supplement.
