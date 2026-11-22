# 284b

## Active scientific line (2026-11-22)

**Ecology Letters invited Method candidate:** [Relation endpoints for ecological inference: when independent answers can support joint biological claims](manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md)

The invited manuscript combines two *different kinds* of completed contribution:

1. **M2 empirical, historical Level A:** 12 prospectively held-out plant taxa, 288 prespecified source-comparison diagnostics (283 evaluable / 5 unresolved), and **0/12 taxa** exceeding their prespecified source-discordance envelopes. The independent biological replication is **12 taxa**, not the 283 technical diagnostics.
2. **M1 exact structural results:** coercing invalid observation keys to biological zero raises false-violation rate by exactly `1-a1` and apparent true-violation sensitivity by exactly `1-a0`. Qualification of an observation state is separate from endpoint false-discovery reliability.

### Crucial source-repair sensitivity (completed 2026-11-22)

After identifying **510 missing Parquet objects** in the nominal GBIF 2026-08-01 source, the original 47-reference and 12-heldout taxon panels were replayed under their exact historical spatial geometry and 2,000-row M comparison frames. The restored **10,215-object** source supports:

| Audit | Signed result |
|---|---:|
| Original geometry SHA reconstructed | 59/59 taxa |
| Repaired source-specific model cells sealed | 2,832/2,832 |
| Recalibrated q95 reference thresholds | 24/24 |
| Eligible reference paired comparisons | 1,033/1,128 |
| Repaired heldout comparison cells evaluable | 285/288 |
| Repaired heldout taxa exceeding q95 | **0/12** |
| Original 283 evaluable cells still evaluable | **282/283** |
| Historical originally eligible cells lost | **1** |
| Historical ineligible cells newly eligible | **3** |

**Disposition:** The heldout *taxon-level* no-exceedance pattern recurs under the repaired source, but the prespecified **strict full original-cell coverage condition fails**. The lost cell is *Nothofagus antarctica* (150 km, niche-forward C0.1/degree1, preserved specimens): its mean outer-fold rank improved, but its SEM increased, bringing mean−SEM below the unchanged 0.50 adequacy floor. No retrospective rescue, source redefinition, or extra independent biological endpoint is authorized.

**Submission status:** `HOLD_FOR_SENSITIVITY_REVIEW`. This is a conditional retrospective input-completeness check, **not** an independent ecological replication or a demonstration of full cell-level robustness. It does **not** replace the original signed Level A 0/12 endpoint.

Primary files:

- [Invited manuscript](manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md), [claim ledger](manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_CLAIM_LEDGER_V1.md), [submission readiness](manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_READINESS_V1.md)
- [Signed original Level A endpoint](results/product_b_same_target_core19_v0_4_heldout_final_receipt.json)
- [Separate restored-GBIF sensitivity terminal](results/gbif_repaired_heldout12_sensitivity_v1.json), [288-cell table](results/gbif_repaired_heldout12_sensitivity_cells_v1.csv)
- [Complete source-completeness decision and four-fold CV mechanism](docs/GBIF_REPAIRED_LEVEL_A_TERMINAL_DECISION_20261122.md)
- [Full source and geometry execution runbook](docs/GBIF_REPAIRED_LEVEL_A_59TAXON_SOURCE_SENSITIVITY_RUNBOOK_20261119.md)

## Fallback / legacy boundary

A standalone Level-A short report remains available in [`manuscript/LEVEL_A_SHORT_REPORT_V0_1.md`](manuscript/LEVEL_A_SHORT_REPORT_V0_1.md), but is a **fallback** only; it is not authorized for simultaneous submission and its historical-source claims require the same source-repair caveat before use.

Unresolved Level-B/Level-C biological candidates, earlier hunting and unopened dependency endpoints are preserved under `legacy/pre_level_a_focus/`. They are **not** positive evidence for the invited paper.

No model-fitting results, postterminal descriptive audits or source-completeness reconstructions should be counted as *new* independent empirical endpoints. The original Level A manuscript is **not yet authorized for submission**, and the invited Method has outstanding human metadata, coauthor approval, figure rendering, archive DOI and journal-policy checks.
