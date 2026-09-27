# Manuscript v0.1

## Title

**Recent rainfall predicts short-window synchrony in frog acoustic communities across continents**

## Running title

Rainfall and frog chorus synchrony

## Abstract

Environmental cues can synchronize reproductive behaviour, but most evidence linking weather to frog calling has been species-specific or local. We tested whether rainfall recency predicts short-window overlap in calling activity across species, using two independent continental-scale acoustic monitoring systems. In the North American Amphibian Monitoring Program (NAAMP; 2001–2015), we prospectively defined each route-run as the replication unit and modelled the proportion of standardized 5-minute stops containing at least two calling species. Across 9,399 runs, 900 routes and 93,383 sampled stops, multispecies calling was slightly more common closer to recent rainfall (odds ratio per 1 SD increase in log-transformed days since rain = 0.969, 95% CI 0.941–0.998, p = 0.0388). The direction persisted in a >=8-stop sensitivity, while the complete-10-stop sensitivity narrowly crossed zero. We then tested the same directional hypothesis in an independent deterministic sample of 40,754 expert-validated Australian FrogID recordings linked prospectively to ERA5 rainfall. Conditional on a recording already containing at least one calling species, the probability of multiple calling species declined strongly with increasing time since rain (odds ratio = 0.853, 95% CI 0.827–0.879, p = 1.13 × 10^-24), with consistent weather-cell and recorder-cluster sensitivities. A prespecified NAAMP test found no rain-associated pairwise network densification, and seasonal-shoulder amplification was unsupported. These results indicate that recent rainfall is associated with transient compression of temporal separation among calling frog species at short observation scales, consistent with shared environmental activation rather than pairwise network rewiring.

## Introduction

Reproductive acoustic behaviour in frogs is tightly linked to environmental conditions. Rainfall, temperature and photoperiod can alter calling probability, calling intensity and seasonal phenology, and local acoustic studies have repeatedly shown that the number of calling species can vary with weather. Hsu, Kam & Fellers (2006), for example, found that calling-species richness and maximum calling intensity covaried with rainfall and temperature in a Taiwanese subtropical forest. Xie et al. (2017) similarly linked acoustic estimates of frog community activity and species richness to recent rainfall in a local sensor study.

These results establish that weather can alter community-level acoustic activity, but they leave a distinct question unresolved: **does a shared environmental cue alter the temporal overlap of species within the same short acoustic observation window?** This distinction matters because greater seasonal richness or overall calling intensity need not imply greater simultaneous overlap. Species can respond to the same weather while remaining temporally segregated, and fine-scale temporal avoidance may persist even when calling activity is aggregated at nightly or minute scales. Studies of acoustic niche partitioning illustrate this scale dependence. Allen-Ankins & Schwarzkopf (2021) found broad aggregation of calling at night and minute scales but evidence of avoidance at finer call scales, while their continental FrogID analysis showed stronger spectral than temporal partitioning among co-occurring species.

We therefore treat **multispecies short-window co-calling** as a community response in its own right. We asked whether recent rainfall is associated with an increased probability that multiple frog species are acoustically active within the same short standardized observation. We first tested a prospectively specified rain-recency hypothesis in NAAMP, a standardized North American monitoring programme. We then tested the same directional prediction in an independent Australian FrogID dataset linked to external ERA5 precipitation, with the validation conditioned on recordings that already contained at least one calling species. This conditioning distinguishes multispecies overlap from the simpler possibility that rain only increases the chance that any frog is heard.

We predicted that (H1) multispecies calling overlap would be greater closer to recent rainfall. Prespecified secondary analyses asked whether (H2) warmer conditions were associated with greater overlap, (H3) the rainfall association was amplified at seasonal sampling shoulders, and (H4) rain increased pairwise co-calling network density. The last two predictions provide mechanistic boundaries: a community-level synchrony response need not imply seasonal-edge amplification or pairwise network rewiring.

## Methods

### NAAMP data

We used the USGS North American Amphibian Monitoring Program data release (DOI 10.5066/F7G44NG0) for the unified-protocol period 2001–2015. NAAMP routes consisted of repeated wetland-associated listening stops surveyed for five minutes. Calling activity was recorded using the programme's calling index. Publisher metadata define CallingIndex values 1–3 as positive calling states.

