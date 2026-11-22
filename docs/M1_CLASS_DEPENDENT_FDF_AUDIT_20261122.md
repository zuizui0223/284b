# M1 qualified-call false discovery under state-dependent validity

**Date:** 2026-11-22  
**Scope:** analytic correction to the active invited Method manuscript, NOT a new biological endpoint  
**Scientific state:** the historical Level-A endpoint and source-restoration terminal are unchanged; submission remains HOLD_FOR_SENSITIVITY_REVIEW.

## 1. Definitions and the estimand

Let F=true denote the biologically compatible function state and F=false a true functional violation, as in the frozen M1 hard-rule notation. A violation call can be issued only when a biological key is valid.

- pi = P(F=false): true violation prevalence among **all candidate keys**.
- a1 = P(valid key | F=true) and a0 = P(valid key | F=false).
- q = P(call function present | F=true, valid key): correct classification on a compatible valid key.
- sp = P(call function absent | F=false, valid key): correct violation classification on a truly violating valid key.

The M1 class-conditional rates FPR_gated=a1(1-q) and TPR_gated=a0*sp have **all underlying keys of the relevant latent class in their denominators**. Invalid keys contribute no violation call and are unresolved, not known biological negatives.

The zero-collapsing ablation instead gives FPR_zero=1-a1*q and TPR_zero=1-a0*(1-sp). Both original M1 identities remain exactly valid:

- FPR_zero - FPR_gated = 1-a1;
- TPR_zero - TPR_gated = 1-a0.

These are not conditional-on-classified-key rates.

## 2. Derivation of the corrected qualified-call FDF

Among all candidate keys, the joint probability of a false qualified violation call is

P(F=true AND valid AND call violation) = (1-pi)*a1*(1-q).

The joint probability of a true qualified violation call is

P(F=false AND valid AND call violation) = pi*a0*sp.

Therefore, when at least one qualified violation call is possible,

FDF_qualified = (1-pi)*a1*(1-q) / [(1-pi)*a1*(1-q) + pi*a0*sp].

If that denominator is zero, the false-discovery fraction is **undefined**. Assigning zero would silently conflate no calls with perfect precision.

**Equal-validity special case:** for a1=a0=a>0, the a factor cancels and

FDF_qualified = (1-pi)*(1-q) / [(1-pi)*(1-q) + pi*sp].

**Conditioning alternative:** whenever (1-pi)*a1 + pi*a0 > 0, define pi_valid = P(F=false | valid) = pi*a0 / [(1-pi)*a1 + pi*a0]. Then the same shorter formula applies with pi_valid instead of pi. Crucially, pi_valid generally differs from unconditional pi if a0 != a1.

The former manuscript stated that the valid-key fraction always cancels while defining pi only as the prevalence of violations. That conflated unconditional and valid-key-conditioned prevalence. This correction retains the original numerical example as an explicitly equal-validity example and provides the general class-dependent expression.

## 3. Exact illustrative checks

All rows assume the same unconditional prevalence pi=0.10, q=0.80 and sp=0.99. No row is an estimate from real ecological survey data.

| a1 | a0 | P(false qualified call) | P(true qualified call) | FDF among issued calls | pi_valid |
|---:|---:|---:|---:|---:|---:|
| 1.00 | 1.00 | 0.1800 | 0.0990 | 0.645161 | 0.100000 |
| 0.70 | 0.90 | 0.1260 | 0.0891 | 0.585774 | 0.125000 |
| 0.90 | 0.70 | 0.1620 | 0.0693 | 0.700389 | 0.079545 |

Selecting only valid keys can improve or worsen the composition of the evaluated set. The appropriate formula depends on which prevalence parameter is being reported.

## 4. Reproducibility and nonpromotion guard

- Implementation: scripts/relation_endpoint_contract.py, function qualified_violation_false_discovery_fraction.
- Regression tests: tests/test_m1_fdf_validity_asymmetry_20261122.py; asserts both asymmetric cases, equal-validity invariance, conditional-prevalence equivalence, undefined zero-call case, input bounds, and original 1-a1/1-a0 identities.
- Submission surfaces corrected: invited Method manuscript Section 4/5, claim ledger EL7, Figure 4 plan, active M1 structural note and submission-readiness gate.
- The analytic correction **does not** change q95, original/resored GBIF fits, heldout 283/288 and 0/12, restored 285/288 and 0/12, the one originally eligible cell lost (282/283 retained), or the historical empirical-ledger count of 1.
- It **does not** make a field estimate of state-dependent observability, independently validate ecological interactions or authorize Level-C conclusions.
- The inviting journal's coauthors must still review the mathematical statement and the separately coverage-limited source-completeness sensitivity before submission; status remains HOLD_FOR_SENSITIVITY_REVIEW.

**Important boundary:** this note records a correction discovered in the submission manuscript and an exact analytic extension. It does not retrospectively alter the predeclared empirical contract or claim a second independent study.
