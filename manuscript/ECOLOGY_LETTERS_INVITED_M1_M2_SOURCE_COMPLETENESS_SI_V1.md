# Supporting information — Historical GBIF source completeness and Level A cross-source comparability

**Companion to:** *Relation endpoints for ecological inference: when independent answers can support joint biological claims* (Ecology Letters invited Method candidate)  
**Status:** retrospective input-completeness sensitivity, completed 2026-11-22; **not** independent biological replication  
**Submission disposition:** `HOLD_FOR_SENSITIVITY_REVIEW`

## S1. Frozen source, taxonomy, and modeling contract

The nominal 2026-08-01 GBIF source export used to fit the historical, prospectively heldout Level A endpoint contained **9,705** available Parquet objects. The later source-integrity audit recovered **510** additional objects belonging to that same nominal export, resulting in a restored **10,215-object** input. This is a correction of upstream source completeness, not a new field survey.

The original taxon split was kept intact: **47 reference taxa and 12 heldout taxa**, with no taxon overlap. For all 59 taxa, the original historical 12 spatial-block centers and three 2,000-row comparison frames (accessible-area M = 150, 300, 500 km) were reconstructed to their original signed SHA-256 identities. Model fitting preserved independent PRESERVED_SPECIMEN versus HUMAN_OBSERVATION response arms, CHELSA bio1–bio19 predictor universe, eight original procedures and the original four-fold predictive-adequacy requirements.

The source-specific complete-snapshot refit sealed **2,256/2,256 reference model cells** and **576/576 heldout model cells**, without unresolved model fits. These 2,832 fitted models contributed **5,664,000** integrity-verified source-specific prediction rows across the fixed comparison frames. These rows are not independent biological replicates.

## S2. Recalibrated reference envelopes before heldout opening

After refitting the reference panel, each original procedure × M cell had to pass the unchanged **minimum of 30 adequate distinct reference taxa** before paired reference-source predictions could be read. All **24 of 24** cells passed this gate, with **35–47** adequate taxa per cell. Of **1,128** reference taxon-by-procedure-by-M pairs, **1,033** were authorized to open and **95** remained closed under the original predictive-adequacy rule.

For every reference cell, the comparator was the original nearest-rank **95th percentile of `1−Schoener D`** across eligible reference taxa. The 24 restored-source thresholds were frozen independently of all 12 restored heldout outcomes. The q95 cutoff is an empirical source-discordance envelope, **not** a nominal 95% confidence interval or a conventional alpha=0.05 hypothesis test.

The full restored per-cell reference table is `results/gbif_repaired_reference47_q95_ceiling_v1.csv`; the signed summary is `results/gbif_repaired_reference47_q95_summary_v1.json`. The historical comparator comes from the original signed `product-b-core19-v0-4-2-reference` artifact (run 34439012066). The historical and restored threshold tables remain distinct.

## S3. Original versus repaired heldout evaluability

| Heldout accounting | Original input | Restored input |
|---|---:|---:|
| Prespecified plant taxa | 12 | 12 (identical taxa) |
| Procedure × M cells per taxon | 24 | 24 (unchanged) |
| Prespecified cell universe | 288 | 288 (identical keyed cells) |
| Evaluable source-paired comparisons | **283** | **285** |
| Unresolved source-paired comparisons | **5** | **3** |
| Evaluated comparisons with discordance above q95 | **0** | **0** |
| Taxa with any above-q95 comparison | **0/12** | **0/12** |

These aggregate counts conceal a change in the *identities* of evaluable cells. **Only 282 of the original 283 evaluable cells remained evaluable.** One originally eligible cell became ineligible; three originally ineligible cells became eligible. Thus the pre-opening stricter sensitivity requirement to retain **all 283 original opened cells** was **not** satisfied, even though the source-repaired taxon-level 0/12 non-exceedance pattern recurred.

The four changed cells are listed below. Eligibility is always evaluated for **both independently fitted sources**; a paired comparison opens only if both satisfy the frozen outer-CV gate.

| Taxon | M (km) | Procedure | Changed source | Original mean−SEM | Restored mean−SEM | Transition |
|---|---:|---|---|---:|---:|---|
| *Nothofagus antarctica* | 150 | `niche_forward|logit_l2_C0.1_degree1` | PRESERVED_SPECIMEN | 0.50698 | 0.49447 | **Open → unresolved** |
| *Eucalyptus globulus* | 150 | `niche_forward|logit_l2_C0.1_degree1` | HUMAN_OBSERVATION | 0.48548 | 0.58617 | Unresolved → open |
| *Larix laricina* | 300 | `niche_forward|logit_l2_C0.1_degree1` | HUMAN_OBSERVATION | 0.44987 | 0.54654 | Unresolved → open |
| *Nothofagus antarctica* | 150 | `niche_forward|logit_l2_C1_degree2` | PRESERVED_SPECIMEN | 0.45403 | 0.50078 | Unresolved → open |

