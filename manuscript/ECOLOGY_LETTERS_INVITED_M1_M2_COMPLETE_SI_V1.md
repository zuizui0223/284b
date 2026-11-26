# Supporting Information — Relation endpoints for ecological inference: M1 mathematics and Level-A source-verified evidence

**Companion manuscript:** *Relation endpoints for ecological inference: when independent answers can support joint biological claims* (invited *Ecology Letters* Method candidate).  
**Draft status:** Integrated Supporting Information for coauthor review, assembled 2026-11-23; **not journal-submitted**, `HOLD_FOR_SENSITIVITY_REVIEW`.  
**Evidence ledger:** exactly **one** historical prospectively held-out empirical endpoint; restored-GBIF source completeness is a retrospective **non-independent** sensitivity analysis; M1 identities and benchmark are analytic/synthetic, **not** ecological field estimates.

## S1. Scope, definitions and evidence hierarchy

The manuscript separates source-specific ecological answer construction from authorization of a *joint* statement. An endpoint specifies (i) a common target/relation and comparison key, (ii) independently constructed answers, (iii) eligibility/adequacy gates, and (iv) a frozen rule determining *consistent*, *attention*, or *unresolved* outcomes. An unidentifiable or inadequate answer remains unresolved rather than being coded as ecological disagreement or as confirmed absence.

**Evidentiary distinctions:** Level A is a controlled test of **same-target, cross-source predictions**, not a field validation of interspecific interactions. M1 is an analytic demonstration of the consequences of replacing unavailable observations with zeros. No cross-role dependency, process knockout, causal necessity or external ecological prediction validation is claimed here. The independent biological evaluation units are the **12 held-out plant taxa**; the 288 method-by-spatial-area diagnostics are repeated within-taxon comparisons. q95 is a calibrated source-discordance envelope, **not** an α=.05 test or a nominal prediction interval.

## S2. Original historical Level-A protocol and opening conditions

Occurrence data were obtained from the frozen GBIF 2026-08-01 source version and separated into `PRESERVED_SPECIMEN` and `HUMAN_OBSERVATION` response streams. Models fitted on one response stream did not use response occurrences from the other. Both streams used a shared source-blind geometry to estimate the same taxon-specific distributional target and compared predicted surfaces on the same 2,000-row climate comparison frame. Predictor universe: **19 CHELSA bio1–bio19 variables**. Spatial accessible-area assumptions: **M=150, 300 and 500 km**. Modelling choices: four fixed predictor-selection strategies (all predictors, VIF filtering, predictive forward selection, niche forward selection) crossed with two prespecified regularized logistic specifications, for eight procedures.

A separate **47-taxon** successor/reference panel calibrated each of **24** procedure-by-M empirical nearest-rank q95 ceilings, requiring at least **30 adequate distinct taxa per reference cell**. All original reference cells passed (34–47 adequate taxa). The independent held-out panel contained **12 taxa × 3 M × 8 procedures = 288** declared cells, with no taxon, procedure, accessible-area or cutoff replacement after viewing held-out outcomes.

Adequacy was evaluated independently for both source-specific answers. The original four-outer-fold gate required mean presence rank ≥0.51 and mean−SEM ≥0.50. Only jointly adequate pairs could be evaluated for discordance `1−Schoener D`; otherwise the cell remained *unresolved*. The one-shot signed historical opening reported **283/288** jointly adequate cells, **five unresolved**, and **0/12 taxa with any exceedance** of its pre-frozen source-specific reference envelope. Those 283 diagnostics are **not 283 independent tests**. The nearest original observed-reference margin was for *Nothofagus betuloides* at M=150 km: observed 0.38624957, q95 0.39084918, difference −0.00459961, observed/reference ratio 0.988.

## S3. Taxon-level historical versus restored-source diagnostics (Table S1)

**Table S1** compares the maximum **evaluable** cell-level ratio `(1−D)/q95` within each taxon. Historical and restored source predictions use their **own separately calibrated q95**; the two columns are descriptive sensitivities of *the same taxa*, **not independent biological replications**. At least one diagnostic was evaluable for every taxon in both arms.

| Held-out plant taxon | Original historical maximum ratio | Restored-source maximum ratio | Restored evaluable / declared |
|---|---:|---:|---:|
| *Nothofagus betuloides* | 0.988 | 0.892 | 24/24 |
| *Nothofagus antarctica* | 0.915 | 0.884 | 23/24 |
| *Eucalyptus delegatensis* | 0.895 | 0.859 | 24/24 |
| *Eucalyptus globulus* | 0.882 | 0.950 | 23/24 |
| *Abies lasiocarpa* | 0.865 | 0.787 | 24/24 |
| *Laguncularia racemosa* | 0.751 | 0.825 | 24/24 |
| *Avicennia marina* | 0.647 | 0.720 | 24/24 |
| *Encelia farinosa* | 0.643 | 0.779 | 24/24 |
| *Atriplex canescens* | 0.636 | 0.725 | 24/24 |
| *Artemisia tridentata* | 0.550 | 0.547 | 24/24 |
| *Larix laricina* | 0.540 | 0.585 | 23/24 |
| *Avicennia germinans* | 0.509 | 0.580 | 24/24 |

