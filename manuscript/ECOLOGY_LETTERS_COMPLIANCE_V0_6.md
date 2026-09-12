# Ecology Letters Method compliance checklist v0.6

Checked against current Ecology Letters/Wiley author guidance and the Method editorial; Stage-1 routing updated after the relation-layer, title and executable-contract fingerprint audits.

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

- pitch: `manuscript/ECOLOGY_LETTERS_300WORD_PITCH_V0_8.md` — 295 words;
- rationale: `manuscript/ECOLOGY_LETTERS_METHOD_PROPOSAL_V0_9.md`;
- email wrapper: `manuscript/ECOLOGY_LETTERS_PROPOSAL_EMAIL_V0_6.md`;
- attachment: `manuscript/figures/ecology_letters_method_proposal_figure_v0_5.svg`;
- title audit: `manuscript/TITLE_AUDIT_V0_1.md`;
- relation-layer separation audit: `manuscript/RELATION_LAYER_SEPARATION_V0_1.md`;
- antecedent audit: `manuscript/CLOSER_ANTECEDENT_AUDIT_V0_4.md`;
- executable contract: `scripts/relation_endpoint_contract.py`;
- freeze utility: `scripts/freeze_relation_endpoint_contract.py`;
- quickstart: `scripts/relation_endpoint_quickstart.py` and `docs/relation_endpoint_quickstart.md`.

Do **not** send until final author list/order, current affiliation(s), corresponding-author email and author-qualification wording are human-confirmed.

## Executable prospectivity guard

The paper's five conceptual contract elements must be represented by a validated executable contract before focal opening. The implementation must preserve:

1. declared biological relation;
2. common biological key/event space;
3. role-specific adapters;
4. role-specific adequacy gates;
5. opening-rule class **and** `opening_rule_reference` identifying the frozen calibration artifact or negative-state qualification protocol that instantiates the rule.

A validated contract can be canonically serialized and SHA-256 fingerprinted. The fingerprint must change if relation, key space, adapter, adequacy rule, opening-rule class or opening-rule reference changes. JSON key ordering must not change the fingerprint.

Hashing is an audit mechanism, not proof of outcome blindness. The defensible claim is that it provides a versionable/timestampable pre-outcome contract identity that can be compared with the object used at opening.

## Reference implementation scope

The reference engine directly evaluates:

- Level A same-target calibrated soft coherence;
- Level B relation-specific soft cross-role coherence;
- Level C directional hard dependency.

Level D mutual dependency and Level E stage coupling are composition-only. They must not be presented as generic direct evaluators; they require separately frozen supported primitive contracts with relation-specific biological semantics.

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

Canonical pre-invitation full-manuscript scientific state remains:

- manuscript: `manuscript/PREFIELD_FLAGSHIP_V0_7.md`;
- invited candidate builder: `scripts/build_prefield_flagship_v0_8_candidate.py`;
- invited handoff: `manuscript/INVITED_MANUSCRIPT_V0_8_HANDOFF.md`;
- title page: `manuscript/ECOLOGY_LETTERS_TITLE_PAGE_V0_2.md`;
- cover letter: `manuscript/ECOLOGY_LETTERS_FULL_COVER_LETTER_V0_1.md`;
- claim boundary: `manuscript/CLAIM_EVIDENCE_LEDGER_V0_4.md`;
- displays: `manuscript/FULL_SUBMISSION_DISPLAY_MANIFEST_V0_1.md`;
- captions: `manuscript/FULL_SUBMISSION_FIGURE_CAPTIONS_V0_1.md`.

Do not silently edit v0.7. If invited, build and audit the v0.8 candidate, then promote it only after title/reference/display/metadata synchronization and the frozen claim boundary are verified.

## Novelty boundary

The paper must explicitly avoid claiming novelty for:

- occupancy / imperfect-detection modelling;
- JSDMs or marginal-versus-joint prediction;
- data fusion;
- co-occurrence / interaction inference;
- LIES / observation-process identifiability;
- model adequacy;
- external validation / held-out testing;
- preregistration / outcome-blind design;
- non-detection ≠ absence;
- Fréchet-Hoeffding bounds / classical coupling theory;
- hashing or content-addressed versioning as a generic computational invention.

The retained methodological object is:

> **prospective authorization of a declared biological relation endpoint across independently generated ecological answers, operationalized as a frozen, fingerprintable contract linking relation semantics, common key, adapters, adequacy and the opening/calibration rule.**

## Formal separation guard

For hard `E->F`, define `v=P(E=1,F=0)`. Given exact marginals only,

`max(0,p_E-p_F) <= v <= min(p_E,1-p_F)`.

At `p_E=p_F=0.5`, both `v=0` and `v=0.5` are compatible with the same perfect marginal answers. This is a classical coupling separation argument, not a new probability theorem.

A JSDM may estimate the missing joint coupling. The relation-endpoint layer remains responsible for the distinct biological question: which joint relation is licensed and what evidence can open or contradict it.

## Existing scientific guards remain unchanged

1. **Level A independent unit:** 12 fresh held-out taxa; 283 evaluable cells are repeated diagnostics, not independent n.
2. **Level-A q95:** prospectively frozen empirical source-discordance envelope, not nominal predictive coverage or alpha=0.05 testing.
3. **Hard-endpoint invalid-state result:** `FPR_zero-FPR_gated=1-a1`; `TPR_zero-TPR_gated=1-a0`; `1-a` only under equal validity.
4. **Zero collapsing:** ablation of the unresolved-state guard, not a competitor to occupancy/JSDM/LIES.
5. **Level C:** pre-outcome endpoint-openability evidence only; no focal biological dependency outcome is opened.
6. **Empirical ledger:** remains **1**.
7. Relation-layer separation, title promotion, quickstart, contract fingerprinting and schema hardening are nonempirical; ledger increment 0.

## Human metadata / archive blockers

Stage 1 still requires human-confirmed author list/order, affiliation(s), corresponding email and author qualification wording.

Before an invited full submission, also verify all-author approval, no-simultaneous-consideration statement, contributions, funding/acknowledgements, conflicts, ORCIDs, related work by final authors, exact final counts and an immutable public archive/DOI.