The primary observational unit was a standardized route-run, not an individual stop. For each run, we counted sampled non-skipped stops and the subset of stops at which at least two distinct frog species had positive calling indices.

### NAAMP primary rainfall model

The predictor was days since rain, transformed as z(log1p(DaysSinceRain)) across eligible runs. We modelled the number of multispecies-calling stops out of sampled stops using a binomial-logit model with State, RunNumber, RouteType and standardized SurveyYear as fixed adjustments. Standard errors were cluster-robust by State × RouteNumber to account for repeated runs of the same route.

The directional hypothesis was beta_rain < 0 because larger DaysSinceRain represents less recent rainfall. Support required a negative coefficient, two-sided cluster-robust p < 0.05 and a 95% confidence interval excluding zero. Two prespecified sensitivities used complete 10-stop runs and runs with at least eight sampled stops.

### NAAMP secondary analyses

Temperature was summarized as mean run-level AirTemp after source-unit conversion and later subjected to a prospectively documented physical plausibility check. The seasonal-shoulder test defined shoulder runs structurally from state-specific sampling windows before opening the interaction. Pairwise network density was tested under a separately frozen pair universe and did not inspect individual edge effects.

### FrogID independent validation

We used FrogID v6 (DOI 10.15468/wazqft), an Australian citizen-science dataset of expert-validated frog call recordings. A deterministic outcome-blind 1/16 sample was frozen before external rainfall values were opened. The final validation contained 40,754 recordings, 18,174 with at least two calling species, 13,148 recorders and 1,623 0.25-degree ERA5 weather cells.

The response was whether an expert-validated recording contained multiple calling species versus one calling species. Thus the validation was explicitly conditional on at least one calling species already being present in the recording.

Hourly ERA5 total precipitation was obtained from the pinned Earthmover public Icechunk source and aggregated to local calendar days. The frozen rainfall predictor was a standardized log-transformed dry-days measure. Standard errors were clustered by ERA5 weather cell, with recorder clustering as a prespecified sensitivity. No NAAMP effect size was used to tune the FrogID model.

### Inference boundaries

All results are observational associations. We did not interpret co-calling as demographic interaction, reproductive success, interspecific facilitation or causal behavioural coordination. NAAMP and FrogID use different observation designs and rainfall measurements, so their odds ratios were not meta-analysed.

## Results

### NAAMP rainfall primary

The primary NAAMP analysis included 9,399 route-runs from 900 routes, comprising 93,383 sampled stops; 41,020 stops contained at least two positively calling species. The rain-recency coefficient was negative (beta = -0.0312, cluster-robust SE = 0.0151), corresponding to an odds ratio of 0.969 per 1 SD increase in log-transformed days since rain (95% CI 0.941–0.998, p = 0.0388). Thus multispecies calling was slightly more common closer to recent rainfall.

The >=8-stop sensitivity supported the same directional rule (p = 0.0431). The complete-10-stop sensitivity was directionally similar but its confidence interval narrowly crossed zero (p = 0.0580).

### Independent FrogID validation

The FrogID validation strongly supported the frozen directional prediction. Increasing rainfall dryness was associated with a lower probability that an already-active recording contained multiple calling species (beta = -0.1592, OR = 0.853, 95% CI 0.827–0.879, p = 1.13 × 10^-24). The result persisted when clustering by recorder rather than weather cell.

Because all recordings in this analysis already contained at least one calling species, this validation shows that the replicated rain association is not explained solely by rainfall increasing the probability of any frog acoustic activity.

### Prespecified secondary boundaries

The NAAMP rain × seasonal-shoulder interaction was not supported (beta = -0.0462, p = 0.0820), and the four-window-state sensitivity was also null.

Rainfall also did not measurably change pairwise co-calling network density conditional on the species pool in complete 10-stop runs (beta = -0.00636, OR = 0.994, p = 0.724); the repeat-edge sensitivity was similarly null (p = 0.790). Individual edge effects were not opened.

NAAMP showed a strong positive temperature association after physical plausibility filtering and within both original source temperature scales, but this temperature result has not received the independent validation obtained for rainfall and is therefore treated as secondary.

## Discussion

