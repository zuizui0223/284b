# Product-B v7.3 — snapshot-internal taxonomy identity gate

## Why v7.3 exists

v7.2 solved live-search pagination drift by freezing a public monthly GBIF snapshot, but JOS003 exposed a separate engineering boundary: a taxon key resolved from the current GBIF taxonomy API cannot automatically be assumed to be the identity used by a previously frozen monthly snapshot. JOS003 is permanently consumed and is not rescanned or rescued.

v7.3 is therefore an engineering-only prospective layer. It does not lower any biological, witness, sampling, control, model, invariant, or knockout threshold. It changes only the way a *new* pair obtains the snapshot species identity used later for sampling.

## Required order

1. Select and freeze a completely new engineering pair from biology/literature only.
2. Freeze biological names, current-taxonomy accepted names, and any manually reviewed synonym names before any snapshot taxonomy row access.
3. Run the literature-witness and independent-frame gates unchanged.
4. Run current-taxonomy review without snapshot occurrence values.
5. Run this snapshot-internal taxonomy identity gate.
6. Only if this gate returns exactly one stable snapshot `specieskey` for the focal host may a separate sampling package later be frozen and authorized.

The identity gate does **not** authorize sampling.

## Allowed snapshot columns

The taxonomy-only scanner may project only:

- `species`
- `specieskey`
- `taxonkey`
- `scientificname`
- `taxonrank`

It must not project coordinates, country, dates, GBIF IDs, occurrence IDs, dataset IDs, recorder fields, uncertainty, issues, licenses, or any environmental value.

## Allowed query values

Before snapshot taxonomy access, the pair declaration must contain an ordered closed set of admissible species names. The set may include:

- the biological name used in the dependency literature;
- the directly resolved current accepted species name;
- a synonym name only when its direct accepted relation was reviewed before snapshot access.

No new name may be added after the taxonomy-only snapshot scan starts.

## Sanitized output

The scanner must immediately deduplicate rows to a sorted set of taxonomy tuples:

`(species, specieskey, taxonkey, scientificname, taxonrank)`

It must not output, log, or persist:

- raw rows;
- matched row counts;
- per-file counts;
- spatial information;
- date information;
- occurrence abundance or density;
- dataset frequencies.

The only permitted empirical output is the distinct tuple set plus static audit metadata proving the frozen snapshot identity.

## Pass/fail rule

The gate passes only when:

- at least one taxonomy tuple is returned;
- every tuple has `taxonrank = SPECIES` or maps to the same declared species through a single `specieskey`;
- exactly one nonblank `specieskey` occurs across all admitted tuples;
- every returned `species` value belongs to the predeclared admissible-name set;
- no undeclared species concept appears.

If zero tuples, multiple species keys, undeclared names, or concept ambiguity occur, the pair becomes `unresolved_snapshot_taxonomy_identity`. No alternative key/name search is allowed for that pair.

## Firewalls

All previously opened or terminal pairs remain excluded, including JOS003. JOS003's zero-hit result is a terminal v7.2 outcome and may not be reinterpreted by v7.3.

v7.3 remains engineering-only. A successful identity gate is infrastructure feasibility, not ecological evidence.
