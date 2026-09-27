# Reviewer attack matrix v0.2 — frog chorus synchrony

## Current status

The programme has independent NAAMP + FrogID support and now passes the predeclared
spatial-confounding diagnostic in both systems.

| Attack | Current answer | Status |
|---|---|---|
| Rainfall effects on frog calling are old. | Agreed. Novelty is short-window multispecies overlap, conditional validation and independent cross-continental replication. | Addressed |
| Brodie et al. 2025 already showed chorus synchrony after rain. | Agreed for rainfall-triggered chorus onset/nightly chorusing. We explicitly position the new contribution at the same-short-observation-window co-calling scale. | Addressed in manuscript v0.2 |
| “Synchrony” overstates what is measured. | Preferred operational wording is **short-window co-calling overlap**; “synchrony” is restricted to the observation-window scale. | Addressed |
| NAAMP effect is small/borderline. | Report exactly: OR=0.969, p=.0388; >=8-stop passes, complete-10-stop p=.058. Independent FrogID and within-route results provide replication/robustness, not effect-size inflation. | Addressed |
| Static spatial species-pool differences explain everything. | NAAMP within-route beta=-.01367, p=2.15e-5; FrogID within-cell beta=-.04265, p=4.30e-20. Both CIs exclude zero. | **Addressed: spatially robust** |
| FrogID simply captures rain causing any frog to call. | FrogID sample is conditional on >=1 calling species; response is one vs multiple species. | Major strength |
| FrogID is opportunistic. | Expert validation, deterministic outcome-blind sample, weather-cell and recorder clustering, state/month/year/hour adjustments, plus within-cell diagnostic. Submission behaviour remains a limitation. | Qualified |
| Rainfall reorganizes pairwise interactions. | Frozen network-density test is null (p=.724; repeat-edge p=.790); no individual edge effects opened. | Rejected |
| Rain effect is strongest at seasonal shoulders. | Frozen interaction null (p=.082; four-window sensitivity null). | Rejected |
| Temperature is the real driver. | Rain persists in joint NAAMP weather/DOY robustness and validates independently in FrogID. Temperature remains NAAMP-only secondary. | Qualified |
| NAAMP and FrogID effects should be meta-analysed. | Forbidden: response conditioning, observation units and rainfall metrics differ. Directional replication only. | Addressed |
| This is causal evidence. | No. Within-space fixed effects remove static spatial differences but not time-varying confounding. | Hard boundary |
| Co-calling implies facilitation or reproductive success. | No. Event-level overlap is behavioural activity only. | Hard boundary |

## Strongest reviewer-safe claim

> Across independent North American and Australian monitoring systems, recent rainfall is associated with increased short-window multispecies frog co-calling. The direction persists within repeatedly sampled routes and within fixed ERA5 weather cells, and in FrogID it remains after conditioning on a frog already being acoustically active.

## Mechanistic interpretation

The data are most consistent with **shared environmental activation** at the observation-window scale.
They do not identify interspecific facilitation, pairwise network rewiring, sub-second phase synchronization,
or demographic effects.
