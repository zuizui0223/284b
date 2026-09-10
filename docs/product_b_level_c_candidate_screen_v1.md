# Product-B Level-C finite candidate screen v1

## Purpose

This screen executes the finite response-blind admission protocol frozen in `config/product_b_level_c_candidate_admission_protocol_v1.json`.

The task is deliberately upstream of occurrence availability, model fitting and any cross-role outcome. Candidates are evaluated only from external biological relation evidence, published operational space/time metadata, role-estimand compatibility, focal-evidence independence, management scope and fresh endpoint identity.

The search stops when either three candidates pass all G1-G7 gates or twelve candidates are screened. Failed candidates remain in the registry and cannot be replaced after the hard stop.

## Terminal result

The finite screen reached twelve candidates before any candidate passed all seven admission gates.

- screened: **12/12**
- fully admitted: **0/3 target**
- query families entered: **3/4**
- fourth frozen query family executed: **no** — the twelve-candidate hard stop had already been reached
- occurrence/source-count feasibility opened: **no**
- focal cross-role outcome opened: **no**
- empirical ledger increment: **0**

This is a candidate-admission terminal, not negative cross-role empirical evidence.

## Candidate decisions

### 1. SMIL001 — *Smilax insularis* -> *Dasineura heterosmilacicola*

Primary dependency evidence: Current Biology 2026, DOI `10.1016/j.cub.2026.03.002`.

The plant-to-midge reproductive dependency is strong, but the breeding experiment is published at Amami-Oshima grain without an exact reviewed population coordinate. The exact 2025 Higashinakama interaction anchor is not borrowed as the 2026 dependency site. Event-time provenance also remains unresolved and a bounded source scan did not recover an independent focal role-answer pair.

Terminal screen state: `blocked_operational_space`.

### 2. BRY001 — *Breynia oblongifolia* -> *Epicephala* pollinator guild

Primary dependency evidence: DOI `10.26786/1920-7603(2021)644`. Independent natural-history/phenology metadata: DOI `10.1186/s12862-021-01889-4`; pollinator-diversity evidence: DOI `10.1186/s12862-018-1314-y`.

Fruit production requires specialist moth pollination at the guild level, but the host carries two co-occurring undescribed *Epicephala* pollinator species. The available phenology study jointly observes plant and moth roles and does not provide the independently sourced focal role answers required by G5.

Terminal screen state: `blocked_focal_evidence_independence`.

### 3. AGL001 — *Aglais urticae* -> *Urtica dioica*

Primary study: DOI `10.1111/1365-2656.13689`.

The study provides strong operational sampling of larvae and nettle patches, but the exact named-host implication fails: *A. urticae* also uses *Urtica urens*. Genus-level nettle specialization cannot be rewritten as dependency on *U. dioica* specifically.

Terminal screen state: `blocked_event_relation`.

### 4. TER001 — *Teriocolias zelia andina* -> *Senna birostris* var. *arequipensis*

Host record: DOI `10.1007/s13744-012-0076-2`; egg phenology: DOI `10.1007/s13744-013-0170-0`.

The primary host record states that oviposition and feeding observations suggest host specificity, not that exact named-host necessity was experimentally established. The later time series is egg phenology rather than a direct larval-development answer.

Terminal screen state: `blocked_event_relation`.

### 5. MAN001 — *Manduca sexta* -> *Nicotiana attenuata*

Host-recognition source: DOI `10.1007/s00359-003-0450-1`.

*M. sexta* larvae are facultative specialists on Solanaceae and can remain polyphagous. A hard dependency on *N. attenuata* is therefore not biologically supported.

Terminal screen state: `blocked_event_relation`.

### 6. HEL001 — *Heliothis subflexa* -> *Physalis angulata*

Host-use source: DOI `10.1111/j.1558-5646.2012.01712.x`.

The moth is strongly specialized on the genus *Physalis*, but many *Physalis* species support development. *P. angulata* cannot be declared the uniquely required named species.

