# GBIF 2026-08-01 source-manifest integrity: missing-multiple-of-20 repair

**Date of discovery:** 2026-11-16 (JST)
**Status:** exact original S3 object manifest **recovered and cryptographically
verified**. Training-row identity and NEON-voucher overlap remain **unresolved**.
This audit does not open a new biological endpoint or change the historical
Level-A result.

## Why the source-model reconstruction first failed

A replay of the published GBIF August-2026 Parquet directory for
*Artemisia tridentata* (frozen snapshot specieskey `GX2B`) gave
**3,420 PRESERVED_SPECIMEN 0.05-degree thinned presences** whereas the
signed model-fit artifact contains **3,285**. The original source-input
denominators were checked directly against the signed archived artifact
10089523542. The November replay stopped before reporting NEON datasetKey
source membership because the source-denominator gate failed. This was
appropriate; data-independent external validation cannot be inferred.

### S3 object-identity replay

A new metadata-only S3 listing was compared with the original frozen
2026-09-04 manifest receipt (original Actions run 33869400385).
The exact same prefix `occurrence/2026-08-01/` now contains:

| Scope | At 2026-09-04 freeze | At 2026-11-16 replay |
|---|---:|---:|
| Occurrence Parquet objects | **9,705** | **10,215** |
| All S3 objects, including citation | **9,706** | **10,216** |
| Canonical manifest SHA-256 | `1b5b2dde8a23e78beafac1d122830e0552c2fbdac4086e9d9d8c161814a7163e` | `ca0d9844cd6816b4e4d550a0152db489b5e6a4c5129f8700fe2f1d818b954cd2` |
| Citation `citation.txt` SHA-256 | `022a524b59c4c037b28f252c08294e0f22c5eb7b3bce5c52a0a5fc6016f17050` | unchanged |

The additional **510 files** are **exactly** numeric filenames divisible
by 20: `000020,000040,…,010200`, with S3 `LastModified` between
**2026-10-23T15:41:19Z and 15:42:18Z**. The 9,705 other file objects retain
`LastModified` of 2026-08-01.

Removing precisely these 510 files from the November object metadata
recovers **9,706 objects** whose *complete canonical SHA-256 (keys,
ETags, byte sizes and LastModified timestamps)* equals the original
September value **exactly**. This is a strong reconstruction of the
original **object set**, not merely an approximate count match.

The origin of the missing-file pattern is independently documented in
GBIF's own repository:
https://github.com/gbif/occurrence/issues/609
(opened 2026-10-23, reporting absent multiples-of-20 Parquet files
in monthly GBIF AWS snapshots since July 2025).

The 510 added Parquet objects are ~4.99% of the current file count
(**not** proof that they represent precisely 4.99% of taxon records).
These metadata checks did not read a single GBIF occurrence row.

## Restored-file raw occurrence exposure of both frozen panels

For a targeted descriptive source-integrity check, **only the 510 restored
Parquet objects** were scanned. The species inventories were not selected
using these outcomes: all **12 originally frozen held-out taxa** (12
snapshot `specieskey` values) and all **47 original successor-reference
taxa** (79 frozen historical `specieskey` values) were retained. Only
`specieskey`, `basisofrecord`, `occurrencestatus`, and `datasetkey`
were projected. Raw identifiers and coordinates were not saved, and no
NEON field observations or model predictions were evaluated.

| Original analysis panel | Restored `HUMAN_OBSERVATION` raw `PRESENT` records | Restored `PRESERVED_SPECIMEN` raw `PRESENT` records | Taxa with at least one restored record |
|---|---:|---:|---:|
| Level-A held-out panel | **15,329** | **2,688** | **12/12** |
| Reference calibration panel | **335,772** | **19,058** | **47/47** |

These are records selected by the historical taxon concept keys and
GBIF occurrence status, **not** spatially thinned/model-admitted counts,
and they do not describe additional unique presence locations or
independent plot observations. It would be wrong to treat these counts
as the magnitude or direction of a model prediction shift.