Every ratio remains below one (source-version-specific reference ceiling). This does **not** imply universal invariance in predicted suitability or full preservation of model adequacy: original 283/288 jointly adequate comparisons became 285/288 under source repair, with only **282/283** original eligible cells retained. The maximum original ratio is 0.988 for *Nothofagus betuloides*; the maximum restored ratio is 0.950 for *Eucalyptus globulus*. The full 288 keyed restored comparisons, including three unresolved rows without assigned discordance, are in `results/gbif_repaired_heldout12_sensitivity_cells_v1.csv` and are not reinterpreted as 288 independent biological units.

## S4. M1 hard-rule derivation, denominator definitions and valid-key selection

Let `F=true` denote a biologically compatible required function, `F=false` a true violation of the hard function requirement, and `V` a valid observation/comparison key. Let `a1=P(V|F=true)`, `a0=P(V|F=false)`, `q=P(correctly call function present|V,F=true)`, and `sp=P(correctly call function absent|V,F=false)`. Here `q` is the sensitivity for detecting a present function, and `sp` is the true-violation classification probability on valid violating keys; the notation follows the frozen M1 contract.

The **gated hard-violation-call rates** are counted per *all keys of the latent class*, not only among classified keys. For compatible keys, `FPR_gated=a1(1−q)`; for genuine violations, `TPR_gated=a0·sp`. If invalid/unknown keys are incorrectly converted into biological absence (zero-collapsing), the corresponding rates are `FPR_zero=1−a1 q` and `TPR_zero=1−a0(1−sp)`. Therefore the exact identities are

```text
FPR_zero − FPR_gated = 1 − a1
TPR_zero − TPR_gated = 1 − a0
```

For class-independent valid-key fraction `a1=a0=a`, the two increments both reduce to `1−a`. These are identities **conditional on the stipulated observation/classification model**, not measurements of natural invalid-key frequencies. An illustrative class-dependent setting (`a1=.70,a0=.90,q=.95,sp=.99`) yields FPR .035 (gated) versus .335 (zero collapse) and true-violation sensitivity .891 versus .991, consistent with the exact +.30/+ .10 increments. No focal dependent-species process or intervention was examined.

### S4.1. Qualified-call false-discovery fraction (FDF)

Define `pi=P(F=false)` as the true-violation prevalence **before** validity filtering. Among all candidate keys,

```text
P(false qualified violation call) = (1-pi) a1 (1-q)
P(true qualified violation call)  = pi a0 sp
FDF_qualified = (1-pi)a1(1-q) / [(1-pi)a1(1-q) + pi a0 sp].
```

FDF is **undefined if the denominator is zero**, not automatically zero. The shorter formula without `a1,a0` is appropriate only if `a1=a0>0`, **or** `pi` is instead defined as the violation prevalence **among valid keys** (`pi_valid`). More explicitly, if the valid-key mixture has nonzero mass, `pi_valid = pi a0 / [(1-pi)a1 + pi a0]`; the shorter formula with `pi_valid` is algebraically equivalent to the general expression. For nondegenerate probabilities the false-discovery odds are multiplied by `a1/a0` relative to an equal-validity scenario at the same unconditional `pi,q,sp`. This is an analytic selection effect, not an estimate of nature.

For `pi=.10,q=.80,sp=.99`:

| Assumed validity (a1 / a0) | False-call mass | True-call mass | FDF among issued calls |
|---|---:|---:|---:|
| 1.00 / 1.00 | .1800 | .0990 | .645161 |
| .70 / .90 | .1260 | .0891 | .585774 |
| .90 / .70 | .1620 | .0693 | .700389 |

The underlying qualifications distinguish what can be *called* from whether an issued call is *reliable*. An observation-validity gate does not by itself guarantee a low false-discovery fraction.

## S5. Synthetic benchmark scope and audit checks

