# Ecology Letters Method compliance checklist v0.5

Checked against current Ecology Letters/Wiley author guidance and the Method editorial; Stage-1 routing updated after the relation-layer separation and title audits.

## Stage 1 — unsolicited Method proposal

Current journal requirements retained:

- Article type: **Method**.
- Full Method manuscripts require direct invitation or approval of an unsolicited proposal.
- Unsolicited proposal maximum: **300 words**.
- Proposal should describe the nature/novelty of the work, disciplinary contribution and author qualifications.
- Quantitative information and/or a conceptual figure can strengthen the proposal.
- Send the proposal to both `ecolets@cefe.cnrs.fr` and `ecolets2@cefe.cnrs.fr`.

Canonical Stage-1 working title:

**Relation endpoints for ecological inference: when independent answers can support joint biological claims**

Canonical Stage-1 package:

- pitch: `manuscript/ECOLOGY_LETTERS_300WORD_PITCH_V0_7.md`;
- rationale: `manuscript/ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_8.md`;
- email wrapper: `manuscript/ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_5.md`;
- attachment: `manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg`;
- title audit: `manuscript/TITLE_AUDIT_V0_1.md`;
- relation-layer separation audit: `manuscript/RELATION_LAYER_SEPARATION_V0_1.md`;
- antecedent audit: `manuscript/CLOSER_ANTECEDENT_AUDIT_V0_4.md`.

Do **not** send until final author list/order, current affiliation(s), corresponding-author email and author-qualification wording are human-confirmed.

## Stage 2 — invited full Method manuscript only

Current limits/expectations retained:

- main text <= **5,000 words**;
- <= **6** figures/tables/text boxes total;
- abstract <= **150 words**;
- method must be the focus;
- technique must transfer to new systems/settings/questions;
- quantitative methods require high-quality code;
- use must be demonstrated in a case study;
- review emphasizes novelty and importance of the method.

Canonical full-submission scientific package remains frozen at:

- manuscript: `manuscript/PREFIELD_FLAGSHIP_V0_7.md`;
- title page: `manuscript/ECOLOGY_LETTERS_TITLE_PAGE_V0_2.md`;
- cover letter: `manuscript/ECOLOGY_LETTERS_FULL_COVER_LETTER_V0_1.md`;
- claim boundary: `manuscript/CLAIM_EVIDENCE_LEDGER_V0_4.md`;
- displays: `manuscript/FULL_SUBMISSION_DISPLAY_MANIFEST_V0_1.md`;
- captions: `manuscript/FULL_SUBMISSION_FIGURE_CAPTIONS_V0_1.md`;
- executable method: `scripts/relation_endpoint_contract.py`;
- deterministic main-figure builder: `scripts/build_prefield_main_figures_v0_2.py`.

The Stage-1 title promotion is editorial only. If invited, the next full-manuscript version should synchronize the selected title and concise relation-layer separation paragraph in one versioned update; do not silently edit v0.7.

## Novelty boundary after JSDM / coupling audit

The paper must explicitly avoid claiming novelty for:

- occupancy / imperfect-detection modelling;
- JSDMs or the distinction between marginal and joint prediction;
- data fusion across observation sources;
- co-occurrence modelling or inference of interaction structure from co-occurrence;
- LIES / observation-process identifiability;
- ecological model adequacy;
- external validation / held-out testing;
- preregistration / outcome-blind design;
- the generic statement that non-detection is not absence;
- Fréchet-Hoeffding bounds or classical coupling theory.

The retained methodological object is:

> **prospective authorization of a declared biological relation endpoint across independently generated ecological answers, including relation/key specification, role-specific adaptation, answer adequacy and endpoint-opening logic.**

## Formal separation guard

For hard `E->F`, define `v=P(E=1,F=0)`. Given exact marginals only,

`max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`.

At `p_E=p_F=0.5`, both `v=0` and `v=0.5` are compatible with the same perfect marginal answers. This must be framed as a **classical coupling separation argument**, not a new probability theorem.

A JSDM may estimate the missing joint coupling. The relation-endpoint layer remains responsible for the distinct biological question: which joint relation is licensed and what evidence can open or contradict it.

## Existing scientific guards remain unchanged

1. **Level A independent unit:** 12 fresh held-out taxa; 283 evaluable cells are repeated diagnostics, not independent n.
2. **Level-A q95:** prospectively frozen empirical source-discordance envelope, not nominal predictive coverage or alpha=0.05 testing.
3. **Hard-endpoint invalid-state result:** `FPR_zero-FPR_gated=1-a1`; `TPR_zero-TPR_gated=1-a0`; `1-a` only under equal validity.
4. **Zero collapsing:** ablation of the unresolved-state guard, not a competitor to occupancy/JSDM/LIES.
5. **Level C:** pre-outcome endpoint-openability evidence only; no focal biological dependency outcome is opened.
6. **Empirical ledger:** remains **1**.
7. **Relation-layer separation audit:** nonempirical; empirical-ledger increment 0.
8. **Title promotion:** editorial only; scientific status and ledger unchanged.

## Graphical abstract / post-invite assets

Current graphical-abstract package remains `manuscript/ECOLOGY_LETTERS_GRAPHICAL_ABSTRACT_V0_2.md` with 50 mm × 60 mm vector source `manuscript/figures/ecology_letters_graphical_abstract_v0_2.svg`. It is a revision-stage asset, not a Stage-1 blocker.

The optional relation-layer separation inset is `manuscript/figures/relation_layer_separation_inset_v0_1.svg`; do not add it as a second unsolicited-proposal attachment unless requested by the editors.

## Human metadata / archive blockers

Stage 1 still requires human-confirmed author list/order, affiliation(s), corresponding email and author qualification wording.

Before an invited full submission, also verify all-author approval, no-simultaneous-consideration statement, contributions, funding/acknowledgements, conflicts, ORCIDs, related work by final authors, exact final counts and an immutable public archive/DOI.
