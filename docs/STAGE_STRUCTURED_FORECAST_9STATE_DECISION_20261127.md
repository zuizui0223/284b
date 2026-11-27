# Stage-structured FIA forecast: completed 9-state exploratory decision

2026-11-27. The three-census protocol was frozen before this outcome was opened. Run [45941515338](https://github.com/zuizui0223/284b/actions/runs/45941515338) completed successfully in all three regions at aa05ca19e0a3e0073be5ee97e22db7cb2432b68f. All 37 distinct FIA/WorldClim input SHA-256 values match the prior regional studies; all three output archives were separately retrieved, verified against their Actions SHA-256 and CRC, and their primary and stable-subset mean squared errors independently reconstructed from aggregated held-out block loss sums. Original M1/M2 invited submission and earlier regional analysis remain unchanged.

## Primary results

4,544 unique eligible three-census physical plots, 17,860 species-plot records and 106 distinct FIA species codes across nine states; 3,099 plots had stable adult composition over t0→t1 (total variation ≤0.10), 1,445 had already changed more. Model scores use held-out spatial blocks, equal plot weight, centered five-year change in log adult-size stem counts with +0.5 offset among the fixed t1 species set; same evaluation rows for paired model comparisons. Regional training and evaluation use the same FIA network, not independent data collection. A: adult history/structure baseline; S: +current early/late sapling stock; H: +sapling history. Positive percentages mean reduced held-out MSE.

| Region | Plots | Species codes | A→S (%) | A→H (%) | S→H (%) |
|---|---:|---:|---:|---:|---:|
| Northeast | 1045 | 44 | 6.143 [4.107,7.625] | 5.980 [3.755,7.684] | -0.173 [-0.416,0.069] |
| Appalachia | 1342 | 87 | 3.051 [1.447,4.522] | 2.951 [1.308,4.539] | -0.103 [-0.427,0.207] |
| Great Lakes | 2157 | 66 | 3.277 [1.922,4.587] | 3.604 [2.350,4.818] | 0.339 [0.003,0.634] |

Conditional 500-resample spatial block bootstrap 95% intervals in brackets. Stock improved over A in all regions; prior sapling change history adds no consistent gain beyond stock. Adult-only A also improves over persistence (zero centered change) in all three full panels.

## Distinguish an advance warning from tracking already ongoing change

Stable subset was prespecified (adult count composition total variation ≤0.10 over t0→t1). After inspecting outcomes, the complementary changing subset and the changing-minus-stable performance contrast were calculated from verified aggregated test loss sums. Jointly resample spatial blocks within region (2000 fixed-seed draws) across both strata, conditional on the existing out-of-fold predictions. This is a retrospective descriptive contrast, NOT a new prospective test, fitted interaction or causal effect.

| Region | Stable n | A→S stable (%) | Changing n | A→S changing (%) | Changing minus stable (percentage points, conditional 95% interval) |
|---|---:|---:|---:|---:|---:|
| Northeast | 721 | 3.584 | 324 | 9.675 | 6.091 [1.502,10.589] |
| Appalachia | 971 | 1.377 | 371 | 5.277 | 3.901 [0.302,7.640] |
| Great Lakes | 1407 | 0.158 | 750 | 6.537 | 6.379 [4.063,8.650] |

All three absolute MSE reduction differences are also positive: 0.004752 [0.002042,0.007635], 0.003668 [0.001363,0.006022], 0.007002 [0.004610,0.009453]. Nevertheless, outcome variance, sample structure, baseline difficulty and unmeasured disturbance can differ across strata; absolute loss differences do not establish a biological mechanism. Only northeast stable subset has a clear conditional gain; two other stable-subset intervals contain zero. The original strong hidden-replacement claim is therefore **not geographically established**. The candidate new ecological question is the context dependence of size-structured leading information: juveniles track ongoing compositional change more reliably than provide a universal early warning of change in previously stable forests.

## Mechanistic restrictions and climate result

| Region | A→S after removing identified sapling→adult crossings (%) | A→S for explicitly linked baseline adult dead/removed fraction (%) | H→HC climate stage mismatch increment (%) |
|---|---:|---:|---:|
| Northeast | 4.179 [2.622,5.571] | -0.104 [-0.263,0.064] | -0.135 [-0.285,-0.031] |
| Appalachia | 2.301 [1.064,3.378] | 0.039 [-0.088,0.168] | -0.018 [-0.047,0.005] |
| Great Lakes | 2.158 [1.078,3.167] | -0.069 [-0.134,-0.014] | 0.014 [-0.063,0.108] |

Linked adult loss endpoints use only explicit complete species-plot link sets, not missing links coded as deaths. 133,280 of 134,061 baseline eligible adult-sized stems have explicit later status (sum across regions); 1,194 direct promotions identified among eligible species. Removing identified promotions is incomplete because sapling microplots sample a smaller area than adult subplots; unobserved ingrowth remains. The results do not show mortality prediction, universal climate-stage niche effects, climate change causation, competition or full recruitment mediation. Operational diameter size groups are not reproductive maturity classes. Stronger late-stage coefficients alone are not novel, and stage-specific prediction is already studied in forestry (e.g. https://doi.org/10.1016/j.ecolind.2022.109654; recent US FIA demography https://doi.org/10.1111/gcb.71124). 

## Decision and next discriminating test

The primary stock forecast improvement is a genuine geographic recurrence in this exploratory analysis, but not an independent confirmatory endpoint (increment 0). Do not promote a generic saplings-predict-adults finding or a universal early warning. The next test should distinguish an actual demographic lag from dependence on forecast difficulty/measurement: hold model, stage bins and stability threshold fixed; use new states outside these nine, compare forecast horizons from four linked censuses where available, and test whether juvenile stock adds value under matched adult baseline error/abundance/size and prior turnover. Mechanism requires explicit recruitment/survival decomposition and later independent climate exposures if climate is invoked. No outcomes from new states have been accessed here.

Machine-readable receipt: results/stage_structured_fia_forecast_v1.json. Protocol: docs/STAGE_STRUCTURED_FORECAST_PROTOCOL_20261127.md. SHA-pinned archives: northeast 15173380970; Appalachia 15172457838; Great Lakes 15172427983. Post-outcome audit: scripts/audit_stage_structured_forecast_stability_v1.py.
