# Restored-GBIF source-completeness sensitivity: closed Level A decision
**Date:** 2026-11-22 · **Repository:** `zuizui0223/284b` · **PR:** #74  
**Status:** `HOLD_FOR_SENSITIVITY_REVIEW` · **Empirical ledger increment:** 0

## Decision

The historical same-target Level A **0/12 taxa exceeding calibrated source-paired discordance thresholds** was reproduced at the **taxon-level no-exceedance pattern** under the repaired 2026-08-01 GBIF object set. However, the **predeclared strict full cell-level coverage robustness criterion was not satisfied**: one of the 283 originally evaluable heldout cells became ineligible under the original predictive adequacy rule. **Do not label this a full robustness pass or a new independent biological confirmation.**

## Version-locked evidence

| Quantity | Historical 9,705-Parquet arm | Restored 10,215-Parquet arm |
|---|---:|---:|
| Reference taxa | 47 | 47 |
| Heldout taxa | 12 | 12 |
| Source-specific model cells (47 reference + 12 heldout) | Frozen historical originals | **2,832/2,832 refitted and sealed** |
| Reference q95 cells | 24 | **24/24 independently recalibrated**, nearest-rank q=.95, n≥30 |
| Eligible paired reference cells | Original signed q95 | **1,033/1,128** (95 closed by unchanged adequacy rule) |
| Heldout comparison universe | 288 | 288 |
| Heldout paired cells opened | 283 | **285** |
| Heldout paired cells kept closed | 5 | **3** |
| q95 exceedance cells | 0 | **0** |
| Heldout taxa requiring attention | **0/12** | **0/12** |
| Historical opened cells retained in restored arm | — | **282/283** |
| Historical opened cells lost | — | **1** |
| Historical closed cells newly opened | — | **3** |
| Fully robust under original-283-coverage criterion | Original endpoint, not applicable | **No** |

The reference 47 and heldout 12 panels retain the exact originally frozen taxonomic keys, source-specific admission/thinning rules, 12-block center SHA, 19 CHELSA core predictors, eight procedures, three M radii (150/300/500 km), and 2,000 common comparison rows per M. All 59 original geometry SHA fingerprints were independently reconstructed. The restored fits contain **4,512,000 reference + 1,152,000 heldout = 5,664,000** SHA-checked scored rows.

### What exactly changed in eligibility?

One original-opened cell was **lost**:

- *Nothofagus antarctica*, M=150 km, `niche_forward|logit_l2_C0.1_degree1`, PRESERVED_SPECIMEN answer. Under the original 4-fold CV rule, the mean presence rank **increased** from **0.60452** to **0.61047**, but its SEM increased from **0.09754** to **0.11600**. Hence its frozen lower evidence bound **fell from 0.50698 to 0.49447**, crossing the **0.50000** chance criterion. The original fixed mean floor remains **0.51000**. Both source-specific final model fits remained sealed; the paired score was correctly **not opened**.

Three original-closed cells became newly evaluable:

- *Eucalyptus globulus*, M=150 km, `niche_forward|logit_l2_C0.1_degree1`: HUMAN_OBSERVATION lower evidence bound **0.48548 → 0.58617**
- *Larix laricina*, M=300 km, `niche_forward|logit_l2_C0.1_degree1`: HUMAN_OBSERVATION lower bound **0.44987 → 0.54654**
- *Nothofagus antarctica*, M=150 km, `niche_forward|logit_l2_C1_degree2`: PRESERVED_SPECIMEN lower bound **0.45403 → 0.50078**

Each of the four changed paired-cell states is explained by **exactly one source-specific original-vs-restored outer-CV adequacy flip** under the untouched four-fold/SEM rule. This is a model-evidence change under restored records, **not** direct evidence of changed plant processes or biological niche boundaries.

### Conditional score stability among common evaluable cells

All **282** originally opened and still-opened matched cells remained below their source-version-specific, separately calibrated q95 thresholds. The SHA-attested postterminal comparison finds:

| Descriptive metric: restored minus original | Median | Min | Max |
|---|---:|---:|---:|
| Source-paired discordance `1−Schoener D` across 282 matched cells | **+0.000698** | −0.096457 | +0.173309 |
| Reference q95 threshold across 24 procedure × M cells | **+0.000275** | −0.071800 | +0.047002 |
| Signed margin `(1−D)−q95` across 282 matched cells | **+0.000744** | −0.110673 | +0.194301 |

