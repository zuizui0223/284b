# Manuscript v0.2

## Title

**Recent rainfall predicts short-window co-calling across frog acoustic communities on two continents**

## Running title

Rainfall and multispecies frog co-calling

## Abstract

Environmental cues can synchronize reproductive behaviour, but rainfall-driven frog chorusing is already well established at species, nightly and seasonal scales. We asked a narrower community-level question: **does recent rainfall increase the probability that multiple frog species are calling within the same short acoustic observation window?** We tested a prospectively specified rain-recency hypothesis in two independent continental monitoring systems. In the North American Amphibian Monitoring Program (NAAMP; 2001–2015), each route-run was the replication unit and the response was the proportion of standardized 5-min stops containing at least two calling species. Across 9,399 runs, 900 routes and 93,383 sampled stops, multispecies co-calling was slightly more common closer to recent rainfall (odds ratio per 1 SD increase in log-transformed days since rain = 0.969, 95% CI 0.941–0.998, p = 0.0388). The direction persisted in a >=8-stop sensitivity, while the complete-10-stop sensitivity narrowly crossed zero. We then tested the same directional prediction in a frozen sample of 40,754 expert-validated Australian FrogID recordings linked prospectively to ERA5 precipitation. Conditional on a recording already containing at least one calling species, the probability of multiple calling species declined strongly with increasing time since rain (odds ratio = 0.853, 95% CI 0.827–0.879, p = 1.13 × 10^-24), with consistent weather-cell and recorder-cluster sensitivities. Post-opening spatial-confounding diagnostics retained the direction using only within-route variation in NAAMP (beta = -0.0137 on the probability scale, p = 2.15 × 10^-5) and within-ERA5-cell variation in FrogID (beta = -0.0426, p = 4.30 × 10^-20). Prespecified tests did not support seasonal-shoulder amplification or rain-driven pairwise network densification. Recent rainfall is therefore associated with greater short-window multispecies co-calling across independent systems, consistent with shared environmental activation that transiently compresses temporal separation at the observation-window scale.

## Introduction

Frog calling is strongly weather dependent. Rainfall and temperature influence calling probability, intensity and seasonal breeding phenology, while local acoustic studies have shown that the number of calling species can vary with weather. Hsu, Kam & Fellers (2006), for example, found that nightly calling-species richness and maximum calling intensity covaried with rainfall and temperature in a Taiwanese subtropical forest. Xie et al. (2017) similarly linked acoustic estimates of community calling activity and species richness to recent rainfall.

Rain can also synchronize the onset of chorusing. Brodie, Allen-Ankins & Schwarzkopf (2025) followed a tropical savanna frog assemblage at three breeding sites over two wet seasons and found that major rainfall events often triggered chorus onset, with explosive breeders frequently chorusing on the night of or immediately after the first major rain. Their result makes an important boundary clear: the novelty of the present study is **not** that rainfall can synchronize frog choruses.

A distinct question remains at a shorter observational scale. When frogs are acoustically active, does a shared rainfall cue alter the probability that **multiple species occupy the same brief calling window**? Seasonal richness, chorus onset and total community calling activity do not answer this directly. Species can respond to the same rain event while remaining temporally separated within a night. Conversely, assemblages can show aggregation at night or minute scales while maintaining avoidance at finer call scales. Allen-Ankins & Schwarzkopf (2021), for example, found broad aggregation at night and minute scales but temporal avoidance at the call scale in a tropical savanna assemblage.

We therefore treat **short-window multispecies co-calling** as a community response in its own right. We first tested a prospectively specified rain-recency prediction in NAAMP, a standardized North American route-stop monitoring programme. We then tested the same directional prediction in an independent Australian FrogID dataset linked to ERA5 precipitation. The FrogID validation was explicitly conditional on a recording already containing at least one calling species, distinguishing multispecies overlap from the simpler possibility that rainfall only increases the probability that any frog calls.

We predicted that (H1) multispecies co-calling would be greater closer to recent rainfall. Prespecified secondary tests asked whether (H2) warmer conditions were associated with greater overlap, (H3) the rain association was amplified at seasonal sampling shoulders, and (H4) rain increased pairwise co-calling network density. The latter two predictions delimit mechanism: a community-level overlap response does not require seasonal-edge amplification or reorganization of particular species-pair associations.

## Methods

### NAAMP data and response

We used the USGS North American Amphibian Monitoring Program data release (DOI 10.5066/F7G44NG0) for the unified-protocol period 2001–2015. NAAMP routes consisted of repeated wetland-associated stops surveyed for five minutes. Calling activity was recorded using the programme's calling index; publisher metadata define CallingIndex 1–3 as positive calling states.

The primary replication unit was a route-run rather than an individual stop. For each eligible run, we counted sampled non-skipped stops and the subset at which at least two distinct species had positive calling indices.

### NAAMP primary rain model

