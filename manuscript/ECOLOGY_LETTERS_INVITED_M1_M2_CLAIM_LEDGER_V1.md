# Ecology Letters invited positive-core claim ledger v1

## Active contribution

The invited manuscript contains two positive contributions from distinct evidentiary types, and a separate retrospective sensitivity audit:

1. **M2 empirical:** prospectively frozen same-target cross-source reproducibility on 12 held-out taxa.
2. **M1 structural:** exact invalid-state decomposition and the separation between process qualification and endpoint false-discovery reliability.

3. **Post-freeze technical sensitivity (not an independent biological endpoint):** restored GBIF 10,215-object source, 59 original taxa refitted, 24 reference q95 thresholds recalibrated, and the original 12 heldout taxa re-evaluated without changing selection rules. The original 0/12 taxon-level non-exceedance pattern recurred; strict retention of every originally evaluable cell **failed**.

The empirical ledger remains **1 historical independent heldout endpoint**. The retrospective source-repair audit contributes **0** additional independent biological endpoints. No focal Level-B/Level-C biological candidate result is needed for the manuscript.

## Allowed claims

| ID | Status | Claim |
|---|---|---|
| EL1 | empirical | 0/12 prospectively held-out taxa contained a frozen-envelope exceedance among evaluable cells. |
| EL2 | empirical | 283 of 288 prespecified diagnostics were evaluable; five remained unresolved because at least one source-specific answer failed adequacy. |
| EL3 | empirical | The closest observed/envelope ratio was 0.988, so the held-out closure was not uniformly far from the boundary. |
| EL4 | exact analytic | `FPR_zero - FPR_gated = 1-a1`. |
| EL5 | exact analytic | `TPR_zero - TPR_gated = 1-a0`. |
| EL6 | exact analytic | If `a1=a0=a`, both increments equal `1-a`. |
| EL7 | exact analytic | For unconditional `pi=P(F=false)`, qualified-call FDF is `(1-pi)a1(1-q)/[(1-pi)a1(1-q)+pi a0 sp]` (when any call can occur); only equal positive validity fractions cancel. The `pi=.10,q=.80,sp=.99` example gives FDF≈0.645 **under equal validity**; asymmetric cases yield ≈0.586 (`a1=.70,a0=.90`) or ≈0.700 (`a1=.90,a0=.70`). This is analytic, not field evidence. |
| EL8 | synthesis | Preserving unresolved states can prevent unsupported negatives without preventing positive closure when the required evidence is present. |
| EL9 | post-freeze sensitivity, not independent replication | After restoration of 510 GBIF Parquet objects (9,705 to 10,215), 47 reference + 12 heldout taxa were refitted across 2,832 source-specific model cells; 0 of 2,832 fitted cells remained unresolved. |
| EL10 | post-freeze sensitivity | All 24 prespecified reference q95 thresholds were recalibrated under the unchanged >=30-adequate-reference-taxa rule; 1,033/1,128 reference paired cells were eligible. |
| EL11 | post-freeze sensitivity | Repaired heldout results had 285/288 evaluable cells, three unresolved, **0/12 taxa with an exceedance**. This is conditional taxon-level recurrence, not an independent ecological confirmation. |
| EL12 | coverage limitation | Of the **283 originally evaluable** heldout cells, only **282 remained evaluable**; one was lost and three previously unresolved cells became evaluable. The pre-opening all-original-283-cell coverage criterion **failed**; `source_completeness_0_of_12_robust=false`. |
| EL13 | model-adequacy mechanism | The lost *Nothofagus antarctica* 150-km specimen cell had mean outer-fold rank **0.6045→0.6105** but SEM **0.0975→0.1160**, moving mean−SEM **0.5070→0.4945** across the original **0.50** gate. The four changed paired-cell eligibility states reflect four source-specific CV adequacy flips, not ecological mechanism changes. |
| EL14 | descriptive paired comparisons | Across 282 common evaluable heldout cells, median restored-minus-original discordance was **+0.000698** (range −0.096457 to +0.173309); across 24 q95 thresholds the median change was **+0.000275** (range −0.071800 to +0.047002). Individual variations can be appreciable; median stability is not universal invariance. |
| EL15 | submission boundary | The signed terminal category is `repaired_source_no_attention_but_original_283_cell_coverage_decreased`. This is **HOLD_FOR_SENSITIVITY_REVIEW**, with 0 new independent empirical ledger increments. |

## Prohibited claims

- 283 independent biological replicates.
- 283/283 as a binomial success experiment.
- universal source invariance.
- q95 as a nominal 95% predictive interval or alpha=.05 test.
- preserved specimens and human observations have identical observation processes.
- Level-C dependency confirmation or falsification.
- Cremastra, Belonocnema or SMIL001 as evidence for the focal paper.
- the structural identities estimate natural frequencies of missingness or invalidity.
- observation-process qualification guarantees a called biological violation is true.
- process necessity or causal mechanism.
- repaired GBIF source completeness was a new independent prospective or biological replication.
- full robustness under retention of all original 283 evaluable cells, or `source_completeness_0_of_12_robust=true`.
- ignoring the lost originally evaluable cell because three formerly ineligible cells became evaluable.
- treating 285 repaired evaluable cells as independent biological replicates or as an unqualified 285/285 success experiment.
- concluding that 0/12 is robust for every original procedure/M/taxon comparison.
- replacing the historical 283/288, 0/12 empirical endpoint or recounting the restored-source sensitivity as a new independent endpoint.
- presenting median source-version changes as uniformly small across all cells or as evidence that observation processes are identical.
