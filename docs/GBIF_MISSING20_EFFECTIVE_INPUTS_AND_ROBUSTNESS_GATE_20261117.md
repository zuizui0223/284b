# 284b — GBIF missing20 source repair: model-input consequences (17 November 2026)

**Status:** verified original-vs-repaired input **source quality audit** for the fixed 12 Level-A held-out taxa, not a completed predictive model robustness experiment.

## Exact comparison

The September-2026 original model used a 2026-08-01 public GBIF S3 Parquet directory with **9,705** published occurrence files; on 2026-10-23 **510 originally missing modulo-20 filenames** were restored, giving **10,215**. The original full S3 object manifest SHA-256 was exactly reconstructed by excluding those 510 October additions.

Using the unchanged original specieskey/basisofrecord/presence filters, original GBIF occurrence adapter, coordinate-quality gate (10,000 m maximum known uncertainty), cross-mode collision component exclusion and deterministic **0.05°** source-specific spatial thinning, the repaired source was evaluated on **all 12 predeclared taxa**. For each species and source, repaired raw counts were required to equal original archived raw counts plus independently counted records from the 510 restored objects. **All 12** taxa passed this check. Each original fit ZIP was independently SHA-verified; each source had a fixed input denominator across original eight procedures and three M radii.

### Effective model-input shifts

| Original observation mode | September source-thinned inputs | Repaired source-thinned inputs | Absolute delta | Relative delta |
|---|---:|---:|---:|---:|
| PRESERVED_SPECIMEN | 15,654 | 16,134 | +480 | +3.07% |
| HUMAN_OBSERVATION | 31,727 | 32,675 | +948 | +2.99% |

| Fixed held-out taxon | Original → repaired PRESERVED_SPECIMEN | Original → repaired HUMAN_OBSERVATION |
|---|---:|---:|
| *Artemisia tridentata* | 3,285 → 3,420 | 4,516 → 4,757 |
| *Atriplex canescens* | 2,686 → 2,821 | 2,990 → 3,137 |
| *Encelia farinosa* | 1,259 → 1,303 | 2,590 → 2,655 |
| *Avicennia germinans* | 1,253 → 1,276 | 1,474 → 1,505 |
| *Avicennia marina* | 1,118 → 1,131 | 3,021 → 3,088 |
| *Laguncularia racemosa* | 1,365 → 1,378 | 1,450 → 1,477 |
| *Nothofagus antarctica* | 182 → 186 | 495 → 510 |
| *Nothofagus betuloides* | 91 → 91 | 235 → 240 |
| *Eucalyptus globulus* | 1,164 → 1,200 | 5,595 → 5,691 |
| *Abies lasiocarpa* | 1,056 → 1,095 | 2,471 → 2,539 |
| *Eucalyptus delegatensis* | 176 → 176 | 551 → 556 |
| *Larix laricina* | 2,019 → 2,057 | 6,339 → 6,520 |

**All 12 taxa changed in at least one mode**; specimen counts changed in **10/12** and human-observation counts changed in **12/12**. None of the 12 saw a reduced thinned source-count total in either mode, although record representatives within existing grid cells may have changed. These are *model-input population size changes*, **not** projected suitability effects.

The raw originally missing records across the same 12 taxa were 2,688 PRESERVED_SPECIMEN and 15,329 HUMAN_OBSERVATION; the quality/collision/thinning gates reduced those to an increase in effective inputs of 480 and 948 respectively. In particular, the missing20 incident is not a uniform 5% inclusion-weight adjustment per source or species.

## External-NEON provenance boundary

Using the **9705 original frozen file set**, each of seven predeclared NEON-candidate taxa also exactly reproduced its original signed model input counts. The known NEON Biorepository herbarium voucher GBIF dataset contributed **6** actual source-thinned fit rows in **3/7** species (*Artemisia tridentata* 2; *Atriplex canescens* 3; *Larix laricina* 1). All six were PRESERVED_SPECIMEN rows, and none has been confirmed to correspond to a prospective 2020–2024 NEON vegetation plot outcome. Four species had no selected row from that one datasetKey; other publication channels and record aliases remain unexamined. Thus **unconditional NEON-source independence has not been qualified**.

