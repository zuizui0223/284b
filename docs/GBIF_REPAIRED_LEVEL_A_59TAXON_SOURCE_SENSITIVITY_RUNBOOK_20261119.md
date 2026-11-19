# Repaired-GBIF Level A sensitivity: fixed 59-taxon decision runbook
**Date:** 2026-11-19 · **Branch:** `analysis/neon-external-truth-preflight-20261115` · **PR:** #74

## Scientific decision at stake

The historical Level A same-target evaluation is a prospectively frozen result for **12 independent heldout taxa**, with 288 prespecified procedure × M diagnostics: **283 evaluable, 5 unresolved, 0/12 taxa with a reference q95 exceedance**. It was fit using 9,705 of the 10,215 current GBIF Parquet data objects in the nominal 2026-08-01 snapshot. The 510 restored objects alter the model-admitted thinned inputs for all 12 heldout and all 47 reference taxa.

The task is a **post-freeze source-completeness sensitivity test**, not a new independent biological experiment. The original historical endpoint remains byte-for-byte preserved, even if the repaired-source outcome changes.

## What is already verified

- Frozen original 59-taxon source-input auditing completed. The source repair changes all 59 model-admitted input populations; the 59-taxon descriptive receipt is source-only.
- Predeclared heldout *Artemisia tridentata* original 12-block geometry reproduced exact historical SHA; 48/48 repaired source fits sealed; within-source score-shift audit completed.
- Predeclared reference *Abies grandis* dual historical-key original 12-block geometry reproduced exact historical SHA; 48/48 repaired source fits sealed; within-source score-shift audit completed.
- The generalized original-reference47 geometry pilot (reference index 1, *Abies grandis*) reproduced original signed spatial center SHA **9eb19bf125fdd06c5e2b9ef901c869c23db6cd9aa88feb1305dffed79ff37f7e**.
- The generalized original-heldout12 geometry pilot (heldout index 0, *Artemisia tridentata*) reproduced original signed spatial center SHA **b9a5db3a5e0324abfdd38626727c170911cfc8994321eb0d24e6d995cd088a15**.

## Fixed execution order and stop rules

| Stage | Frozen units | Opening boundary |
|---|---:|---|
| Original reference geometry (currently running; [#44447154218](https://github.com/zuizui0223/284b/actions/runs/44447154218)) | 47 taxa × 12 original centers × 3 SHA-pinned M frames | No repaired models or paired D |
| Original heldout geometry (currently running; [#44454068403](https://github.com/zuizui0223/284b/actions/runs/44454068403)) | 12 taxa × 12 original centers × 3 SHA-pinned M frames | No repaired models or paired D |
| Repaired reference source fits (gated, **not launched**) | 47 taxa × 2 sources × 8 procedures × 3 M = **2,256** source fits | No reference or heldout paired D |
| Repaired heldout source fits (gated, **not launched**) | 12 taxa × 2 sources × 8 procedures × 3 M = **576** source fits | No paired D or q95 opening |
| Repaired reference pre-D (gated, **not launched**) | 1,128 candidate source pairs; 24 reference procedure × M cells | Qualify at least 30 distinct reference taxa per cell before reading scores |
| Repaired reference q95 (gated, **not launched**) | Exactly 24 thresholds; original nearest-rank 0.95 rule | Reference-only paired D; heldout remains sealed |
| Repaired original 12-heldout one-shot sensitivity (gated, **not launched**) | Exactly 288 original keyed cells | Read only when 24 q95 are sealed; no posthoc taxa/method/M selection |

All data and model artifacts must match originally signed SHA-256 archives, including the exact historical 9,705-object and current 10,215-object source manifests. Any missing taxon, failed original spatial-center SHA, changed comparison frame, opened forbidden outcome, undersized reference cell or mismatched score-row identity fails closed. No taxon or model substitution; all unresolved cells remain explicitly unresolved.

## Source-repair sensitivity interpretation

The original 283 opened heldout cells are **signed and keyed by taxon, M and procedure**. The repaired one-shot code compares the same 288-key universe and requires the original 283 opened-cell identities to remain evaluable before reporting full robustness. There are three possible dispositions:

1. **Robust on the originally opened cells:** zero repaired q95 exceedances, **all original 283 evaluable cells remain evaluable**, all 24 repaired reference thresholds frozen. This supports *source-completeness robustness* of the historical 0/12 claim, not new independent biological validation.
2. **Coverage-limited:** zero repaired exceedances but one or more of the original 283 cells becomes unresolved. The original 0/12 result is **not declared fully robust**; list lost old keys and newly evaluable new keys.
3. **Attention:** any repaired heldout taxon exceeds the separately recalibrated repaired-source q95; document which taxa and the signed settings. The historical 0/12 is **sensitive** to source restoration. This is not automatically a biological falsification.

Both the original frozen reference and newly recalibrated reference are shown distinctly. Do not compare repaired-source heldout scores against the un-recalibrated historical thresholds.

The original signed empirical endpoint is not replaced or recounted: **new independent biological evidence increment = 0** for the retrospective repair sensitivity. Manuscript submission status remains **HOLD_FOR_SENSITIVITY_REVIEW** even when the result is computed.

## Reproducible entrypoints

- `config/gbif_original_reference47_geometry_manifest_v1.json` and `config/gbif_original_heldout12_geometry_manifest_v1.json`: original fixed 47+12 taxa and artifact identities.
- `.github/workflows/gbif_original_reference47_geometry_scaleout_v1.yml` and `.github/workflows/gbif_original_heldout12_geometry_scaleout_v1.yml`: original source-only geometry replay, currently launched.
- `.github/workflows/gbif_repaired_reference47_fixed_original_centers_v1.yml` and `.github/workflows/gbif_repaired_heldout12_fixed_original_centers_v1.yml`: separately gated source-specific model refits, not launched.
- `.github/workflows/gbif_repaired_reference47_preD_v1.yml` and `.github/workflows/gbif_repaired_reference47_q95_v1.yml`: separately gated adequacy-before-paired-D and reference recalibration, not launched.
- `scripts/evaluate_gbif_repaired_heldout12_source_completeness_v1.py` and `.github/workflows/gbif_repaired_heldout12_source_completeness_final_v1.yml`: source-repair retrospective heldout one-shot sensitivity, not launched; requires signed original 288-cell CSV SHA and all 283 original open-cell IDs.
- The launch authorization for each gated downstream stage **must not be written until its specific signed upstream result exists**. No assumptions that a queued/running workflow will succeed.
