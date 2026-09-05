# Product-B v5 — literature-only obligate-pair registry protocol

## Status

**Response-blind literature curation only.** This step does not inspect occurrence records, occurrence counts, environmental values, candidate-model outcomes, invariant outcomes, or process-knockout outcomes. It does not freeze or authorize empirical execution.

This protocol is the next declaration step after the design-only invariant prototype. It exists to prevent the biological answer-check from being defined by the same occurrence data that will later be evaluated.

## 1. Phase-1 scope decision

Phase 1 is restricted to one obligacy class:

`obligate_pollination_mutualism`

Do not mix parasitoids, holoparasites, mycoheterotrophs, lichens, or ant-plants into the first empirical panel. Those classes operate at different biological scales and have different observation processes. They may be added only as separately declared extensions after the first class has an admissible registry and a usable sampling denominator.

The initial direction is deliberately asymmetric:

`Y_requires_X`

where:

- `X` = the host plant required for reproduction/development of the pollinating seed parasite;
- `Y` = the obligate pollinator/seed-parasite species.

Phase 1 does **not** infer `X_requires_Y` merely because a system is described as an obligate mutualism. A plant may have geographically replacing or coexisting pollinator species even when each pollinator is host-specialized. Plant-to-pollinator direction is therefore declared only if a separate literature audit establishes that exact species-level dependency over the declared geographic scope.

## 2. Inclusion rule

A candidate pair is eligible for the literature registry only when all of the following are supported without occurrence-data inspection:

1. Both partners are identified to species level in the source literature.
2. The source establishes active pollination or membership in the obligate pollinating lineage rather than a non-pollinating cheater lineage.
3. `Y` uses `X` as its reproductive/developmental host at the declared scope.
4. The available literature does not establish another accepted host species for `Y` within that scope.
5. Any known geographic replacement, multiple-pollinator case, cryptic lineage, or taxonomic caveat is written into `known_boundary` rather than silently ignored.
6. The direction is no stronger than the evidence. A system can be biologically mutualistic while the registry entry remains only `Y_requires_X`.

If any condition cannot be checked from independent literature, the pair is not promoted into the eligible registry. It may be retained in an exclusion ledger with a reason.

## 3. Evidence hierarchy

Preferred evidence, in order:

1. taxonomic/systematic revision with explicit host and behavior data;
2. primary ecological or population-genetic study explicitly identifying host use/specificity;
3. primary natural-history study;
4. review only as corroboration, not as the sole basis for a species-level pair when a primary source is available.

Every eligible row must contain at least one DOI. Multiple DOI values may be separated by `;` when a second source is needed to close a taxonomic or geographic caveat.

## 4. Geographic scope is binding

A literature statement may be local or regional rather than global. The registry therefore records `declared_geographic_scope`.

Later empirical occurrence processing must respect that scope. A pair supported only for continental Southeast Asia cannot be evaluated as though the same one-to-one association were established in Australia or another biogeographic region.

Changing a geographic scope after looking at occurrence or invariant outcomes is forbidden.

## 5. Taxon keys are not resolved in this step

The candidate schema contains `x_taxon_key` and `y_taxon_key`, but literature curation is separated from taxonomy-backbone resolution.

In this step:

- scientific names are populated;
- taxon-key fields remain blank;
- `taxon_key_status = pending_response_blind_taxonomy_resolution`.

A later taxonomy-only pass may resolve accepted names and stable backbone keys. That pass must not request occurrence counts, maps, environmental values, or model outputs.

## 6. Phase-1 eligible literature panel

The initial panel is deliberately conservative.

### Glochidion–Epicephala

Kawakita & Kato (2016), DOI `10.3897/zookeys.568.6721`, provides species-level host and pollination behavior for Japanese Epicephala. The revision states that the relevant pollinating species are host-specialized, while also documenting important exceptions.

Eligible directional pairs:

- `Glochidion acuminatum` → host of `Epicephala anthophilia`;
- `Glochidion zeylanicum` → host of `Epicephala bipollenella`;
- `Glochidion lanceolatum` → host of `Epicephala lanceolatella`;
- `Glochidion lanceolatum` → host of `Epicephala perplexa`.

