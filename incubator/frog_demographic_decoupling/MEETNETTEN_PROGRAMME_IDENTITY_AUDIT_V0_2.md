# Meetnetten programme-identity audit v0.2

This note supersedes the narrower source-identity audit v0.1. No adult-to-offspring outcome value was opened.

## Same monitoring projects on both sides

The publisher's public SQL defines target-species status using the same internal project keys in both the chorus and larvae/metamorph occurrence views:

| Species | Chorus ProjectKey | Larvae/metamorph ProjectKey |
|---|---:|---:|
| *Hyla arborea* | 13 | 13 |
| *Pelobates fuscus* | 152 | 152 |

The protocols differ, as they should:

- chorus: ProtocolID 5/33;
- larvae/metamorphs: ProtocolID 25/32.

Both event views derive `locationID` from the same `dbo.DimLocation.LocationID`, and both serialize the identity as `INBO:MEETNET:LOCATION:<six digits>`.

This means the candidate design is not a spatial post-hoc merger. It is a prospective linkage of **different life-stage protocols within the same species-specific monitoring project and publisher identity system**.

## Frozen analysis identity

Candidate unit:

```
locationID × scientificName × calendar_year
```

Only `Hyla arborea` and `Pelobates fuscus` are admitted initially because both are target species on both protocol sides under the same project identity.

## Adult side

For both species the publisher states that calling males are counted in reproductive habitat at least twice per year.

Candidate seasonal breeding-effort summary:

```
max(valid calling-male individualCount)
```

within the candidate unit.

This is fixed before opening adult-downstream associations. It avoids treating repeat visits as separate populations or summing the same males repeatedly.

## Downstream side

The larvae/metamorph protocol explicitly uses larval counting to determine reproductive success. The public measurement extension provides number of sweeps plus pond-context variables.

Primary downstream stage is prospectively `larva`. `metamorph` is secondary and opens only if its raw sample structure is adequate.

An observed count of zero is an observed survey outcome, not proof of total reproductive failure.

## Core ecological interpretation

If adult calling abundance predicts larval production similarly everywhere, there is little evidence for habitat-dependent decoupling.

If the adult-to-larva relationship changes systematically with pond conditions, the result supports a **stage-specific habitat filter on conversion of breeding effort into offspring production**.

This is the current biological claim target.

## Claims not authorized by these data alone

- recruitment into the adult population;
- local population persistence;
- an ecological trap;
- a pre-extinction early-warning signal;
- causal effects of pond management without an appropriate identification design.

## Next unopened quantity

The next permitted value is the number of exact shared `locationID × species × year` units and their repeat-visit/temporal-order structure.

Adult counts, larval counts, their correlation and environmental-effect directions remain closed during that audit.
