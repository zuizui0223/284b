# NEON external plot evidence: preregistered feasibility protocol v1

Frozen before any NEON plant detection/absence counts are read on 2026-11-15.
This is a **separate feasibility study**, not an extension of the
confirmatory Level-A endpoint, and not a Level-C biological-dependency test.

## Motivation

The signed same-target Level-A endpoint establishes that two independently
fitted GBIF source models can agree *within an independently frozen
source-discordance envelope* on 12 held-out species. It does not establish
whether either agreed-upon predicted suitability pattern is ecologically
correct against separately standardized plant surveys.

The target-identity swap controls are post-hoc constructed errors. Their
observed behavior, even in high comparative climate overlap, does not
supply known labels of **natural biological mismatch**.

## Independent reference candidate

**NEON Plant presence and percent cover, DP1.10058.001**, proposed fixed
release `RELEASE-2026`. Provider documentation:
- https://data.neonscience.org/data-products/DP1.10058.001
- https://data.neonscience.org/data-api/endpoints/products/
- https://data.neonscience.org/data-api/endpoints/data-query/

The product documents taxonomically identified plant presence and percent
cover at nested 1, 10, and 100 m² subplots within 400 m² plots.
A completed standardized survey can support plot-level detection or a
*protocol-conditional non-detection*; no single incomplete or non-detection
plot proves species absence throughout the macroclimate pixel.
NEON reports that collection was suspended during 2026; the present study
would be limited to historical released surveys. NEON releases are
versioned, but the existence and contents of this exact product/release must
be independently checked.

## Frozen candidate taxa and structural gate

Before any NEON taxa/plot detections are read, the US-domain subset of the
previously opened 12 taxa is fixed to exactly seven species, listed verbatim
in `config/neon_external_validation_preflight_v1.json`.

No taxon may be added or replaced because its NEON performance is known.
At least three independent NEON sites and ten completed positive and
ten completed non-detection plot keys per taxon are required to evaluate a
taxon. At least three taxa must meet these pre-set structural gates. If
fewer do, stop with a *non-estimable* outcome, not an alternative dataset
or threshold adjustment.

## Evaluation design IF source integrity is independently verified

1. Audit whether original GBIF model-fitting records contain data derived
   from NEON plant surveys, vouchers or duplicated site-time records.
   Without evidence of independence, the NEON analysis is observational
   context, not truly external validation. The present historical GBIF
   models cannot simply be declared independent.
2. Resolve GBIF species concepts and NEON identification/uncertainty codes
   on a predeclared basis. A taxonomic uncertainty, an unsurveyed plot,
   unidentifiable taxon, or incomplete bout must be unresolved, never
   converted into species absence.
3. Align historical frozen model predictions for PRESERVED_SPECIMEN and
   HUMAN_OBSERVATION to NEON plot coordinates with appropriate CHELSA
   predictor values. Audit temporal and geographic extrapolation.
4. Test **rank discrimination for plot-scale detections against conditional
   non-detections** using held-out site blocks. Aggregate uncertainty at
   independent site and taxon levels. This is not a regional occupancy or
   negative interaction inference. Fix a positive/negative score before
   any external label is opened, and keep the original q95 reference
   separate: that envelope calibrated *source agreement*, not accuracy.
5. Compare the two source models' external ranking behavior. An agreement
   between them may coexist with poor external skill (a possible
   false-concordance case) or with robust skill, but not until directly
   measured. Do not impute plot absences from missing NEON records.

## Pre-flight endpoint

The only currently authorized action is reading NEON **product metadata**
without requesting species records or biological labels. A machine
receipt will describe product identity, release/site availability and
whether API access succeeded. It **cannot** certify that enough focal
species are surveyed or that NEON and GBIF data are fully independent.

A separate explicit source-provenance review and data-access decision is
required before any species-level outcome can be authorized. No broad
predictive performance claim or Ecology Letters Methods submission upgrade
follows automatically from metadata feasibility.
