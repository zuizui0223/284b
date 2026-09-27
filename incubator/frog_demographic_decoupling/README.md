# Frog demographic decoupling — standalone-project incubator v0.4

This branch is an **incubator only** for a new empirical amphibian project. It is scientifically separate from 284b Paper 1 and must not be merged into the Paper 1 claim surface.

## Ecological question

> **Under what pond conditions does adult breeding effort cease to translate into downstream larval or metamorph production?**

The biological sequence of interest is:

```
calling/breeding adults -> eggs -> larvae -> metamorphs -> juveniles
```

Only the richest transition actually identifiable from the public monitoring data will be analysed. Larvae or metamorphs are **downstream offspring production**, not automatically recruitment into the adult population.

## Focal candidate — same monitoring projects, different life-stage protocols

The strongest design is the pair of standardized Flemish **Meetnetten** programmes.

### Adult breeding activity
**Chorus counts**, DOI `10.15468/d4bu8j`
- current public snapshot: 963 sampling events / 1,436 occurrence rows;
- repeated calling-male counts;
- `Hyla arborea` is target species under publisher ProjectKey **13**;
- `Pelobates fuscus` is target species under publisher ProjectKey **152**.

### Downstream production
**Larvae and metamorph counts**, DOI `10.15468/swgure`
- current public snapshot: 697 events / 2,995 occurrences / 3,741 measurement-or-fact rows;
- explicit `larva` / `metamorph` stages;
- `Hyla arborea` again uses ProjectKey **13**;
- `Pelobates fuscus` again uses ProjectKey **152**;
- observation effort includes number of sweeps;
- pond context includes maximum depth, permanent water column, fish presence, pH, shade, pond surface and water quality.

Thus the candidate comparison links **different protocols within the same species-specific monitoring projects**, rather than combining unrelated datasets post hoc.

## Exact identity contract

At publisher source commit `inbo/meetnetten-occurrences@70cf1c1e9a2b3d32be16bfa6ca12bfea4fd6303a`, both event views derive:

```
locationID = INBO:MEETNET:LOCATION:<DimLocation.LocationID>
eventID = INBO:MEETNET:EVENT:<FieldworkSampleID>
parentEventID = INBO:MEETNET:VISITID:<FieldworkVisitID>
```

The only authorized seasonal linkage is therefore:

```
locationID × scientificName × calendar_year
```

Nearest-coordinate matching, generalized-grid overlap and fuzzy locality matching are forbidden.

The actual raw overlap count is **still unopened**.

See:
- `protocol_v0_4.json`
- `MEETNETTEN_PROGRAMME_IDENTITY_AUDIT_V0_2.md`
- `scripts/audit_meetnetten_join.py`

## Candidate ecological estimand

The first biological relationship is:

> **seasonal adult calling-male abundance -> larval production**

with metamorph production secondary only if its raw sample structure is adequate.

Adult effort is summarized prospectively from repeated chorus visits. Downstream abundance retains number of sweeps as observation effort. Pond state then tests whether the conversion of breeding effort into offspring production changes with environmental context.

An observed downstream zero is an observed survey outcome under a declared effort. It is not automatically total reproductive failure.

## Prospective hypotheses

**H1 — Baseline coupling.** Within species, greater seasonal calling-male abundance is associated with greater larval production when habitat permits successful development.

**H2 — Habitat-dependent conversion.** The adult-to-larva relationship changes with pond conditions rather than being a fixed conversion across sites and years.

**H3 — Stage specificity.** If metamorph data are structurally adequate, habitat effects on adult-to-metamorph conversion can differ from effects on adult-to-larva conversion.

**H4 — Species heterogeneity.** `Hyla arborea` and `Pelobates fuscus` can differ in the habitat conditions that weaken breeding-to-offspring conversion.

**H5 — External recurrence.** Any broad amphibian claim requires recurrence in an independent monitoring programme.

## Prior-art boundary

Greenberg, Zarnoch & Austin (2017, *Ecosphere* 8:e01789, DOI `10.1002/ecs2.1789`) already showed that adult breeding effort, hydroregime and weather can differentially predict juvenile recruitment among anuran species.

Therefore this project does **not** claim to discover that breeding effort can be weakly related to later reproduction.

The prospective novelty is:

> **localize the bottleneck to an explicit life-stage transition, identify the habitat context that changes stage conversion, compare that bottleneck between species, and require independent-programme recurrence before generalizing.**

## Claims currently allowed

- breeding-to-larval production coupling;
- habitat-dependent stage conversion;
- downstream offspring production;
- stage-specific bottleneck.

## Claims currently forbidden

Without additional demographic data, do not claim:
- recruitment into the adult population;
- population persistence;
- demographic ghost populations;
- ecological traps;
- local-extinction early warning.

## Independent validation candidates

- **PINK coastal Flanders** — >1,900 occurrences, 243 ponds, >10 species, repeated within-programme surveys of calls, eggs and larvae.
- **Mohonk Preserve** — long-term hydroclimate validation of adult/egg/larva transitions; juvenile field excluded as same-cohort recruitment unless phenology proves compatibility.
- **Natterjack sightings** — full conceptual stage coverage but only 19 public events / 117 occurrence rows; feasibility example only.
- **CROA** — recent external replication candidate.

## Next unopened gate

Before any adult-to-offspring association or environmental-effect direction is calculated:

1. materialize the current publisher DwC-A event/occurrence tables;
2. count exact shared `locationID × species × year` units;
3. require at least 30 exact shared units;
4. verify at least 20 shared units with >=2 chorus visits;
5. verify at least 20 units with a chorus observation not later than the downstream survey;
6. audit larva versus metamorph frequencies and number-of-sweeps coverage.

`scripts/audit_meetnetten_join.py` performs only this structural audit and deliberately cannot read abundance values or emit the ecological result.

## Working title

**Where the life cycle breaks: habitat-dependent conversion of amphibian breeding effort into offspring production**
