# Product-B Layer-1 empirical feasibility result

## Frozen sequence

The same-target cross-source calibration panel contained 36 taxa selected in Product-A before Product-B cross-source outcomes existed. No taxon was added or replaced after Product-B outcomes were opened.

The prospective gate sequence was:

1. current taxonomy identity;
2. frozen 2026-08-01 snapshot-internal taxonomy identity;
3. independent source-mode sampling adequacy for `PRESERVED_SPECIMEN` and `HUMAN_OBSERVATION`;
4. only then, independent ecological model fitting and paired answer checking.

## Empirical result

### Current taxonomy

All **36/36** taxa resolved as exact accepted species concepts in current GBIF taxonomy without opening occurrence counts or coordinates.

### Frozen snapshot identity

Only **12/36** taxa passed the predeclared v7.3 rule requiring one stable snapshot-internal `specieskey` for the declared species concept.

The remaining **24/36** were unresolved, dominated by `snapshot_specieskey_not_unique`. All 36 declared species names were nevertheless encountered during the deterministic snapshot scan, so the principal problem was not simple name absence.

### Source-mode sampling

All **12/12** snapshot-identity-passed taxa passed the unchanged source-specific sampling floors in both observation modes:

- at least 50 retained independent records;
- at least 30 unique 10-km equal-area cells;
- at least 10 inverse-Simpson effective 10-km cells.

No sampling-passed taxon was selected from a replacement pool, and the 24 upstream taxonomy-unresolved taxa remained unresolved.

Thus the observed gate trajectory was:

`36 current-taxonomy-resolved -> 12 snapshot-identity-resolved -> 12 source-mode-sampling-passed`.

## Interpretation

For this panel, the first major attrition in paired ecological answer checking is **taxonomic representation inside the historical occurrence snapshot**, not source-mode occurrence availability.

The result distinguishes three identities that are often treated as interchangeable:

1. the biological species concept;
2. the current taxonomy service identity;
3. the taxonomic identity encoded inside a historical occurrence snapshot.

A species can be unambiguous under (1) and (2) while remaining non-unique under (3). That matters before model fitting because two otherwise independent ecological answers cannot be cleanly compared until both are known to refer to the same frozen data-level biological entity.

This result does **not** show that specimen-derived and human-observation-derived niche estimates are coherent. It shows that, once strict snapshot identity is established, both independent evidence views are empirically adequate for model construction in all 12 surviving taxa.

## Consequence for the original calibration design

The frozen soft-cross-check calibration requires at least 30 complete taxa for a procedure-by-M 95th-percentile reference ceiling. Because only 12 taxa pass the strict single-key snapshot identity gate, the current panel cannot create that reference ceiling.

Therefore any cross-source niche overlap estimated from these 12 taxa is descriptive/engineering evidence only. It cannot be labeled `paired_crosscheck_consistent` or `paired_crosscheck_attention_required` under the frozen calibration contract.

The 24 unresolved taxa are not retroactively rescued. A future unopened calibration may prospectively test a closed biological-concept-to-snapshot-key-set representation, but that would be a new design evaluated on fresh taxa.

## Next unopened question

For the 12 admissible taxa:

> Does the same frozen modeling procedure recover a similar ecological answer when the biological target is unchanged but the independent observation system changes?

Both source-specific answers will be fit independently on one shared, source-symmetric M/background frame. Paired discordance remains sealed until all prediction surfaces are frozen.