Terminal screen state: `blocked_event_relation`.

### 7. PSI001 — *Pseudophilotes sinaicus* -> *Thymus decussatus*

Phenological dependency source: DOI `10.1016/j.baae.2014.05.003`; host-plant patch dynamics: DOI `10.1093/jpe/rtu004`.

This system passes the biological, spatial, temporal and role-estimand gates unusually well. However, the focal stronghold Farsh Shoeib has been subject to conservation interventions including fencing, path construction and grazing control. Under the prospectively frozen G6 rule, a relation-space pattern that can be altered by deliberate management is engineering-only rather than a confirmatory natural endpoint.

Terminal screen state: `engineering_only_management_confounded`.

### 8. KBB001 — Karner blue -> *Lupinus perennis*

Natural host-use evidence: DOI `10.1016/S0006-3207(97)00165-1`; phenology experiment: DOI `10.1111/csp2.147`.

The larval host relation is strong, but the best event-level phenology study uses field-placed Karner blue eggs in conservation-managed habitat. The frozen management/intervention gate therefore prevents confirmatory admission.

Terminal screen state: `engineering_only_management_confounded`.

### 9. PAR001 — *Parnassius smintheus* -> *Sedum lanceolatum*

Local host-use source: DOI `10.1046/j.1365-2311.2002.00426.x`; later population study: DOI `10.1002/ecs2.1816`.

The butterfly is close to monophagous on *S. lanceolatum* at the focal Alberta system, but later work explicitly notes multiple host species across its broader range and calls the focal relationship virtually monophagous. That is insufficient for the exact hard named-host implication required by G1.

Terminal screen state: `blocked_event_relation`.

### 10. FHI001 — *Ficus hispida* -> *Ceratosolen marchali*

Local pollinator-response source: DOI `10.1186/s12862-026-02494-z`.

The study resolves population-specific scent attraction and exact study localities, but it does not itself establish the proposed hard event statement that *F. hispida* reproductive success at those populations requires *C. marchali*. Several exact study sites are botanical gardens, adding a separate management concern.

Terminal screen state: `blocked_event_relation`.

### 11. GLO_LAN_001 — *Epicephala lanceolatella* -> *Glochidion lanceolatum*

Revision and host-association source: DOI `10.3897/zookeys.568.6721`.

The moth is reported as known only from *G. lanceolatum*, with larvae reared from fruit and seed feeding documented. Under the frozen admission rule, however, a known-only association is not adversarial experimental proof that no alternative host can support development.

Terminal screen state: `blocked_event_relation`.

### 12. OPM_FIG_001 — *Ceratosolen fusciceps* -> *Ficus racemosa*

Primary population-specificity source: DOI `10.1111/j.1365-294X.2010.04654.x`.

This candidate is not scientifically re-screened as fresh. Existing Product-B provenance records its occurrence execution as already consumed and terminal `unresolved_sampling`. G7 therefore forbids reopening or relabelling it as a new endpoint.

Terminal screen state: `excluded_previously_consumed_endpoint`.

## What the screen says

The screen shows that moving from Level A same-target reproducibility to Level C biological dependency is not mainly a matter of finding famous obligate interactions. A confirmatory event-level endpoint simultaneously needs:

1. an exact external directional implication;
2. operational event space and time;
3. role answers that actually measure the event-relevant quantities;
4. focal evidence independent of the relation-defining evidence;
5. a relation space not manufactured by management;
6. a genuinely fresh endpoint.

Several candidates passed most of these requirements, but none passed all seven under the finite prospective contract.

This is a useful structural result for study design, but it is **not** an empirical conclusion about cross-role biological coherence.

## Hard stop

The registry is frozen at twelve rows. The fourth search query is not executed and no replacement system is added. Because zero candidates are fully admitted, post-registry source/sampling feasibility is not authorized.

The 284b empirical ledger therefore remains **1**, corresponding only to the already-closed Level-A core19 held-out endpoint.
