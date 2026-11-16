# Ecology Letters invited positive-core claim ledger v1

## Active contribution

The invited manuscript contains only two completed positive contributions:

1. **M2 empirical:** prospectively frozen same-target cross-source reproducibility on 12 held-out taxa.
2. **M1 structural:** exact invalid-state decomposition and the separation between process qualification and endpoint false-discovery reliability.

No focal Level-B/Level-C biological candidate result is needed for the manuscript.

## Allowed claims

| ID | Status | Claim |
|---|---|---|
| EL1 | empirical | 0/12 prospectively held-out taxa contained a frozen-envelope exceedance among evaluable cells. |
| EL2 | empirical | 283 of 288 prespecified diagnostics were evaluable; five remained unresolved because at least one source-specific answer failed adequacy. |
| EL3 | empirical | The closest observed/envelope ratio was 0.988, so the held-out closure was not uniformly far from the boundary. |
| EL4 | exact analytic | `FPR_zero - FPR_gated = 1-a1`. |
| EL5 | exact analytic | `TPR_zero - TPR_gated = 1-a0`. |
| EL6 | exact analytic | If `a1=a0=a`, both increments equal `1-a`. |
| EL7 | exact analytic | Process qualification does not control endpoint false-discovery fraction; at `pi_valid=.10,q=.80,sp=.99`, FDF is approximately .645. | 
| EL7a | exact analytic | If `pi_all` is defined before validity filtering, FDF also depends on class-specific validity `a1,a0`; the simplification using `pi_all` requires `a1=a0>0`. |
| EL7b | exact analytic | With nondegenerate probabilities, class validity multiplies FDF odds by `a1/a0` relative to equal validity at fixed population prevalence and `q,sp`. |
| EL8 | synthesis | Preserving unresolved states can prevent unsupported negatives without preventing positive closure when the required evidence is present. |
| EL9 | post-freeze data-integrity audit | The 2026-09-04 frozen GBIF source object set had 9,705 Parquet files; 510 modulo-20 files were added on 2026-10-23. Excluding exactly those 510 files restores the complete original canonical object manifest SHA-256. The 12-taxon Level-A result is conditional on the original incomplete source. This is metadata provenance, not a new biological endpoint. |

## Prohibited claims

- 283 independent biological replicates.
- 283/283 as a binomial success experiment.
- universal source invariance.
- evidence of robustness to the October-2026 repaired 10,215-file GBIF snapshot without a separate rerun.
- a claim that the current 2026-08-01 GBIF S3 directory is byte-for-byte identical to the September-2026 frozen source.
- inference that exactly 5% of focal taxon presences were missing just because 510 of 10,215 Parquet files were absent.
- q95 as a nominal 95% predictive interval or alpha=.05 test.
- preserved specimens and human observations have identical observation processes.
- Level-C dependency confirmation or falsification.
- Cremastra, Belonocnema or SMIL001 as evidence for the focal paper.
- the structural identities estimate natural frequencies of missingness or invalidity.
- observation-process qualification guarantees a called biological violation is true.
- process necessity or causal mechanism.
