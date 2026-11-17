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

Let `pi_valid=P(F=false | valid key)` be the prevalence of true violations *among valid keys*. Among qualified valid-key violation calls,

`FDF_valid = (1-pi_valid)(1-q) / [(1-pi_valid)(1-q) + pi_valid*sp]`.

At `pi_valid=0.10`, `q=0.80`, and `sp=0.99`, `FDF ≈ 0.645`. This remains the original illustrative calculation.

Crucially, if prevalence `pi_all` is instead defined over *all* at-risk keys, class-dependent validity does not cancel:

`FDF_all = (1-pi_all)*a1*(1-q) / [(1-pi_all)*a1*(1-q) + pi_all*a0*sp]`.

The conditional prevalence is `pi_valid = pi_all*a0 / [(1-pi_all)*a1 + pi_all*a0]`. Thus `pi_valid=pi_all` when `a1=a0>0`, but not generally. For illustration, `pi_all=.10, a1=.70, a0=.90, q=.80, sp=.99` gives `pi_valid=.125` and `FDF_all≈.586`. A zero probability of qualified calls makes FDF undefined.

Therefore a measurement gate can authorize whether a negative state is admissible without guaranteeing that a called violation is reliable on its own. Replication or aggregation rules remain a separate evidentiary layer. See `docs/qualified_fdf_prevalence_conditioning_v1.md` for the explicit derivation.

## Scope

This result is positive and remains active, but it is **not part of the Level-A Ecology Report**. It explains why the broader 284b program preserves unresolved states instead of converting missing or invalid observations into biological zeros.

The result is structural/synthetic and does not establish a focal Level-C biological dependency.
