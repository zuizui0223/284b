# Cross-source reproducibility of species-distribution predictions across prospectively held-out plant taxa

**Target journal:** Ecology  
**Manuscript type:** Report  
**Status:** Level-A standalone draft v0.1  
**Author metadata:** TODO before submission

## Abstract

Biodiversity records collected as preserved specimens and human observations arise from different observation processes, raising a practical question for species-distribution modelling: do independently fitted models recover reproducible ecological predictions when the biological target is held fixed? We tested cross-source reproducibility prospectively rather than selecting models after viewing source agreement. Preserved-specimen and human-observation records were separated before fitting. For each taxon, both sources used the same 19 CHELSA bioclimatic predictors, source-symmetric comparison geometry, three prespecified accessible-area radii (150, 300 and 500 km), and eight prespecified modelling procedures. Procedure-by-area discordance envelopes were calibrated from an independent successor panel and frozen before opening outcomes for 12 held-out taxa. The 12 taxa generated 288 prespecified diagnostics. Both source-specific answers passed their adequacy gates in 283 cells; five remained unresolved. No held-out taxon contained an exceedance of its corresponding frozen empirical source-discordance envelope. The closest evaluable cell had discordance 0.38625 against a frozen ceiling of 0.39085, showing that the result was not produced only by uniformly loose bounds. These results provide a controlled empirical demonstration that strongly different biodiversity data streams can yield reproducible same-target distribution predictions when comparison geometry, estimand and evaluation rules are fixed prospectively. The result is conditional on answer adequacy and does not imply universal source invariance.

**Key words:** biodiversity data; citizen science; cross-validation; GBIF; museum specimens; reproducibility; source bias; species distribution models

## Introduction

Species-distribution models increasingly draw on biodiversity records produced by observation processes that were never designed to be interchangeable. Preserved specimens reflect collecting histories, institutional priorities and uneven spatial effort, whereas human-observation records reflect accessibility, observer behaviour and contemporary participation. These differences can propagate into estimated distributions, and a substantial literature has therefore focused on imperfect detection, sampling bias, source-specific correction and data fusion (Guillera-Arroita 2017; Pacifici et al. 2017; Erickson & Smith 2021). Community-science observations can improve distribution modelling in some settings, but the value of adding them depends on the species, data structure and evaluation design (Matutini et al. 2021; Gaier & Resasco 2023).

Here we ask a narrower question. Suppose two data streams are used to estimate the **same ecological target**, while the estimand, environmental predictor universe, accessible-area semantics and comparison frame are held common. If each source-specific model is built independently, are the resulting ecological predictions reproducible on taxa that were not used to define the acceptable level of source-to-source discordance?

This question differs from asking whether the two observation processes are identical. They are not expected to be. It also differs from asking whether pooling sources improves predictive accuracy. Instead, it treats data provenance as a prospective generalization problem: source-specific answers are constructed independently, an empirical range of expected disagreement is calibrated without access to focal held-out outcomes, and fresh taxa are then opened once under the frozen rule.

This design addresses two common routes to overstatement. First, if modelling procedures or spatial extents are chosen after cross-source agreement is inspected, apparent reproducibility can be produced by selection. We therefore retain a prespecified matrix of procedures and accessible areas rather than choosing the combination with the best agreement. Second, failed or inadequate models should not be converted into disagreement. A comparison cell is evaluated only when both source-specific answers pass the same predeclared adequacy logic; otherwise it remains unresolved.

We tested this design using preserved-specimen and human-observation records for plant taxa. Our independent biological replication level was 12 prospectively held-out taxa. Each taxon was evaluated across three accessible-area radii and eight modelling procedures, while procedure-by-area discordance envelopes were calibrated from a separate successor panel and frozen before held-out predictions were compared. We asked whether any held-out taxon showed source discordance beyond the corresponding frozen envelope.

## Methods

### Data sources and information separation

Occurrence data came from a frozen GBIF snapshot dated 1 August 2026 (DOI 10.15468/dl.fs3btq). Records were separated by GBIF basis-of-record into PRESERVED_SPECIMEN and HUMAN_OBSERVATION streams. The two response streams were kept independent during model fitting: occurrences from one mode could not enter the likelihood, predictor selection or prediction fitting of the other mode.

