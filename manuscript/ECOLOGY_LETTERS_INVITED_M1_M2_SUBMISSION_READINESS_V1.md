# Ecology Letters invited M1+M2 submission readiness v1 — updated 2026-11-22

**Current manuscript decision: HOLD_FOR_SENSITIVITY_REVIEW.** All original and repaired-source computations have completed; this does not mean the source-completeness sensitivity fully passed. Final human scientific approval of the conditional claim is outstanding.

## Scientific package

- [x] Positive-core full manuscript exists.
- [x] Historical Level-A empirical endpoint is complete and preserved (283/288 evaluable, 0/12 taxa with q95 exceedance).
- [x] Original 59-taxon source geometry and all 2,832 source-specific repaired-GBIF model fits are signed and audited.
- [x] All 24 repaired-source reference q95 thresholds recalibrated under original >=30-taxon adequacy rule; 1,033/1,128 reference paired cells eligible.
- [x] One-shot repaired-source sensitivity terminal complete: 285/288 evaluable, 0/12 taxa with q95 exceedance, zero new independent empirical endpoints.
- [x] Source-repair strict original-evaluability check **failed**: only 282/283 original evaluable cells retained, one lost, three gained. Original terminal remains unmodified.
- [x] Four changed cells traced to the original four-fold CV mean-minus-SEM adequacy gate, with no cutoff/method/taxon selection changes.
- [x] Main paper, claim ledger, cover letter and Figure 2 plan updated to disclose the source-repair coverage limitation.
- [ ] Coauthors review and approve precise claim strength after the one-cell coverage loss; do **not** replace this item with more model fitting.
- [x] Independent replication unit is 12 taxa.
- [x] 283 evaluable cells are not presented as independent n.
- [x] Five unresolved cells remain unresolved.
- [x] Exact identities use class-specific `a1` and `a0`; `1-a` is only the equal-validity corollary.
- [x] FDF is separated from observation-validity qualification; the invited manuscript uses the class-specific `a1/a0` general formula for unconditional prevalence, and restricts the old validity-cancelling example to equal positive validity.
- [ ] Coauthors verify the corrected FDF definition, undefined zero-call edge case and Figure 4 against the mathematical audit before scientific signoff.
- [x] Level-C candidate systems are excluded from the focal manuscript.
- [x] Claim ledger exists.
- [x] Four-item figure plan exists.
- [x] Cover letter updated to M1+M2 positive core.
- [x] Title-page template updated to M1+M2 positive core.

## Submission-format checks

- [x] Abstract guarded at <=150 words by CI.
- [x] Planned display count <=6.
- [ ] Final main-text word count verified on the submission derivative.
- [ ] Final reference formatting verified.
- [x] Four primary figures rendered to PDF/SVG/PNG, integrity checked and visually inspected at original output size; overlaps fixed after first render ([figure QA receipt](ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_QA_20261122.md), CI run 45032223808).
- [x] Figure captions and accessibility/alt text drafted for all four displays (`manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_CAPTIONS_V1.md`).
- [x] Standalone 173-mm vector PDF print-size preflight and minimal lettering verified (7.06/6.00/6.10/6.12 pt for Figures 1–4); overlap-free proof inspected. This is not the compiled journal proof.
- [ ] Final figures placed and verified inside the compiled submission manuscript / portal-generated reviewer PDF.
- [x] Signed source-completeness sensitivity Supporting Information draft prepared: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SOURCE_COMPLETENESS_SI_V1.md` (59 fitted taxa, 24 thresholds, 288 keyed heldout cells, four adequacy flips, 282/283 original-cell retention).
- [x] Integrate the complete M1+M2 Supporting Information into one review draft, including M1 theorem/FDF, 8,748-case analytic benchmark, 12-species source-version Table S1, 24 restored-q95 Table S2 and GBIF coverage-limited terminal: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COMPLETE_SI_V1.md`.
- [x] Run automated section/table/provenance guards for this integrated SI (`tests/test_el_invited_complete_si_20261123.py`).
- [ ] Final journal-specific typography, numbering and upload/portal formatting of the integrated SI confirmed by authors.
- [ ] Anonymous/review manuscript generated if required by the current portal.

## Reproducibility

- [x] Level-A machine-readable endpoint receipt retained.
- [x] Level-A structural audit retained.
- [x] Exact invalid-state scripts/results retained.
- [x] CI guard blocks Level-C leakage and pseudoreplication language.
- [x] SHA-verified provenance for the historical empirical endpoint and the separate retrospective source-repair sensitivity retained.
- [x] Automated manuscript+supplement source-version labels, 12 taxon ratios, restored 24 reference q95 values, 288-key eligibility, M1 identities and 0/12 conditional wording crosschecked against signed terminal receipts.
- [ ] Human scientific verification of final manuscript and supplement interpretation (coauthor decision memo `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COAUTHOR_DECISION_MEMO_20261123.md`).
- [ ] Permanent versioned archive DOI minted.
- [ ] Archive identity pinned in title page / Open Research Statement.

## Human metadata blockers

- [ ] Final authors/order.
- [ ] Affiliations.
- [ ] Corresponding-author address/email/ORCID.
- [ ] CRediT contributions.
- [ ] Funding.
- [ ] Acknowledgements.
- [ ] Conflict-of-interest statement.
- [ ] All-author approval.
- [ ] No-simultaneous-submission confirmation.
- [ ] Ecology Letters invitation/approved-proposal reference/date.
- [ ] Final AI-use disclosure reconciled with current journal policy and actual use.

## Stop rule

No new ecological endpoint hunting belongs in this manuscript. In particular, **do not** repair the lost original evaluable cell by lowering its four-fold adequacy threshold or selecting a different procedure, taxon or M after results are seen.

The historic taxon-level no-exceedance pattern recurs with restored GBIF, but **the pre-opening full original-283-cell retention criterion failed**. Before considering submission, coauthors must explicitly accept the coverage-limited inference and verify that the abstract, Results, cover letter, supplementary accounting and final scientific claims consistently report **282/283 retained**, rather than a misleading full robustness pass. If the invited methodological claim needs full robustness rather than conditional no-exceedance, hold or revise journal strategy instead of changing the sealed result.

Only after this scientific sign-off **and** completion of human metadata, archival DOI, figures, final journal checks, author approval and disclosures may the invited M1+M2 paper be submitted. The Level-A-only report remains a fallback, not a parallel simultaneous submission.