The two `G. lanceolatum` entries remain `Y_requires_X` only because two pollinator species coexist on that plant. This is exactly why the invariant is directed rather than symmetric.

### Ficus–Ceratosolen

`Ficus racemosa` / `Ceratosolen fusciceps` is admitted with a geographic boundary. Kobmoo et al. (2010), DOI `10.1111/j.1365-294X.2010.04654.x`, supports a single pollinating wasp species across the sampled continental Southeast Asian range and explicitly discusses divergence outside that regional panel. The declared scope is therefore continental Southeast Asia rather than the full global range of the fig.

The initial direction is `Ceratosolen fusciceps requires Ficus racemosa`.

### Yucca–Tegeticula

The Tegeticula species complex contains both pollinators and non-pollinating cheaters and includes host-use heterogeneity. Phase 1 therefore admits only species for which the host-use evidence is sufficiently narrow.

Althoff et al. (2006), DOI `10.1080/10635150600697325`, reports host-use data for the pollinating species complex. Two conservative directional pairs are retained:

- `Yucca elata` → reproductive host of `Tegeticula elatella`;
- `Yucca schidigera` → reproductive host of `Tegeticula mojavella`.

These are directional moth-to-host declarations only.

## 7. Explicit exclusion ledger

The following examples are **not** eligible in Phase 1 under the current pairwise invariant:

| Candidate | Decision | Reason |
| --- | --- | --- |
| `Glochidion obovatum` / `Epicephala obovatella` | exclude | `E. obovatella` is also documented from `G. rubrum`; a single-host pair would overstate the biology. |
| `Glochidion rubrum` / `Epicephala obovatella` | exclude | same multi-host problem. |
| `Glochidion obovatum` / `Epicephala corruptrix` | exclude | the species is documented from both `G. obovatum` and `G. rubrum`, and its interaction status is not equivalent to the four core obligate-pollinating species. |
| `Ficus hispida` / a single `Ceratosolen` species | exclude | multiple geographically replacing pollinator species are now documented; a global one-pair invariant is biologically false. |
| `Yucca baccata` / `Tegeticula baccatella` | exclude | host-use sources report more than one named Yucca host; strict single-host nesting cannot be assumed. |
| `Yucca rostrata` / `Tegeticula rostratella` | exclude | `T. rostratella` is also reported from `Y. rigida`; the present pair schema cannot encode a required host set. |
| any non-pollinating yucca-moth cheater | exclude | seed use without active pollination is not the predeclared Phase-1 obligacy class. |

The exclusion ledger is a design protection, not a negative biological claim. Some excluded systems may become admissible under a future **host-set** invariant, but that would be a new predeclared estimand rather than a post-hoc repair.

## 8. Association scale

For all Phase-1 pairs the declared biological scale is:

`reproductive_host_dependence`

This means the pollinator's reproduction/development requires the host's reproductive structure. It does **not** mean that every coarse environmental grid cell containing the host must contain the pollinator.

The later SDM/audit grain remains to be frozen separately. Until that grain is frozen, no empirical containment result may be calculated.

## 9. Promotion states for registry rows

Literature rows use one of three registry states:

- `eligible_literature_only`: biological direction is sufficiently supported for a later taxonomy/sampling preflight;
- `excluded_biological_ambiguity`: literature itself shows that the pairwise direction would overstate the biology;
- `unresolved_literature`: evidence is insufficient or conflicting.

`eligible_literature_only` is **not** authorization to retrieve occurrences. It only permits the row to enter the next response-blind taxonomy-resolution step.

## 10. Next allowed step

After this file and the literature registry are committed, the next allowed operation is a taxonomy-only resolution pass for the eligible rows.

That pass may inspect accepted scientific names and stable taxonomic identifiers. It must not inspect:

- occurrence records;
- occurrence counts or unique-cell counts;
- maps or range summaries derived from occurrence data;
- environmental values;
- any invariant metric;
- any Product-A outcome;
- any process-knockout outcome.

Only after taxonomy resolution is separately recorded should a sampling-availability preflight be designed.