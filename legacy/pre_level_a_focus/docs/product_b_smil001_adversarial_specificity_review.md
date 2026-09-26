# SMIL001 adversarial specificity and relation-space review

## Purpose

`SMIL001` is the first response-blind candidate considered for a fresh Product-B cross-role Level-C/D endpoint after the Level-A same-target core19 endpoint closed empirically.

Pair:

- X: *Smilax insularis* (syn. *Heterosmilax japonica* in the 2025 pollination paper)
- Y: *Dasineura heterosmilacicola*

The candidate was selected from external biological literature, not from occurrence overlap, fitted surfaces, or a focal cross-role outcome.

This review asks two separate questions:

1. Which dependency direction is strong enough to admit prospectively?
2. At what spatial and temporal grain can that dependency be represented without inventing relation-space keys?

## External evidence

### Plant -> pollinator direction

Current Biology 2026 (`10.1016/j.cub.2026.03.002`) experimentally tested pollinator dependence of *S. insularis* on Amami-Oshima. Fine-mesh visitor exclusion prevented the normal fruit-set pathway, and the study concludes that fruit set depends entirely on *D. heterosmilacicola*.

This is strong evidence for a directional biological statement at the declared reproductive event:

`successful S. insularis reproduction requires D. heterosmilacicola pollinator access`

The same study conducted fieldwork across Amami-Oshima, Tokunoshima, Okinawa, Ishigaki and Yonaguni, but the breeding-system experiment itself is reported at Amami-Oshima spatial grain.

### Pollinator -> plant direction

ZooKeys 2025 (`10.3897/zookeys.1234.146453`) describes *D. heterosmilacicola* from the *Heterosmilax japonica* / *Smilax insularis* system. Female midges visit flowers, larvae feed on pollen and floral tissue in fallen male flowers, and the host plant is listed as the male flower of *H. japonica*.

This is strong host-association and brood-site evidence. It is not, by itself, an adversarial demonstration that no alternative larval host exists anywhere in the species' relevant range. A response-blind exact-species literature search did not locate an alternative host, but failure to find a report is not proof of exclusivity.

Therefore the current admission is asymmetric:

- `X_requires_Y`: admissible Level-C candidate;
- `Y_requires_X`: not yet admitted as a hard direction;
- `mutual_obligacy`: not yet admitted as Level D.

## Why raw niche overlap is not the hard test

The biological event supported by experiment is successful plant reproduction, not equality of adult plant and midge occurrence distributions.

A raw range-overlap or bidirectional niche-containment test would therefore overstate the external biology. Adult plant occupancy can persist without current pollination; the midge is mobile; accessible-area semantics differ between roles; and interaction opportunity is seasonal.

The confirmatory relation must instead be defined on a common event space such as:

`plant reproductive opportunity x flowering window`

with a directional statement that the plant opportunity requires adequate midge visitation/reachability at the same opportunity.

## Spatial provenance

The two primary studies resolve space at different grains.

### Exact interaction-observation sites from ZooKeys 2025

The 2025 paper gives exact field sites:

- Amami-Oshima, Higashi-nakama: 28.2856 N, 129.4355 E, 120 m;
- Iriomote, Funaura: 24.3987 N, 123.8040 E, 20 m;
- Iriomote, Komi: 24.2929 N, 123.8964 E, 140 m;
- Yonaguni, Mt Kubura: 24.4572 N, 122.9586 E, 90 m.

These are valid response-blind **interaction-observation anchors**.

### Causal plant-dependency experiment from Current Biology 2026

The 2026 breeding-system experiment is reported for Amami-Oshima, from early July to late September 2024. The article text located in the response-blind review does not publish the exact coordinate of the experimental population.

The 2025 Higashi-nakama coordinate and the 2026 Amami-Oshima breeding experiment must therefore **not** be silently equated. They may refer to the same or a nearby population, but that linkage is not established by the published provenance reviewed here.

Consequently, exact-site hard-relation keys remain unresolved.

## Temporal provenance

The 2025 study reports that the plant bears flowers from March to August across the Ryukyu Archipelago. Its results also note that male flowers were observed only in March in that particular study, while specimen records include larval material from March, April and June.

The 2026 study sampled across late May to late September 2024 and early July to late August 2025. Detailed pollinator observation on Amami-Oshima used early July to mid-August windows, while the breeding-system experiment ran from early July to late September 2024.

These are not one interchangeable temporal quantity:

- broad species flowering season;
- local male-flower observations;
- pollinator-observation window;
- breeding-system experimental window.

A confirmatory relation-space contract must choose the temporal key according to the biological event rather than collapsing all four into one fixed month range.

## Operational decision

The candidate is biologically strong enough to continue **qualification**, but not to open a focal cross-role relation.

Current state:

`unresolved_exact_dependency_experiment_site`

Reasons:

1. the hard plant-dependency evidence is spatially resolved only to Amami-Oshima in the reviewed 2026 article text;
2. the exact 2025 Amami interaction site cannot be assumed to be the exact 2026 exclusion-experiment population;
3. the event-specific flowering-window key still needs a prospectively justified operational definition;
4. role-specific plant and midge answer contracts are not yet frozen.

This is a representation/operationalization gap, not a biological counterexample and not a sampling failure.

## Role-X design consequence

A generic plant SDM is not automatically an estimator of successful reproduction. The plant side must distinguish:

- local plant viability/occupancy;
- flowering/reproductive opportunity;
- successful fruit set.

The hard dependency pertains to the latter two, not merely to adult occurrence.

The cleanest first implementation should therefore avoid relabeling a plant occurrence surface as reproductive success. Candidate options, in decreasing evidential strength, are:

1. independently observed/frozen flowering populations or reproductive-opportunity records;
2. a prospectively validated flowering-opportunity model with its own adequacy gate;
3. a plant SDM only as a lower-level viability component, not as the hard-event answer by itself.

## Role-Y design consequence

The midge side requires visitation or reachability support during the same flowering opportunity. EOG provides a useful architecture for keeping local possibility, reachability and observation support distinct, but it is not a plug-in pollinator-visitation estimator. A new role-Y contract must still freeze:

- source states;
- transition/movement semantics;
- spatial grain;
- temporal horizon;
- local viability/support representation;
- observation model if used;
- adequacy gate.

The midge's raw occurrence SDM must not be silently relabeled as visitation probability.

## Next admissible work

Before focal occurrence relation opening, Product-B may:

1. search response-blind external sources for a published exact coordinate or unambiguous site identity for the 2026 Amami breeding-system population;
2. freeze a defensible event-specific flowering-window representation;
3. design and synthetically validate role-X reproductive-opportunity and role-Y visitation/reachability contracts;
4. only after those items are frozen, run source-blind sampling/answer-construction feasibility.

If the exact dependency population cannot be resolved, the protocol must either remain unresolved at exact-site Level C or prospectively define a coarser island-level relation whose biological interpretation is genuinely valid. It must not manufacture a coordinate by borrowing the 2025 site.

## Empirical boundary

No focal SMIL001 occurrence relation has been opened.

- counts as empirical evidence: false
- counts as empirical conclusion: false
- 284b empirical ledger remains unchanged at 1