The unchanged original predictive-adequacy gate used **four outer folds**, required mean presence rank ≥ **0.51**, and required mean−SEM ≥ **0.50** for each independently fitted answer. For the **lost** *Nothofagus antarctica* specimen-source cell, the mean rank was **0.60452 → 0.61047** (higher after restoration), but SEM was **0.09754 → 0.11600**, so the evidence lower bound crossed below 0.50. This is a change in source-specific predictive uncertainty and adequacy, **not** evidence that its ecological distribution or the underlying biological mechanism changed.

For completeness, the three cells that remained unresolved after restoration were *Eucalyptus globulus* at M=150 km, `predictive_forward|logit_l2_C0.1_degree1` (HUMAN_OBSERVATION inadequate); *Larix laricina* at M=150 km, `niche_forward|logit_l2_C0.1_degree1` (PRESERVED_SPECIMEN inadequate); and the *Nothofagus antarctica* cell lost from the original-opened set. No unresolved cell was assigned a discordance or counted as an exceedance.

## S4. Matched old-versus-restored source-pair scores

Across the **282 cells eligible in both versions**, the original and restored score vectors refer to exactly the same frozen taxon, method, M, spatial centers and 2,000 background rows. The following are **descriptive changes across repeated diagnostics**; the 282 values are not independent taxa or a confirmatory sample.

| Restored minus original | Median | Minimum | Maximum |
|---|---:|---:|---:|
| Source-paired discordance `1−D` (282 common cells) | +0.000698 | −0.096457 | +0.173309 |
| Reference nearest-rank q95 (24 cells) | +0.000275 | −0.071800 | +0.047002 |
| Discordance minus version-matched q95 (282 common cells) | +0.000744 | −0.110673 | +0.194301 |

All **282 common evaluable cells** remained under their *respective* version-matched reference envelope. Across all **285 restored evaluable cells**, the closest negative margin was **−0.016911**, for *Eucalyptus globulus*, M=500 km, `predictive_forward|logit_l2_C0.1_degree1` (discordance 0.323324, q95 0.340236).

Median changes are small, but the range is not: reporting only the medians would incorrectly suggest uniformly invariant source-paired predictions. The restored reference thresholds were calibrated anew using the 47 original reference taxa; repaired heldout scores were never compared with unchanged historical thresholds as the primary source-repair evaluation.

## S5. Information boundary, endpoint identities and audit status

The historical empirical endpoint remains `same_target_cross_source_reproducibility_heldout12_core19_v0_4`, with fingerprint `80465bdefd484a8e9d5adcdbd792820ff1716c2b589ff9ad2a278c6c9494646c`. Its originally opened 283 cells and five unresolved cells are **not overwritten**.

The distinct retrospective sensitivity endpoint is `gbif_20260801_restored510_historical_levelA_source_sensitivity_v1`, fingerprint `87b92c461bfbae117a473ac12ce673517878dfbc4b87316d7b8cddc91eadcf48`. Its signed classification is **`repaired_source_no_attention_but_original_283_cell_coverage_decreased`**. The prescribed strong full-retention robustness flag is **false**. Its independent empirical ledger increment is **0**.

Key machine-readable audit files:

- `results/gbif_original_59taxon_geometry_lock_v1.json` — exact 47+12 disjoint original taxa and signed historical geometry
- `results/gbif_repaired_reference47_fit_audit_v1.json` and `results/gbif_repaired_heldout12_fit_audit_v1.json` — 2,832 sealed source-specific fits
- `results/gbif_repaired_reference47_preD_feasibility_v1.json` and `results/gbif_repaired_reference47_q95_ceiling_v1.csv` — 24 independent reference gates and thresholds
- `results/gbif_repaired_heldout12_sensitivity_v1.json` and `results/gbif_repaired_heldout12_sensitivity_cells_v1.csv` — original-vs-restored source retrospective terminal, all 288 cell keys
- `results/gbif_repaired_heldout12_postterminal_coverage_audit_v1.json` — exact 282 retained, one lost and three gained cells
- `results/gbif_repaired_heldout12_postterminal_score_drift_v1.json` — signed 282-cell paired-score and 24-cell reference threshold changes
- `results/gbif_repaired_heldout12_postterminal_cv_switch_v1.json` — original/repaired four-fold source-adequacy evidence for four changed cells

**Interpretation:** The absence of calibrated heldout taxon-level source-discordance exceedances recurred under restored GBIF source inputs. Nonetheless, **the exact original-283-cell evaluability-retention sensitivity failed**, and the result must be presented as **coverage-limited**. This is not new independent field evidence, does not establish universal source invariance, and provides no direct causal information on ecological processes.
