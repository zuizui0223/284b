# NAAMP chorus synchrony model contract v0.1

Frozen before any weather–synchrony coefficient is calculated.

## Biological endpoint

The primary event is a standardized NAAMP listening stop.

A stop is **multi-species synchronous** when at least two distinct species have publisher-defined positive CallingIndex values (1, 2 or 3) during that same stop survey.

The primary analysis does not treat 10 stops in one route run as 10 independent weather replicates. Instead, each `RunID` is one statistical observation:

- successes = sampled stops with >=2 calling species
- trials = all non-skipped sampled stops in that run

## Primary hypothesis

`DaysSinceRain` is the prospectively selected weather-pulse variable because coverage is 100%.

Primary predictor:

`z(log1p(DaysSinceRain))`

Expected sign: **negative**.

A negative coefficient means that as time since rain increases, the probability of a multi-species chorus decreases; equivalently, recent rain is associated with stronger community synchrony.

## Model

Binomial logit:

`multi_species_stops / sampled_stops ~ rain_z + C(State) + C(RunNumber) + C(RouteType) + year_z`

Uncertainty is cluster-robust by `State × RouteNumber` because routes are surveyed repeatedly.

Support requires:
- negative rain coefficient;
- two-sided p < 0.05;
- 95% cluster-robust CI excluding zero.

Report beta, OR per 1 SD increase in log1p days-since-rain, 95% CI, and p.

## Sensitivities

Run the same frozen model:
1. complete 10-stop runs only;
2. runs with >=8 sampled stops.

They cannot replace the primary result.

## Closed extensions

Temperature stays closed until TempScale conversion semantics are frozen.

Seasonal-shoulder interaction stays closed until RunNumber/protocol semantics are frozen.

Network-edge analyses are secondary and may not select pairs after viewing effects.

No causal weather claim is authorized.
