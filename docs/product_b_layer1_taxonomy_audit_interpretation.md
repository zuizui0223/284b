# Product-B Layer-1 taxonomy audit: frozen interpretation

## Status

This note records the first empirical Layer-1 pre-model result for the paired biological answer-check framework. It is an interpretation of already-opened taxonomy-only evidence, not a new gate and not an authorization to alter any failed taxon.

## Frozen panel

The calibration panel contains the 36 Product-A v2.7.1 candidate taxa selected before Product-B cross-source discordance existed. All 36 entered the taxonomy audit. No occurrence counts, coordinates, fitted models, paired discordance values, or sampling outcomes were used to select or replace taxa.

## Current-taxonomy result

Using GBIF current `/v2/species/match` plus direct usage verification, all 36/36 panel taxa resolved as exact accepted species-level current-taxonomy concepts.

Therefore the panel is not limited by inability to identify the intended biological names in the current taxonomy.

## Frozen-snapshot result

The same 36 declared biological names were then evaluated inside the prospectively frozen 2026-08-01 GBIF occurrence snapshot using only the allowlisted taxonomy projection:

- `species`
- `specieskey`
- `taxonkey`
- `scientificname`
- `taxonrank`

The scan persisted neither matched row counts nor coordinates, occurrence identifiers, dates, dataset fields, or raw rows.

Under the pre-existing v7.3 rule requiring exactly one nonblank snapshot `specieskey` for the closed declared name set:

- 12/36 taxa passed snapshot-internal identity;
- 24/36 were unresolved;
- the dominant unresolved reason was `snapshot_specieskey_not_unique`;
- in some cases non-species taxon ranks also occurred within the rows carrying the declared species name.

All 36 declared species names were observed in the deterministic snapshot fragment scan. Thus the principal problem was not simple absence of the name from the snapshot; it was multiplicity of taxonomic identities attached to that biological species label.

## Positive inference

This establishes a reproducible distinction between two identity layers:

1. **current biological/taxonomic identity** can be unambiguous; while
2. **identity encoded in a historical occurrence snapshot** can remain non-unique for the same declared species label.

The result generalizes the taxonomy-version mismatch previously encountered in single engineering pairs: it is present at panel scale and occurs before model fitting or ecological answer comparison.

This is an evidence-interface result, not evidence that the biological taxonomy itself is ambiguous and not an ecological cross-validity result.

## Consequence for Layer 1

The original calibration contract requires at least 30 complete taxa per procedure × M cell before a 95th-percentile cross-source discordance ceiling may be frozen. Because only 12 taxa pass the strict single-snapshot-specieskey gate, the 36-taxon calibration cannot satisfy that 30-taxon requirement under the current identity contract even if all 12 later pass sampling and model adequacy.

The 24 unresolved taxa are not replaced, rescued, or reclassified after this result.

The 12 identity-passed taxa remain useful for the already-frozen engineering question:

> Among taxa with stable snapshot-internal identity, can both preserved-specimen and human-observation evidence independently satisfy the unchanged 50 records / 30 unique 10-km cells / 10 effective-cell floors?

That source-mode sampling execution is a separate stage. Its outcome must not retroactively change the taxonomy interpretation above.

## Successor boundary

A future unopened calibration may prospectively define one biological species concept as a closed set of historical snapshot identities rather than requiring one snapshot key, but such a successor cannot be used to retroactively rescue these 24 opened taxa or to claim that the present calibration achieved its 30-taxon requirement.
