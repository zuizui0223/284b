# RMNP reproductive-state model contract v0.2

## Question

> **Among site-years where adult boreal chorus frogs are confirmed, what habitat conditions determine whether egg/larval stages are also present?**

This is not a re-analysis of overall occupancy. Kissel et al. (2025) already analysed occupancy, colonization and persistence in these RMNP data. The endpoint here is **reproductive-stage occupancy conditional on confirmed adult-stage evidence**.

## Why *Pseudacris maculata*

The choice was made from stage-coverage structure only:

- *Pseudacris maculata*: Adult stage recorded in 77 post-2002 site-years.
- *Lithobates sylvaticus*: 7.
- *Ambystoma mavortium*: 12.

No adult→offspring association or environmental effect was inspected. Wood frog and tiger salamander cannot replace Pseudacris later because they yield a more interesting result.

## Reproductive endpoint

Positive = stage code contains **E or L**.

Juvenile (J) and metamorph (M) are deliberately excluded even though juvenile structural coverage is high. This prevents widening the endpoint after seeing stage availability.

A site-year enters the confirmatory analysis only if adult stage A is observed at least once.

## Observation model

Repeated visits estimate detection of E/L.

- `psma=0`: valid non-detection.
- `psma=1` with E/L: positive.
- `psma=1` with A but no E/L: valid non-detection.
- `psma=1` with only J/M/U/NA stage: unresolved for this endpoint.
- `psma=NA`: no observation.

Detection depends prospectively on day-of-year (linear + quadratic) and percent surveyed.

## Process hypotheses

Primary: **shallow wetland** (first valid annual max depth <=1 m) lowers `P(E/L state | adult confirmed)`.

Secondary: fish presence lowers the same probability.

Year and site area are prespecified adjustments. Water/air temperature, weather and wind are not promoted to process drivers after seeing results.

## Hard estimability gate

Before fitting:

- >=50 adult-confirmed site-years;
- >=30 adult-confirmed site-years with >=2 valid reproductive-stage observation visits;
- >=15 reproductive-positive adult-confirmed site-years.

If this fails, the confirmatory RMNP analysis stops. Thresholds will not be relaxed.

## Claims

Allowed: habitat-dependent reproductive-stage occupancy / decoupling among adult-confirmed wetlands.

Not allowed: recruitment into the adult population, population growth, ecological trap, causal management effect, or extinction early warning.
