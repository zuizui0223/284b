# Frog chorus synchrony — standalone empirical programme v1.0

This branch contains a **fresh empirical amphibian programme**, scientifically separate from 284b Paper 1 and from the prospectively closed stage-filtering frog programme.

## Main ecological question

> **Does recent rainfall synchronize breeding calls across frog species, increasing the probability that multiple species call within the same short acoustic observation window?**

The response is community-level **co-calling synchrony**, not species occupancy, demographic recruitment, or acoustic-frequency partitioning.

## Main result — independent support in two acoustic systems

### 1. NAAMP — standardized North American monitoring

USGS North American Amphibian Monitoring Program (DOI `10.5066/F7G44NG0`), 2001–2015.

Primary unit = standardized route-run. Each run contains repeated 5-minute wetland-associated listening stops.

Frozen primary:
- 9,399 runs
- 900 routes
- 93,383 sampled stops
- 41,020 multi-species calling stops
- predictor = `z(log1p DaysSinceRain)`
- beta = **-0.0312**
- OR = **0.969**
- 95% OR CI = **[0.941, 0.998]**
- p = **0.0388**
- frozen support rule = **PASS**

Interpretation: multi-species calling is slightly more common closer to recent rainfall.

The effect is small. The >=8-stop sensitivity passes (p=0.043), whereas the complete-10-stop sensitivity narrowly crosses zero (p=0.058).

### 2. FrogID — independent Australian validation

Expert-validated FrogID call recordings, deterministic outcome-blind 1/16 sample from the pinned public release.

Frozen validation:
- 40,754 recordings
- 18,174 recordings with >=2 calling species
- 1,623 independent ERA5 weather cells
- 13,148 recorders
- rainfall = Earthmover public Icechunk ERA5 hourly total precipitation, aggregated to local calendar days
- response = multi-species vs single-species recording, **conditional on a recording already containing at least one calling frog**
- beta(dryness) = **-0.1592**
- OR = **0.8528**
- 95% OR CI = **[0.8273, 0.8792]**
- p = **1.13e-24**
- frozen support rule = **PASS**
- recorder-cluster sensitivity = **PASS**

The external validation is classified prospectively as **independent_support_robust**.

## Current ecological conclusion

> **Across independent North American and Australian acoustic monitoring systems, frog species are more likely to overlap within the same short calling window closer to recent rainfall.**

The FrogID validation is important because it conditions on an already-active frog recording. Therefore the replicated result cannot be explained solely by rainfall increasing the probability that *any* frog calls.

A defensible interpretation is **weather-triggered community synchrony**: shared environmental cues transiently compress temporal separation among calling species.

## Temperature

NAAMP also shows a strong positive association between ambient temperature and event-level multispecies calling overlap after:
- physical plausibility QC (-10 to 45 °C);
- separate checks within source Celsius and Fahrenheit strata;
- flexible day-of-year adjustment.

This temperature signal has **not** received the independent external validation obtained for rainfall, so rainfall remains the cross-dataset result.

## Prespecified negatives

Two predictions were not supported in NAAMP:

### Seasonal-shoulder amplification
Rain × breeding-season shoulder:
- beta = -0.0462
- p = 0.082
- **not supported**

### Pairwise network densification
Rain effect on co-calling network density:
- beta = -0.00636
- p = 0.724
- repeat-edge sensitivity p = 0.790
- **not supported**

Thus rainfall is not supported as a driver of pairwise network rewiring.

## External validation trail

### Sunshine Coast survey
The biological survey structure was adequate:
- 120 parent surveys
- 121 multi-species call quadrats
- 11 years

But only 63.3% of parent surveys had deterministic registry coordinates, below the frozen 90% weather-link gate. The programme was closed **before** any weather effect was opened.

### FrogID
The current compatible public release passed all structural gates:
- 655,502 recordings
- 291,617 multi-species recordings
- 100% event-time/date/coordinate coverage in the structural audit
- 8 states/territories

A deterministic 1/16 sample was frozen before ERA5 weather values were opened.

## Inference boundaries

Allowed:
- recent rainfall is **associated with** greater short-window multispecies calling overlap;
- the direction receives independent support across NAAMP and FrogID;
- the FrogID result shows the pattern exists conditional on at least one species already calling;
- warmer conditions are associated with greater overlap in NAAMP.

Not allowed:
- rainfall **causes** interspecific synchrony;
- rainfall produces interspecific facilitation;
- rainfall rewires pairwise calling networks;
- the NAAMP and FrogID odds ratios are directly comparable or meta-analytic replicates;
- co-calling implies demographic interaction, competition, or reproductive success.

## Key receipts

- `NAAMP_MODEL_CONTRACT_V0_1.json`
- `NAAMP_PRIMARY_RECEIPT_V0_1.json`
- `NAAMP_SYNTHESIS_RECEIPT_V0_1.json`
- `FROG_SYNTHESIS_CONTRACT_V0_1.json`
- `FROGID_VALIDATION_MODEL_CONTRACT_V0_4.json`
- `FROGID_VALIDATION_RECEIPT_V0_2.json`
- `FROG_CROSS_DATASET_SYNTHESIS_V0_1.json`

## Working title

**Rainfall recency predicts multispecies frog chorus synchrony across continental acoustic monitoring systems**
