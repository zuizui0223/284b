# Active scientific scope — updated 2026-11-22

284b has one invited manuscript line combining two separately identified positive contributions, plus a non-independent retrospective data-completeness sensitivity audit.

## Primary manuscript — Ecology Letters invited Method (M1 + M2)

- Canonical paper: `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md`
- Submission status: **HOLD_FOR_SENSITIVITY_REVIEW**, not ready for submission.
- **M2 (one historical empirical endpoint):** original prospectively held-out 12 taxa, 288 procedure × M diagnostics, **283 evaluable / 5 unresolved**, **0/12 taxa with an exceedance** of the frozen q95 reference envelope.
- **M1 (exact structural results):** `FPR_zero − FPR_gated = 1−a1`, `TPR_zero − TPR_gated = 1−a0`; equal-validity result `1−a`; process qualification alone does not guarantee low false-discovery fraction.
- The 12 heldout taxa, not 283 repeated diagnostics, are the independent biological replication units.

## Repaired-GBIF source sensitivity — completed, coverage-limited

Nominal historical GBIF 2026-08-01 object set originally had 9,705 Parquet objects; 510 restored objects produced the full 10,215-object input. The **same** original 47 reference taxa and 12 heldout taxa were retained.

- **59/59** original spatial geometries exactly reconstructed and SHA-checked.
- **2,832/2,832** repaired-source model cells sealed (2,256 reference, 576 heldout).
- 24/24 new q95 thresholds calibrated from original reference taxa under unchanged rule (at least 30 eligible taxa per procedure × M).
- Repaired heldout panel: **285/288 evaluable, 3 unresolved, 0/12 taxa with q95 exceedance**.
- Historical original-opened cells retained: **282/283**; **one** original opened cell became unresolved while **three** previously unresolved cells became evaluable.
- The exact original-cell-retention robustness gate **failed**. One *Nothofagus antarctica* specimen-source cell crossed mean−SEM=0.50 after increased outer-fold variability; the model's mean rank did not deteriorate.

Interpretation: taxon-level 0/12 is repeated conditionally under source restoration, but the **strict full cell-level source robustness result is negative**. This is a *post-freeze source-completeness sensitivity check*, not independent new biological evidence. It contributes **0** new empirical endpoint increments. The original historical Level A endpoint remains unchanged, and neither threshold changes nor posthoc taxon/procedure/M substitution is permitted to rescue the outcome.

Signed evidence: `results/gbif_repaired_heldout12_sensitivity_v1.json`; `results/gbif_repaired_heldout12_postterminal_cv_switch_v1.json`; `docs/GBIF_REPAIRED_LEVEL_A_TERMINAL_DECISION_20261122.md`.

## Fallback

`manuscript/LEVEL_A_SHORT_REPORT_V0_1.md` is a historical Level-A standalone fallback and is **not a simultaneous submission**. Any future use requires the same source-completeness disclosure and coauthor review.

## Legacy boundary

Unresolved Level-B/Level-C candidate programs, other candidate-hunting experiments, and unopened biological dependency outcomes remain in `legacy/pre_level_a_focus/` for provenance. They are not evidence for this invited manuscript.

## Submission gates

Coauthors must review and accept the exact coverage-limited strength of the claim before the manuscript can advance to final submission. Outstanding work includes actual author details/order/approvals, versioned data/code DOI, journal requirements, figure rendering/accessibility, supporting information, conflict/funding/AI-use statements, and final text/policy checks.

Do **not** claim 283 independent taxa, universal source invariance, nominal q95 confidence intervals, a repaired-source independent replication, or full original-283-cell retention. Do **not** lower the original mean−SEM adequacy criterion to convert the source-completeness sensitivity into full robustness.
