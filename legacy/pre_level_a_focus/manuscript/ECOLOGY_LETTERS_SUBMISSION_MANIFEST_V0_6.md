# Ecology Letters submission manifest v0.6

This is the single Stage-1 routing surface for the reviewer-hardened pre-field Paper 1 after relation-layer separation, title promotion and executable contract fingerprinting. Older proposal/manuscript/title-page/compliance/ledger versions remain provenance only unless explicitly re-promoted.

## Stage 1 — unsolicited Method proposal

### Working title

**Relation endpoints for ecological inference: when independent answers can support joint biological claims**

Use exactly:

- proposal text: `manuscript/ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md`;
- proposal rationale: `manuscript/ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md`;
- email wrapper: `manuscript/ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md`;
- one attachment: `manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg`;
- compliance gate: `manuscript/ECOLOGY_LETTERS_COMPLIANCE_V0_6.md`;
- title audit: `manuscript/TITLE_AUDIT_V0_1.md`;
- novelty support: `manuscript/CLOSER_ANTECEDENT_AUDIT_V0_4.md`;
- formal separation support: `manuscript/RELATION_LAYER_SEPARATION_V0_1.md` and `results/relation_layer_separation_v0_1.json`;
- executable contract engine: `scripts/relation_endpoint_contract.py`;
- contract freeze CLI: `scripts/freeze_relation_endpoint_contract.py`;
- executable quickstart: `scripts/relation_endpoint_quickstart.py` and `docs/relation_endpoint_quickstart.md`;
- generic frozen-contract demonstration: `config/relation_endpoint_contract_example.json` and `results/relation_endpoint_contract_example_freeze_v0_1.json`.

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

## Executable contract identity

The proposal's prospective endpoint is now represented as a fingerprintable object. The complete validated contract includes:

- relation class and explicit biological relation;
- common biological key/event space;
- left and right adapters;
- left and right adequacy gates;
- opening-rule class;
- `opening_rule_reference` identifying the frozen calibration artifact or negative-state qualification protocol that instantiates the opening rule.

Canonical JSON and SHA-256 fingerprinting make any semantic change — including swapping only the opening-rule reference — produce a different contract identity. This is an audit mechanism, not proof of outcome blindness.

The committed generic example fingerprint after binding its opening-rule reference is:

`aeced85ab6708b6d3713e46babbc2c32654dae2d728d5127d1d5c9e05c949da6`

This example is synthetic and increments the empirical ledger by 0.

## Stage 2 — invited full Method manuscript

Use only after invitation/approved proposal.

The canonical **scientific** manuscript remains `manuscript/PREFIELD_FLAGSHIP_V0_7.md` until invitation. Its older heading is frozen provenance and must not be copied into an invited submission unchanged.

At invitation:

1. run `scripts/build_prefield_flagship_v0_8_candidate.py`;
2. follow `manuscript/INVITED_MANUSCRIPT_V0_8_HANDOFF.md`;
3. integrate the promoted title and concise relation-layer separation paragraph;
4. synchronize the title page, cover letter, claim/evidence ledger and any affected captions;
5. preserve the fingerprintable contract implementation and exact scientific boundary;
6. promote v0.8 only after the invitation-specific audit passes.

Frozen full-submission assets remain:

- manuscript source: `manuscript/PREFIELD_FLAGSHIP_V0_7.md`;
- title page: `manuscript/ECOLOGY_LETTERS_TITLE_PAGE_V0_2.md`;
- full cover letter: `manuscript/ECOLOGY_LETTERS_FULL_COVER_LETTER_V0_1.md`;
- claim/evidence ledger: `manuscript/CLAIM_EVIDENCE_LEDGER_V0_4.md`;
- six-display routing: `manuscript/FULL_SUBMISSION_DISPLAY_MANIFEST_V0_1.md`;
- captions: `manuscript/FULL_SUBMISSION_FIGURE_CAPTIONS_V0_1.md`;
- graphical abstract package: `manuscript/ECOLOGY_LETTERS_GRAPHICAL_ABSTRACT_V0_2.md`.

## Scientific claim boundary

### Level A

- independent fresh held-out units: **12 taxa**;
- 288 prespecified repeated diagnostics;
- 283 evaluable diagnostics, five unresolved;
- no held-out taxon contains an empirical-envelope exceedance among evaluable cells;
- 283 is not independent n;
- q95 is a prospectively frozen empirical source-discordance envelope, not nominal predictive coverage.

### Level B

Fresh empirical relation endpoint unopened.

### Level C

- two architecture-qualified systems are pre-outcome openability demonstrations only;
- both stop at candidate-specific negative-state calibration;
- focal cross-role values, hard invariant, soft cross-check and process knockout remain sealed;
- unavailable/missing/failed/uncalibrated non-detection is not biological absence.

### Quantitative invalid-state result

- `a1=P(valid key | F=true)`;
- `a0=P(valid key | F=false)`;
- `FPR_zero-FPR_gated=1-a1`;
- `TPR_zero-TPR_gated=1-a0`;
- `1-a` only under `a1=a0=a`;
- zero collapsing is an ablation of the unresolved-state guard.

### Relation-layer separation result

For hard `E->F`, exact marginal answers alone bound

`max(0,p_E-p_F) <= P(E=1,F=0) <= min(p_E,1-p_F)`.

At exact `p_E=p_F=0.5`, both zero violation and violation probability 0.5 are compatible with the same marginals. This is classical Fréchet-Hoeffding coupling logic used as a separation argument, not claimed as new probability theory.

A JSDM may estimate the missing joint coupling. The endpoint contract governs the distinct biological authorization problem: which joint relation is licensed and what state can open or contradict it.

### Ledger

Empirical ledger remains **1**. Relation-layer separation, title promotion, contract fingerprinting and schema hardening each increment the empirical ledger by 0.

## Superseded Stage-1 routing

Do not use as canonical for sending:

- proposal pitches before v0.8;
- proposal rationales before v0.9;
- proposal email wrappers before v0.6;
- compliance checklists before v0.6;
- submission manifests before v0.6;
- the previous working title `Prospective validation of ecological answers: from cross-source reproducibility to identifiable biological absence`.

Older files remain provenance only.
