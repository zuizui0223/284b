# Paper 1 Methods candidate v0.10 — main-text compressed

**Status:** noncanonical editorial compression. Scientific thresholds, candidate identities, endpoint states and empirical ledger are unchanged. Audit/provenance detail is routed to `PAPER1_SUPPLEMENT_V0_1.md`.

## Methods

### Relation-endpoint contract

We treat the relation joining independently generated ecological answers as an explicit inferential object rather than an implicit consequence of upstream model choice. Before focal comparison values are viewed, a relation-endpoint contract freezes five scientific components: (1) the biological relation, (2) the event or key space at which it applies, (3) role-specific adapters mapping each answer into that space, (4) adequacy gates determining whether each answer exists for a key, and (5) an opening rule defining admissible endpoint states. The implementation also stores an `opening_rule_reference` identifying the frozen empirical envelope, calibration artifact or negative-state qualification protocol that instantiates that rule.

The reference engine (`scripts/relation_endpoint_contract.py`) validates the contract, serializes it to deterministic canonical JSON and returns a SHA-256 fingerprint. Missing or unknown fields are rejected. Fingerprinting makes endpoint drift inspectable; it is an audit device, not proof of outcome blindness. Calibrated soft keys return `consistent`, `attention_required` or `unresolved`. Directional hard keys return `hard_violation_authorized`, `no_observed_violation`, `noninformative_for_implication` or `unresolved`. Implementation and round-trip fingerprint audits are in Supplement S2.

### Why answer accuracy does not identify the relation

For directional dependency `E -> F`, let `p_E=P(E=1)` and `p_F=P(F=1)` be exact role-specific marginals and `v=P(E=1,F=0)` the hard-violation probability. Classical Fréchet–Hoeffding coupling bounds imply

`max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`.

At `p_E=p_F=0.5`, the same exact marginals admit both `v=0` and `v=0.5`. We use this established result only as a separation argument: marginal accuracy does not determine the downstream hard relation. Joint statistical models may estimate coupling; the biological relation, common key and contradiction rule must still be declared separately.

### Controlled same-target empirical anchor

We tested whether a fully prespecified soft relation could close on fresh held-out taxa using independent preserved-specimen and human-observation reconstructions. Within each procedure-by-accessible-area cell, target identity, estimand, predictor universe, estimator/procedure identity, accessible-area semantics, comparison frame, adequacy logic and the successor-derived reference rule were held fixed before held-out opening.

The independent biological units were 12 held-out taxa. Each taxon contributed a prespecified 3-area × 8-procedure matrix, yielding 288 repeated diagnostics. A diagnostic was evaluable only when both source-specific answers passed predeclared adequacy. Discordance was `1 - Schoener D` and was compared with the corresponding frozen nearest-rank q95 **empirical source-discordance envelope**. The 24-cell calibration, successor counts, comparison-frame construction and cell-level diagnostic receipts are reported in Supplement S1. q95 is not interpreted as nominal 95% predictive coverage or a hypothesis-test threshold.

### Directional dependency and negative-state identifiability

For a hard relation we write `E(k) -> F(k)`, where `E(k)` is the dependent event and `F(k)` the required biological function at opportunity key `k`. A hard contradiction requires an adequately positive event and an adequately negative function at the same key. When several providers can satisfy the requirement, `F` is defined at the aggregate function level rather than as occurrence of one named provider.

Detected function, calibrated functional absence, unresolved non-detection and observation failure/missingness are distinct states. Only calibrated functional absence can supply `F(k)=false`. The frozen Level-C process-qualification floor requires key-level sensitivity `>=0.80`, hard false-negative rate `<=0.20` and specificity `>=0.95`, with explicit quality-control and missingness rules. These thresholds authorize whether a negative state may enter the endpoint; they are not universal final standards for a biological conclusion. The prospective confidence-bound repair and calibration-feasibility details are in Supplements S4–S5.

### Exact unresolved-state ablation

To isolate the consequence of deleting `unresolved`, we compared the identifiability-gated hard rule with a zero-collapsing ablation that deliberately treats invalid observation or valid non-detection as `F=false` when `E=true`. This is an ablation of one guardrail, not a competitor to occupancy or other detection-aware models.

Let `q` be key-level sensitivity on valid compatible keys, `sp` specificity on valid true-violation keys, `a1=P(valid key | F=true)` and `a0=P(valid key | F=false)`. Then

`FPR_zero - FPR_gated = 1-a1`

and

`TPR_zero - TPR_gated = 1-a0`.

The common `1-a` identity is the equal-validity special case `a1=a0=a`. Full derivations, the 8,748-scenario stress grid and the base-rate/false-discovery analysis are in Supplement S3.

### Prospective cross-role openability audit

We tested whether real cross-role systems could satisfy the information requirements of a directional endpoint without opening focal biological outcomes. Each candidate required prospectively separated relation evidence (`R`), dependent-event data (`X`) and required-function/resource data (`Y`). Candidate discovery was finite and response-blind; gates required a common biological key, direct role estimands, provenance separation and no post hoc redefinition. Unavailable sources, failed downloads, missing records and uncalibrated zeros were never allowed to count as biological absence.

Two systems survived the architecture gates: `CREMV3-007` (*Cremastra appendiculata* var. *variabilis*) and `BELV3-012` (*Belonocnema treatae* / live-oak budbreak). Paper 1 uses them only to test endpoint openability. Their focal hard invariant, soft cross-check and process-knockout outcomes remain sealed. The full candidate screen, source qualification and raw/supplementary-source audits are in Supplement S6.
