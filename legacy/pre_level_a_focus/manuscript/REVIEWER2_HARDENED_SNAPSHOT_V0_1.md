# Reviewer-2-hardened pre-field submission snapshot v0.1

This record fixes the strongest pre-field Paper 1 state after adversarial review hardening and before any new Level-C field-calibration data are entered.

## Immutable reconstruction point

Reviewer-hardening PR: `#29`

Squash-merge commit:

`baea8ca17b91ee103a4bfa12ba856b3a20658582`

Use that commit to reconstruct the exact reviewer-hardened scientific state. This snapshot file itself is a later pointer and must not be confused with the reconstruction commit.

## Canonical paper package at the reconstruction point

- manuscript: `manuscript/PREFIELD_FLAGSHIP_V0_7.md`
- proposal pitch: `manuscript/ECOLOGY_LETTERS_300WORD_PITCH_V0_6.md`
- proposal rationale: `manuscript/ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_6.md`
- proposal email wrapper: `manuscript/ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_3.md`
- proposal figure: `manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg`
- submission routing: `manuscript/ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_2.md`
- adversarial audit: `manuscript/REVIEWER2_ADVERSARIAL_AUDIT_V0_1.md`
- executable endpoint engine: `scripts/relation_endpoint_contract.py`
- generalized invalid-state audit: `results/pre_field_state_dependent_invalidity_v0_2.json`
- Level-A structure audit: `results/reviewer2_level_a_structure_audit_v0_1.json`

## Reviewer-hardened claim boundary

### Level A

The independent held-out biological units are **12 taxa**. Their prespecified 3 accessible-area × 8 procedure matrix produced 288 cell diagnostics. Of these, 283 were evaluable and all fell within their corresponding prospectively frozen empirical source-discordance envelopes; five remained unresolved. The 283 cells are repeated diagnostics rather than 283 independent replicates, and no binomial success-probability claim is authorized from that cell count.

The nearest-rank q95 reference is an empirical envelope calibrated from 34–47 adequate successor taxa per reference cell. It is not claimed to be a nominal 95% predictive interval, an alpha=0.05 hypothesis test, or family-wise error control.

### Hard endpoint decomposition

For a directional hard endpoint `E(k) -> F(k)`, allow observation validity to depend on latent function state:

- `a1 = P(valid | F=true)`;
- `a0 = P(valid | F=false)`.

The exact invalid-state coercion ablation gives:

- `FPR_zero - FPR_gated = 1-a1`;
- `TPR_zero - TPR_gated = 1-a0`.

The previously reported equal `1-a` increments are the controlled special case `a1=a0=a`. Zero collapsing is an ablation of the unresolved-state guard, not a competitor to occupancy or other detection-aware methods.

### Level C

The two retained systems are used only as **pre-outcome endpoint-openability stress tests**. They reached a common measurement boundary because functional absence lacked candidate-specific calibration. No focal cross-role biological value, hard invariant, soft cross-check, process knockout, confirmation or falsification is part of Paper 1.

### Empirical ledger

The empirical ledger remains **1**, contributed solely by the completed Level-A held-out endpoint.

## Method status

Paper 1 now contains an executable estimator-agnostic five-part relation-endpoint contract rather than only a workflow description. Repository tests guard the soft and directional-hard state machines, unresolved-state semantics, manuscript word/display limits, claim boundaries, generalized invalid-state result, and Level-A replication interpretation.

## Remaining pre-send items

Only human submission metadata remain:

1. final author list;
2. current affiliation(s);
3. corresponding-author email;
4. directly relevant coauthor qualification sentence(s);
5. final proofreading/export of the proposal attachment.

No additional Level-C field result is required to send the Ecology Letters Method proposal.
