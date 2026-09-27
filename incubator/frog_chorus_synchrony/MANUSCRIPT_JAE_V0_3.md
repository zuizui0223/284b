# Recent rainfall predicts greater short-window co-calling in frog communities across continents

## Abstract

1. **Environmental cues can align animal activity, but community temporal niches need not be fixed.** Rainfall-driven frog calling is well established at species and seasonal scales. We tested whether recent rainfall is also associated with greater overlap among species within the same short acoustic observation window.

2. **We used two independent continental monitoring systems under prospectively specified analysis rules.** In the North American Amphibian Monitoring Program (NAAMP), the response was the proportion of standardized 5-min route stops containing at least two calling species. We independently validated the directional prediction in expert-verified Australian FrogID recordings linked to ERA5 precipitation, conditional on a recording already containing at least one calling species.

3. **Recent rainfall predicted greater short-window multispecies co-calling in both systems.** Across 9,399 NAAMP runs and 93,383 sampled stops, co-calling declined weakly with increasing time since rain (odds ratio per 1 SD increase in log-transformed days since rain = 0.969, 95% CI 0.941–0.998). In 40,754 FrogID recordings, increasing antecedent dry-spell duration likewise reduced the odds of multiple calling species (odds ratio = 0.853, 95% CI 0.827–0.879).

4. **The direction persisted when static spatial differences were removed.** Within-route NAAMP analysis remained negative (β = -0.0137 on the probability scale, 95% CI -0.0200 to -0.00737), as did within-ERA5-cell FrogID analysis (β = -0.0426, 95% CI -0.0518 to -0.0335). Prespecified analyses did not support stronger rainfall effects at seasonal shoulders or rainfall-driven pairwise network densification.

5. **These results show that community temporal structure can be environmentally elastic at short timescales.** Shared rainfall cues are associated with transiently greater overlap in species’ reproductive acoustic activity across independent systems, without evidence that particular species-pair relationships are reorganized. The observational design supports shared environmental activation, not a causal rainfall effect or interspecific facilitation.

## Keywords

acoustic community; anurans; ecoacoustics; environmental cue; rainfall; synchrony; temporal niche; weather

## Introduction

Animal communities are organized not only in space and by resource use but also in time. Temporal niche partitioning can reduce interference among species, yet activity schedules are also plastic responses to environmental conditions. Short-lived environmental pulses may therefore change the degree to which species occupy the same behavioural window even when their broader seasonal niches remain distinct.

Frog acoustic communities provide a strong system in which to test this idea because calling is tightly linked to weather and reproductive activity. Rainfall and temperature influence calling probability, intensity and seasonal breeding phenology, while local acoustic studies have shown that calling-species richness can vary with weather. Hsu, Kam and Fellers (2006), for example, found that nightly calling-species richness and maximum calling intensity covaried with rainfall and temperature in a Taiwanese subtropical forest. Xie et al. (2017) similarly linked community calling activity and species richness to recent rainfall.

Rain can also synchronize chorus onset. Brodie, Allen-Ankins and Schwarzkopf (2025) followed a tropical savanna frog assemblage at three breeding sites over two wet seasons and found that major rainfall events often triggered chorus onset, with explosive breeders frequently chorusing on the night of or immediately after the first major rain. The novelty of the present study is therefore not that rainfall can stimulate frog calling or synchronize seasonal chorus onset.

A distinct question remains at a shorter observational scale: **when frogs are acoustically active, does a shared rainfall cue alter the probability that multiple species occupy the same brief calling window?** Seasonal richness, chorus onset and total community activity do not answer this directly. Species can respond to the same rain event while remaining temporally separated within a night. Conversely, assemblages can aggregate at night or minute scales while maintaining avoidance at finer call scales. Allen-Ankins and Schwarzkopf (2021), for example, found broad aggregation at night and minute scales but temporal avoidance at the call scale in a tropical savanna assemblage. FrogID analyses have likewise demonstrated acoustic niche structure among co-calling species (Allen-Ankins & Schwarzkopf, 2022).

