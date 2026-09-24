# Frog chorus synchrony — standalone empirical incubator v0.1

This branch starts a **fresh empirical programme** after the previous stage-resolved frog programme was prospectively closed. It is not a rescue, retuning, or continuation of the failed fish × reproductive-stage hypothesis.

## Ecological question

> **Do short-term weather pulses synchronize breeding activity across frog species, temporarily compressing temporal niche partitioning within local choruses?**

The biological object is a **standardized calling assemblage** observed during one listening event, not species occupancy, recruitment, or life-stage conversion.

## Primary data source

North American Amphibian Monitoring Program (NAAMP), USGS data release:
- DOI: `10.5066/F7G44NG0`
- ScienceBase item: `583dc314e4b0d1899f9dea8d`
- standardized core era: **2001–2015**
- design: fixed routes, 10 wetland-associated stops, 5-minute listening surveys, repeated seasonal sampling periods, local survey conditions recorded.

The programme covered much of the eastern and central United States under a unified protocol.

## Why this is a new question

Prior NAAMP work estimated occupancy and occupancy trends. Frog phenology studies have tested species-specific calling responses to temperature/rainfall, and FrogID has been used to test calling phenology, co-occurrence, and acoustic niche partitioning.

This programme instead asks whether **weather changes the number and composition of species calling together during the same standardized observation window**.

The target is therefore dynamic community synchrony, not:
- occupancy trend;
- species-specific first calling date;
- stage-specific reproductive filtering;
- acoustic-frequency partitioning.

## Prospective hypotheses

**H1 — Pulse synchrony.**
Warm/wet survey conditions increase within-event calling-species richness relative to otherwise comparable survey events.

**H2 — Rainfall compression.**
Recent rainfall produces a stronger increase in co-calling richness than temperature alone where rainfall metadata are available under the NAAMP protocol.

**H3 — Seasonal-position dependence.**
The synchronizing effect of weather is strongest near the shoulders of the local breeding season, when normally staggered species can be pulled into the same calling window.

**H4 — Community reconfiguration.**
Weather pulses change not only richness but also the topology of event-level co-calling networks: species pairs that rarely call together under ordinary conditions become temporarily connected.

## Hard boundaries

- One event = one standardized stop-level listening period when that identity is recoverable.
- Multiple species in the same event are direct co-calling evidence.
- A species absent from an event is **not** automatically a biological absence unless the source table/protocol makes non-detection interpretable for that event.
- No causal climate claim is authorized from observational weather associations.
- No species pair, region, or weather variable may be chosen because it gives the strongest effect.
- No reuse of the previous frog programme's opened outcomes.

## First gate

Before any weather–synchrony association is opened, perform a structural audit only:
1. inventory immutable/raw USGS files;
2. identify route/stop/survey/date identity;
3. identify species and call-index fields;
4. identify weather/temperature/rain/wind fields;
5. count standardized 2001–2015 survey events;
6. count events with at least two species records only as an estimability quantity;
7. freeze one event key and one primary weather variable family.

No regression coefficient or effect direction is opened during this gate.

## Working title

**Weather pulses compress temporal niches in frog breeding communities**
