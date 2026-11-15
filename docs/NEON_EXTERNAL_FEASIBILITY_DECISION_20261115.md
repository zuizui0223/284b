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

## Geographical and scale mismatch that could invalidate the test

A 400 m² plot-scale detection label and a CHELSA-bioclimate
distribution surface do not have the same spatial grain.
Before reading NEON species labels, require a *label-blind* spatial
estimability check using released plot coordinates: both frozen
source-specific models must generate more than one distinguishable
score across a site's plot keys. A site where all plot locations
collapse to one CHELSA climate cell cannot test within-site ranking;
it must not be interpreted as ecological evidence for or against the
model. If fewer than three independent sites provide score contrast
and qualified complete surveys for a taxon, that taxon's
**within-site discrimination endpoint is unestimable**.

The original seven-taxon candidate list and the rule requiring at
least three externally evaluable taxa remain frozen; there must be no
post-outcome taxon substitutions or adaptive threshold changes.

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