We therefore treat **short-window multispecies co-calling** as a community response in its own right. We first tested a prospectively specified rain-recency prediction in the North American Amphibian Monitoring Program (NAAMP), a standardized route-stop monitoring programme. We then tested the same directional prediction in an independent Australian FrogID dataset linked prospectively to ERA5 precipitation. The FrogID validation was explicitly conditional on a recording already containing at least one calling species, separating multispecies overlap from the simpler possibility that rainfall only increases the probability that any frog calls.

We predicted that (H1) multispecies co-calling would be greater closer to recent rainfall. Prespecified secondary tests asked whether (H2) warmer conditions were associated with greater overlap, (H3) the rain association was amplified at seasonal sampling shoulders and (H4) rain increased pairwise co-calling network density. The latter two hypotheses constrain interpretation: a community-level overlap response need not imply seasonal-edge amplification or reorganization of particular species-pair associations.

## Materials and Methods

### NAAMP data and standardized acoustic response

We used the USGS North American Amphibian Monitoring Program data release for the eastern and central United States (Foreman, Grant, & Weir, 2017; DOI 10.5066/F7G44NG0). We restricted the analysis to the unified-protocol period 2001–2015. NAAMP routes comprised repeated wetland-associated stops surveyed acoustically for 5 min. Publisher metadata define CallingIndex values 1–3 as positive calling states.

The primary replication unit was a route-run rather than an individual stop. For each eligible run, we counted sampled non-skipped stops and the subset at which at least two distinct species had positive calling indices. This run-level binomial response avoids treating the approximately 10 stops within a route-run as independent biological replicates.

### NAAMP rain model

Before opening the rainfall association, we froze the predictor as z[log(1 + DaysSinceRain)]. We modelled multispecies-calling stops out of sampled stops using a binomial-logit model with State, RunNumber, RouteType and standardized SurveyYear as fixed adjustments. Standard errors were cluster-robust by State × RouteNumber to account for repeated runs of the same route.

The directional hypothesis was β_rain < 0 because larger DaysSinceRain represents less recent rainfall. Support required a negative coefficient, two-sided cluster-robust P < 0.05 and a 95% confidence interval excluding zero. Two prespecified sensitivities used complete 10-stop runs and runs with at least eight sampled stops.

### FrogID independent validation

FrogID is an Australian citizen-science programme in which smartphone recordings of calling frogs are reviewed by expert validators (Rowley et al., 2019; Rowley & Callaghan, 2020). We used FrogID version 6.0 (Australian Museum, 2025; DOI 10.15468/wazqft). FrogID records are presence-only calling records, and a single submission event can contain more than one expert-validated species (Rowley & Callaghan, 2020).

A deterministic outcome-independent 1/16 sample was frozen before external rainfall values were opened. The final validation contained 40,754 recordings, including 18,174 with at least two calling species, from 13,148 recorders and 1,623 0.25° ERA5 cells.

The binary response was whether a recording contained one versus multiple expert-validated calling species. Every analysed recording was therefore already acoustically positive for at least one frog species.

### ERA5 rainfall linkage

We linked FrogID recording events prospectively to ERA5 precipitation. ERA5 is a global atmospheric reanalysis with hourly output (Hersbach et al., 2020). Hourly total precipitation was aggregated to complete local calendar days. The frozen exposure was the number of consecutive dry days immediately before each recording, defining a dry day as <1 mm precipitation, capped at 30 days and transformed as z[log(1 + dry days)].

The FrogID primary model adjusted for state-by-month, calendar year and cyclic local hour. Standard errors were clustered by ERA5 weather cell; clustering by recorder was a prespecified sensitivity. Because the rainfall metrics differ between NAAMP and FrogID, their odds ratios were treated as directional replication rather than pooled or meta-analysed.

### Spatial-confounding diagnostics

