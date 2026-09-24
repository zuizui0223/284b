# Frog demographic decoupling — standalone-project incubator v0.2

This branch is an **incubator only** for a new empirical amphibian project. It is scientifically separate from 284b Paper 1 and must not be merged into the Paper 1 claim surface. Protocol v0.2 supersedes v0.1 after a publisher-metadata audit showed that the initially named Natterjack primary system has only 19 public sampling events.

## Ecological question

**Where in the amphibian life cycle does environmental stress first break the link between breeding activity and downstream reproductive success?**

Candidate sequence:

```
adult breeding activity -> eggs -> larvae/tadpoles -> terrestrial juveniles
```

A juvenile-recruitment endpoint is **not guaranteed**. If same-cohort juvenile timing and stage-specific observation are not identifiable, the project will prospectively stop at the richest supported upstream transition rather than call a missing juvenile record recruitment failure.

## Novelty boundary

Greenberg, Zarnoch & Austin (2017, Ecosphere 8:e01789, DOI 10.1002/ecs2.1789) already showed that adult breeding effort, hydroregime and weather can differentially predict juvenile recruitment across six anuran species.

The target here is narrower and more mechanistic:

> **stage-localized demographic decoupling** — identify which explicit life-cycle transition becomes limiting under environmental stress, account for the stage observation process, and require recurrence in an independent standardized monitoring programme before generalizing.

## Primary dataset status

**UNRESOLVED — pending raw structural estimability and join audit.**

We will not choose a primary dataset using transition effect sizes, signs, significance, posterior support or model fit.

Current candidates:

- **Meetnetten chorus counts** — 963 events / 1,436 occurrences; adult breeding activity.
- **Meetnetten larvae & metamorphs** — 697 events / 2,995 occurrences / 3,741 measurement-fact rows; downstream reproductive-success sampling plus pond environment.
- **PINK coastal Flanders** — >1,900 occurrences from 243 ponds and >10 species; repeated within-programme observations of calls, eggs and larvae.
- **Natterjack sightings** — only 19 events / 117 occurrences; full conceptual stage coverage but too small to predeclare as primary.
- **Mohonk Preserve** — long-term hydroclimate validation; juvenile field excluded from same-cohort recruitment unless phenology proves compatibility.
- **CROA** — optional recent external replication.

For the two large Meetnetten programmes, **Hyla arborea** and **Pelobates fuscus** are shared target species. Cross-programme analysis is allowed only if publisher-provided site/event identity or a prospectively frozen deterministic identity bridge can join them. Coordinate-nearest matching is forbidden.

## Candidate hypotheses

**H1 — Stage-localized bottleneck.** Environmental stress does not weaken all stages equally.

**H2 — Hydroperiod mechanism.** Aquatic-habitat persistence and pond state explain the downstream bottleneck.

**H3 — Strategy dependence.** Bottleneck location differs among species with different breeding/development strategies.

**H4 — Recurrence.** Broad amphibian claims require the transition-level pattern to recur in an independent programme.

## What happens next

The next analysis is **estimability only**:

1. inspect raw publisher archives;
2. count site-years and repeat visits;
3. freeze source-specific stage mappings;
4. separate explicit absence from missing and unsurveyed states;
5. test deterministic fixed-site identity across Meetnetten programmes;
6. audit stage timing/cohort compatibility;
7. select the richest identifiable endpoint without viewing ecological effect direction.

See `protocol_v0_2.json` and `DATA_SOURCE_AUDIT_V0_2.md`.

## Working title

**Where the life cycle breaks: stage-specific demographic decoupling across amphibian monitoring programmes**
