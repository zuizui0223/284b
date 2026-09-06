# First ten successor artifacts and post-fit integration checks

## Empirical scope

The fixed execution is run `34032659571`, SHA `5d16212538d8b25d12235d2bb11b9a5e184a113b`. The first-ten receipt is a completion-order diagnostic subset, not an estimate of the final 47-taxon outcome. The other 37 taxa are not classified by this receipt. Existing first-four and first-seven receipts are retained.

The ten audited artifacts contain 480 source fit cells: 442 final fits sealed, 329 answers adequate, 38 final-fit unresolved, 52 with incomplete outer-fold rows, 37 with nonfinite validation metrics and 24 below the frozen performance rule. The five disjoint states sum to 480. Of 240 paired cells, 152 are pre-discordance eligible and 88 unresolved.

The additional three taxa distinguish different failure layers:

| Taxon | Final fits sealed | Adequate answers | Pre-D eligible pairs |
| --- | ---: | ---: | ---: |
| Abies procera | 48/48 | 47/48 | 23/24 |
| Abies sibirica | 48/48 | 27/48 | 6/24 |
| Acacia melanoxylon | 30/48 | 0/48 | 0/24 |

For Abies sibirica all source cells have complete finite four-fold evidence, but 21 fail the frozen performance criterion. Acacia melanoxylon instead has 18 unresolved final fits, 16 incomplete-fold cases and 14 nonfinite-validation cases. Neither result establishes cross-source disagreement: no prediction member was decoded, no paired D or q95 was computed, and no process intervention was opened. Error-state differences do not alone identify biological causes.

Reproduce using the existing helper and exact archive IDs/hashes in `results/product_b_same_target_successor_first10_progress_v0_1.json`:

```sh
PYTHONPATH=. python scripts/audit_same_target_progress_receipt.py \
  --receipt results/product_b_same_target_successor_first10_progress_v0_1.json \
  --artifact-dir audit_zips --check
```

## Synthetic-only integration coverage

The added integration suite runs the existing feasibility, strict-calibration and strict-held-out CLI entry points on artificial 47-taxon and 12-taxon fixtures. All files live in a temporary directory. It does not run, restart or inspect any empirical fit or real paired prediction.

The fixture tests the unchanged 29-versus-30 eligible-taxa boundary, nearest-rank q95, retention of all 24 reference cells and all 288 held-out cells, reference equality versus strict exceedance, and closure for inadequate answers or unavailable references. Negative sentinel scores in forbidden cells and a recording wrapper test that those cells do not reach the caller through the filtered reader. Pre-D feasibility is run with Arrow dataset access prohibited. Incomplete artifact inventory and an empty authorization set are also checked.

The numbers produced by these fixtures are software expectations, not biological results or new reference thresholds. The running empirical execution, scientific contracts and existing post-fit controller are unchanged.