The **small median shifts do not imply that every cell is stable**: both discordance and q95 changes can be substantial in individual procedure/M cases. The nearest restored heldout margin is still negative, **−0.016911**, for *Eucalyptus globulus* at M=500 km under `predictive_forward|logit_l2_C0.1_degree1`.

## Interpretation / reporting boundary

1. **Permitted:** The qualitative absence of heldout taxon-level exceedances recurs after repairing the originally incomplete GBIF input, refitting all 59 taxa and recalibrating the complete 24-cell reference q95 matrix. All 282 common evaluable cells agree on non-exceedance. The original-source and restored-source fit sets remain non-independent sensitivity arms.
2. **Required qualification:** One original eligible cell is no longer evaluable, despite three gains elsewhere. Therefore **strict retention of all original 283 evaluable cells is false**. The exact sealed terminal classification is `repaired_source_no_attention_but_original_283_cell_coverage_decreased`.
3. **Not permitted:** Calling the terminal sensitivity a fully robust source-replication success; replacing the original 0/12 endpoint; claiming a new independent empirical test; interpreting SDM source concordance as proof of biological process equivalence; excluding the lost cell post hoc; changing the M/procedure/taxon rule or adequacy cutoff to rescue the result.
4. **Manuscript disposition:** **HOLD_FOR_SENSITIVITY_REVIEW** pending supervisor/coauthor assessment of the small but real coverage loss, its signed four-fold mechanism and the conditional strength of the Ecology Letters submission claim. Further descriptive audits cannot promote the strict `robust=false` endpoint.

## Manuscript-ready Results text (English)

> All 59 originally prespecified taxa were refitted following restoration of 510 GBIF Parquet objects to the historical 2026-08-01 export, while retaining the original spatial partitions, evaluation frames, predictors and model procedures. All 2,832 source-specific fits were successfully sealed. The 47-taxon reference panel supported recalibration of all 24 prespecified 95th-percentile discordance thresholds, with at least 30 adequate reference taxa per setting. In the 12-taxon heldout panel, 285 of 288 comparisons were evaluable, compared with 283 historically, and none exceeded its corresponding recalibrated reference threshold (0 of 12 taxa requiring attention). Nevertheless, only 282 of the 283 historically evaluable comparisons remained evaluable: one *Nothofagus antarctica* comparison failed the unchanged prediction-adequacy lower-bound criterion following source restoration, while three previously unresolved comparisons became evaluable. Thus, the absence of exceedances was reproduced among evaluable cells, but the stricter criterion requiring preservation of all original evaluable comparisons was not met. This analysis is a retrospective source-completeness sensitivity check, not an independent biological replication.

## Exact signed audit trail

- Historical one-shot original empirical receipt: `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json`, endpoint fingerprint `80465bdefd484a8e9d5adcdbd792820ff1716c2b589ff9ad2a278c6c9494646c`
- Original 59-taxon spatial metadata provenance: `results/gbif_original_59taxon_geometry_lock_v1.json`
- Repaired reference fit audit: `results/gbif_repaired_reference47_fit_audit_v1.json`, run [#44480047903](https://github.com/zuizui0223/284b/actions/runs/44480047903)
- Repaired heldout source fit audit: `results/gbif_repaired_heldout12_fit_audit_v1.json`, run [#44480087256](https://github.com/zuizui0223/284b/actions/runs/44480087256)
- Reference pre-D and recalibration: `results/gbif_repaired_reference47_preD_feasibility_v1.json`; `results/gbif_repaired_reference47_q95_summary_v1.json`; [run #45013001115](https://github.com/zuizui0223/284b/actions/runs/45013001115)
- Distinct retrospective one-shot terminal `results/gbif_repaired_heldout12_sensitivity_v1.json` and 288-key CSV; [run #45013147700](https://github.com/zuizui0223/284b/actions/runs/45013147700); fingerprint `87b92c461bfbae117a473ac12ce673517878dfbc4b87316d7b8cddc91eadcf48`
- Postterminal exact 288-key coverage receipt: `results/gbif_repaired_heldout12_postterminal_coverage_audit_v1.json`
- Original/repaired signed 282-cell score and 24-q95 drift: `results/gbif_repaired_heldout12_postterminal_score_drift_v1.json`
- Original 4-fold CV evidence explaining the 4 eligibility transitions: `results/gbif_repaired_heldout12_postterminal_cv_switch_v1.json`

All postterminal diagnostics and the retrospective sensitivity ledger themselves contribute **zero** new independent biological conclusions.
