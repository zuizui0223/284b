# Ecology Letters submission manifest v0.3

This is the single routing surface for the reviewer-hardened Paper 1 submission package. Older proposal/manuscript/title-page/compliance/ledger versions remain provenance only and must not be used for submission unless explicitly re-promoted.

## Stage 1 — unsolicited Method proposal

Use exactly:

- proposal text: `manuscript/ECOLOGY_LETTERS_300WORD_PITCH_V0_6.md`;
- proposal rationale/audit package: `manuscript/ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_6.md`;
- email wrapper: `manuscript/ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_3.md`;
- attachment: `manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg`;
- compliance gate: `manuscript/ECOLOGY_LETTERS_COMPLIANCE_V0_3.md`.

Recipients under current journal guidance:

- `ecolets@cefe.cnrs.fr`;
- `ecolets2@cefe.cnrs.fr`.

### Stage-1 send blockers

Do not send until all four are human-confirmed:

1. final author list and order;
2. current affiliation(s);
3. corresponding-author email;
4. qualification wording for the frozen author list.

No new Level-C field data are required for Stage 1.

## Stage 2 — invited full Method manuscript

Use only after an invitation/approved proposal:

- manuscript: `manuscript/PREFIELD_FLAGSHIP_V0_7.md`;
- title page: `manuscript/ECOLOGY_LETTERS_TITLE_PAGE_V0_2.md`;
- full cover letter: `manuscript/ECOLOGY_LETTERS_FULL_COVER_LETTER_V0_1.md`;
- claim/evidence ledger: `manuscript/CLAIM_EVIDENCE_LEDGER_V0_4.md`;
- six-display routing: `manuscript/FULL_SUBMISSION_DISPLAY_MANIFEST_V0_1.md`;
- captions: `manuscript/FULL_SUBMISSION_FIGURE_CAPTIONS_V0_1.md`;
- full compliance gate: `manuscript/ECOLOGY_LETTERS_COMPLIANCE_V0_3.md`;
- method implementation: `scripts/relation_endpoint_contract.py`;
- deterministic figure generation: `scripts/build_prefield_main_figures_v0_2.py`.

Canonical display items:

1. `manuscript/figures/figure1_relation_endpoint_contract_v0_1.svg`;
2. `manuscript/figures/figure2_level_a_empirical_anchor_v0_2.svg`;
3. `manuscript/figures/figure3_event_function_dependency_v0_1.svg`;
4. `manuscript/figures/figure4_parallel_openability_audits_v0_1.svg`;
5. `manuscript/figures/figure5_invalid_state_decomposition_v0_3.svg`;
6. `manuscript/TABLE1_CLAIM_EVIDENCE_MATRIX_V0_1.md`.

### Stage-2 additional blockers

Before full submission, additionally verify:

- proposal invitation details;
- all-author approval and no-simultaneous-consideration statements before including them in the cover letter;
- author contributions, funding/acknowledgements, competing interests and ORCIDs as applicable;
- current author affiliations/contact details;
- recent related work by the final author team and explicit differentiation in the cover letter;
- exact final abstract/main-text/reference/display counts;
- immutable public archive/release and DOI(s).

## Scientific claim boundary — immutable for this pre-field paper

### Level A

- independent fresh held-out biological units: **12 taxa**;
- prespecified repeated diagnostics: 288;
- evaluable diagnostics: 283;
- unresolved diagnostics: 5;
- no held-out taxon contains an empirical-envelope exceedance among evaluable cells;
- 283 is not an independent sample size;
- nearest-rank q95 is a prospectively frozen empirical source-discordance envelope, not nominal predictive coverage.

### Level B

- fresh empirical relation endpoint unopened.

### Level C

- Cremastra and Belonocnema/live-oak systems are architecture-qualified pre-outcome openability demonstrations;
- both remain blocked at candidate-specific negative-state calibration;
- focal cross-role values, hard invariant, soft cross-check and process knockout remain sealed;
- unavailable / missing / failed / uncalibrated non-detection states are not biological negatives.

### Quantitative method result

- `a1=P(valid key | F=true)`;
- `a0=P(valid key | F=false)`;
- `FPR_zero - FPR_gated = 1-a1`;
- `TPR_zero - TPR_gated = 1-a0`;
- `1-a` is only the equal-validity special case `a1=a0=a`;
- zero collapsing is an ablation of the unresolved-state guard, not a competing detection-aware model.

### Ledger

Empirical ledger remains **1**.

## Files explicitly superseded for submission routing

Do not use these as canonical submission files:

- `PREFIELD_FLAGSHIP_V0_6.md` or earlier;
- `ECOLOGY_LETTERS_TITLE_PAGE_V0_1.md`;
- `ECOLOGY_LETTERS_COMPLIANCE_V0_2.md` or earlier;
- `CLAIM_EVIDENCE_LEDGER_V0_2.md` or earlier;
- proposal pitch versions before v0.6;
- proposal figures before v0.5.

They remain repository provenance only.