## Why the q95/Level-A result is still unresolved

Source-thinned presence deltas do not determine how the eight SDM procedures, spatial folds, predicted ecological-suitability maps, model adequacy or calibrated reference q95 ceilings will change. The reference cohort itself contained additional raw records in all **47/47** fixed reference taxa; therefore the old q95 baseline cannot simply be re-used as if its calibration distribution were unaffected.

The eight-shard source-input audit for **all 47 fixed original reference taxa** has now
**completed successfully** in Actions run `43901310863`. All eight shards
passed, all original signed reference model-fit ZIP digests and 79 historical
taxon keys matched, and every taxon's repaired raw source counts equalled
its original raw counts plus the independently counted October backfill.

| Reference calibration source | September original source-thinned inputs | Repaired 10,215-file source-thinned inputs | Delta | Relative delta |
|---|---:|---:|---:|---:|
| PRESERVED_SPECIMEN | **87,979** | **91,223** | **+3,244** | **+3.69%** |
| HUMAN_OBSERVATION | **978,446** | **1,000,586** | **+22,140** | **+2.26%** |

**All 47/47 reference taxa** changed their original effective source-input
population in at least one mode; the PRESERVED_SPECIMEN count changed in
45/47 and HUMAN_OBSERVATION in 47/47. No taxon had a net decreased
source-thinned count in either mode. This is not a claim that the underlying
0.05° representative input row identity is unchanged when counts happen to
match.

Notable heterogeneous changes, pre-existing fixed taxa only:
*Artemisia filifolia* +26.73% PRESERVED_SPECIMEN input count,
*Onoclea sensibilis* +480 specimen inputs and +804 human-observation
inputs, *Populus tremula* +2,051 human-observation inputs,
*Viburnum opulus* +2,000 human-observation inputs.
These illustrate that a uniform 5% completeness correction is invalid
at the per-species/per-source modeling grain.

Verified machine receipt:
`results/gbif_repaired_reference47_thinning_v1.json`.
Even with 47+12 input populations reconstructed, **no repaired 47-taxon
model predictions, 24 reference q95 envelopes or repaired 12-taxon
paired-source agreement outcomes** have yet been computed.

The two legitimate upcoming research estimands are now separated in
`config/gbif_missing20_fixed_vs_rebuilt_geometry_v1.json`:
1. **Fixed-frame sensitivity:** rebuild source presences with restored records while holding the historical common M background rows, frozen 2000 comparison-row IDs, historical 12-block centers and model/adequacy procedures fixed; re-calibrate 24-cell q95 on the original 47 taxa before testing the original 12.
2. **Rebuilt-design sensitivity:** allow restored source occurrences to change the common source-blind area geometry and selected evaluation frame. This is separately versioned; model D values from nonidentical frames cannot be treated as directly paired.

**Original scientific endpoint unchanged:** prospective historical Level-A source agreement, 0/12 held-out taxa exceeding frozen envelopes (283/288 evaluable, five unresolved). **New independent biological endpoint count: zero.** This source-completeness robustness check cannot be promoted to a fresh, independent heldout experiment or to a causal biological mechanism.

## Reproducibility

- Source manifest repair `results/neon_aug_gbif_missing20_recovery_v1.json`
- Raw new records `results/gbif_restored510_heldout12_exposure_v1.json`, `results/gbif_restored510_reference47_exposure_v1.json`
- Verified source-thinned 12 taxa `results/gbif_repaired_heldout12_thinning_v1.json`
- Reference original 47 source audit `config/gbif_repaired_reference47_thinning_v1.json`
- Seven-taxon NEON source `results/neon_seven_taxon_original_source_lineage_v1.json`
- Full 59-taxon future comparison gate `config/gbif_missing20_restoration_sensitivity_v1.json`
- Primary and secondary geometric estimands `config/gbif_missing20_fixed_vs_rebuilt_geometry_v1.json`

No NEON plant observation outcomes, plot detections/absences, or repaired-source model predictions have been opened in this audit.
