# Spatial-confounding robustness receipt v0.1

The predeclared post-opening diagnostic asked whether the rainfall–co-calling association
persisted when inference was driven only by **weather variation within the same spatial
sampling unit**.

The frozen classification rule was:

- **spatially robust**: both diagnostics negative and both 95% CIs exclude zero;
- directionally consistent qualified: both negative but one or both CIs include zero;
- mixed: signs differ;
- spatial contradiction: either diagnostic is significantly positive.

## NAAMP: within route

Using 9,256 runs from 797 repeatedly sampled routes:

- beta on probability scale = **-0.01367**
- 95% CI = **[-0.01998, -0.00737]**
- p = **2.15 × 10^-5**

Thus the rain-recency direction remains within routes after removing all time-invariant
route differences.

## FrogID: within ERA5 weather cell

Using 40,020 recordings from 1,071 informative 0.25-degree ERA5 cells:

- beta on probability scale = **-0.04265**
- 95% CI = **[-0.05175, -0.03354]**
- p = **4.30 × 10^-20**

The diagnostic uses exact within-cell demeaning of the outcome, frozen dry-spell exposure,
month indicators, calendar year and local-hour sine/cosine terms, with cell-clustered SEs.

The first conditional-logit implementation failed computationally before an effect estimate
was opened. The replacement estimator was documented prospectively as a nonempirical
computational repair. A later serialization-only failure occurred after the repaired effect
was printed; the rerun emitted the same values as a durable artifact.

## Classification

**SPATIALLY ROBUST**

Static differences among routes or ERA5 cells in species pools, habitat, observer access,
or other time-invariant spatial properties are therefore insufficient to explain the
replicated direction.

This remains an observational association. Time-varying local confounding is not eliminated,
and the original NAAMP and FrogID effect estimates remain the primary results.
