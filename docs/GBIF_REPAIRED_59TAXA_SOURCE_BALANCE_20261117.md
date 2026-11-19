# GBIF source-restoration heterogeneity: fixed 59 taxa (17 November 2026)

## Evidence and boundary

This is a **source-input metadata synthesis, not an ecological prediction or new independent holdout**. The original public GBIF 2026-08-01 snapshot had 9,705 Parquet files; the same nominal prefix contained 10,215 after 510 missing files were restored on 23 October. The fixed reference 47-taxon and heldout 12-taxon source audits have independently passed original signed-source, taxonomy, input-count, raw-parity and deterministic spatial-thinning checks.

Using exactly those already verified data-quality receipts, the new 59-taxon auditor compares admitted, spatially-thinned model inputs by source. No raw occurrence rows, plot labels, old or repaired ecological prediction scores or q95 calibration are read.

| Source | Original signed 59-taxon inputs | Repaired inputs | Increase |
|---|---:|---:|---:|
| PRESERVED_SPECIMEN | 103,633 | 107,357 | 3.59345% |
| HUMAN_OBSERVATION | 1,010,173 | 1,033,261 | 2.28555% |

At least one source mode increased by 5% or more for **13/59** taxa. HUMAN_OBSERVATION/PRESERVED_SPECIMEN input ratio increased in **34** and decreased in **25** taxa. The maximum specimen-relative increase was **26.7273%** in the original reference species *Artemisia filifolia*.

The difference between source modes and taxa shows why a single uniform missingness multiplier cannot reproduce the input composition of the repaired models. This result neither demonstrates changed predicted suitabilities nor establishes any ecological mechanism.

## Reproducibility

- Audited source receipts: results/gbif_repaired_heldout12_thinning_v1.json, results/gbif_repaired_reference47_thinning_v1.json.
- Source-only code: scripts/audit_gbif_repaired_59taxa_source_balance_v1.py.
- Fail-closed tests: tests/test_gbif_repaired_59taxa_source_balance_v1.py.
- CI: .github/workflows/gbif_repaired_59taxa_source_balance_v1.yml.
- Outputs, when verified by CI: results/gbif_repaired_59taxa_source_balance_v1.json and results/gbif_repaired_59taxa_source_balance_cells_v1.csv.

The program validates original source-audit statuses, panel sizes (12 and 47), species uniqueness, reference/heldout original totals, source-specific non-negative differences, pre-existing raw-count parity and absence of opened ecological response/validation endpoints. Summary contains SHA-256 digests of the two original input receipts.

## Paper consequence

Keep original historical Level-A **283/288 evaluable, 0/12 taxon-envelope exceedance** as its separate time-stamped empirical endpoint. Submission remains on **HOLD** until all 47 fixed reference models and 12 heldout models are re-fitted under SHA-matched original 12-block centers and the same original 2,000-row M frames, the 24 q95 ceilings are recalibrated, and the 12 heldout taxa are evaluated once under the repaired source. This analysis does not lift the HOLD and adds **zero** independent empirical biological conclusions.