Across two independent continental acoustic monitoring systems, frog species were more likely to overlap within the same short calling window closer to recent rainfall. The NAAMP effect was small and only marginally robust across its two prespecified route-completeness sensitivities, but the independently designed FrogID analysis reproduced the predicted direction with a substantially clearer signal. Most importantly, the FrogID validation was conditioned on recordings that already contained a calling frog. The replicated pattern therefore cannot be reduced to the familiar observation that rainfall simply activates frog calling.

We interpret the cross-dataset result as **weather-triggered community synchrony**: a shared environmental cue is associated with transient compression of temporal separation among calling species. This framing extends earlier local work linking rainfall to calling-species richness and community activity. Hsu et al. (2006) showed that nightly calling richness tracked rainfall and temperature, and Xie et al. (2017) identified lagged rainfall relationships with community calling activity and species richness. Our contribution is to show that rainfall recency predicts overlap at the scale of individual short acoustic observations and that the directional association recurs in independent North American and Australian monitoring systems.

The result also clarifies the relationship between environmental activation and acoustic niche partitioning. Previous work has shown that frog assemblages can be broadly aggregated at night or minute scales while maintaining avoidance at finer call scales. Our response operates at the observation-window scale and therefore does not imply that species cease fine-scale call avoidance. Instead, rainfall may increase the probability that multiple species enter the same active acoustic window while spectral or sub-minute partitioning remains intact.

Two negative results constrain mechanism. First, the rainfall association was not stronger at the prespecified seasonal shoulders. Second, rainfall did not densify the pairwise co-calling network conditional on the available species pool. The community signal is therefore better described as shared activation than as evidence that rainfall reorganizes specific species-pair relationships. This distinction also prevents interpreting the pattern as interspecific facilitation.

The contrast between NAAMP and FrogID is informative. NAAMP uses a standardized route-stop design and produced a small effect after adjustment for state, sampling window, route type and year. FrogID is opportunistic but expert validated, and its conditional response asks a stricter question: given that at least one frog is already calling, is the recording more likely to contain multiple calling species after recent rain? Agreement across these distinct observation systems increases confidence in the direction of the community-level association, even though the effect sizes are not directly comparable.

Several limitations remain. Neither dataset randomizes rainfall, so causal claims are unwarranted. NAAMP's rainfall variable and FrogID's ERA5-derived dry-days predictor differ in construction. Short-window co-calling is not equivalent to direct behavioural synchronization among individuals, nor does it imply competition, facilitation or reproductive success. Finally, independent validation currently exists for rainfall but not for the strong NAAMP temperature association.

The broader implication is that temporal niche structure can be environmentally elastic. Species may retain characteristic seasonal and acoustic niches while shared weather cues transiently increase their overlap. At sufficiently short behavioural timescales, stochastic environmental pulses may therefore compress community temporal structure without rewiring the underlying pairwise network.

## References — core set

- Allen-Ankins S, Schwarzkopf L. 2021. Spectral overlap and temporal avoidance in a tropical savannah frog community. *Animal Behaviour* 180:1–11. DOI 10.1016/j.anbehav.2021.07.024.
- Allen-Ankins S, Schwarzkopf L. 2022. Using citizen science to test for acoustic niche partitioning in frogs. *Scientific Reports* 12:2447. DOI 10.1038/s41598-022-06396-0.
- Hsu M-Y, Kam Y-C, Fellers GM. 2006. Temporal organization of an anuran acoustic community in a Taiwanese subtropical forest. *Journal of Zoology* 269:331–339. DOI 10.1111/j.1469-7998.2006.00044.x.
- Xie J, Towsey M, Zhu M, Zhang J, Roe P. 2017. An intelligent system for estimating frog community calling activity and species richness. *Ecological Indicators* 82:13–22. DOI 10.1016/j.ecolind.2017.06.015.

## Current claim boundary

**Supported:** recent rainfall is associated with greater short-window multispecies calling overlap, independently supported in NAAMP and FrogID.

**Not supported:** seasonal-shoulder amplification; rain-driven pairwise network densification.

**Secondary only:** warmer conditions are associated with greater co-calling overlap in NAAMP.

**Not authorized:** causation, interspecific facilitation, demographic effects, reproductive-success effects, or meta-analysis of the two odds ratios.
