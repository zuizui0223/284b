# Meetnetten structural receipt v0.1

This receipt records only source structure. No calling-male abundance, larval abundance, adult→offspring association, or environmental-effect direction was opened.

## Fixed source versions

- Chorus: DOI `10.15468/d4bu8j`, version 1.27, SHA-256 `686c5a7aacc8f49e41a0642ecaa9efd8c3564304b0a4d4b027f3df2debec69fd`.
- Larvae/metamorphs: DOI `10.15468/swgure`, version 1.24, SHA-256 `c2cc960122ea398545edb661318160cd2b5b66a75a73dba8f7a3f61bd9c4f920`.

## Exact publisher-identity overlap

- exact shared `locationID × species × year`: **247**
- *Hyla arborea*: **245**
- *Pelobates fuscus*: **2**
- shared units with >=2 chorus events: **233**
- shared units with at least one chorus event not later than downstream survey: **247**

### Downstream structural rows

- *Hyla arborea* larva: 448
- *Hyla arborea* metamorph: 229
- *Pelobates fuscus* larva: 4
- *Pelobates fuscus* metamorph: 2

## Decision

**Hyla arborea passes the identity/replication/time-order part of the structural gate.**

**Pelobates fuscus fails prospectively as a focal species** because only 2 exact shared location-species-years exist. It cannot be rescued later because its result looks interesting.

The overall Meetnetten gate is not yet open because the first audit found **0 shared units with non-empty `number of sweeps` metadata**. This is treated as a measurement-schema problem, not as permission to ignore effort.

The next audit is allowed to inspect:
- MeasurementOrFact row types;
- measurementType labels;
- whether measurementValue is populated;
- event-level coverage of those labels.

It remains forbidden to inspect abundance values or ecological associations during that repair.

## Current ecological scope

The prospective focal system is now **Hyla arborea only**. A two-species comparison is no longer part of the confirmatory target unless an independent, prospectively new dataset supplies a separate validation role; *Pelobates fuscus* cannot be reinstated in this Meetnetten analysis.