After both cross-system rain effects had been opened, we froze a diagnostic targeted specifically at time-invariant spatial confounding.

For NAAMP, we estimated a weighted within-route fixed-effects linear-probability diagnostic in which run-level multispecies-stop proportion, rainfall exposure, year and sampling-window indicators were exactly demeaned within route. The coefficient therefore used only temporal weather variation among repeated surveys of the same route.

For FrogID, we analogously demeaned the one-versus-multiple-species outcome, frozen dry-spell exposure, month indicators, calendar year and local-hour cyclic terms within each 0.25° ERA5 weather cell. Standard errors were clustered by cell. These probability-scale diagnostics were robustness analyses, not replacements for the primary logistic estimates.

### Secondary analyses and mechanistic boundaries

Temperature, seasonal shoulder and pairwise network density were governed by separate frozen secondary contracts. NAAMP temperature data underwent source-scale and physical-plausibility checks before interpretation; the resulting association remains NAAMP-only and was not independently validated.

For the network analysis, the species-pair universe was frozen before any rain effect was opened. The analysis tested whether rain changed pairwise co-calling density conditional on the available species pool; individual edge effects were not opened.

### Ethics and inference boundaries

This study is a secondary analysis of previously collected, publicly released acoustic-monitoring and citizen-science records. We conducted no new animal capture, handling or field sampling.

All estimates are observational associations. Co-calling does not identify causal rainfall effects, interspecific facilitation, fine-scale phase synchronization among individual callers, reproductive success or demographic consequences.

## Results

### NAAMP rain primary

The primary analysis included 9,399 route-runs from 900 routes, comprising 93,383 sampled stops; 41,020 stops contained at least two calling species. Rainfall recency was associated with a small increase in multispecies co-calling: β = -0.0312 (cluster-robust SE = 0.0151), equivalent to an odds ratio of 0.969 per 1 SD increase in log-transformed days since rain (95% CI 0.941–0.998, P = 0.0388; Fig. 2a).

The ≥8-stop sensitivity retained the frozen support rule (P = 0.0431). The complete-10-stop sensitivity was directionally similar but narrowly crossed zero (P = 0.0580).

### Independent FrogID validation

FrogID independently supported the frozen directional prediction. Increasing antecedent dry-spell duration was associated with a lower probability that an already-active recording contained multiple calling species (β = -0.1592, odds ratio = 0.853, 95% CI 0.827–0.879, P = 1.13 × 10^-24; Fig. 2a). The result also passed recorder-clustered inference.

Because the validation was conditional on at least one calling species already being present, this cross-system agreement cannot be reduced to rainfall merely increasing the probability that any frog is acoustically active.

### Within-space robustness

The rain direction persisted when estimates were derived from temporal variation within the same spatial sampling units (Fig. 2b).

Within 797 repeatedly surveyed NAAMP routes (9,256 runs), greater time since rain remained negatively associated with multispecies-stop probability (β = -0.01367, 95% CI -0.01998 to -0.00737, P = 2.15 × 10^-5).

Within 1,071 informative FrogID ERA5 cells (40,020 recordings), the analogous probability-scale association was β = -0.04265 (95% CI -0.05175 to -0.03354, P = 4.30 × 10^-20).

These diagnostics show that static geographic differences in local species pools are insufficient to explain the replicated rain direction, while leaving time-varying local confounding unresolved.

### Secondary boundaries

The prespecified NAAMP rain × seasonal-shoulder interaction was not supported (β = -0.0462, P = 0.0820), including the four-window-state sensitivity.

Rain also did not measurably change pairwise co-calling network density conditional on the available species pool in complete 10-stop runs (β = -0.00636, odds ratio = 0.994, P = 0.724); the repeat-edge sensitivity was similarly null (P = 0.790). Individual edge effects were not opened.

