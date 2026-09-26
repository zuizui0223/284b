# Product-B v5 — occurrence preprocessing protocol

## Status

**Operationally specified and unit-testable; no empirical occurrence read has been authorized or performed.**

This document supplements, but does not relax or replace, the already frozen numeric sampling thresholds in `product_b_v5_sampling_availability_preflight.md` and `config/product_b_v5_sampling_preflight_contract.json`.

The supplement exists because the phrase “same date + coordinate” is not reproducible until date parsing, coordinate precision and identity-group closure are declared. These choices are fixed here before any occurrence count or map is opened.

## 1. Pure-module boundary

`product_b_v5/occurrence_preprocessing.py` receives occurrence rows that have already been mapped to a small declared schema and whose WGS84 coordinates have already been projected to EPSG:6933.

The module does **not**:

- contact GBIF or any other occurrence service;
- resolve taxonomy;
- choose a geographic scope;
- perform a CRS lookup;
- alter a sampling threshold;
- read environmental rasters;
- compute invariant or process-knockout outcomes.

Network code, when it eventually exists, must first pass the fail-closed authorization guard.

## 2. Coordinate-quality gate

Before the collision graph is built, a row is excluded when any of the following holds:

- WGS84 latitude/longitude is missing, non-finite or outside valid ranges;
- projected EPSG:6933 easting/northing is missing or non-finite;
- a reported coordinate uncertainty is invalid or greater than **10,000 m**.

Missing coordinate uncertainty is **not** treated as evidence of precision. It is retained but counted explicitly in the audit. This prevents missing metadata from becoming either an automatic pass or an automatic data-loss mechanism.

The 10-km uncertainty ceiling is fixed before availability counts and matches the sampling-support cell edge. It is a data-quality rule, not a biological scale claim.

## 3. Identity normalization

### Identifier fields

`occurrence_id_lineage`, `event_id`, `catalog_or_specimen_number` and `dataset_key` have outer whitespace removed. Case is otherwise preserved; the preflight does not silently rewrite source identifiers.

### Recorder

Recorder strings are Unicode-NFKC normalized, internal whitespace is collapsed, and text is case-folded. This prevents formatting-only differences in recorder names from evading the declared collision rule.

### Event day

Only a valid leading ISO calendar date `YYYY-MM-DD` is used. A timestamp such as `2026-09-03T15:20:00` maps to `2026-09-03`. Month-only, year-only or invalid calendar strings do not contribute a date witness.

### Coordinate identity key

Latitude and longitude are each formatted to exactly five decimal places in WGS84. This is approximately metre-scale identity normalization over much of the globe and is used **only** inside the composite same-record witnesses. It is not occurrence thinning, spatial matching for the ecological analysis, or the 10-km support grid.

## 4. Collision graph and connected-component closure

Each quality-admissible record receives every available identity token from the frozen witness set:

1. occurrence-ID lineage;
2. event ID;
3. catalog/specimen number;
4. dataset key + event day + five-decimal coordinate key;
5. normalized recorder + event day + five-decimal coordinate key.

Records sharing a token are connected in an undirected graph. The graph is then closed over **connected components across witness types**.

If a component contains at least one `x` record and at least one `y` record, **every record in that component is excluded from both partners before denominators are calculated**.

This closes a subtle leakage route. For example, if `X1` shares event ID with `Y1`, and `Y1` shares specimen lineage with `X2`, all three records are contaminated as one connected evidence component even though `X1` and `X2` do not share the same token directly.

A component containing only one partner is not removed by this cross-partner rule.

## 5. Meaning of “independent records”

For this sampling preflight, `independent_records` means **records retained after the declared cross-partner contamination exclusion and coordinate-quality gate**.

It does **not** mean statistically IID sampling events, and this branch does not add an unplanned within-partner thinning rule after seeing data. The already-frozen unique-cell and inverse-Simpson effective-cell floors provide separate protection against extreme spatial pseudoreplication.

## 6. Frozen 10-km support grid

For already projected EPSG:6933 metres,

`cell = (floor(easting / 10000), floor(northing / 10000))`.

The zero origin and floor rule are explicit, including for negative projected coordinates. Cell origin or edge cannot be shifted after counts are opened.

## 7. Required audit output

The preprocessing result must retain, per partner:

- raw rows;
- coordinate-quality exclusions;
- quality-exclusion reasons;
- records with missing coordinate uncertainty;
- collision exclusions;
- mixed-partner collision components and their witness types;
- retained records;
- occupied 10-km cells;
- inverse-Simpson effective cells.

These are denominator diagnostics. None is an ecological result.

## 8. State-machine position

The response-blind chain is now:

`literature declaration -> taxonomy gate -> authorization guard -> occurrence quality gate -> cross-partner collision closure -> sampling summaries -> frozen sampling gate -> later model/invariant analysis`

A downstream stage cannot rescue an upstream failure.

## 9. Still not authorized

The committed execution manifest remains fail-closed. This implementation step does not authorize:

- occurrence search or download;
- occurrence counts or maps;
- empirical sampling-preflight classification;
- environmental extraction;
- invariant evaluation;
- process knockout.

The next empirical action, if separately authorized, is therefore mechanically narrow: execute the frozen sampling preflight only for the already frozen eligible pair set, with all preprocessing decisions above unchanged.
