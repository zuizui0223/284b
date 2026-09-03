# Product-B v5 — response-blind taxonomy resolution protocol

## Status

**Taxonomy-only / no occurrence inspection.** This step follows the literature-only pair declaration and precedes any sampling-availability preflight.

It may inspect taxonomic checklists, taxonomic revisions, accepted/synonym status and stable taxonomy identifiers. It must not inspect occurrence records, occurrence counts, unique-cell counts, range maps derived from occurrences, environmental values, invariant metrics, model outcomes or process-knockout outcomes.

## 1. Why the taxonomy contract must be explicit in 2026

GBIF is transitioning taxonomic interpretation toward the Catalogue of Life eXtended Release (CoL XR). The historical GBIF Backbone is no longer updated, but GBIF documents that its identifiers remain preserved and supported for backwards compatibility.

Product-B v5 therefore separates two questions:

1. **Reproducible matching identifier:** can the literature taxon be represented by an exact species-level identifier in one frozen matching checklist?
2. **Concept conflict:** does current independent taxonomy contradict the species concept assumed by the literature pair?

A stable legacy key does not override a concept conflict. Conversely, a current taxon page without a reproducible frozen checklist identity is not enough to authorize sampling.

## 2. Frozen matching checklist for this prototype

For the first sampling-availability preflight, the compatibility matching checklist is:

- taxonomy: historical `GBIF Backbone Taxonomy`;
- checklist key: `d7dddbf4-2cf0-4f39-9b2a-bb099caae36c`;
- identifier field: legacy numeric GBIF `taxonKey`/usage key where an exact species-level match is independently verified.

This is a reproducibility choice, not a claim that the historical backbone is taxonomically superior. It is chosen because the existing Product-B apparatus is written around `taxon_key`, GBIF preserves these identifiers for API compatibility, and a checklist key can be declared explicitly.

A future CoL-XR-native line would require a separate non-retroactive contract and must not silently replace this checklist after sampling outcomes are known.

## 3. Exact-match rule

A literature taxon is `resolved_exact_legacy_key` only when:

- the scientific name resolves at species rank;
- the legacy numeric key is attributable to that species concept rather than merely its genus or a fuzzy/higher-rank match;
- no known taxonomic conflict would merge the literature-defined biological species with another taxon in a way that changes the obligate-pair statement.

Do not accept:

- genus-only matches;
- fuzzy matches;
- keys inferred from occurrence records;
- keys recovered from occurrence downloads;
- post-hoc name substitutions chosen because they improve record availability.

## 4. Conflict rule

Use `unresolved_taxonomic_concept_conflict` when independent taxonomy disagrees in a way that could alter the biological pair.

Examples already found response-blind:

### Glochidion acuminatum

The current GBIF/Catalogue-of-Life presentation treats `Glochidion acuminatum` as a synonym of `Glochidion triandrum`, whereas a taxonomic study indexed by GBIF and later regional revisions recognize `G. acuminatum` as distinct. Because the obligate-pollination literature is written at the `G. acuminatum` species concept, mapping it automatically to `G. triandrum` could broaden the host concept and manufacture nesting. The pair therefore stops at taxonomy preflight.

### Glochidion zeylanicum

Current Catalogue-of-Life presentation on GBIF retains `Glochidion zeylanicum`, while Kew/WCVP places the name in synonymy under `Phyllanthus obliquus var. obliquus`. This cross-checklist disagreement is not resolved by choosing the version that produces more records. The pair remains unresolved until a separate taxonomic-concept decision is justified without occurrence data.

### Glochidion lanceolatum

Current Kew/POWO and a modern Taiwan revision accept `Glochidion lanceolatum` as a species, despite historical treatment as `G. zeylanicum var. lanceolatum`. This is not itself a reason to exclude the biological pair, but an exact frozen legacy key is still required before sampling eligibility.

## 5. Taxonomy states

Partner-level states:

- `resolved_exact_legacy_key` — exact species-level legacy key, no blocking concept conflict;
- `unresolved_missing_exact_legacy_key` — name is biologically/taxonomically recognizable but an exact frozen legacy key has not been independently verified in this step;
- `unresolved_taxonomic_concept_conflict` — competing taxonomic treatments could change the biological species concept;
- `unresolved_other_taxonomy` — another taxonomy-only issue prevents safe matching.

Pair-level state:

- `eligible_for_sampling_preflight` — both partners are `resolved_exact_legacy_key` and neither has a blocking concept conflict;
- `unresolved_taxonomy` — at least one partner is unresolved.

Taxonomy eligibility is not empirical execution authorization. It only permits a later sampling-availability preflight.

## 6. Evidence provenance

The taxonomy registry records where each identifier/status came from. A legacy key may be recorded when a GBIF Backbone species page directly exposes it, or when an independent taxonomic identifier source explicitly attributes that numeric identifier to GBIF. The latter is marked as secondary provenance rather than silently treated as a direct GBIF lookup.

Current taxonomic-concept evidence may use Catalogue of Life, Kew/POWO/WCVP, or primary taxonomic revisions. These sources are used only to detect concept conflicts, not to inspect distributions or occurrence availability.

## 7. Current response-blind audit outcome

The first taxonomy audit is intentionally conservative.

- `Ficus racemosa` / `Ceratosolen fusciceps`: both exact legacy GBIF Backbone keys are directly verifiable; pair may enter the sampling-availability preflight.
- `Yucca schidigera` / `Tegeticula mojavella`: exact legacy keys are available, but the moth key is secondary-provenance in the current audit; the row is retained with provenance made explicit. The pair may enter a later key-verification substep but is not silently treated as equivalent to direct verification.
- `Yucca elata` / `Tegeticula elatella`: host plant legacy key is available; exact moth legacy key was not independently verified in this pass, so the pair remains unresolved.
- all four `Glochidion–Epicephala` rows remain unresolved for this first sampling preflight because at least one partner has either a taxonomic-concept conflict or an unverified exact legacy key.

This narrowing is a preflight result, not a biological failure and not a reason to replace the panel after inspecting occurrences.

## 8. Non-retroactivity

The literature registry remains unchanged. Taxonomy resolution is stored as a downstream overlay.

Do not:

- rewrite literature names to maximize matches;
- delete unresolved pairs because they are inconvenient;
- substitute a congener or broader taxon;
- switch checklist after learning occurrence availability;
- reinterpret a taxonomy failure as an invariant failure.

## 9. Next allowed operation

After the taxonomy overlay and its validator are committed, the next step may be a **sampling-availability preflight specification**.

That specification may define minimum records, minimum unique cells, asymmetry ceilings, same-record exclusions and stop rules. It must be frozen before any counts are read.

Occurrence counts themselves are not opened in the taxonomy step.