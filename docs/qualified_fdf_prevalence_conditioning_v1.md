# Qualified hard-call FDF: prevalence conditioning (analytic audit v1)

**Status:** mathematical clarification only; no new empirical endpoint or Level-C opening.

## States and conditioning

Among at-risk biological keys, let `F=true` mean a compatible function and
`F=false` a genuine violation; `V` means the key is valid for negative
inference. Define:

- `pi_all=P(F=false)` before validity filtering;
- `a1=P(V|F=true)`, `a0=P(V|F=false)`;
- `q=P(detect F|V,F=true)` (valid-key sensitivity);
- `sp=P(call F absent|V,F=false)` (valid-key specificity).

A *gated* hard-violation call requires `V` and an absent-function
classification. Therefore, as fractions of all at-risk keys:

`P(false call)=(1-pi_all)*a1*(1-q)`

`P(true call)=pi_all*a0*sp`

and, provided at least one qualified call can occur,

`FDF_all=[(1-pi_all)*a1*(1-q)] / [(1-pi_all)*a1*(1-q)+pi_all*a0*sp]`.

By Bayes' rule, the true-violation prevalence **among valid keys** is

`pi_valid=pi_all*a0 / [(1-pi_all)*a1+pi_all*a0]`

whenever valid-key mass is nonzero. Substituting `pi_valid` into the
conditional-valid formula gives

`FDF_valid=(1-pi_valid)*(1-q) / [(1-pi_valid)*(1-q)+pi_valid*sp]`.

The two expressions are identical once their prevalence denominators are
matched. In particular, if `a1=a0>0`, then `pi_valid=pi_all` and the
valid-key factor cancels. If `a1!=a0`, **it does not cancel for a fixed
population prevalence**.

An exact corollary makes the selection effect transparent. For nondegenerate
probabilities (0 < FDF < 1), the false-discovery *odds* are

`FDF_all/(1-FDF_all) = [(1-pi_all)/pi_all] * [a1/a0] * [(1-q)/sp]`.

Thus relative to equal validity at the same population prevalence and
conditional detection characteristics, the FDF odds are multiplied by
`a1/a0`. Higher validity for compatible versus violating keys increases
false-discovery odds; the reverse reduces them. This is a theoretical
selection statement, not a directional ecological prediction.
If qualified calls have zero probability, FDF is undefined (not zero).

## Source-safe illustrative numbers

With `pi_all=.10, q=.80, sp=.99` and equal nonzero validity:
`FDF=.18/(.18+.099)=.645161...`.

For the *illustrative* class-specific validity fractions `a1=.70, a0=.90`,
with the same `pi_all,q,sp`:
`pi_valid=.125` and
`FDF=.126/(.126+.0891)=.585774...`.

These are analytic demonstrations, **not ecological observations**, not a
new positive empirical conclusion, and not estimates of real missingness.
The original frozen Level-A result (12 taxa, 283 evaluable cells) and M1
invalid-state identities (`1-a1`, `1-a0`) are unchanged.

## Reproducibility

Implementation: `scripts/relation_endpoint_contract.py` functions
`qualified_violation_false_discovery_fraction` and
`valid_key_violation_prevalence`.

Regression tests: `tests/test_qualified_fdf_prevalence.py`.
