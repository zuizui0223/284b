# Frog demographic decoupling — standalone-project incubator v0.1

This branch is an **incubator only** for a new empirical amphibian project. It is scientifically separate from 284b Paper 1 and must not be merged into the Paper 1 claim surface. The intended next step is extraction to a dedicated repository once the raw-data gates below are passed.

## Core ecological question

**Where in the amphibian life cycle does environmental stress first break the link between breeding activity and successful recruitment?**

We treat the life cycle as a sequence of stage transitions rather than a binary presence/absence problem:

```
adult breeding activity -> eggs -> larvae/tadpoles -> terrestrial juveniles
```

The project is not intended to show merely that adult breeding effort and recruitment can be weakly associated. That antecedent already exists. Greenberg, Zarnoch & Austin (2017, Ecosphere 8:e01789, DOI 10.1002/ecs2.1789) analysed 22 years at eight wetlands and showed that breeding effort, hydroregime and weather can differentially predict juvenile recruitment across six anuran species.

The new target is **stage-localized demographic decoupling**: estimate which transition fails, under what environmental conditions, and whether the same transition-level signature recurs in independent standardized monitoring programmes.

## Data roles

### Primary full-chain system — Flanders Natterjack toad
- Dataset: Meetnetten.be — Sightings for Natterjack toad in Flanders, Belgium.
- DOI: 10.15468/2xfw8y.
- Period: 2016–2023.
- Standardized design: three nocturnal visits per site/year.
- Recorded life stages: egg strings, tadpoles, terrestrial juveniles <2 cm, terrestrial juveniles >2 cm, adults observed, adults heard/calling males.
- Role: primary full-chain `adult -> egg -> larva -> juvenile` analysis.

### Independent multi-species stage validation — PINK coastal Flanders
- Dataset: PINK — Amphibia monitoring for the permanent surveillance of coastal areas in Flanders, Belgium.
- DOI: 10.15468/jvtefa.
- Period: 2007–2016.
- Scope: 243 ponds, >10 species, repeated pond visits.
- Protocol includes calling adults plus egg/larval observations.
- Role: multi-species validation of upstream transition decoupling. Juvenile recruitment is not assumed available.

### Independent standardized Flanders networks
- Chorus counts for Amphibia: DOI 10.15468/d4bu8j.
- Larvae and metamorph counts for Amphibia: DOI 10.15468/swgure.
- Role: supplementary cross-programme validation if fixed-site identities and time units can be joined without reconstruction ambiguity.

### Long-term hydroclimate validation — Mohonk Preserve
- Dataset DOI: 10.15468/dypfbs.
- Data paper: Garretson et al. 2020, DOI 10.3897/BDJ.8.e50121.
- 11 vernal pools, 1931–2020; consistent monitoring from 1991 onward.
- Fields include chorus code/count, adults, amplectant pairs, egg masses, tadpoles/larvae, juveniles and paired environmental measurements.
- **Boundary:** sampling is concentrated in spring, so current-year juvenile recruitment is not assumed identifiable. Mohonk is provisionally limited to `adult/call -> egg -> larva` and hydroclimate effects unless raw timing proves otherwise.

### Optional contemporary urban replication — CROA, southern France
- Dataset DOI: 10.15468/xfz3uy.
- Since 2023, up to three visits/grid/year.
- Records adult, juvenile, egg mass, tadpole and calling behaviour.
- Role: external replication only after adequate temporal depth and stage counts are demonstrated.

## Primary estimands

For site `s`, year `t`, stage `k`, define latent seasonal occurrence `Z[s,t,k]`.

Primary transition parameters:
- `T_AE = P(Egg=1 | AdultBreeding=1)`
- `T_EL = P(Larva=1 | Egg=1)`
- `T_LJ = P(Juvenile=1 | Larva=1)`

Primary decoupling metric:
- `D_AJ = 1 - P(Juvenile=1 | AdultBreeding=1)`

No observed zero is automatically interpreted as a biological failure. Stage-specific observation/detection is modelled from repeated visits and date/phenology where estimable.

## Hypotheses

**H1 — Stage-localized decoupling.**
Transition probabilities are not equally sensitive to environmental stress; at least one downstream transition weakens more strongly than the upstream adult-to-egg transition.

**H2 — Hydroclimate modulation.**
Dry/warm conditions and reduced aquatic-habitat persistence reduce downstream transition probabilities, with the strongest effect expected on aquatic-development-to-juvenile recruitment where full-chain data permit that endpoint.

**H3 — Reproductive-strategy heterogeneity.**
The location and strength of the bottleneck differ among species or programmes with different breeding and larval-development strategies.

**H4 — Cross-programme recurrence.**
A transition-level signature observed in the primary Natterjack system must recur in at least one independent monitoring programme before any broad amphibian-general claim is made.

## Hard gates before outcome analysis

1. Preserve raw sampling-event identity and visit date.
2. Demonstrate repeat visits within site-year.
3. Quantify stage-specific positive counts before fitting any decoupling model.
4. Require explicit stage coding; do not infer life stage from free text unless a frozen mapping is documented.
5. Separate structural absence, explicit `absent`, missing record and missing survey.
6. Do not classify recruitment failure until a stage-specific detection model is estimable.
7. Mohonk juvenile counts are excluded from the primary recruitment endpoint unless cohort timing can be shown to match the same breeding cycle.
8. Any cross-dataset join must use publisher-provided site/event identifiers or a prospectively frozen deterministic mapping. No coordinate-nearest rescue.
9. Environmental covariates must be defined before outcome-based model selection.
10. Greenberg et al. 2017 is treated as prior art; novelty cannot be “breeding effort does not always predict recruitment.”

## First decision after raw-data import

The first raw-data task is an **estimability audit**, not hypothesis testing. The audit reports:
- number of sites and site-years;
- visits per site-year;
- positive detections per stage;
- explicit absences vs missing rows;
- overlap of stages within site-year;
- date distribution of each stage;
- candidate stage-specific detection replication.

Only after this audit passes will the confirmatory model be frozen.

## Working title

**Where the life cycle breaks: stage-specific demographic decoupling across amphibian monitoring programmes**

