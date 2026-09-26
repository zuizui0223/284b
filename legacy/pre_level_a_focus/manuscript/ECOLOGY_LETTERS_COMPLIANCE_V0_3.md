# Ecology Letters Method compliance checklist v0.3

Checked against current Ecology Letters/Wiley author guidance and the Method editorial on 2026-09-11.

## Proposal stage — mandatory before a full Method submission

- Article type: **Method**.
- A full Method manuscript is considered only after direct invitation or approval of an unsolicited proposal.
- Unsolicited proposal maximum: **300 words**.
- Proposal should describe the nature and novelty of the work, its contribution to the discipline and the qualifications of the author(s).
- Method editorial guidance explicitly allows quantitative information and/or a conceptual figure in the proposal.
- Proposal must be sent to both `ecolets@cefe.cnrs.fr` and `ecolets2@cefe.cnrs.fr`.

Canonical proposal package:

- pitch: `manuscript/ECOLOGY_LETTERS_300WORD_PITCH_V0_6.md`;
- rationale: `manuscript/ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_6.md`;
- email wrapper: `manuscript/ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_3.md`;
- attachment: `manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg`.

Do **not** send until the final author list, affiliation(s), corresponding-author email and author-qualification sentence(s) are frozen.

## Full Method manuscript — only if invited

Current journal limits and expectations:

- main text maximum: **5,000 words**;
- maximum: **6** figures/tables/text boxes total;
- abstract maximum: **150 words**;
- the method itself must be the focus;
- the technique should be sufficiently specified to transfer to new settings, systems and research questions;
- quantitative methods require high-quality code;
- Method papers should demonstrate use in a case study;
- evaluation emphasizes novelty and importance of the method.

Canonical full-submission package:

- manuscript: `manuscript/PREFIELD_FLAGSHIP_V0_7.md`;
- title page: `manuscript/ECOLOGY_LETTERS_TITLE_PAGE_V0_2.md`;
- cover letter: `manuscript/ECOLOGY_LETTERS_FULL_COVER_LETTER_V0_1.md`;
- claim boundary: `manuscript/CLAIM_EVIDENCE_LEDGER_V0_4.md`;
- display routing: `manuscript/FULL_SUBMISSION_DISPLAY_MANIFEST_V0_1.md`;
- captions: `manuscript/FULL_SUBMISSION_FIGURE_CAPTIONS_V0_1.md`;
- executable method: `scripts/relation_endpoint_contract.py`;
- deterministic Figure 2/5 builder: `scripts/build_prefield_main_figures_v0_2.py`.

Repository CI enforces the 150-word abstract ceiling, 5,000-word main-text ceiling, <=300-word proposal and six-display-item boundary.

## Title-page / metadata fields to finalize from human-confirmed information

Before a full submission, freeze and verify:

- full final author list and order;
- current affiliations;
- corresponding-author contact details;
- running title (<45 characters under current guidance);
- <=10 keywords;
- exact abstract and main-text word counts at export;
- exact reference count after final formatting;
- figure/table/text-box counts;
- author contribution/authorship statement where required;
- funding and acknowledgements;
- competing interests where required;
- ORCID identifiers where supplied by authors.

Do not infer any of these from Git commit authorship or old institutional context.

## Data and code accessibility

Before full submission/publication packaging:

- create an immutable archival release of the canonical code, receipts, synthetic audits and display-generation materials;
- insert public archive DOI(s) in the Data and Code Availability statement and title-page metadata where required;
- ensure the archive reproduces the pre-field claim boundary rather than silently incorporating future focal Level-C results.

## Graphical abstract

Current journal guidance requires a graphical abstract at revision stage. Prepare it only from the reviewer-hardened relation-endpoint architecture; do not use unopened Level-C focal results. Keep it visually simple and minimize text. This is not a blocker for sending the unsolicited Method proposal.

## Scientific claims that must remain fixed during submission preparation

1. **Level A independent unit:** 12 fresh held-out taxa. The 283 evaluable procedure-by-area cells are repeated diagnostics, not independent n.
2. **Level-A q95:** a prospectively frozen empirical source-discordance envelope, not a nominal 95% predictive interval or alpha=0.05 test.
3. **Hard-endpoint general result:** with `a1=P(valid|F=true)` and `a0=P(valid|F=false)`, false-violation inflation is `1-a1` and apparent sensitivity gain is `1-a0`; `1-a` is only the equal-validity corollary.
4. **Zero collapsing:** an ablation/forbidden operation that deletes `unresolved`, not a competitor to occupancy, LIES or other detection-aware models.
5. **Level C:** pre-outcome endpoint-openability evidence only. No focal dependency outcome is opened.
6. **Empirical ledger:** remains 1.

## Antecedent boundary

The manuscript must continue to acknowledge as established antecedents/components:

- occupancy and imperfect-detection modelling;
- interaction/co-occurrence models;
- Chadwick et al. (2024) LIES: Latency, Identifiability, Effort and Scale;
- Getz et al. (2018) model adequacy/data determinacy;
- independent external validation;
- preregistration and Registered Reports;
- the generic principle that non-detection is not automatically biological absence.

The retained novelty claim is **relation choice and endpoint authorization across independently generated ecological answers**, operationalized as a five-part executable contract and state machine.

## Internal go/no-go before sending the proposal

GO on scientific package only when all are true:

- pitch remains <=300 words;
- proposal figure v0.5 is the attached quantitative/conceptual figure;
- author qualifications correspond exactly to the frozen author list;
- no focal Level-C value is inserted;
- no unavailable/missing/non-detection state is interpreted as a biological negative;
- the latest canonical proposal files from `ECOLOGY_LETTERS_SUBMISSION_MANIFEST_V0_3.md` are used.

Human blockers remain author list/order, current affiliation(s), corresponding-author email and coauthor qualification wording.

## Internal go/no-go before an invited full submission

In addition to the proposal-stage checks:

- manuscript v0.7 and claim ledger v0.4 are canonical;
- all six display items and captions match the full-display manifest;
- cover letter has verified author-approval / no-simultaneous-consideration statements before those claims are made;
- related work by final authors is checked and distinguished in the cover letter;
- immutable archive/release and DOI(s) are inserted;
- final reference and metadata counts are recomputed from the export-ready manuscript.
