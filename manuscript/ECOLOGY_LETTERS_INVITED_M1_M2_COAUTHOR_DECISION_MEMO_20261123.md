# Coauthor scientific decision memo — invited M1+M2 Ecology Letters Method candidate

**Prepared:** 2026-11-23 · **Repository:** `zuizui0223/284b`, draft PR #74  
**State:** `HOLD_FOR_SENSITIVITY_REVIEW` — review material only. **No coauthor consent, submission, acceptance or peer-review decision is implied.**

## Decision requested of the author team

Please assess whether the manuscript's central inference is justified when the **historical prospective Level-A test** had 0/12 held-out plant taxa with an empirical source-discordance envelope exceedance among 283/288 evaluable procedure×M diagnostics, and the **retrospective restoration of 510 missing GBIF Parquet objects** preserved the **taxon-level 0/12 pattern** among 285/288 evaluable diagnostics, but failed the predeclared *strict full original-cell coverage* rule because only **282 of the 283 original evaluable comparisons** remained evaluable.

This is **not** a vote to reinterpret `robust=false` as `true`; that state is fixed. The authorial decision is about an accurate, transparent *coverage-limited* Method paper.

## Exact scientific evidence to sign off

1. **M2, independent biological evidence (one original endpoint):** 12 prospectively held-out taxa, 288 fixed repeated diagnostics, 283 evaluated, five unresolved, zero taxa with any empirical q95 exceedance. The nearest observed-reference ratio was 0.988 for *Nothofagus betuloides*. A q95 envelope is not a nominal confidence/prediction interval or a binomial success probability.
2. **GBIF source-repair sensitivity (non-independent):** same 12 held-out and 47 reference taxa, same original geometry/estimands/procedures and fixed adequacy gate. Both source-specific models refitted for 2,832 procedure×M×source cells. All 24 reference q95 thresholds were recalibrated before opening repaired held-out pairs. All 285 evaluated repaired pairs remained below their own version-matched q95. Of 283 historically evaluable cells, only 282 remained evaluable (one lost, three newly evaluable from five previously unresolved), so prespecified full original-coverage robustness is **false**.
3. **The lost cell:** *Nothofagus antarctica*, M=150 km, `niche_forward|logit_l2_C0.1_degree1`, specimen model. Mean presence rank increased from 0.60452 to 0.61047 while SEM rose from 0.09754 to 0.11600, moving mean−SEM from 0.50698 to 0.49447 below the unchanged 0.50 threshold. The cell must be unresolved in restored-source scoring.
4. **M1 theorem:** `FPR_zero−FPR_gated=1−a1`; `TPR_zero−TPR_gated=1−a0` per original latent class, with invalid keys unresolved under gating. Qualified-call false discovery with unconditional `pi=P(true violation)` is `(1−pi)a1(1−q)/[(1−pi)a1(1−q)+pi a0 sp]` when the denominator is positive. The shorter FDF expression applies with unconditional pi only when `a1=a0>0`; otherwise use `pi_valid` conditional on validity. At `pi=.10,q=.80,sp=.99`, analytic examples yield 0.645 (equal validity), 0.586 (`a1=.7,a0=.9`) and 0.700 (`a1=.9,a0=.7`). No natural a1/a0 frequencies were measured.
5. **Inferential boundary:** this method paper does **not** demonstrate species-interaction causality, an obligate functional dependence, process necessity, external field prediction accuracy or universal source-invariance. The original empirical evidence ledger remains **one**.

## Permissible decisions after coauthor review

- **Qualified approval:** accept a Method submission whose primary empirical statement is *conditional same-target source agreement within frozen, empirically calibrated bounds*. Explicitly report that source repair preserved 0/12 taxon-level non-exceedance but failed the strict 283/283 original-evaluability-retention criterion.
- **Request further revision without new endpoint hunting:** narrow the framing or move parts of the coverage analysis into SI while preserving the failed predeclared criterion prominently in Results and Abstract. Further posthoc analytic diagnostics do not convert `robust=false` into a pass.
- **Hold or change journal strategy:** if the agreed journal claim requires independent external validation or strict source-version robustness, do not submit a stronger conclusion than the available evidence.

No option authorizes changing prespecified taxa, source filtering, M, procedure, adequacy cutoffs, q95 rule, or the sealed primary endpoints after seeing outcomes.

## Files to inspect together

- Main Method paper: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md`
- **Complete** M1+M2 SI (S1–S11, Table S1 for 12 taxa, Table S2 for 24 q95 thresholds): `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COMPLETE_SI_V1.md`
- Mathematically corrected M1 note: `docs/M1_CLASS_DEPENDENT_FDF_AUDIT_20261122.md`
- Exact signed source-repair terminal: `results/gbif_repaired_heldout12_sensitivity_v1.json`
- Exact CV transition evidence: `results/gbif_repaired_heldout12_postterminal_cv_switch_v1.json`
- Figures 1–4 and alt text: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_CAPTIONS_V1.md`; rendered artwork audit `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_QA_20261122.md`
- Author approval/metadata gate: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_READINESS_V1.md`

## Outstanding administrative work after a scientific decision

Final and correct author list and order, affiliations, corresponding-author information, CRediT, funding and conflicts, journal-appropriate AI disclosure, the exact invitation/approved proposal reference, original-and-supplement DOI archiving, final formatted main manuscript and SI, compiled journal portal/reviewer proof, any mandated anonymization and confirmation of no simultaneous submission.

**Current verdict:** ready **for coauthor scientific review**, **not** authorized for submission or merge merely because source checks and figures passed.