After documented physical-plausibility filtering and source-scale checks, NAAMP retained a strong positive association between temperature and multispecies overlap (odds ratio = 1.474, 95% CI 1.397–1.556, P = 9.62 × 10^-46). The temperature association was positive within both original Celsius- and Fahrenheit-coded subsets. Because temperature was not independently validated, it remains a secondary result.

## Discussion

Across independent North American and Australian acoustic monitoring systems, frog species were more likely to occupy the same short calling window closer to recent rainfall. The NAAMP primary effect was small and one route-completeness sensitivity narrowly crossed zero, but the independently designed FrogID validation reproduced the predicted direction with a clearer signal. Crucially, FrogID asked a conditional question: among recordings in which a frog was already calling, were multiple species more likely after recent rain? The predicted association remained.

This result extends, rather than overturns, prior work on rainfall-driven chorusing. Hsu et al. (2006) and Xie et al. (2017) established community-level associations between rain and calling activity or richness. Brodie et al. (2025) directly showed rainfall-triggered onset and synchrony of chorusing in a tropical savanna assemblage. Our contribution is narrower: rain recency predicts **co-calling within individual short acoustic observations**, and that relationship recurs under two distinct continental sampling systems, including a validation conditioned on acoustic activity already being present.

The within-space diagnostics strengthen this interpretation. The direction persisted when NAAMP comparisons were restricted to temporal variation within the same route and when FrogID comparisons were restricted to temporal variation within the same ERA5 cell. The replicated pattern is therefore not readily attributable to the static fact that wetter regions or routes may simply contain richer frog assemblages. These fixed-effects diagnostics do not remove time-varying local confounding, however, and neither dataset identifies a causal rainfall effect.

The term synchrony should be interpreted at the scale actually measured. We identify increased **short-window co-calling overlap**, not millisecond-scale phase locking or coordinated responses among individual callers. Earlier work shows that frog assemblages can be aggregated at night or minute scales while preserving avoidance at finer call scales (Allen-Ankins & Schwarzkopf, 2021). Rainfall may therefore place more species inside the same active acoustic window without eliminating spectral or sub-minute partitioning.

Two prespecified negative results constrain mechanism. Rainfall did not detectably strengthen co-calling at seasonal shoulders, and it did not densify the pairwise co-calling network. The community signal is therefore better characterized as shared environmental activation than as evidence that rainfall reorganizes particular species-pair relationships. No evidence here supports interspecific facilitation.

The contrast between monitoring systems is also informative. NAAMP uses standardized route-stop sampling and yielded a small association. FrogID is opportunistic but expert validated and offers a stricter conditional outcome. Agreement in direction across those designs, plus within-space persistence in both systems, supports the generality of the association without implying that their effect sizes estimate the same population parameter.

Several limitations remain. Rainfall was not randomized. NAAMP DaysSinceRain and ERA5-derived FrogID antecedent dry days are related but nonidentical exposures. FrogID submission behaviour can vary with weather even after recorder clustering and cell fixed effects. Detection of an additional quiet species may itself vary with chorus intensity. Temperature has only NAAMP support. Finally, short-window co-calling is a behavioural observation and does not demonstrate reproductive success or population consequences.

The broader implication is that temporal niche structure can be environmentally elastic. Species can retain characteristic breeding seasons and call-partitioning mechanisms while shared weather cues transiently increase their overlap at short behavioural timescales. Environmental pulses may therefore compress community temporal separation without requiring detectable pairwise network rewiring.

## Data Availability

NAAMP source data are publicly available from the U.S. Geological Survey data release (Foreman et al., 2017; DOI 10.5066/F7G44NG0). FrogID version 6.0 is publicly available as an Australian Museum occurrence dataset (DOI 10.15468/wazqft). ERA5 is documented by Hersbach et al. (2020).

The standalone analysis repository will preserve the exact source digests, frozen analysis contracts, derived non-sensitive weather linkage, result receipts and figure-generation code. We intend to archive that repository on Zenodo for the submitted version and will insert the resulting DOI before final submission.

## References

