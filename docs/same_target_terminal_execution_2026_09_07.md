# Successor run: terminal state and reference feasibility, 2026-09-07

## Execution has stopped; it is not still fitting

Source run `34032659571`, execution SHA `5d16212538d8b25d12235d2bb11b9a5e184a113b`, ended at 2026-09-07 01:31:10 UTC (10:31:10 JST). Forty-five taxon jobs succeeded and uploaded artifacts. Two were cancelled, and the aggregate was skipped. Both failed-job annotations explicitly report exceeding the configured 5h30m limit.

Missing artifacts are for index 8, **Alisma plantago-aquatica**, and index 35, **Populus tremula**. They are execution-unknown, not demonstrably poor models, and their predictions were neither imputed nor inspected. Repeatedly polling the original run will not complete it.

## Completed evidence, with the full denominator retained

The audit reads only contract.json, fit_inventory.csv and outer_cv_fold_metrics.csv from all 45 SHA256-verified archives. The existing progress-receipt helper validates each archive, and a per-cell replay independently reconciles the same state counts.

Across all 47 scheduled taxa / 2,256 source cells:

| Source-cell state | Count |
| --- | ---: |
| Answer adequate under the frozen four-fold rule | 1,581 |
| Final fit unresolved in a saved artifact | 266 |
| Outer-fold rows incomplete | 103 |
| Validation metric nonfinite | 144 |
| Complete finite evaluation below the performance floor | 66 |
| Execution artifact missing (two taxa) | 96 |

There are 1,894 sealed final fits among 2,160 source cells with saved artifacts. Across the full 1,128 paired-cell denominator, 730 pairs meet pre-discordance eligibility, 350 have known insufficient source evidence, and 48 remain execution-unknown. Twenty-three taxa support all 24 procedure/M comparisons. None of these counts establishes cross-source agreement.

## What completing only the missing two executions can change

For each frozen procedure/M cell, let n be the eligible distinct taxa among saved artifacts. Its final eligibility count lies between n and n+2 if only the two missing executions are completed and existing results remain fixed. These are logical bounds, not confidence intervals or an imputation assumption.

| Diagnostic category | Reference cells |
| --- | ---: |
| Already at least 30 eligible taxa | 12 |
| Below 30, but n+2 could reach 30 | 6 |
| Even n+2 is below 30 | 6 |

Observed counts (linear specification / quadratic specification):

| Strategy | M=150 km | M=300 km | M=500 km |
| --- | ---: | ---: | ---: |
| all | 26 / 27 | 27 / 30 | 25 / 27 |
| vif | 29 / 29 | 27 / 28 | 28 / 29 |
| predictive_forward | 33 / 36 | 36 / 36 | 36 / 37 |
| niche_forward | 30 / 32 | 28 / 33 | 31 / 30 |

This measures evaluation availability, not which strategy is biologically superior. The 45 completed taxa are not a random subsample; execution censoring may be informative. No strategy or M is selected from these counts.

## Information and execution boundary

The original complete-run authorization is unchanged. This diagnostic does not authorize calibration, even for the 12 cells whose observed count meets 30. Empirical paired D, q95, held-out outcomes and process interventions remain unopened.

The narrow recovery scope is now known: preserve all 45 original artifacts and complete only indices 8 and 35, with explicitly recorded continuation provenance rather than pretending the cancelled first attempt succeeded. A computational partition must preserve the frozen scientific model, common frame and all procedure/M cells. No such recovery run was started by this audit, and no new candidate panel or relaxed threshold is justified by it.

## Reproduction and provenance

Audit run `34076881576` succeeded at implementation SHA `8f6cbf4de123cb8c253b5ff3c7f07774650a471b`. Artifact `10002365752` contains the full audit, source job/artifact/run metadata, the reference-bound CSV and both cancellation annotations. Its ZIP SHA256 and every member SHA256 are recorded in `results/product_b_same_target_successor_terminal_receipt_v0_1.json`. The exact 45 source archive IDs and hashes are in the accompanying terminal_artifacts CSV; the terminal_taxa CSV retains all 47 rows, with blank unknown numeric values for missing executions.

```bash
PYTHONPATH=. python scripts/audit_same_target_terminal_run.py \
  --output-dir terminal_audit --archive-dir terminal_zips
```

This command requires authenticated read access through `gh`. It does not refit models, read prediction/model ZIP members, alter the original execution, or write to GitHub.
