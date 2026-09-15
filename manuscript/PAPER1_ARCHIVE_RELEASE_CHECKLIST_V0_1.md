# Paper 1 archive/release checklist v0.1

**Purpose:** freeze the exact invited-full-submission package without opening new biological outcomes.

## Release contents

### Manuscript

- exact materialized `PREFIELD_FLAGSHIP_V0_10_CANDIDATE.md` plus SHA/identity receipts;
- `ECOLOGY_LETTERS_TITLE_PAGE_V0_3.md` after human fields are completed;
- `ECOLOGY_LETTERS_FULL_COVER_LETTER_V0_2.md` after invitation/human fields are completed;
- `PAPER1_SUPPLEMENT_V0_1.md` and `PAPER1_SUPPLEMENT_MANIFEST_V0_1.md`;
- `PAPER1_V0_10_SUBMISSION_SURFACE.md`;
- `CLAIM_EVIDENCE_LEDGER_V0_5.md`.

### Displays — production source of truth

- `figure1_relation_endpoint_contract_v1_0.svg`;
- `figure2_level_a_empirical_anchor_v1_0.svg`;
- `figure3_relation_layer_and_event_function_v1_0.svg`;
- `figure4_parallel_openability_audits_v1_0.svg`;
- `figure5_invalid_state_decomposition_v1_0.svg`;
- `TABLE1_CLAIM_EVIDENCE_MATRIX_V0_2.md`;
- `FULL_SUBMISSION_FIGURE_CAPTIONS_V0_3.md`;
- `FULL_SUBMISSION_DISPLAY_MANIFEST_V0_3.md`.

Retain the preceding v0.x SVGs as provenance, but do not mix them into the upload route. Figures 1–5 are exported from v1 SVGs at **173 mm final width**, with minimum final-size text **6.13 pt**. The vector-PDF export is regenerated with `scripts/export_paper1_submission_figures.py`; binary PDFs need not be treated as hand-edited scientific sources.

### Executable Method and production objects

- `scripts/relation_endpoint_contract.py`;
- `scripts/freeze_relation_endpoint_contract.py`;
- `scripts/relation_endpoint_quickstart.py`;
- example contract configuration and freeze receipt;
- `scripts/build_prefield_flagship_v0_10_candidate.py`;
- `scripts/build_paper1_submission_figures_v1.py`;
- `scripts/render_paper1_submission_figures.py`;
- `scripts/export_paper1_submission_figures.py`.

### Evidence and audit receipts

Include the canonical Level-A empirical receipt/structure audit, relation-layer separation receipt, generalized state-dependent invalidity receipt, v8.1 pre-data repair/operating-characteristic receipts and Level-C source-qualification/calibration/source-reconstruction receipts routed from the Supplement manifest.

## Identity rule

Before upload/submission:

1. confirm manuscript SHA-256 `66ad208f2a922800cb7f1d14f96b28295de13af4cdbdbec2f8b698b8fa320cc5`;
2. regenerate and verify the five v1 SVGs from their builder;
3. regenerate 173-mm vector PDFs from those exact SVGs and verify page size/font embedding;
4. record the release commit/tag;
5. record archive/DOI identifier;
6. record the exact six display-file hashes;
7. confirm that claim ledger, Supplement manifest and submission surface point to the same release state.

Do not generate a new manuscript or figure identity by manual editing after hashing. Substantive edits require rematerialization and a new identity.

## Exclusion rule

The archive for Paper 1 must not silently include later focal Level-C outcome files as evidence for the submitted manuscript. Later calibration or biological outcomes may be archived separately, but they do not retroactively change the Paper-1 empirical ledger unless a new manuscript version explicitly authorizes that scientific transition.

## Final blockers

Archive DOI/tag creation remains deferred until full-submission invitation/approval and final authorship/affiliations are confirmed. Scientific thresholds, candidate identities and focal Level-C seals are not production variables.