The frozen predictor was z(log1p(DaysSinceRain)). We modelled multispecies-calling stops out of sampled stops using a binomial-logit model with State, RunNumber, RouteType and standardized SurveyYear as fixed adjustments. Standard errors were cluster robust by State × RouteNumber, reflecting repeated runs of the same route.

The directional hypothesis was beta_rain < 0 because larger DaysSinceRain represents less recent rainfall. Support required a negative coefficient, two-sided cluster-robust p < 0.05 and a 95% confidence interval excluding zero. Two prespecified sensitivities used complete 10-stop runs and runs with at least eight sampled stops.

### Independent FrogID validation

We used FrogID (DOI 10.15468/wazqft), an Australian citizen-science dataset of expert-validated frog call recordings. A deterministic outcome-independent 1/16 sample was frozen before external rainfall values were opened. The final validation contained 40,754 recordings, including 18,174 with at least two calling species, from 13,148 recorders and 1,623 0.25-degree ERA5 cells.

The binary response was whether a recording contained one versus multiple expert-validated calling species. Thus every observation was already acoustically positive for at least one frog species.

Hourly ERA5 total precipitation was obtained from the pinned Earthmover public Icechunk archive. Hourly precipitation was aggregated to complete local calendar days. The frozen exposure was the number of consecutive dry days immediately before the recording (<1 mm precipitation per day), capped at 30 and transformed as z(log1p(dry days)). The primary model adjusted for state-by-month, calendar year and cyclic local hour, with standard errors clustered by ERA5 weather cell; recorder clustering was a prespecified sensitivity.

### Spatial-confounding diagnostics

After both cross-system rain effects had been opened, we froze a diagnostic specifically targeting time-invariant spatial confounding.

For NAAMP, we estimated a weighted within-route fixed-effects linear-probability model: the run-level multispecies-stop proportion, rainfall exposure, year and sampling-window indicators were exactly demeaned within route. Inference therefore used only temporal variation among repeated surveys of the same route.

For FrogID, we analogously demeaned the one-versus-multiple-species outcome, frozen dry-spell exposure, month indicators, calendar year and local-hour cyclic terms within each 0.25-degree ERA5 weather cell, with cell-clustered standard errors. These probability-scale diagnostics were not substitutes for the primary logistic estimates and could not upgrade a failed primary result.

### Secondary boundaries

Temperature, seasonal shoulder and pairwise network density were governed by separate frozen secondary contracts. Temperature remained NAAMP-only. The network test froze the pair universe before opening any effect and did not inspect individual edge effects.

### Inference boundaries

All estimates are observational associations. Co-calling does not identify causal rainfall effects, interspecific facilitation, phase synchronization among individual callers, reproductive success or demographic consequences. NAAMP and FrogID differ in observation design and rainfall measurement, so their odds ratios were not meta-analysed.

## Results

### NAAMP rain primary

The primary analysis included 9,399 route-runs from 900 routes, comprising 93,383 sampled stops; 41,020 stops contained at least two calling species. Rainfall recency was associated with a small increase in multispecies co-calling: beta = -0.0312 (cluster-robust SE = 0.0151), equivalent to OR = 0.969 per 1 SD increase in log-transformed days since rain (95% CI 0.941–0.998, p = 0.0388).

The >=8-stop sensitivity retained the frozen support rule (p = 0.0431). The complete-10-stop sensitivity was directionally similar but narrowly crossed zero (p = 0.0580).

### Independent FrogID validation

FrogID strongly supported the frozen directional prediction. Increasing dry-spell duration was associated with a lower probability that an already-active recording contained multiple calling species (beta = -0.1592, OR = 0.853, 95% CI 0.827–0.879, p = 1.13 × 10^-24). The result also passed recorder-clustered inference.

Because the validation was conditional on at least one calling species already being present, this cross-system agreement cannot be reduced to rainfall merely increasing the probability that any frog is acoustically active.

### Within-space robustness

The rain direction also persisted after eliminating all time-invariant differences among the spatial sampling units used in each dataset.

Within 797 repeatedly surveyed NAAMP routes (9,256 runs), greater time since rain remained negatively associated with the multispecies-stop probability (beta = -0.01367, 95% CI -0.01998 to -0.00737, p = 2.15 × 10^-5).

Within 1,071 informative FrogID ERA5 cells (40,020 recordings), the analogous probability-scale association was beta = -0.04265 (95% CI -0.05175 to -0.03354, p = 4.30 × 10^-20).

These diagnostics indicate that static geographic differences in local species pools are insufficient to explain the replicated rain direction.

### Secondary boundaries

The prespecified NAAMP rain × seasonal-shoulder interaction was not supported (beta = -0.0462, p = 0.0820), including the four-window-state sensitivity.

Rain also did not measurably change pairwise co-calling network density conditional on the available species pool in complete 10-stop runs (beta = -0.00636, OR = 0.994, p = 0.724); the repeat-edge sensitivity was similarly null (p = 0.790). Individual edge effects were not opened.

