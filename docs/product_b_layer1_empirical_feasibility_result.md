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

## Next unopened question at the time of this result

For the 12 admissible taxa:

> Does the same frozen modeling procedure recover a similar ecological answer when the biological target is unchanged but the independent observation system changes?

Both source-specific answers were to be fit independently on one shared, source-symmetric M/background frame. Paired discordance remained sealed until all prediction surfaces were frozen.

## Historical status and successor continuation

This document is intentionally retained as the terminal result of the **original 36-taxon panel**. Its statement that the original panel could not form a >=30-taxon q95 reference remains true and must not be rewritten as though that panel later succeeded.

The research program subsequently opened a distinct, prospectively governed successor continuation rather than retroactively replacing the 24 taxonomy-unresolved taxa. That continuation eventually produced a separate core19 v0.4 same-target endpoint after outcome-blind finite-frame qualification and explicitly versioned engineering repairs.

The later endpoint therefore does not invalidate this feasibility result. Instead, the two results occupy different levels:

- this document: **why the original panel stopped before calibrated cross-validity**;
- `docs/product_b_same_target_core19_empirical_result.md`: **the later fresh successor/held-out endpoint that did reach calibrated cross-validity**.

In the completed core19 v0.4 endpoint, successor reference calibration froze 24/24 procedure-by-M cells under the unchanged >=30 adequate-taxa and nearest-rank q95 rules. A fresh held-out 12-taxon matrix then opened 283 paired cells, and all 283 remained within their frozen successor reference ceilings; five cells stayed closed at the predeclared answer-adequacy gate.

Thus Product-B now has an empirical Level-A cross-validity result, but it came from the separately qualified successor/core19 path, **not** from post-hoc rescue of this original 36-taxon panel.