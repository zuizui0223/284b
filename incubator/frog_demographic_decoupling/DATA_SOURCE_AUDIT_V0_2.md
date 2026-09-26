# Public-data source audit v0.2 — primary reset before outcome opening

## Decision

**No dataset is currently designated primary.** Protocol v0.1 prematurely labelled the Flanders Natterjack sighting dataset as the primary full-chain system based on stage coverage. Current publisher metadata show that this dataset contains only **19 sampling events and 117 occurrence rows**, so that designation is withdrawn before any demographic-coupling outcome is opened.

Primary-system selection is now an estimability decision, not a biological-result decision.

## Current candidate inventory

| Candidate | Current public scale | Stage information | Authorized role now |
|---|---:|---|---|
| Meetnetten chorus counts | 963 events; 1,436 occurrences | calling males/adult breeding activity | large upstream candidate |
| Meetnetten larvae/metamorph counts | 697 events; 2,995 occurrences; 3,741 measurement/fact rows | larvae / reproductive-success protocol + pond environment | large downstream candidate |
| PINK coastal Flanders | >1,900 occurrences; 243 ponds; >10 species | calls + eggs + larvae during repeated pond visits | large within-programme multi-species candidate |
| Natterjack sightings | 19 events; 117 occurrences | adults/calls + egg strings + tadpoles + terrestrial juveniles | small full-chain feasibility/calibration only |
| Mohonk Preserve | 11 pools; long time series | calls/adults + eggs + larvae + juvenile field | long-term upstream + hydroclimate validation; juvenile cohort unresolved |
| CROA southern France | since 2023 | adult + egg + tadpole + juvenile + calls | optional external replication |

## Why the large Meetnetten pair is promising

The chorus dataset is explicitly a fixed-location standardized monitoring network for **Hyla arborea**, **Epidalea calamita** and **Pelobates fuscus**.

The larvae/metamorph dataset is also fixed-location standardized monitoring and targets **Triturus cristatus**, **Hyla arborea** and **Pelobates fuscus**. It has 697 events and 2,995 occurrence rows plus 3,741 measurement/fact rows. The publisher states that June–mid-July larvae counts are used to determine reproductive success, and records pond properties such as maximum depth, fish presence, shading, surface area, permanent water column and water quality.

Therefore **Hyla arborea** and **Pelobates fuscus** are prospectively interesting shared taxa for an adult-breeding -> larval-success analysis.

But no cross-programme biological relation is opened yet. A valid join requires publisher-provided compatible fixed-site/event identities or a deterministic identity bridge frozen before transition outcomes are inspected. Generalized coordinates are not sufficient for nearest-neighbour joining.

## Why PINK may be even cleaner

PINK contains >1,900 occurrences from 243 ponds across >10 species. Each pond is visited in three periods. During visits observers listen for calling adults and search for larvae or eggs; the second visit also uses a scoop net for larvae and the third June visit uses the net.

Because adult calling, egg and larval evidence occur inside one monitoring programme, PINK can avoid a cross-programme join for the upstream life-cycle question.

The raw Darwin Core fields must still show that stage/detection information is encoded with enough fidelity to reconstruct the declared stages without free-text improvisation.

## Natterjack is retained, but not rescued

The Natterjack sighting dataset remains scientifically useful because its protocol contains the entire conceptual sequence from calling/observed adults through egg strings and tadpoles to terrestrial juveniles. However, the current public dataset has only 19 events. It is therefore retained only as a small full-chain feasibility/calibration system. It cannot become primary unless a future prospectively identified release materially expands the sampling frame; an unfavourable result elsewhere cannot trigger such a rescue.

## Mohonk boundary

Mohonk remains valuable for long-term hydroclimate variation and upstream adult/call -> egg -> larva transitions. Its juvenile field is not authorized as same-year recruitment until raw phenology demonstrates that it corresponds to the same breeding cohort.

## Prior-art boundary

Greenberg, Zarnoch & Austin (2017; Ecosphere 8:e01789; DOI 10.1002/ecs2.1789) already showed over 22 years and six anuran species that adult breeding effort, hydroregime and weather can differentially predict juvenile recruitment.

Therefore the paper cannot be sold as the discovery that “breeding activity does not always predict recruitment.”

The remaining ecological target is:

> **Which life-cycle transition becomes the demographic bottleneck under environmental stress, and does the same stage-specific bottleneck recur across independent monitoring programmes or reproductive strategies?**

## Frozen next step

Before any transition coefficient, environmental-effect sign or model comparison is opened:

1. materialize or inspect the raw archives;
2. count events, sites, site-years and repeated visits;
3. freeze source-specific stage mappings;
4. audit explicit absence vs missing/unsurveyed states;
5. test whether chorus and larvae programmes share an admissible site identity for Hyla/Pelobates;
6. audit stage phenology and cohort compatibility;
7. then select the richest **identifiable** endpoint using only structural estimability information.

No candidate may be selected because it produces a more interesting demographic-decoupling result.