Both source modes and both reference/held-out panels are materially
exposed to the repaired source, with a *much larger raw HUMAN_OBSERVATION
restoration count*. Consequently, the original 24 q95 calibration
envelopes and the 12-taxon held-out comparison could both change.
The evidence does not determine the sign of their changes.
Scanning **only the restored files** found zero direct NEON voucher
`datasetKey` rows in those subsets; it provides **no** guarantee
about historical 9,705-file model inputs or duplicated data under
other GBIF publication keys.

Results:
- `results/gbif_restored510_heldout12_exposure_v1.json`
- `results/gbif_restored510_reference47_exposure_v1.json`

A future restored-source sensitivity analysis is now specified
**before any corrected model outcome is opened**, at
`config/gbif_missing20_restoration_sensitivity_v1.json`.
Its 47+12 biological units, 24 procedure×M reference cells and
original adequacy/quantile rules are immutable. It must report missing
and unestimable states, may not replace taxa, and cannot be counted
as an independent fresh-taxon ecological validation.

## Consequences for 284b

1. The Level-A 12-taxon held-out result (0/12 above frozen envelopes;
   283/288 evaluable) remains a valid **historical endpoint conditional on
   the incomplete September-observed 9,705-file snapshot**. That original
   result and mathematical M1 statements are not edited in place.
2. The currently advertised date prefix is **not an immutable data
   identity**, and naive replay with 10,215 files is a *different*
   experiment. The extra 135 thin-presence rows in the initial
   Artemisia reanalysis are consistent with this source change,
   but causal attribution requires replay on the recovered 9,705-file set.
3. Original source completeness and source-model sensitivity to a
   restored file set remain **unmeasured**. Do not call the original
   experiment universally reproducible on today's public GBIF data.
   A new completeness sensitivity rerun would be a **new,
   separately versioned** ecological endpoint, not a repair of the
   previously signed same-target result.
4. Source datasetKey overlap with NEON has **not** been tested yet:
   the attempted November query had the wrong source input denominator.
   That provenance gate remains a hard STOP. Neither missing/added
   file counts nor metadata signatures establish which NEON vouchers
   entered the original model.

## Concrete corrective action

The reproducibility path is now fixed. Use ONLY the 9,705 filenames whose
numeric basename is **not** divisible by 20; require their full source
object-list SHA-256 to match the 2026-09-04 frozen value *before* reading
occurrences. The new validation script
`scripts/audit_original_gbif_neon_historical_replay_v2.py`
uses those paths for the same original GBIF scanner and data-cleaning
rules, and checks both signed model source counts for the sole
predeclared species `Artemisia tridentata`:

- PRESERVED_SPECIMEN: **3,285**
- HUMAN_OBSERVATION: **4,516**

Only on exact model-input count reproduction may aggregate
NEON voucher `datasetKey`
`3fed506c-d04f-4cd4-b373-bd602572f39b` membership be interpreted
as an *input lineage check*. No raw occurrence identifiers, locations,
NEON plots or NEON species labels are saved. A zero count for this single
datasetKey is NOT equivalent to complete source independence.

### Machine-readable audit references

- Frozen original: `legacy/pre_level_a_focus/results/product_b_v7_2_snapshot_metadata_freeze_v0_1.json`
- November full source integrity: `results/neon_original_gbif_manifest_replay_v1.json`
- Cryptographically recovered original object set:
  `results/neon_aug_gbif_missing20_recovery_v1.json`
- Signed original model counts:
  `config/original_gbif_neon_datasetkey_pilot_v1.json`
- Targeted historical replay:
  `scripts/audit_original_gbif_neon_historical_replay_v2.py`
- Original, prospectively frozen Level-A empirical receipt:
  `results/product_b_same_target_core19_v0_4_heldout_final_receipt.json`

**New empirical conclusion ledger increment: 0.**
