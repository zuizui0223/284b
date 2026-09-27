# Meetnetten source-identity audit v0.1

## Result

The public publisher source code supports a **non-spatial, publisher-defined join candidate** between the amphibian chorus and larvae/metamorph monitoring programmes.

At publisher repository commit `70cf1c1e9a2b3d32be16bfa6ca12bfea4fd6303a`, both event views construct:

- `eventID = INBO:MEETNET:EVENT:<FieldworkSampleID>`;
- `parentEventID = INBO:MEETNET:VISITID:<FieldworkVisitID>`;
- `locationID = INBO:MEETNET:LOCATION:<DimLocation.LocationID>`.

Both views are derived from the same Meetnetten database and join their samples to the same `dbo.DimLocation` table. Therefore exact `locationID` equality has publisher-defined semantics across the two programmes.

This is substantially stronger than matching generalized public coordinates.

## Authorized prospective join

A candidate seasonal join is now frozen as:

```
locationID × scientificName × calendar_year
```

with shared target species restricted initially to:

- `Hyla arborea`
- `Pelobates fuscus`

The raw overlap count is still unopened. The join is **structurally authorized but empirically unevaluated**.

## Forbidden joins

The following are not admissible:

- nearest-coordinate matching;
- overlap of generalized 1/5/10-km grid centroids;
- fuzzy locality-name matching;
- choosing a spatial tolerance after seeing adult/larval correspondence;
- species substitutions or taxonomic pooling selected after seeing the outcome.

## Observation semantics from publisher code/specifications

### Chorus programme

The occurrence extension contains:
- `individualCount`;
- `sex=male` under the specification;
- `lifeStage` including `adult`;
- explicit `occurrenceStatus=present/absent`, generated from count > 0 versus 0.

The protocol counts calling males repeatedly during the breeding season.

Candidate adult breeding index, frozen before raw outcome opening:

> the maximum valid adult-male `individualCount` across chorus visits for a `locationID × species × year`.

The maximum is used to avoid mechanically multiplying the same seasonal breeding population by the number of repeated visits. A missing target-species row is not converted to zero.

### Larvae/metamorph programme

The occurrence extension contains:
- `individualCount`;
- `lifeStage` including `larva` and `metamorph`;
- explicit `occurrenceStatus=present/absent`.

The measurement/fact extension includes:
- number of sweeps;
- maximum depth;
- permanent water column;
- fish present;
- pH;
- shade;
- pond surface;
- water quality;
- sampling effort type.

The publisher describes June–mid-July larval counts as a measure used to determine reproductive success.

Candidate downstream response:
- larval count, retaining number of sweeps as observation effort;
- metamorph count only if raw stage and effort coverage pass an estimability audit.

An observed zero is **not** called biological recruitment failure.

## Ecological question after this audit

The most defensible first paper is no longer “do frogs call but fail to recruit?”

It is:

> **Under what pond conditions does adult breeding effort cease to translate into larval or metamorph production?**

This is an empirical population/reproductive-ecology question. The endpoint is a stage conversion relationship, not a methodological demonstration.

## Raw gate still required

Before fitting the relationship, the public DwC-A exports must establish:

1. the count of exact shared `locationID × species × year` units;
2. repeat chorus visits per shared unit;
3. larva/metamorph stage frequencies;
4. number-of-sweeps coverage;
5. explicit absence versus missing target rows;
6. temporal ordering of chorus and downstream surveys.

No ecological slope or environmental interaction is opened during this gate.
