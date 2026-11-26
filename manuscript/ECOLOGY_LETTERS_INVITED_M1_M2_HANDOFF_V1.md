# Ecology Letters invited M1+M2 handoff v1

## Decision

Use this branch as the invited full-manuscript development line, but keep the invited submission in **HOLD_FOR_SENSITIVITY_REVIEW** until coauthors explicitly accept the coverage-limited source-repair result. Original Level A is a completed historical empirical endpoint, not an automatically robust complete-snapshot endpoint.

The paper is deliberately narrowed to **completed positive results only**:

- M2: historical Level-A held-out empirical closure (12 taxa; 283/288 evaluable; 0/12 exceedances), **plus a separately labeled retrospective GBIF source-completeness sensitivity** (same 12 taxa; 285/288 evaluable; 0/12 exceedances; only 282/283 original evaluable cells retained). This sensitivity does not add a new independent endpoint.
- M1: exact invalid-state identities + FDF separation.

The previous Level-C candidate/openability material remains repository provenance but is not required in the focal manuscript.

## Canonical manuscript

`manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md`

## Why this is stronger

The paper now closes one coherent argument:

1. A conservative endpoint rule is not merely a refusal mechanism.
2. With sufficient evidence, it closes positively across fresh held-out taxa.
3. When evidence is invalid, coercing it into biological zero has an exact error cost.
4. Even after a process qualifies, final attribution still depends on base rate and aggregation.

Thus the manuscript can be read without any failed or unopened ecological candidate programme. The restored-data sensitivity itself must, however, be transparent about its **failed strict full original-cell retention** test. The one now-unresolved original cell was *Nothofagus antarctica* at 150 km; its lower outer-CV evidence bound crossed below 0.50 because the SEM increased, despite a slightly higher mean predictive rank.

## Fallback

`manuscript/LEVEL_A_SHORT_REPORT_V0_1.md` remains an independent Ecology Report fallback if the invited Ecology Letters route is not pursued.

## Integrated Supporting Information and coauthor review

The complete S1–S11 SI, including both 12-taxon (historical/restored) and 24-configuration restored-q95 tables, mathematical proof and source repair qualification, is now `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COMPLETE_SI_V1.md`. The original source-completeness-only SI remains a signed evidence module. The coauthor decision memo is `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COAUTHOR_DECISION_MEMO_20261123.md`; it requests explicit signoff on **coverage-limited** inference without retrospectively changing `robust=false`.

All four vector manuscript figures and 173-mm print preflight have passed. The remaining figure-specific check is actual placement in the compiled journal reviewer/proof document.

## Current signed scientific source and submission gate

- Original signed Level A: `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json` (historical 0/12, 283/288).
- Restored source-repair final: `results/gbif_repaired_heldout12_sensitivity_v1.json` (0/12, 285/288, original 282/283 retained; strict full-coverage robustness **false**).
- Independent completed CV mechanism audit: `results/gbif_repaired_heldout12_postterminal_cv_switch_v1.json`.
- Invited manuscript and submission claim gate: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md`, `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_CLAIM_LEDGER_V1.md`, `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_READINESS_V1.md`.
- **Do not** alter thresholds or choose new taxa/procedures to make the original 283/283 retention condition pass. That outcome is a documented data-completeness limitation.
- The retrospective repair produces **zero** additional independent ecological results and is not the final author decision to submit.

## Journal-format preflight

The current Method draft is within the journal's preliminary source-text limits (abstract 135 words; main sections 1–7 about 2,392 words; four main figures, eight keywords, nine references), and running title is 29 characters. See `docs/EL_METHOD_JOURNAL_PREFLIGHT_20261123.md` for the counting method and official journal requirements. **This does not establish final journal-formatted readiness.** The final reviewer PDF, published-as-supplied Supporting Information format, archive DOI, conflict/funding metadata and author agreement remain outstanding.

## Remaining human/admin blockers

- author list/order;
- affiliations;
- corresponding-author metadata;
- acknowledgements/funding/conflicts;
- permanent archive DOI;
- final journal-form AI disclosure;
- final compiled submission PDF/portal proof (standalone four figures are already rendered and print-size inspected);
- explicit coauthor sign-off on the exact source-completeness limitation and the conditional strength of the invited Ecology Letters claim;
- final journal formatting, complete-SI upload/numbering proof and coauthor scientific approval.

No new ecological endpoint hunting is required for this manuscript.
