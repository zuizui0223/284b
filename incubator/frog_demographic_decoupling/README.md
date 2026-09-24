# Frog demographic decoupling — standalone-project incubator v0.3

This branch is an **incubator only** for a new empirical amphibian project. It is scientifically separate from 284b Paper 1 and must not be merged into the Paper 1 claim surface.

## Ecological question

> **Under what habitat conditions does adult breeding effort cease to translate into downstream offspring production?**

The intended biological sequence is:

```
calling/breeding adults -> eggs -> larvae -> metamorphs -> juveniles
```

The project will analyse only the richest stage transition that the public monitoring data actually identify. It will not call a larval or metamorph record “recruitment to the adult population.”

## Current strongest candidate

The strongest candidate is now the pair of standardized Flemish **Meetnetten** programmes, not the tiny Natterjack full-chain dataset.

### Adult breeding activity
**Chorus counts**, DOI `10.15468/d4bu8j`
- 963 sampling events;
- 1,436 occurrence rows;
- repeated calling-male counts;
- target species include `Hyla arborea` and `Pelobates fuscus`.

### Downstream production
**Larvae and metamorph counts**, DOI `10.15468/swgure`
- 697 sampling events;
- 2,995 occurrence rows;
- 3,741 measurement/fact rows;
- explicit larva/metamorph stages;
- number of sweeps plus pond depth, permanence, fish, pH, shade, surface and water-quality measurements;
- target species include the same `Hyla arborea` and `Pelobates fuscus`.

## Exact join — no spatial matching

The publisher's public source repository shows that both datasets derive `locationID` from the same Meetnetten `DimLocation.LocationID` and serialize it as:

```
INBO:MEETNET:LOCATION:<six digits>
```

Therefore the only authorized cross-programme join candidate is exact:

```
locationID × scientificName × calendar_year
```

Nearest coordinates, generalized-grid overlap and fuzzy locality names are forbidden. The **number of actual shared site-years has not yet been opened**.

Shared target species are frozen prospectively to:

- `Hyla arborea`
- `Pelobates fuscus`

See `MEETNETTEN_SOURCE_IDENTITY_AUDIT_V0_1.md` and `protocol_v0_3.json`.

## Candidate ecological estimand

The first candidate relationship is:

> seasonal adult breeding effort -> larval/metamorph production

Adult effort will be summarized from repeated valid chorus visits; downstream abundance retains sampling effort (number of sweeps). Pond state then tests whether the conversion of adult breeding effort into offspring production changes with environmental context.

This is **not** an absence test. An observed downstream zero remains an observed zero under a known sampling effort unless a later observation model justifies a stronger state.

## Prior-art boundary

Greenberg, Zarnoch & Austin (2017, Ecosphere 8:e01789, DOI 10.1002/ecs2.1789) already showed that adult breeding effort, hydroregime and weather can differentially predict juvenile recruitment among anuran species.

The new target is therefore not “breeding effort sometimes fails to predict recruitment.” It is:

> **localize the demographic bottleneck to an explicit life-stage transition, identify the habitat context that changes stage conversion, and require recurrence in an independent monitoring programme before generalizing.**

## Independent validation candidates

- **PINK coastal Flanders** — >1,900 occurrences, 243 ponds, >10 species, repeated within-programme surveys that listen for adults and search for eggs/larvae.
- **Mohonk Preserve** — long-term hydroclimate validation of upstream adult/egg/larva transitions; juvenile field not used as same-cohort recruitment without phenology proof.
- **Natterjack sightings** — full conceptual stage coverage but only 19 public events / 117 occurrence rows; feasibility example only.
- **CROA** — recent external replication candidate.

## Next gate

No adult-downstream association is open yet. First:

1. materialize the current publisher DwC-A tables;
2. count exact shared `locationID × species × year` units;
3. verify repeated chorus visits and downstream temporal ordering;
4. audit larva versus metamorph frequencies;
5. quantify number-of-sweeps coverage;
6. only then freeze and fit the biological model.

`scripts/audit_meetnetten_join.py` performs this join audit without reading counts or computing an ecological association.

## Working title

**Where the life cycle breaks: habitat-dependent conversion of amphibian breeding effort into offspring production**