NAAMP showed a strong positive temperature association after documented plausibility and source-scale checks, including a joint weather/day-of-year robustness model, but temperature was not independently validated and remains secondary.

## Discussion

Across independent North American and Australian acoustic monitoring systems, frog species were more likely to occupy the same short calling window closer to recent rainfall. The NAAMP primary effect was small and one route-completeness sensitivity narrowly crossed zero, but the independently designed FrogID validation reproduced the predicted direction with a clearer signal. Crucially, FrogID asked a conditional question: among recordings in which a frog was already calling, were multiple species more likely after recent rain? The answer remained positive in the predicted direction.

This result extends, rather than overturns, prior work on rainfall-driven chorusing. Hsu et al. (2006) and Xie et al. (2017) established community-level associations between rain and calling activity or richness. Brodie et al. (2025) directly showed rainfall-triggered onset and synchrony of chorusing in a tropical savanna assemblage. Our contribution is narrower: rain recency predicts **co-calling within individual short acoustic observations**, and that relationship recurs under two distinct continental sampling systems, including a validation conditioned on acoustic activity already being present.

The within-space diagnostics strengthen this interpretation. The direction persisted when NAAMP comparisons were restricted to temporal variation within the same route and when FrogID comparisons were restricted to temporal variation within the same ERA5 cell. Thus the replicated pattern is not readily attributable to the static fact that wetter regions or routes may simply contain richer frog assemblages. These fixed-effects diagnostics do not, however, remove time-varying local confounding, and neither dataset identifies a causal rainfall effect.

The term synchrony should also be interpreted at the scale actually measured. We identify increased **short-window co-calling overlap**, not millisecond-scale phase locking or coordinated responses among individual callers. Earlier work shows that frog assemblages can be aggregated at night or minute scales while preserving avoidance at finer call scales. Rainfall may therefore place more species inside the same active acoustic window without eliminating spectral or sub-minute partitioning.

Two prespecified negative results constrain mechanism. Rainfall did not detectably strengthen co-calling at seasonal shoulders, and it did not densify the pairwise co-calling network. The community signal is therefore better characterized as shared environmental activation than as evidence that rainfall reorganizes particular species-pair relationships. No evidence here supports interspecific facilitation.

The contrast between monitoring systems is also informative. NAAMP uses standardized route-stop sampling and yielded a small association. FrogID is opportunistic but expert validated and offers a stricter conditional outcome. Agreement in direction across those designs, plus within-space persistence in both systems, supports the generality of the association without implying that their effect sizes estimate the same population parameter.

Several limitations remain. Rainfall was not randomized. NAAMP DaysSinceRain and ERA5-derived FrogID antecedent dry days are related but nonidentical exposures. FrogID submission behaviour can vary with weather even after recorder clustering and cell fixed effects. Detection of an additional quiet species may itself vary with chorus intensity. Temperature has only NAAMP support. Finally, short-window co-calling is a behavioural observation and does not demonstrate reproductive success or population consequences.

The broader implication is that temporal niche structure can be environmentally elastic. Species can retain characteristic breeding seasons and call-partitioning mechanisms while shared weather cues transiently increase their overlap at short behavioural timescales. Environmental pulses may therefore compress community temporal separation without requiring detectable pairwise network rewiring.

## References — core set

- Allen-Ankins S, Schwarzkopf L. 2021. Spectral overlap and temporal avoidance in a tropical savannah frog community. *Animal Behaviour* 180:1–11. DOI 10.1016/j.anbehav.2021.07.024.
- Allen-Ankins S, Schwarzkopf L. 2022. Using citizen science to test for acoustic niche partitioning in frogs. *Scientific Reports* 12:2447. DOI 10.1038/s41598-022-06396-0.
- Brodie S, Allen-Ankins S, Schwarzkopf L. 2025. Environmental influences on chorusing patterns in an Australian tropical savanna frog community. *Ecosphere* 16:e70153. DOI 10.1002/ecs2.70153.
- Hsu M-Y, Kam Y-C, Fellers GM. 2006. Temporal organization of an anuran acoustic community in a Taiwanese subtropical forest. *Journal of Zoology* 269:331–339. DOI 10.1111/j.1469-7998.2006.00044.x.
- Xie J, Towsey M, Zhu M, Zhang J, Roe P. 2017. An intelligent system for estimating frog community calling activity and species richness. *Ecological Indicators* 82:13–22. DOI 10.1016/j.ecolind.2017.06.015.

## Current claim boundary

**Supported:** more recent rainfall is associated with greater short-window multispecies co-calling, independently supported in NAAMP and FrogID and directionally retained in within-route and within-weather-cell analyses.

**Not supported:** seasonal-shoulder amplification; rain-driven pairwise network densification.

**Secondary only:** warmer conditions are associated with greater co-calling overlap in NAAMP.

**Not authorized:** rainfall causation, first-ever rainfall synchrony, interspecific facilitation, pairwise network rewiring, phase synchronization, demographic effects, reproductive-success effects, or meta-analysis of the two odds ratios.
