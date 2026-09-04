# Product-B v7.2 — snapshot-stable occurrence transport engineering

## Why v7.2 exists

JOS001 crossed the occurrence boundary only as an engineering pilot. Its focal `Yucca brevifolia` query entered multi-page GBIF `/occurrence/search` pagination, but the server-reported total count changed between pages. The already-frozen fail-closed transport therefore stopped before a 50/30/10 sampling decision could be produced.

JOS001 is consumed and cannot be rerun. v7.2 is a new transport-engineering line, not a rescue of JOS001 and not a relaxation of any ecological or sampling threshold.

## Primary transport

v7.2 forbids live offset-based `/occurrence/search` as a scientific execution source. The primary source is one **GBIF monthly full occurrence snapshot** hosted in the public GBIF AWS Open Data bucket.

The first transport-engineering snapshot is frozen prospectively as:

- provider: AWS Open Data;
- region: `us-east-1`;
- bucket: `gbif-open-data-us-east-1`;
- snapshot date: `2026-08-01`;
- occurrence prefix: `occurrence/2026-08-01/occurrence.parquet/`;
- citation object: `occurrence/2026-08-01/citation.txt`.

This snapshot is frozen **before a new v7.2 engineering pair is selected**. No pair may be admitted until snapshot metadata auditing has succeeded.

## Metadata-only snapshot freeze

The initial snapshot audit may read only:

1. anonymous S3 object-listing metadata for the frozen snapshot prefix; and
2. the frozen snapshot's `citation.txt` object.

It may not download or inspect any Parquet occurrence data row.

The audit must record:

- the exact sorted object key set under the frozen snapshot prefix;
- object count and total bytes;
- an SHA256 digest of canonicalized `(key, size, ETag, last-modified)` metadata;
- the SHA256 digest of `citation.txt`;
- the DOI stated in `citation.txt`, if present;
- whether at least one `occurrence.parquet/` object exists.

Only after this metadata audit succeeds may a **new, previously unopened engineering pair** be selected under the existing v7.1 literature-only feasibility rules.

## Scientific contract remains unchanged

v7.2 changes transport semantics only.

- Direction remains `Y_requires_X`.
- X sampling floor remains >=50 independent records, >=30 unique 10-km cells and >=10 effective cells.
- Y remains primary-literature witness evidence, >=5 independent witnesses in >=3 unique 10-km cells.
- Witnesses cannot define the evaluation frame.
- Coordinate uncertainty ceiling remains 10 km.
- At least 5 sampling-adequate replacement hosts remain required.
- No opened v5-v7.1 pair can be reused.
- Candidate selection still cannot inspect occurrence counts, density maps, cell statistics, model support, invariant values or process-knockout values.

## Snapshot-native taxonomy boundary

GBIF cloud snapshots contain interpreted `taxonkey` / `specieskey` fields. Since snapshots from 2025-08-01 onward store these keys as strings in preparation for taxonomy transition, v7.2 does not silently assume that a legacy v5 checklist key is the same as a snapshot-native key.

For every future v7.2 pair and replacement host, a taxonomy-only bridge to the frozen snapshot's native interpreted taxon key must be frozen before Parquet rows are filtered. No occurrence availability may be used to choose or repair that bridge.

## Required snapshot fields

Before occurrence execution, the Parquet schema must independently confirm the availability and types of at least:

- `gbifid`, `datasetkey`, `occurrenceid`;
- `institutioncode`, `collectioncode`, `catalognumber`;
- `recordedby`, `eventdate`;
- `countrycode`, `occurrencestatus`;
- `decimallatitude`, `decimallongitude`, `coordinateuncertaintyinmeters`;
- `taxonkey`, `specieskey`, `scientificname`;
- `issue`, `license`, `lastinterpreted`.

If schema parity is inadequate for the frozen preprocessing contract, v7.2 stops at `unresolved_snapshot_schema`; fields are not silently dropped or substituted after occurrence rows are seen.

## Query semantics after a future pair is frozen

A future engineering execution will scan the **same frozen snapshot object set** for focal and controls. Filters must be declared before rows are opened and may include only the frozen snapshot-native taxon key, the independently declared country/frame filter, `occurrencestatus = PRESENT`, and non-null coordinates. The existing downstream coordinate-quality, projection, cell and sampling logic is reused.

## Secondary import path

A completed GBIF occurrence download may be imported only if an already-created download key, DOI, exact predicate, download metadata and archive SHA256 are frozen before the archive rows are opened. v7.2 will not store GBIF usernames/passwords and will not create authenticated downloads from repository CI.

## Nonretroactivity

- Never rerun JOS001 with the snapshot transport.
- Never use JOS001's partial live-search execution to select a v7.2 pair.
- Never compare snapshot counts with live-search counts to choose a favorable source.
- Never switch snapshot date after a future pair's occurrence rows are opened.
- A snapshot transport pass is engineering feasibility only until a newly held-out confirmatory endpoint is independently declared.