A source-blind pooled coordinate representation was allowed only to define symmetric comparison geometry. Source labels were removed before constructing common accessible-area and spatial-block geometry, and record frequency from either source could not weight that geometry. Thus the two models answered the same spatial question without sharing response occurrences.

### Held-out design

The focal test consisted of 12 prospectively frozen held-out plant taxa. Held-out taxa were not replaced after model fitting or source-discordance outcomes. Within every taxon, all three accessible-area radii (M = 150, 300 and 500 km) and all eight procedures were retained as a sensitivity matrix rather than treated as candidates from which a favourable result could be selected.

For each taxon-by-M combination, both source-specific answers used the same 2,000-row comparison/background frame. Accessible areas were defined around source-blind common geometry, and the same rows and environmental values were used for the two observation modes.

### Environmental predictors and modelling procedures

The final endpoint used the 19 CHELSA bioclimatic variables bio1-bio19. This core-climate universe was frozen prospectively as a distinct endpoint version before its focal held-out discordance was opened.

The procedure library crossed four predictor strategies with two regularized logistic specifications. The predictor strategies were: all predictors, variance-inflation filtering, predictive forward selection and niche-oriented forward selection. The two logistic specifications used L2 regularization with C = 0.1 and degree 1, or C = 1.0 and degree 2. This produced eight procedures for each accessible-area radius.

Model assessment used prespecified inner and outer folds. Source-specific prediction adequacy was evaluated separately under the frozen outer-fold AUC/uncertainty rule before any paired source discordance could be opened. A procedure or accessible-area radius could not be dropped because of its later cross-source result.

### Prospective reference envelopes

The acceptable source-to-source discordance was calibrated independently of the 12 focal held-out taxa. For each of the 24 procedure-by-M cells, the reference required at least 30 prospectively adequate successor taxa. All 24 cells met this requirement, with 34-47 distinct adequate successor taxa per cell.

For each cell we froze the nearest-rank 0.95 quantile of the successor-panel discordance distribution. We refer to this quantity as an **empirical source-discordance envelope**. It is not interpreted as a nominal 95% predictive interval, a frequentist alpha = 0.05 test, or a universal threshold across biological questions.

Reference envelopes were frozen before held-out paired discordance was opened. Held-out outcomes were not used to choose taxa, procedures, accessible areas, predictor subsets or a rescue rule.

### Cross-source endpoint

For every evaluable taxon-by-procedure-by-M cell, source discordance was defined as 1 minus Schoener's D between the two predictions on the common comparison frame. A cell was evaluable only if both independently fitted source-specific answers passed adequacy. If either answer failed or was unavailable, the cell remained unresolved.

The independent biological units were the 12 held-out taxa. The 24 within-taxon cells are repeated sensitivity diagnostics and are not treated as independent replicates. The focal taxon-level diagnostic asked whether a held-out taxon contained any evaluable cell exceeding its corresponding frozen procedure-by-M envelope.

All outcome-opening and reference steps were recorded in frozen machine-readable receipts with content hashes and endpoint fingerprints.

## Results

The 12 held-out taxa generated 288 prespecified procedure-by-area diagnostics. Both source-specific answers passed adequacy in 283 cells. Five cells remained unresolved: two for Eucalyptus globulus, two for Larix laricina and one for Nothofagus antarctica. These cells were not recoded as either agreement or disagreement.

None of the 12 held-out taxa contained an empirical-envelope exceedance among its evaluable cells. Thus the taxon-level outcome was **0 of 12 taxa with an exceedance**. Every taxon contributed 22-24 evaluable cells.

The result was not driven solely by extremely permissive envelopes. The closest evaluable cell occurred for Nothofagus betuloides at M = 150 km under the predictive-forward, C = 1, degree-2 procedure. Its observed discordance was 0.38625 and its frozen envelope was 0.39085, a margin of only 0.00460. The observed-to-envelope ratio was 0.988.

Across the 12 taxa, the maximum observed-to-envelope ratio ranged from 0.509 to 0.988. One of 283 evaluable diagnostics was within 0.025 of its envelope, six were within 0.05 and 22 were within 0.10. The complete taxon-level maximum ratios were: Nothofagus betuloides 0.988; Nothofagus antarctica 0.915; Eucalyptus delegatensis 0.895; Eucalyptus globulus 0.882; Abies lasiocarpa 0.865; Laguncularia racemosa 0.751; Avicennia marina 0.647; Encelia farinosa 0.643; Atriplex canescens 0.636; Artemisia tridentata 0.550; Larix laricina 0.540; and Avicennia germinans 0.509.