Allen-Ankins, S., & Schwarzkopf, L. (2021). Spectral overlap and temporal avoidance in a tropical savannah frog community. *Animal Behaviour*, 180, 1–11. https://doi.org/10.1016/j.anbehav.2021.07.024

Allen-Ankins, S., & Schwarzkopf, L. (2022). Using citizen science to test for acoustic niche partitioning in frogs. *Scientific Reports*, 12, 2447. https://doi.org/10.1038/s41598-022-06396-0

Australian Museum. (2025). FrogID [Occurrence dataset, version 6.0]. https://doi.org/10.15468/wazqft

Brodie, S., Allen-Ankins, S., & Schwarzkopf, L. (2025). Environmental influences on chorusing patterns in an Australian tropical savanna frog community. *Ecosphere*, 16, e70153. https://doi.org/10.1002/ecs2.70153

Foreman, T., Grant, E. H., & Weir, L. A. (2017). *North American Amphibian Monitoring Program (NAAMP) anuran detection data from the eastern and central United States (1994–2015)* [Data release]. U.S. Geological Survey. https://doi.org/10.5066/F7G44NG0

Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., Nicolas, J., Peubey, C., Radu, R., Schepers, D., Simmons, A., Soci, C., Abdalla, S., Abellan, X., Balsamo, G., Bechtold, P., Biavati, G., Bidlot, J., Bonavita, M., … Thépaut, J.-N. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society*, 146, 1999–2049. https://doi.org/10.1002/qj.3803

Hsu, M.-Y., Kam, Y.-C., & Fellers, G. M. (2006). Temporal organization of an anuran acoustic community in a Taiwanese subtropical forest. *Journal of Zoology*, 269, 331–339. https://doi.org/10.1111/j.1469-7998.2006.00044.x

Rowley, J. J. L., Callaghan, C. T., Cutajar, T., Portway, C., Potter, K., Mahony, S., Trembath, D. F., Flemons, P., & Woods, A. (2019). FrogID: Citizen scientists provide validated biodiversity data on frogs of Australia. *Herpetological Conservation and Biology*, 14, 155–170.

Rowley, J. J. L., & Callaghan, C. T. (2020). The FrogID dataset: expert-validated occurrence records of Australia’s frogs collected by citizen scientists. *ZooKeys*, 912, 139–151. https://doi.org/10.3897/zookeys.912.38253

Xie, J., Towsey, M., Zhu, M., Zhang, J., & Roe, P. (2017). An intelligent system for estimating frog community calling activity and species richness. *Ecological Indicators*, 82, 13–22. https://doi.org/10.1016/j.ecolind.2017.06.015

## Figure legends

**Figure 1. Independent acoustic systems test the same short-window co-calling prediction.** NAAMP provides standardized 5-min North American route-stop surveys in which recent-rainfall exposure predicts the proportion of sampled stops containing at least two calling species. FrogID provides independent Australian expert-validated short recordings linked to ERA5 precipitation; its outcome is one versus multiple calling species conditional on at least one species already calling. The systems are interpreted as directional replication rather than pooled effect estimates. Spatial robustness is assessed using temporal variation within NAAMP routes and within FrogID ERA5 cells. Neither analysis identifies a causal rainfall effect.

**Figure 2. Rain-recency associations replicate across systems and persist within spatial units.** (a) Primary logistic associations shown separately because NAAMP uses programme-reported days since rain whereas FrogID uses ERA5 antecedent dry days. Points are odds ratios per 1 SD increase in the respective dryness exposure with 95% confidence intervals: NAAMP 0.969 (0.941–0.998) and FrogID 0.853 (0.827–0.879). (b) Probability-scale fixed-spatial-unit diagnostics: NAAMP within-route β = -0.01367 (95% CI -0.01998 to -0.00737) and FrogID within-ERA5-cell β = -0.04265 (95% CI -0.05175 to -0.03354). Negative values indicate greater short-window multispecies co-calling closer to recent rainfall. These are observational associations, not causal estimates.