The pre-field analytic identifiability benchmark used a fixed grid of **8,748 parameter scenarios** (not a Monte Carlo simulation and not real observed key-level data). Of these, **4,320** passed the scripted calibration gate and **4,428** did not; the identities above were reproduced to machine precision (maximum absolute numerical discrepancy ~1.11×10⁻¹⁶ in each class-rate identity). Those scenario counts depend on the benchmark's chosen threshold grid, not on ecological sampling prevalence. The grid explored event detection, window completeness, missingness, device failure, replication opportunities, specificity and hypothetical violation prevalence. Under a failing calibration gate, a hard biological negative was never authorized. These findings are **synthetic algorithm/identity checks**, not independent confirmation of any ecological dependence or mechanism.

The original benchmark summary is `results/pre_field_identifiability_benchmark_summary_v0_1.json`, and the state-dependent extension is `results/pre_field_state_dependent_invalidity_v0_2.json`. Exact structural implementations reside in `scripts/relation_endpoint_contract.py` and the audit `scripts/audit_state_dependent_invalidity_v0_2.py`. Regression tests `tests/test_m1_fdf_validity_asymmetry_20261122.py` protect both asymmetric FDF cases, the zero-call undefined edge, the `pi_valid` equivalence and the frozen `1−a1`/`1−a0` identities.

**Submission disposition:** `HOLD_FOR_SENSITIVITY_REVIEW`

## S6. Frozen source, taxonomy, and modeling contract

The nominal 2026-08-01 GBIF source export used to fit the historical, prospectively heldout Level A endpoint contained **9,705** available Parquet objects. The later source-integrity audit recovered **510** additional objects belonging to that same nominal export, resulting in a restored **10,215-object** input. This is a correction of upstream source completeness, not a new field survey.

The original taxon split was kept intact: **47 reference taxa and 12 heldout taxa**, with no taxon overlap. For all 59 taxa, the original historical 12 spatial-block centers and three 2,000-row comparison frames (accessible-area M = 150, 300, 500 km) were reconstructed to their original signed SHA-256 identities. Model fitting preserved independent PRESERVED_SPECIMEN versus HUMAN_OBSERVATION response arms, CHELSA bio1–bio19 predictor universe, eight original procedures and the original four-fold predictive-adequacy requirements.

The source-specific complete-snapshot refit sealed **2,256/2,256 reference model cells** and **576/576 heldout model cells**, without unresolved model fits. These 2,832 fitted models contributed **5,664,000** integrity-verified source-specific prediction rows across the fixed comparison frames. These rows are not independent biological replicates.

## S7. Recalibrated reference envelopes before heldout opening

After refitting the reference panel, each original procedure × M cell had to pass the unchanged **minimum of 30 adequate distinct reference taxa** before paired reference-source predictions could be read. All **24 of 24** cells passed this gate, with **35–47** adequate taxa per cell. Of **1,128** reference taxon-by-procedure-by-M pairs, **1,033** were authorized to open and **95** remained closed under the original predictive-adequacy rule.

For every reference cell, the comparator was the original nearest-rank **95th percentile of `1−Schoener D`** across eligible reference taxa. The 24 restored-source thresholds were frozen independently of all 12 restored heldout outcomes. The q95 cutoff is an empirical source-discordance envelope, **not** a nominal 95% confidence interval or a conventional alpha=0.05 hypothesis test.

The full restored per-cell reference table is `results/gbif_repaired_reference47_q95_ceiling_v1.csv`; the signed summary is `results/gbif_repaired_reference47_q95_summary_v1.json`. The historical comparator comes from the original signed `product-b-core19-v0-4-2-reference` artifact (run 34439012066). The historical and restored threshold tables remain distinct.

### Table S2. Recalibrated 24-cell restored-source reference thresholds

These are **restored-source** empirical q95 envelopes, not historical q95 values or nominal 95% coverage guarantees. Sample size is the number of adequate distinct reference taxa within each predeclared procedure-by-accessible-area setting; the minimum gate is 30.

