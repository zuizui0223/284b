# 284b — NEON external-validation feasibility decision (15 November 2026)

## Decision

**Metadata GO; independent biological validation STOP/UNRESOLVED.**

The historic Level-A experiment (12 held-out taxa, 283 evaluable cells,
five unresolved, zero reference-envelope exceedance taxa) does **not**
establish ecological predictive truth. NEON field plots are a promising
different data-generating process, but neither species-level eligibility
nor independence from original model fitting is established.

## Verified released source inventory

- NEON product: Plant presence and percent cover `DP1.10058.001`
- Fixed release: `RELEASE-2026`; published 2026-01-23
- DOI: https://doi.org/10.48443/9g4s-hq52
- NEON product endpoint: https://data.neonscience.org/api/v0/products/DP1.10058.001?release=RELEASE-2026
- Original public JSON SHA-256 matches two separately obtained responses:
  `623e78f46fc8fad3622275555954caea8f10e1dc582c67de34940d927b68fb41`.
- **47** listed NEON sites, **1,093 site×month availability memberships**,
  spanning **2013-06 through 2024-12**; 111 distinct listed months.
- Neither number is a count of complete plot surveys, taxonomic records,
  target plants, unique plot detections, or true absences.
- Product-specific metadata source receipt:
  `results/neon_external_metadata_preflight_v1.json`
  and repeated site-month audit:
  `results/neon_release_site_month_inventory_v2.json`.

## Independent-data leakage is an actual risk, not a confirmed event

GBIF registry `3fed506c-d04f-4cd4-b373-bd602572f39b` is the
**NEON Biorepository Terrestrial Plant Collection (Herbarium Vouchers)**;
registered **2020-05-22** (DOI 10.15468/bmmg36), six years before
284b's original **2026-08-01** GBIF snapshot.

That does **not** prove an individual NEON voucher was included in the
old source-model likelihood; it establishes a possible historical
republication route. The old model reader used `datasetkey`, `gbifid`,
`occurrenceid`, `catalognumber`, event date and coordinates in memory,
but under the old source contract raw row identifiers were not retained.
A metadata-only GBIF registry audit verifies this publication path:
`results/neon_gbif_registry_risk_v1.json`.

To inspect actual model-input membership without opening NEON species
outcomes, a **single predeclared taxon pilot** has been launched using
the exact original public GBIF snapshot. Its first requirement is to
reproduce the original signed model source-thinning counts for
*Artemisia tridentata*: 3,285 PRESERVED_SPECIMEN and 4,516
HUMAN_OBSERVATION presences. It outputs only aggregate datasetKey counts.
No conclusions should be based on this pilot until its signed audit
receipt and CI result are available. Absence of one known dataset key
would **not** establish complete third-source independence.

## Why treating plot non-detection as species absence is unsafe

NEON DP1.10058.001 records vegetation in nested 1, 10 and 100 m²
subplots. Complete 400 m² occurrence lists must be reconstructed as
the *union of nested measurements*, because larger nested subplots
typically report additional species rather than repeating taxa detected
at smaller scales. In 2019 onward, the larger subplots are sampled
biennially. In 2020 onward, the `samplingImpractical` and
`biophysicalCriteria` flags help identify unsampled or poor-quality
events. Sensitive-species identifications and taxon concept histories
also need checking.

The source code `scripts/neon_complete_bout_gate_v1.py` therefore
demands the full **6×1m² + 6×10m² + 4×100m²** records at a consistent
site/plot/event/bout, plus appropriate observability flags, before
authorizing a **protocol-conditional 400 m² non-detection**.
Missing or uncertain survey evidence remains **unresolved**.
Synthetic regression tests pass; **no real NEON plant outcomes have
been accessed**.

Primary potential interval: 2020–2024. Historical 2013–2019 site-month
metadata remains documented but is not silently considered equivalent
to the post-2020 fully flagged survey protocol.

## Geographical support audit and revised validation grain

