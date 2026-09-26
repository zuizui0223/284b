# Reviewer-2 adversarial audit v0.1

Purpose: attack the pre-field Ecology Letters Method paper at the points most likely to cause desk rejection or major revision, using the repository's own frozen artifacts rather than rhetorical defence.

## 1. “283/283 is pseudoreplication dressed up as sample size”

**Attack.** The held-out design has 12 taxa, not 283 independent biological replicates. The 283 opened values are repeated procedure × accessible-area diagnostics within taxa. Reporting 283/283 without qualification can be read as inflating replication.

**Repository check.** The final artifact contains 12 prospectively held-out taxa and 288 prespecified cells. Five cells are unresolved, leaving 283 evaluable diagnostics. Each taxon contributes 22–24 evaluable cells. No held-out taxon contains a ceiling exceedance, so the taxon-level statement is 12/12 taxa with no exceedance among their evaluable cells.

**Required manuscript fix.** Explicitly state that the independent held-out biological units are 12 taxa; 283 is the count of evaluable cell diagnostics, not an inferential n. Do not compute a binomial probability from 283 successes. Keep the cell-level result because the relation was prospectively defined at the procedure × M cell, but separate that from replication.

## 2. “q95 sounds like a 95% prediction interval, but it is not one”

**Attack.** The nearest-rank q95 reference is an empirical quantile estimated from 34–47 successor taxa per cell. It is not automatically a finite-sample 95% predictive interval and is not an alpha=0.05 test, especially with 24 correlated reference cells.

**Repository check.** All 24 ceilings were frozen before held-out discordance was opened, with 34–47 distinct adequate successor taxa per cell. The rule was nearest-rank q95.

**Required manuscript fix.** Call it a prospectively frozen empirical source-discordance envelope. Explicitly deny a nominal 95% predictive-coverage or hypothesis-testing interpretation. The Level-A claim is conditional cross-source reproducibility relative to that predeclared envelope.

## 3. “The 1-a theorem is algebraically obvious and rests on hidden symmetry”

**Attack.** Under the original benchmark, one valid-key fraction `a` is applied to both compatible keys (`F=true`) and true violations (`F=false`). If validity depends on latent state, the equal increments need not be equal.

**Repair.** Generalize to

- `a1 = P(valid | F=true)`;
- `a0 = P(valid | F=false)`.

Then

`FPR_zero - FPR_gated = 1-a1`

and

`TPR_zero - TPR_gated = 1-a0`.

The published `1-a` identity becomes the exact equal-validity corollary `a1=a0=a`, not an unstated universal law. A state-dependent synthetic audit is added without reading focal Level-C data.

**Interpretive consequence.** The mathematical contribution should be sold as an endpoint-level error decomposition and an executable authorization rule, not as a difficult theorem.

## 4. “Zero-collapsing is a straw-man competitor”

**Attack.** Contemporary occupancy and detection-aware methods do not generally advocate recoding failed observations as biological absence. Beating such a comparator does not establish superiority over modern observation models.

**Required manuscript fix.** Define zero-collapsing as an **ablation / forbidden operation**, not a competing statistical method. Its purpose is to quantify the exact cost of violating the endpoint contract's unresolved-state rule. Occupancy, LIES and other detection-aware approaches are admissible upstream components when their sampling design identifies the needed state.

## 5. “This is a philosophy, not a Method”

**Attack.** A five-part checklist can look like methodological advice rather than an executable technique.

**Repair.** Add an estimator-agnostic reference implementation, `scripts/relation_endpoint_contract.py`, with a frozen contract object and explicit endpoint state machine. It evaluates:

- calibrated soft relations, returning `consistent`, `attention_required` or `unresolved`;
- hard directional implications, returning `hard_violation_authorized`, `no_observed_violation`, `noninformative_for_implication` or `unresolved`.

The engine never turns an inadequate answer or unqualified negative into a biological contradiction. Tests enforce this behaviour.

## 6. “Level C is unfinished empirical work”

**Attack.** The real-system section can read as a study that failed to obtain its main result.

**Required manuscript fix.** State explicitly that no Level-C biological outcome is part of Paper 1. The two retained systems are **pre-outcome stress tests of endpoint openability**. Their scientific role is to demonstrate that the method can stop at a measurement boundary after relation, key alignment and evidence independence have succeeded.

Move development-history detail out of the main narrative where possible. Candidate-screen counts are provenance, not the headline result.

## 7. “The paper confuses endpoint qualification with evidence for a biological violation”

**Attack.** Sensitivity/specificity thresholds only qualify the observation process. They do not ensure a low false-discovery fraction for a rare biological violation.

**Existing strength.** The manuscript already derives the base-rate dependence and shows `FDF ≈ 0.645` at `pi=0.10`, `q=0.80`, `sp=0.99`.

**Required emphasis.** Keep three decisions separate: observation-process qualification, focal endpoint opening and final evidentiary interpretation/replication. Do not call calibration “validation of the dependency.”

## 8. “The calibration minima are practically underpowered”

**Attack.** 30 positive and 60 negative calibration units are only feasibility minima. Exact lower-bound requirements make pass probability low near the threshold.

**Existing strength.** The outcome-blind v8.1 audit already shows this and forbids post-hoc sample extension.

**Required emphasis.** Present the operating-characteristic audit as a reason sample size must be frozen prospectively, not as permission to alter the historical v8.1 minimum after field outcomes.

## 9. Strongest defensible paper after adversarial audit

The paper should not claim that it invented imperfect-detection modelling, observation-process identifiability, external validation, preregistration, or the general maxim that non-detection is not absence.

Its strongest defensible contribution is:

> An executable relation-endpoint contract for composing independently generated ecological answers into prospectively declared soft or hard biological relations, with explicit answer-existence states, relation-specific calibration and authorization of the falsifying state.

The empirical and analytic supports are distinct:

1. **Level A:** 12 fresh held-out taxa, represented by 288 prespecified cell diagnostics, show no exceedance among 283 evaluable cells under prospectively frozen empirical source-discordance envelopes; five cells remain unresolved.
2. **Hard-endpoint ablation:** invalid-state coercion produces exactly class-specific error increments `1-a1` and `1-a0`; the original `1-a` result is the equal-validity corollary.
3. **Real-system openability audit:** two biologically different Level-C architectures reach the same measurement boundary without opening focal biological outcomes.

## 10. Recommendation

**Proceed with Ecology Letters Method proposal**, but only after manuscript v0.7 incorporates the independence/envelope caveats, generalized validity result, ablation wording and executable engine. These changes narrow the claims but materially reduce desk-review and Reviewer-2 risk.
