# Evidence-boundary structural result

This active note preserves the positive methodological result that is separate from the Level-A empirical short report.

## Exact invalid-state decomposition

For a hard relation in which a biological negative is admissible only on a valid observation key, let

- `a1 = P(valid key | F=true)`;
- `a0 = P(valid key | F=false)`;
- `q` be key-level sensitivity conditional on `F=true` and a valid key;
- `sp` be specificity conditional on `F=false` and a valid key.

If invalid keys are incorrectly collapsed into biological negatives, then the exact class-conditional changes are

`FPR_zero - FPR_gated = 1 - a1`

and

`TPR_zero - TPR_gated = 1 - a0`.

When validity is class-independent (`a1=a0=a`), both increments equal `1-a`. This is an analytic identity, not an empirical frequency estimate.

The frozen state-dependent audit gives a representative example with `a1=0.70`, `a0=0.90`, `q=0.95`, and `sp=0.99`: false-violation rate rises from 0.035 to 0.335 when invalid states are collapsed, whereas apparent true-violation sensitivity rises from 0.891 to 0.991.

## Qualification does not control false discovery

Let `pi=P(F=false)` denote unconditional true-violation prevalence over all keys. If observation validity differs by latent class, the false-discovery fraction among **qualified violation calls** is

`FDF = (1-pi)*a1*(1-q) / [(1-pi)*a1*(1-q) + pi*a0*sp]`,

provided the denominator is positive. If no qualified violation calls can occur, FDF is **undefined**, not zero. The shorter form `(1-pi)*(1-q) / [(1-pi)*(1-q) + pi*sp]` applies for equal positive validity fractions (`a1=a0>0`). Alternatively the shorter form always applies when `pi` is **redefined** as prevalence among valid keys, rather than prevalence among all keys.

For the equal-validity illustrative case, `pi=0.10`, `q=0.80`, and `sp=0.99` give `FDF≈0.645`. With the same unconditional prevalence and response characteristics but `a1=0.70, a0=0.90`, FDF is ≈0.586; reversing validities (`a1=0.90, a0=0.70`) gives ≈0.700. These are exact structural examples, **not** frequencies estimated from field data.

Thus an observation gate can authorize whether a negative is admissible without ensuring that a called violation is reliable. Class-dependent observation validity can also change the prevalence composition of the qualified set. Replication or aggregation remains a separate evidentiary layer.

## Scope

This result is positive and remains active, but it is **not part of the Level-A Ecology Report**. It explains why the broader 284b program preserves unresolved states instead of converting missing or invalid observations into biological zeros.

The result is structural/synthetic and does not establish a focal Level-C biological dependency.