A 400 m² plot (20 × 20 m) and CHELSA V2.1 `bio1`–`bio19`
climatologies (approximately kilometre-scale) **do not describe the
same spatial grain**. Site-internal plots may share the same model
predictor cell, giving identical predictions even when observed
species differ. A within-site plot-level ranking test is therefore
**not a defensible primary estimand without positive evidence of
within-site predictor-score variation**.

The primary candidate estimand is instead **between-site relative
ranking** of complete 400 m² plot-bout detection fractions against
two frozen source-specific climate-suitability model scores.
Sites, and then taxa, are the independent units; plot bouts within
one site are repeated/clustered measurements, not independent
macroclimate gradients. Even at site scale, a failure to detect a
species is not identified biological absence, and no causal inference
is licensed.

### Source-only geography completed before species labels

The `RELEASE-2026` public site metadata were successfully audited for
all 47 plant-product sites. They span **20 NEON ecological domains**
with 1,081 site-centroid pairs. The smallest pairwise centroid
distance is **1.697 km**, and no pair is within 1 km. This confirms
that sites provide geographically distinct centroids, **not**
that all sites have different CHELSA predictor vectors.

Separately, exactly seven signed historical `core19` comparison-frame
ZIPs (each with three M radii and 2,000 pre-frozen rows per radius)
were verified by artifact and internal parquet SHA-256. For each of
7 taxa × 3 M × 47 NEON site centroids = **987** possible combinations,
we computed the nearest geodesic distance from a site centroid to a
frozen source-blind comparison point. Using a predeclared 25 km
*geographic proximity proxy*, **all 21 taxon×M settings** had at
least **three** NEON site centroids near an original comparison
point (observed 4–16 sites per taxon×M). Thus geography alone does
not immediately rule out the seven-taxon screen.

This is **not proof** that the sites lie in the full biologically
accessible region for each taxon, that any focal species was detected
at NEON, that the historical models can produce distinct CHELSA
predictions at the actual field plots, or that their GBIF training
records are independent from NEON. The sample of 2,000 frame points
does not define the full M geometry. No taxon has been substituted,
and no NEON plant record or plot coordinate has been opened.

Source receipts:
`results/neon_site_geography_preflight_v1.json`,
`results/neon_frame_site_proximity_v1.json`, and
`results/neon_frame_site_proximity_cells_v1.csv`.
New estimand design version is **separate** from the originally frozen
`config/neon_external_validation_preflight_v1.json`, which is not
silently redefined after metadata review.

The original seven-taxon candidate list and minimum three evaluable
taxa remain unchanged. Without full survey completeness, enough
species-level variation, a source-independence audit, and identifiable
between-site model-score contrast, external validation remains
**STOP/UNRESOLVED**.

## Publication boundary and next gate

1. **Complete the exact-snapshot source datasetKey provenance pilot.**
   If direct NEON-voucher inputs are found, the current historical
   source model cannot be claimed to be independent of that voucher
   source. If none are found, other overlap channels still need audit.
2. Verify NEON raw-table schema, complete event coverage, real per-taxon
   presence/nondetection gate counts, and any site-level score variation
   only under a separately versioned and authorized opening contract.
3. Report stop/non-estimable if eligibility or independence cannot be
   established. Do not present a successful metadata availability
   check as a successful field validation.

Current empirical-ledger increment: **zero**. No Level-C focal
ecological dependency outcome was opened or inferred.

## Public protocol references

- NEON fixed data release: https://data.neonscience.org/data-products/DP1.10058.001/RELEASE-2026
- NEON Quick Start Guide v2: https://data.neonscience.org/api/v0/documents/quick-start-guides/NEON.QSG.DP1.10058.001v2?fallback=html&inline=true
- Official NEON plot aggregation implementation (pinned source):
  https://github.com/NEONScience/neonPlants/blob/d90c5fb75d22bc0334750ad57fccc1c1d2915459/R/stackPlantPresence.R
- NEON vouchers in GBIF: https://www.gbif.org/dataset/3fed506c-d04f-4cd4-b373-bd602572f39b