## Discussion

Independent models built from preserved specimens and human observations produced reproducible same-target distribution predictions across all 12 prospectively held-out taxa under the frozen evaluation design. This is a stronger statement than demonstrating agreement in a dataset used to choose models or thresholds: the held-out taxa, procedure matrix and accessible-area matrix were fixed, and their paired source outcomes remained closed until the source-discordance envelopes had been calibrated elsewhere.

The result is useful precisely because the two data streams are not equivalent. Specimen and human-observation records have different sampling histories and biases, yet those differences did not force the ecological answers outside the empirically calibrated range of cross-source variation for any held-out taxon that could be evaluated. Data provenance can therefore alter the observation process without necessarily destroying reproducibility of the downstream same-target distribution answer.

At the same time, the result should not be converted into a universal source-invariance claim. The independent replication level is 12 taxa, not the 283 evaluable cells. The cells deliberately repeat the comparison across modelling procedures and accessible-area assumptions, so their value is robustness diagnosis rather than additional biological replication. The five unresolved cells also matter: reproducibility was assessed conditional on both source-specific answers meeting adequacy, rather than by treating an inadequate model as a biological disagreement.

The near-boundary Nothofagus betuloides result further constrains interpretation. At least one held-out condition approached its frozen reference ceiling closely. The empirical envelopes therefore did real work; they were not simply so wide that any pair of predictions would have passed. Conversely, the envelope itself is an empirical calibration tied to this same-target design. It should not be exported as a universal tolerance to different taxa, predictor universes, modelling families, life stages or interacting species.

Our test also does not determine why the two sources converged. Shared broad-scale climate signal may dominate source-specific sampling structure after the common target and comparison geometry are fixed, but the present design does not identify that mechanism. Nor does it compare the predictive value of pooled versus separated data, estimate causal effects of observation mode, or establish that every biodiversity data source will behave similarly.

The broader implication is methodological but empirical: reproducibility across biodiversity data streams can be tested as an out-of-taxon generalization problem. Rather than asking whether two sources look similar after analysis choices have been optimized, researchers can freeze the target, source-specific fitting rules, comparison geometry and expected discordance before opening new taxa. In this experiment, independently reconstructed ecological answers survived that test across all 12 held-out taxa.

## Open Research Statement

The analysis contracts, frozen endpoint receipts, audit summaries and reconstruction code are maintained in the public 284b repository. The focal machine-readable evidence is results/product_b_same_target_core19_v0_4_heldout_final_receipt.json and results/reviewer2_level_a_structure_audit_v0_1.json. A permanent archival DOI should be inserted here before submission.

## Acknowledgments and AI disclosure

Author acknowledgments: TODO.

A generative AI system (OpenAI ChatGPT) was used to assist with manuscript organization and drafting from author-controlled repository evidence. The author is responsible for verification, interpretation and final text. This disclosure should be reconciled with the journal's submission-form requirements before submission.

## Literature Cited

Erickson, K. D., and A. B. Smith. 2021. Accounting for imperfect detection in data from museums and herbaria when modeling species distributions: combining and contrasting data-level versus model-level bias correction. Ecography 44:1341-1352. https://doi.org/10.1111/ecog.05679

Gaier, A. G., and J. Resasco. 2023. Does adding community science observations to museum records improve distribution modeling of a rare endemic plant? Ecosphere 14:e4419. https://doi.org/10.1002/ecs2.4419

Guillera-Arroita, G. 2017. Modelling of species distributions, range dynamics and communities under imperfect detection: advances, challenges and opportunities. Ecography 40:281-295. https://doi.org/10.1111/ecog.02445

Matutini, F., J. Baudry, G. Pain, M. Sineau, and J. Pithon. 2021. How citizen science could improve species distribution models and their independent assessment. Ecology and Evolution 11:3028-3039. https://doi.org/10.1002/ece3.7210

Pacifici, K., B. J. Reich, D. A. W. Miller, B. Gardner, G. E. Stauffer, S. Singh, A. McKerrow, and J. A. Collazo. 2017. Integrating multiple data sources in species distribution modeling: a framework for data fusion. Ecology 98:840-850. https://doi.org/10.1002/ecy.1710
