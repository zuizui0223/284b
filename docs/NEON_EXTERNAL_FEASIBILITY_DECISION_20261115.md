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

## Source lineage audit: known NEON voucher dependency confirmed (16 November)

GBIF registry `3fed506c-d04f-4cd4-b373-bd602572f39b` identifies
the **NEON Biorepository Terrestrial Plant Collection (Herbarium Vouchers)**,
registered 2020-05-22, before the original 2026-08-01 GBIF source snapshot
(DOI 10.15468/bmmg36).

The original frozen public snapshot **initially contained only 9,705 GBIF
Parquet objects**, while 510 numbered multiple-of-20 files were subsequently
restored on 2026-10-23. A naive November scan of all 10,215 files falsely
failed the source-count parity check (3,420 instead of 3,285 thinned specimen
presences for *Artemisia tridentata*). Explicitly restricting the re-scan to
the **exact original 9,705 objects** (canonical full S3 manifest
`1b5b2dde8a23e78beafac1d122830e0552c2fbdac4086e9d9d8c161814a7163e`)
successfully reconstructed both signed source-specific denominators:
**3,285 PRESERVED_SPECIMEN and 4,516 HUMAN_OBSERVATION**.

The source-lineage check then established that **24 raw specimen records**
were from the specific NEON Biorepository voucher GBIF dataset. After
the original exact quality/admission/cross-mode-collision filters and 0.05°
source-specific spatial thinning, **2 actual input rows** still had that
NEON datasetKey in the original PRESERVED_SPECIMEN model source; **0** in
HUMAN_OBSERVATION. This is a **verified source-level dependency**, not
merely a potential registry publication route. Signed archive identities
and raw model-input denominators were checked in Actions run
`43790470181`, receipt
`results/neon_original_gbif_historical_replay_v2.json`.

**Inferential distinction:** these two records were GBIF specimens
published by a NEON biorepository. Their inclusion means that the
historical *Artemisia* specimen model **cannot be advertised as entirely
source-independent of NEON-derived biological materials**. It does
**not** demonstrate that either voucher was collected in any exact
2020–2024 NEON DP1.10058.001 plot-bout proposed for validation;
that record-level/plot-level overlap remains unknown. Neither
the two-row magnitude nor its possible impact on fitted predictions
has been measured.

This result changes the status of the planned external study:
**no unconditional independent NEON validation of the frozen historical
*Artemisia* specimen model**. To claim clean independence one would
need either a separately versioned leakage-excluded model fit plus a new
holdout, or demonstrably disjoint independent plot/event labels,
supported by record-lineage verification, before any NEON plant labels
are opened. The seven candidate taxa remain fixed without
outcome-based replacement. An additional historic-source provenance
audit covering **all seven** is underway in a separate locked workflow,
and is not yet an external prediction result.

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

1. **Accept the first historic-source lineage finding.** At least two
   NEON voucher rows entered the original *Artemisia* specimen model.
   Finish the seven fixed taxa provenance check, and audit alternative
   NEON/GBIF publication channels before any blanket independence claim.
   Direct voucher provenance and exact plot-outcome reuse are different.
   Independently validate only a separately qualified disjoint-source
   model or disjoint site/event holdout with documented exclusions.
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