| Accessible radius M (km) | Modeling procedure | Eligible reference taxa | Restored q95 for 1−D |
|---:|---|---:|---:|
| 150 | `all|logit_l2_C0.1_degree1` | 41 | 0.31614 |
| 150 | `all|logit_l2_C1_degree2` | 45 | 0.44248 |
| 150 | `niche_forward|logit_l2_C0.1_degree1` | 35 | 0.34092 |
| 150 | `niche_forward|logit_l2_C1_degree2` | 45 | 0.39865 |
| 150 | `predictive_forward|logit_l2_C0.1_degree1` | 36 | 0.31882 |
| 150 | `predictive_forward|logit_l2_C1_degree2` | 44 | 0.43785 |
| 150 | `vif|logit_l2_C0.1_degree1` | 38 | 0.29816 |
| 150 | `vif|logit_l2_C1_degree2` | 44 | 0.41722 |
| 300 | `all|logit_l2_C0.1_degree1` | 43 | 0.31101 |
| 300 | `all|logit_l2_C1_degree2` | 47 | 0.44869 |
| 300 | `niche_forward|logit_l2_C0.1_degree1` | 41 | 0.41618 |
| 300 | `niche_forward|logit_l2_C1_degree2` | 46 | 0.42765 |
| 300 | `predictive_forward|logit_l2_C0.1_degree1` | 41 | 0.34109 |
| 300 | `predictive_forward|logit_l2_C1_degree2` | 46 | 0.48836 |
| 300 | `vif|logit_l2_C0.1_degree1` | 41 | 0.29355 |
| 300 | `vif|logit_l2_C1_degree2` | 47 | 0.43334 |
| 500 | `all|logit_l2_C0.1_degree1` | 44 | 0.30738 |
| 500 | `all|logit_l2_C1_degree2` | 47 | 0.44754 |
| 500 | `niche_forward|logit_l2_C0.1_degree1` | 39 | 0.36772 |
| 500 | `niche_forward|logit_l2_C1_degree2` | 46 | 0.45879 |
| 500 | `predictive_forward|logit_l2_C0.1_degree1` | 42 | 0.34024 |
| 500 | `predictive_forward|logit_l2_C1_degree2` | 47 | 0.48439 |
| 500 | `vif|logit_l2_C0.1_degree1` | 42 | 0.29494 |
| 500 | `vif|logit_l2_C1_degree2` | 46 | 0.42213 |

## S8. Original versus repaired heldout evaluability

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

## S9. Matched old-versus-restored source-pair scores

Across the **282 cells eligible in both versions**, the original and restored score vectors refer to exactly the same frozen taxon, method, M, spatial centers and 2,000 background rows. The following are **descriptive changes across repeated diagnostics**; the 282 values are not independent taxa or a confirmatory sample.

| Restored minus original | Median | Minimum | Maximum |
|---|---:|---:|---:|
| Source-paired discordance `1−D` (282 common cells) | +0.000698 | −0.096457 | +0.173309 |
| Reference nearest-rank q95 (24 cells) | +0.000275 | −0.071800 | +0.047002 |
| Discordance minus version-matched q95 (282 common cells) | +0.000744 | −0.110673 | +0.194301 |

All **282 common evaluable cells** remained under their *respective* version-matched reference envelope. Across all **285 restored evaluable cells**, the closest negative margin was **−0.016911**, for *Eucalyptus globulus*, M=500 km, `predictive_forward|logit_l2_C0.1_degree1` (discordance 0.323324, q95 0.340236).

Median changes are small, but the range is not: reporting only the medians would incorrectly suggest uniformly invariant source-paired predictions. The restored reference thresholds were calibrated anew using the 47 original reference taxa; repaired heldout scores were never compared with unchanged historical thresholds as the primary source-repair evaluation.

## S10. Information boundary, endpoint identities and audit status

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

## S11. Supplement evidence index, display and audit restrictions

**Displays:** Figure 1 documents the prospective endpoint and unresolved-state gate; Figure 2 displays 12 historical/restored taxon maxima and the exact 2×2 eligibility transition; Figure 3 depicts the class-conditional zero-collapse identities; Figure 4 shows the **three theoretical FDF curves**. Their captions and alternative text are in `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_CAPTIONS_V1.md`; signed output ID and 173-mm vector print-size audit are recorded in `manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_QA_20261122.md`.

**Canonical fixed and retrospective endpoints:** `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json` has historical fingerprint `80465bdefd484a8e9d5adcdbd792820ff1716c2b589ff9ad2a278c6c9494646c`, and `results/gbif_repaired_heldout12_sensitivity_v1.json` has separate retrospective fingerprint `87b92c461bfbae117a473ac12ce673517878dfbc4b87316d7b8cddc91eadcf48`. The latter is `repaired_source_no_attention_but_original_283_cell_coverage_decreased`, expressly **not** the full original-283-cell-coverage robustness result. No endpoint, threshold or source-specific model result was altered by composing this SI.

**What this SI does not establish:** no observational equality of specimen/human recording processes; no universal source-invariance or nominal 95% generalization guarantee; no 283/285 independent ecological replicates; no cross-species causal dependency or process necessity; no field-estimated valid-key fraction `a0/a1`; no independent ecological replication from restoring GBIF objects; no support for overriding the predeclared full-retention criterion.

**Authorial review gate:** This integrated SI is prepared for scientific and journal-format review but must remain `HOLD_FOR_SENSITIVITY_REVIEW` until coauthors explicitly accept the one-cell eligibility loss, verify the FDF conditioning and approve all scientific statements and disclosures. DOI, authorship, funding/conflicts, final compiled journal proof and reviewer-blinding settings remain to be confirmed.

